import fs from 'node:fs';import assert from 'node:assert/strict';import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8'),review=JSON.parse(fs.readFileSync(new URL('ecografia-revisada.json',import.meta.url),'utf8'));
let parsed=0;for(const m of html.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/g)){if(/type=|src=/.test(m[1])||!m[2].trim())continue;new vm.Script(m[2]);parsed++}
assert.equal(Object.keys(review.presets).length,9);for(const p of Object.values(review.presets)){assert(html.includes(JSON.stringify(p.tip)));assert(p.evidence.every(id=>review.sources.some(s=>s.id===id)))}
for(const forbidden of ['>Doppler color</button>','>Simular trombo</button>','function noiseTex(','if(ve.sap){const e=','con Doppler color se ven dos señales azules','L 12–5 MHz','const lum=thr?'])assert(!html.includes(forbidden),forbidden);
for(const required of ['COLOR ANATÓMICO · NO DOPPLER','ESQUEMA · NO CLÍNICO','SIN COLAPSO: EJEMPLO, NO DIAGNÓSTICO','ECO_EVIDENCE[PRESETS[0].id]','const cf=1-S.comp','revision-ecografia.html'])assert(html.includes(required),required);
assert(html.includes("S.comp=0;S.thr=false;setTog('tThr',false)"));assert(!html.includes('ctx.drawImage(TEX'));
console.log(JSON.stringify({clinicalImagesGenerated:false,unvalidatedDopplerRemoved:true,syntheticSaphenousEyeRemoved:true,syntheticThrombusRemoved:true,reviewedWindows:9,reviewedFichaTexts:6,inlineScriptsParsed:parsed,scope:'Documentary and software checks, not clinical validation'}));
