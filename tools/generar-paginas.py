#!/usr/bin/env python3
"""Genera las páginas estáticas para buscadores a partir de los datos de la herramienta (index.html):

  - anatomia-venosa-miembros-inferiores/index.html   guía con todas las venas
  - venas/<vena>/index.html                           una página por vena
  - sitemap.xml
  - la lista de venas con enlaces dentro del <noscript> de index.html

Uso (desde cualquier carpeta, requiere Python 3 y Node):
    python tools/generar-paginas.py

Cada vez que cambies una ficha en index.html, vuelve a ejecutarlo y sube los archivos generados.
"""
import datetime
import html
import io
import json
import os
import re
import struct
import subprocess
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

SITE = 'https://anatomia.flebologiamexico.com/'
IMF = 'https://flebo.mx/'
OFERTA = 'https://flebo.mx/oferta-educativa/'
BOLETIN = 'https://boletin.flebologiamexico.com/'
GUIDE_PATH = 'anatomia-venosa-miembros-inferiores/'
GUIDE = SITE + GUIDE_PATH
TODAY = datetime.date.today().isoformat()
E = html.escape

res = subprocess.run(['node', os.path.join('tools', 'extraer-datos.js'), 'index.html'], capture_output=True, check=True)
D = json.loads(res.stdout.decode('utf-8'))
V, REFS = D['V'], D['REFS']
REFBYN = {r['n']: r for r in REFS if 'n' in r}

SYSORDER = [
    ('sup', 'Venas superficiales', 'sistema venoso superficial'),
    ('deep', 'Venas profundas', 'sistema venoso profundo'),
    ('perf', 'Venas perforantes', 'grupo de las venas perforantes'),
    ('pel', 'Venas pélvicas', 'sistema venoso pélvico'),
]
SYSNAME = {k: n for k, n, _ in SYSORDER}
SYSDESC = {k: d for k, _, d in SYSORDER}


def slugify(t):
    t = unicodedata.normalize('NFD', t).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')


ORDER = [v for k, _, _ in SYSORDER for v in V if v['sys'] == k]
SLUG = {}
for v in ORDER:
    s = slugify(v['n'])
    assert s not in SLUG.values(), 'slug repetido: ' + s
    SLUG[v['id']] = s
URLV = lambda v: f'venas/{SLUG[v["id"]]}/'


def png_size(path):
    with open(path, 'rb') as f:
        h = f.read(24)
    return struct.unpack('>II', h[16:24])


LW, LH = png_size('assets/logo-imf.png')

STYLE = '''
:root{--bg:#EEF0F3;--surface:#fff;--ink:#16181C;--muted:#575C64;--line:#E0E3E8;--line2:#CDD2D9;--accent:#C62821;--accent-ink:#fff;--tint:#FBEDEC;
 --f-display:"Montserrat","Public Sans",system-ui,sans-serif;--f-body:"Public Sans",system-ui,-apple-system,"Segoe UI",sans-serif;--f-latin:"Source Serif 4",Georgia,serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0F1012;--surface:#1A1B1E;--ink:#EDEDEE;--muted:#A8ABB0;--line:#2B2D31;--line2:#3B3E44;--accent:#E5544B;--accent-ink:#fff;--tint:#2A1B1B;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0F1012;--surface:#1A1B1E;--ink:#EDEDEE;--muted:#A8ABB0;--line:#2B2D31;--line2:#3B3E44;--accent:#E5544B;--accent-ink:#fff;--tint:#2A1B1B;color-scheme:dark}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:84px}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.65 var(--f-body)}
a{color:var(--accent)}
a:focus-visible,button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.top{position:sticky;top:0;z-index:10;background:var(--surface);border-bottom:2px solid var(--accent)}
.top-in{max-width:1100px;margin:0 auto;min-height:64px;display:flex;align-items:center;gap:8px 22px;flex-wrap:wrap;padding:6px max(16px,env(safe-area-inset-right,0px)) 6px max(16px,env(safe-area-inset-left,0px))}
.top img{display:block;height:44px;width:auto}
.top .logo-w{display:none}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .top .logo-c{display:none}:root:not([data-theme="light"]) .top .logo-w{display:block}}
:root[data-theme="dark"] .top .logo-c{display:none} :root[data-theme="dark"] .top .logo-w{display:block}
.top nav{margin-left:auto;display:flex;gap:6px 20px;flex-wrap:wrap;font:600 14.5px var(--f-body)}
.top nav a{text-decoration:none;color:var(--ink);padding:8px 2px}
.top nav a:hover{color:var(--accent)}
main{max-width:860px;margin:0 auto;padding:36px max(16px,env(safe-area-inset-right,0px)) 56px max(16px,env(safe-area-inset-left,0px))}
.crumbs{font-size:13.5px;color:var(--muted);margin:0 0 14px}
.crumbs a{color:var(--muted)}
h1{font:800 clamp(30px,5vw,44px)/1.1 var(--f-display);letter-spacing:-.02em;margin:0 0 16px;text-wrap:balance}
.lead{font-size:18px;line-height:1.6;margin:0 0 22px;max-width:62ch}
.cta{display:flex;flex-wrap:wrap;gap:10px 12px;margin:0 0 30px}
.btn{display:inline-flex;align-items:center;gap:8px;padding:13px 20px;border-radius:8px;font:600 15px var(--f-body);text-decoration:none;border:1.5px solid var(--accent)}
.btn.p{background:var(--accent);color:var(--accent-ink)}
.btn.s{background:var(--surface);color:var(--accent)}
.btn:hover{filter:brightness(1.08)}
.toc{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin:0 0 36px}
.toc h2{font:700 16px var(--f-display);margin:0 0 10px}
.toc ul{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:8px}
.toc a{display:inline-flex;gap:8px;align-items:center;text-decoration:none;color:var(--ink);border:1px solid var(--line2);border-radius:99px;padding:6px 14px;font-size:14.5px;font-weight:500}
.toc a span{font-size:12px;color:var(--muted)}
.toc a:hover{border-color:var(--accent);color:var(--accent)}
.sys{margin:0 0 44px}
.sys>h2{font:800 clamp(24px,3.4vw,30px)/1.15 var(--f-display);margin:0 0 18px;padding-bottom:10px;border-bottom:2px solid var(--accent)}
.vein{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:22px 24px;margin:0 0 16px}
.vein h3{font:700 22px/1.2 var(--f-display);margin:0}
.vein h3 a{color:inherit;text-decoration:none}
.vein h3 a:hover{color:var(--accent)}
.latin{font:italic 400 18px var(--f-latin);color:var(--muted);margin:4px 0 10px}
.pills{margin:0 0 6px;display:flex;gap:6px;flex-wrap:wrap}
.pill{font-size:12px;font-weight:600;padding:2px 10px;border:1px solid var(--line2);border-radius:99px;color:var(--muted);text-decoration:none}
a.pill:hover{border-color:var(--accent);color:var(--accent)}
.alt{margin:0 0 6px;color:var(--muted);font-size:14.5px}
.vein h4,.vein.single h2{font:700 15px var(--f-display);margin:16px 0 2px}
.vein.single h2{font-size:19px;margin:22px 0 4px}
.vein.single h2:first-of-type{margin-top:6px}
.vein p{margin:0}
.vfoot{display:flex;justify-content:space-between;gap:8px 16px;flex-wrap:wrap;margin-top:18px!important;padding-top:14px;border-top:1px solid var(--line);font-size:14.5px;color:var(--muted)}
.vfoot a{font-weight:500}
.see3d{font-weight:600!important;text-decoration:none}
.see3d:hover{text-decoration:underline}
.refs h2,.block h2{font:800 clamp(22px,3.2vw,28px)/1.15 var(--f-display);margin:0 0 10px;padding-bottom:10px;border-bottom:2px solid var(--accent)}
.refs h3{font:700 12px var(--f-body);letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin:22px 0 6px}
.reflist{margin:0;padding:0;list-style:none}
.reflist li{position:relative;padding:8px 0 8px 3em;font-size:14.5px;line-height:1.55;border-bottom:1px solid var(--line)}
.reflist li::before{content:"[" attr(value) "]";position:absolute;left:0;color:var(--accent);font-weight:600;font-variant-numeric:tabular-nums}
.reflist li:target{background:var(--tint)}
.src{white-space:nowrap}
.notes{margin:28px 0 0;font-size:13.5px;color:var(--muted)}
.block{margin:0 0 40px}
.rel{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:8px}
.rel a{display:inline-block;text-decoration:none;color:var(--ink);border:1px solid var(--line2);border-radius:99px;padding:6px 14px;font-size:14.5px;font-weight:500;background:var(--surface)}
.rel a:hover{border-color:var(--accent);color:var(--accent)}
.pn{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;margin:0 0 40px}
.pn a{flex:1 1 240px;text-decoration:none;color:var(--ink);background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:14px 18px;font-weight:600}
.pn a small{display:block;font:500 12px var(--f-body);color:var(--muted);letter-spacing:.06em;text-transform:uppercase;margin-bottom:2px}
.pn a:hover{border-color:var(--accent)}
.pn .next{text-align:right}
.imf{background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:12px;padding:22px 24px;margin:0 0 44px}
.imf h2{font:800 22px/1.2 var(--f-display);margin:0 0 6px}
.imf p{margin:0 0 14px}
.imf ul{margin:0;padding-left:1.1em}
.imf li{margin:4px 0}
footer{background:#141414;color:#E9E9EA;border-top:4px solid var(--accent)}
.foot-in{max-width:1100px;margin:0 auto;padding:28px max(16px,env(safe-area-inset-right,0px)) 28px max(16px,env(safe-area-inset-left,0px));display:flex;flex-wrap:wrap;gap:20px 40px;justify-content:space-between;font-size:14px;line-height:1.7}
footer a{color:#fff}
footer p{margin:0}
footer ul{list-style:none;margin:0;padding:0}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
'''

NOTES = ('Contenido revisado contra la bibliografía citada (octubre de 2026). Huesos y músculos del modelo 3D: BodyParts3D, © DBCLS, '
         'CC BY-SA 2.1 Japón, adaptados; las venas y su relación con estas estructuras son modelado propio del IMF. '
         'Nomenclatura según el consenso internacional de anatomía venosa (UIP/IFAA). Material docente: no sustituye el juicio clínico.')

ORG = {
    "@type": "Organization", "@id": IMF + "#org", "name": "Instituto Mexicano de Flebología y Linfología, S.C.",
    "alternateName": "Instituto Mexicano de Flebología", "url": IMF, "logo": SITE + "icon-512.png",
    "sameAs": [IMF, OFERTA, BOLETIN],
}


def shell(title, desc, path, og_type, graph_nodes, main, og_title=None):
    url = SITE + path
    og_title = og_title or title
    graph = {"@context": "https://schema.org", "@graph": graph_nodes + [ORG]}
    return f'''<!doctype html>
<html lang="es-MX">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#1A1B1E" media="(prefers-color-scheme: dark)">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="es_MX">
<meta property="og:site_name" content="Instituto Mexicano de Flebología">
<meta property="og:title" content="{E(og_title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{E(og_title)}">
<meta name="twitter:description" content="{E(desc)}">
<meta name="twitter:image" content="{SITE}og-image.png">
<script type="application/ld+json">{json.dumps(graph, ensure_ascii=False)}</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;700;800&family=Source+Serif+4:ital,opsz,wght@1,8..60,400&family=Public+Sans:wght@400;500;600&display=swap">
<style>{STYLE}</style>
</head>
<body>
<header class="top"><div class="top-in">
  <a href="/" aria-label="Anatomía venosa 3D del IMF"><img class="logo-c" src="/assets/logo-imf.png" width="{LW}" height="{LH}" alt="Instituto Mexicano de Flebología"><img class="logo-w" src="/assets/logo-imf-blanco.png" width="{LW}" height="{LH}" alt=""></a>
  <nav aria-label="Principal"><a href="/">Modelo 3D</a><a href="/{GUIDE_PATH}">Guía de anatomía</a><a href="{OFERTA}" target="_blank" rel="noopener">Aprende en el IMF</a><a href="{BOLETIN}" target="_blank" rel="noopener">Boletín</a></nav>
</div></header>
<main>
{main}
</main>
<footer><div class="foot-in">
  <div><p><b>Instituto Mexicano de Flebología y Linfología, S.C.</b></p><p>Formación médica en flebología, linfología y ecografía vascular.</p><p>© 2026 IMF. Material de uso académico.</p></div>
  <ul><li><a href="{IMF}" target="_blank" rel="noopener">flebo.mx</a></li><li><a href="{OFERTA}" target="_blank" rel="noopener">Aprende flebología en el IMF</a></li><li><a href="{BOLETIN}" target="_blank" rel="noopener">Boletín de noticias flebológicas</a></li><li><a href="/">Anatomía venosa 3D</a></li><li><a href="/{GUIDE_PATH}">Guía de anatomía venosa</a></li></ul>
</div></footer>
</body>
</html>
'''


def write(path, text):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    io.open(path, 'w', encoding='utf-8', newline='').write(text)


IMF_BLOCK = f'''  <section class="imf" aria-labelledby="imf-h">
    <h2 id="imf-h">Aprende flebología en el IMF</h2>
    <p>El Instituto Mexicano de Flebología forma médicos en flebología, linfología y ecografía vascular. Esta herramienta es parte de ese material docente.</p>
    <ul>
      <li><a href="{OFERTA}" target="_blank" rel="noopener">Oferta educativa del IMF</a>: cursos y programas para médicos.</li>
      <li><a href="{IMF}" target="_blank" rel="noopener">flebo.mx</a>: sitio del Instituto Mexicano de Flebología.</li>
      <li><a href="{BOLETIN}" target="_blank" rel="noopener">Boletín de noticias flebológicas</a>: noticias de flebología.</li>
    </ul>
  </section>'''


def ref_links(arr, base=''):
    return ' '.join(f'<a href="{base}#ref-{n}">[{n}]</a>' for n in sorted(arr))


def ref_li(r):
    u = f' <a class="src" href="{E(r["u"])}" rel="noopener" target="_blank">Ver fuente ↗</a>' if r.get('u') else ''
    return f'<li id="ref-{r["n"]}" value="{r["n"]}">{E(r["a"])}{u}</li>'


# =====================================================================  guía
toc = ''.join(f'<li><a href="#{k}">{n} <span>{sum(1 for v in V if v["sys"] == k)}</span></a></li>' for k, n, _ in SYSORDER)
sections = ''
for k, heading, _ in SYSORDER:
    arts = ''
    for v in [x for x in V if x['sys'] == k]:
        alt = f'<p class="alt">También: {E(v["alt"])}</p>' if v['alt'] else ''
        pair = '<span class="pill">Pareadas</span>' if v['pair'] else ''
        arts += f'''
    <article class="vein" id="v-{v['id']}">
      <h3><a href="/{URLV(v)}">{E(v['n'])}</a></h3>
      <p class="latin">{E(v['ta'])}</p>
      <p class="pills"><span class="pill">{E(v['ab'])}</span>{pair}</p>
      {alt}
      <h4>Trayecto</h4><p>{E(v['curso'])}</p>
      <h4>Drena en</h4><p>{E(v['drena'])}</p>
      <h4>Ecografía</h4><p>{E(v['us'])}</p>
      <h4>Relevancia clínica</h4><p>{E(v['clin'])}</p>
      <p class="vfoot"><span>Referencias: {ref_links(v['refs'])}</span><span><a class="see3d" href="/{URLV(v)}">Ficha completa →</a> · <a class="see3d" href="/#v-{v['id']}">Ver en el modelo 3D →</a></span></p>
    </article>'''
    sections += f'\n  <section class="sys" id="{k}">\n    <h2>{heading}</h2>{arts}\n  </section>'

reflist, open_ol = '', False
for r in REFS:
    if 'g' in r:
        reflist += ('</ol>' if open_ol else '') + f'<h3>{E(r["g"])}</h3><ol class="reflist">'
        open_ol = True
    else:
        reflist += ref_li(r)
reflist += '</ol>' if open_ol else ''

G_TITLE = 'Anatomía venosa de los miembros inferiores: guía | IMF Flebología'
G_DESC = ('Guía de anatomía venosa de los miembros inferiores: trayecto, drenaje, ecografía y relevancia clínica de cada vena '
          'de la pierna y el muslo. Con modelo 3D interactivo del IMF.')
g_main = f'''  <p class="crumbs"><a href="/">Anatomía venosa 3D</a> › Anatomía venosa de los miembros inferiores</p>
  <h1>Anatomía venosa de los miembros inferiores</h1>
  <p class="lead">Guía de las venas de la pierna y el muslo, organizadas por sistema: superficial, profundo, perforante y pélvico. De cada vena encontrarás su trayecto, adónde drena, cómo se ve en la ecografía y por qué importa en la clínica. Es el texto de referencia del Anatomía venosa 3D del Instituto Mexicano de Flebología.</p>
  <div class="cta">
    <a class="btn p" href="/">Abrir el modelo 3D interactivo</a>
    <a class="btn s" href="{OFERTA}" target="_blank" rel="noopener">Aprende flebología en el IMF</a>
  </div>
  <nav class="toc" aria-label="Índice de esta guía"><h2>En esta guía</h2><ul>{toc}<li><a href="#referencias">Referencias</a></li></ul></nav>
{sections}
{IMF_BLOCK}
  <section class="refs" id="referencias">
    <h2>Referencias</h2>
    {reflist}
    <p class="notes">{E(NOTES)}</p>
  </section>'''
g_nodes = [
    {"@type": "MedicalWebPage", "@id": GUIDE + "#page", "url": GUIDE, "name": "Anatomía venosa de los miembros inferiores",
     "description": G_DESC, "inLanguage": "es-MX", "isPartOf": {"@id": SITE + "#website"},
     "about": {"@type": "AnatomicalSystem", "name": "Sistema venoso del miembro inferior",
               "alternateName": ["Venas de la pierna", "Anatomía venosa de los miembros inferiores"]},
     "audience": {"@type": "MedicalAudience", "audienceType": "Clinician"}, "publisher": {"@id": IMF + "#org"},
     "image": SITE + "og-image.png", "primaryImageOfPage": {"@type": "ImageObject", "url": SITE + "og-image.png"},
     "hasPart": [{"@type": "WebPage", "url": SITE + URLV(v), "name": v['n']} for v in ORDER]},
    {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Anatomía venosa 3D", "item": SITE},
        {"@type": "ListItem", "position": 2, "name": "Anatomía venosa de los miembros inferiores", "item": GUIDE}]},
]
write(GUIDE_PATH + 'index.html', shell(G_TITLE, G_DESC, GUIDE_PATH, 'article', g_nodes, g_main, 'Anatomía venosa de los miembros inferiores'))


# =====================================================================  una página por vena
def first_sentence(t):
    return re.split(r'(?<=[.!?])\s', t.strip(), maxsplit=1)[0]


def trim(t, n):
    if len(t) <= n:
        return t
    return t[:n].rsplit(' ', 1)[0].rstrip(',;:.') + '…'


for i, v in enumerate(ORDER):
    path = URLV(v)
    url = SITE + path
    title = f'{v["n"]}: anatomía, trayecto y ecografía | IMF'
    if len(title) > 66:
        title = f'{v["n"]}: anatomía | IMF Flebología'
    desc = trim(f'{v["n"]} ({v["ta"]}): trayecto, drenaje, ecografía y relevancia clínica. {first_sentence(v["curso"])}', 158)
    intro = (f'{v["n"]} ({v["ta"]}), abreviada {v["ab"]}, forma parte del {SYSDESC[v["sys"]]} del miembro inferior. '
             f'{"Se presenta en pares. " if v["pair"] else ""}'
             'Esta ficha resume su trayecto, adónde drena, cómo se identifica en la ecografía y su relevancia clínica.')
    alt = f'<p class="alt">También llamada: {E(v["alt"])}</p>' if v['alt'] else ''
    pair = '<span class="pill">Pareadas</span>' if v['pair'] else ''
    cited = ''.join(ref_li(REFBYN[n]) for n in sorted(v['refs']) if n in REFBYN)
    same = [x for x in ORDER if x['sys'] == v['sys'] and x['id'] != v['id']]
    rel = ''.join(f'<li><a href="/{URLV(x)}">{E(x["n"])}</a></li>' for x in same)
    prev_, next_ = (ORDER[i - 1] if i > 0 else None), (ORDER[i + 1] if i < len(ORDER) - 1 else None)
    pn = ''
    if prev_:
        pn += f'<a class="prev" href="/{URLV(prev_)}"><small>← Anterior</small>{E(prev_["n"])}</a>'
    if next_:
        pn += f'<a class="next" href="/{URLV(next_)}"><small>Siguiente →</small>{E(next_["n"])}</a>'
    main = f'''  <p class="crumbs"><a href="/">Anatomía venosa 3D</a> › <a href="/{GUIDE_PATH}">Anatomía venosa de los miembros inferiores</a> › {E(v['n'])}</p>
  <h1>{E(v['n'])}</h1>
  <p class="latin">{E(v['ta'])}</p>
  <p class="pills"><span class="pill">{E(v['ab'])}</span>{pair}<a class="pill" href="/{GUIDE_PATH}#{v['sys']}">{E(SYSNAME[v['sys']])}</a></p>
  {alt}
  <p class="lead">{E(intro)}</p>
  <div class="cta">
    <a class="btn p" href="/#v-{v['id']}">Ver esta vena en el modelo 3D</a>
    <a class="btn s" href="{OFERTA}" target="_blank" rel="noopener">Aprende flebología en el IMF</a>
  </div>
  <article class="vein single">
    <h2>Trayecto</h2><p>{E(v['curso'])}</p>
    <h2>Drena en</h2><p>{E(v['drena'])}</p>
    <h2>Ecografía</h2><p>{E(v['us'])}</p>
    <h2>Relevancia clínica</h2><p>{E(v['clin'])}</p>
  </article>
  <section class="refs block" style="margin-top:36px">
    <h2>Referencias de esta ficha</h2>
    <ol class="reflist">{cited}</ol>
    <p class="notes"><a href="/{GUIDE_PATH}#referencias">Ver la lista completa de referencias</a>. {E(NOTES)}</p>
  </section>
  <section class="block"><h2>Otras {E(SYSNAME[v['sys']].lower())}</h2><ul class="rel">{rel}</ul></section>
  <nav class="pn" aria-label="Venas anterior y siguiente">{pn}</nav>
{IMF_BLOCK}'''
    nodes = [
        {"@type": "MedicalWebPage", "@id": url + "#page", "url": url, "name": v['n'], "description": desc, "inLanguage": "es-MX",
         "isPartOf": {"@id": SITE + "#website"},
         "about": {"@type": "Vein", "name": v['n'], "alternateName": [x for x in (v['ta'], v['alt']) if x],
                   "partOfSystem": {"@type": "AnatomicalSystem", "name": "Sistema venoso del miembro inferior"}},
         "audience": {"@type": "MedicalAudience", "audienceType": "Clinician"}, "publisher": {"@id": IMF + "#org"},
         "image": SITE + "og-image.png"},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Anatomía venosa 3D", "item": SITE},
            {"@type": "ListItem", "position": 2, "name": "Anatomía venosa de los miembros inferiores", "item": GUIDE},
            {"@type": "ListItem", "position": 3, "name": v['n'], "item": url}]},
    ]
    write(path + 'index.html', shell(title, desc, path, 'article', nodes, main, v['n']))

# =====================================================================  sitemap
urls = [('', '1.0'), (GUIDE_PATH, '0.9')] + [(URLV(v), '0.7') for v in ORDER]
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for p, pr in urls:
    sm.append(f'  <url>\n    <loc>{SITE}{p}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>{pr}</priority>\n  </url>')
sm.append('</urlset>\n')
write('sitemap.xml', '\n'.join(sm))

# =====================================================================  lista de venas con enlaces en el <noscript> de la portada
lis = ''
for k, heading, _ in SYSORDER:
    items = [v for v in V if v['sys'] == k]
    lis += f'<h2>{E(heading)}</h2><ul>' + ''.join(
        f'<li><a href="{URLV(v)}">{E(v["n"])}</a>' + (f' ({E(v["alt"])})' if v['alt'] else '') + f' <i>{E(v["ta"])}</i></li>' for v in items) + '</ul>'
block = '<!--lista-venas-->' + lis + '<!--/lista-venas-->'
idx = io.open('index.html', encoding='utf-8', newline='').read()
if '<!--lista-venas-->' in idx:
    idx = re.sub(r'<!--lista-venas-->.*?<!--/lista-venas-->', lambda m: block, idx, count=1, flags=re.S)
else:
    m = re.search(r'<h2>Sistema venoso superficial</h2>.*?(?=</div></noscript>)', idx, re.S)
    assert m, 'no encontré la lista de venas en el noscript'
    idx = idx.replace(m.group(0), block, 1)
write('index.html', idx)

print(f'ok: guía + {len(ORDER)} páginas de vena + sitemap ({len(urls)} URL)')
