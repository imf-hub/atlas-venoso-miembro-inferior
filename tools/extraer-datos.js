// Lee los datos de la herramienta (venas, referencias, sistemas) desde index.html y los imprime como JSON.
// Uso: node tools/extraer-datos.js index.html
const fs = require('fs');
const s = fs.readFileSync(process.argv[2] || 'index.html', 'utf8');
const pm = t => 'https://pubmed.ncbi.nlm.nih.gov/?term=' + encodeURIComponent(t);
// Auxiliares del modelo 3D que usan las fichas; aquí solo importan los textos.
const Pd = new Proxy({}, { get: () => [] }), C = new Proxy({}, { get: () => [] });
const perfPts = () => [], offsetPts = () => [], arr = () => [], atY = () => ({}), surf = () => [], v3 = () => ({}), mkCurve = () => ({});
const grab = (marker, close) => { const a = s.indexOf(marker); const b = s.indexOf(close, a) + close.length; return s.slice(a + marker.length, b).replace(/;$/, ''); };
const V = eval('(' + grab('const V=', '\n];') + ')');
const REFS = eval('(' + grab('const REFS=', '\n];') + ')');
const SYS = eval('(' + grab('const SYS=', '};') + ')');
process.stdout.write(JSON.stringify({
  V: V.map(v => ({ id: v.id, sys: v.sys, n: v.n, alt: v.alt || '', ta: v.ta, ab: v.ab, en: v.en, abSource: v.abSource, abNote: v.abNote, pair: !!v.pair, curso: v.curso, drena: v.drena, us: v.us, clin: v.clin, refs: v.refs })),
  REFS, SYS
}));
