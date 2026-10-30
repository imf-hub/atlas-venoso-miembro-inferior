const KEY = 'atlas/valoraciones-v1.json';
const ATLAS = 'https://anatomia.flebologiamexico.com';
const SELF = 'https://opiniones-atlas-venoso-imf.ferver.chatgpt.site';
const allowed = new Set([ATLAS, SELF, 'http://127.0.0.1:8810']);
const empty = () => ({version: 1, votes: {}});
export function summarize(data) {
  const stars = [0, 0, 0, 0, 0];
  let likes = 0;
  for (const v of Object.values(data.votes)) {
    if (v.like) likes++;
    if (v.rating) stars[v.rating - 1]++;
  }
  const ratings = stars.reduce((a, b) => a + b, 0);
  const sum = stars.reduce((a, b, i) => a + b * (i + 1), 0);
  return {likes, ratings, average: ratings ? Math.round(sum / ratings * 100) / 100 : null, stars};
}
const wait = ms => new Promise(resolve => setTimeout(resolve, ms));
async function hash(token) {
  return [...new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(token)))].map(b => b.toString(16).padStart(2, '0')).join('');
}
function dashboard(stats) {
  return `<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Opiniones del Atlas · IMF</title><style>body{margin:0;background:#f6f7f8;color:#17232a;font:16px/1.6 system-ui}main{max-width:760px;margin:8vh auto;padding:28px}h1{font-size:32px;line-height:1.2}.brand{color:#a71d24;font-size:12px;font-weight:700;letter-spacing:.1em}.cards{display:flex;flex-wrap:wrap;gap:16px}.card{flex:1;min-width:145px;padding:24px;background:white;border:1px solid #d8dee3;border-radius:12px}.card strong{display:block;font-size:36px;color:#09603c}a{color:#09603c}table{border-collapse:collapse;width:100%;margin:26px 0}td,th{text-align:left;padding:10px;border-bottom:1px solid #d8dee3}.note{color:#52616a;font-size:14px}</style><main><p class="brand">INSTITUTO MEXICANO DE FLEBOLOGÍA</p><h1>Así valoran los usuarios el atlas</h1><p>Likes y estrellas recibidos desde el Atlas Anatómico Venoso.</p><div class="cards"><div class="card"><strong>${stats.likes}</strong>Me gusta</div><div class="card"><strong>${stats.average ?? '—'}</strong>Media de 5 estrellas</div><div class="card"><strong>${stats.ratings}</strong>Valoraciones</div></div><table><thead><tr><th>Estrellas</th><th>Valoraciones</th></tr></thead><tbody>${stats.stars.map((n, i) => `<tr><td>${i + 1} de 5</td><td>${n}</td></tr>`).reverse().join('')}</tbody></table><p><a href="/">Actualizar resumen</a> · <a href="/api/summary" download="resumen-atlas.json">Ver datos del resumen</a> · <a href="${ATLAS}">Volver al atlas</a></p><p class="note">Cada navegador conserva un identificador aleatorio para actualizar su voto sin sumarlo de nuevo. Cambiar de navegador o borrar sus datos puede permitir otra valoración. Estos números representan opiniones, no visitas ni personas únicas verificadas.</p></main></html>`;
}
export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin');
    const path = new URL(request.url).pathname;
    const headers = {'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff', 'Vary': 'Origin'};
    if (allowed.has(origin)) Object.assign(headers, {'Access-Control-Allow-Origin': origin, 'Access-Control-Allow-Methods': 'GET, POST, OPTIONS', 'Access-Control-Allow-Headers': 'Content-Type', 'Access-Control-Max-Age': '86400'});
    const json = (data, status = 200) => Response.json(data, {status, headers});
    if (origin && !allowed.has(origin)) return json({error:'Origen no permitido.'}, 403);
    if (request.method === 'OPTIONS') return new Response(null, {status: 204, headers});
    if (!env.BUCKET) return json({error:'El guardado no está disponible.'}, 503);
    try {
      if (request.method === 'GET' && (path === '/' || path === '/api/summary')) {
        const object = await env.BUCKET.get(KEY);
        const stats = summarize(object ? await object.json() : empty());
        if (path === '/api/summary') return json(stats);
        return new Response(dashboard(stats), {headers: {...headers, 'Content-Type':'text/html; charset=utf-8', 'Content-Security-Policy':"default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; frame-ancestors 'none'"}});
      }
      if (path !== '/api/vote') return json({error:'Ruta no encontrada.'}, 404);
      if (request.method !== 'POST') return json({error:'Método no permitido.'}, 405);
      if (!origin || !allowed.has(origin)) return json({error:'Origen requerido.'}, 403);
      if (!request.headers.get('Content-Type')?.startsWith('application/json')) return json({error:'Formato no permitido.'}, 415);
      const text = await request.text();
      if (text.length > 512) return json({error:'Solicitud demasiado grande.'}, 413);
      let input;
      try { input = JSON.parse(text); } catch { return json({error:'Solicitud inválida.'}, 400); }
      const {token, like, rating, revision} = input || {};
      if (typeof token !== 'string' || !/^[a-f0-9-]{36}$/.test(token) || typeof like !== 'boolean' ||
          !(rating === null || Number.isInteger(rating) && rating >= 1 && rating <= 5) ||
          !Number.isSafeInteger(revision) || revision < 1 || revision > Date.now() + 120000) return json({error:'Valoración inválida.'}, 400);
      const id = await hash(token);
      for (let attempt = 0; attempt < 7; attempt++) {
        const object = await env.BUCKET.get(KEY);
        const data = object ? await object.json() : empty();
        const previous = data.votes[id];
        if (previous && previous.revision >= revision) return json({saved:true, ...summarize(data)});
        data.votes[id] = {like, rating, revision};
        const result = await env.BUCKET.put(KEY, JSON.stringify(data), {
          onlyIf: object ? {etagMatches: object.etag} : {etagDoesNotMatch:'*'},
          httpMetadata: {contentType:'application/json'}
        });
        if (result) return json({saved:true, ...summarize(data)});
        await wait(150 + Math.random() * 300);
      }
      return json({error:'Hay varias valoraciones en curso. Vuelve a intentarlo.'}, 503);
    } catch {
      return json({error:'No se pudo guardar o consultar la valoración. Vuelve a intentarlo.'}, 503);
    }
  }
};
