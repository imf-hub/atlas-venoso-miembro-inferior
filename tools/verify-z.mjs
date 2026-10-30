import fs from 'node:fs';import assert from 'node:assert/strict';import vm from 'node:vm';import {execFileSync} from 'node:child_process';
import {GLTFLoader} from 'three/examples/jsm/loaders/GLTFLoader.js';
globalThis.window={};await import('../assets/z-runtime.js');
const root=new URL('../',import.meta.url),html=fs.readFileSync(new URL('index.html',root),'utf8');
const meta=JSON.parse(fs.readFileSync(new URL('assets/z-anatomy/metadata.json',root)));
const load=async f=>{const b=fs.readFileSync(new URL('assets/z-anatomy/'+f+'.glb',root));assert.equal(b.readUInt32LE(8),b.length);return await new Promise((ok,bad)=>new GLTFLoader().parse(b.buffer.slice(b.byteOffset,b.byteOffset+b.length),'',ok,bad))};
const records=[];for(const layer of ['vascular','bones','surface','muscles']){const m=await load(layer);m.scene.traverse(o=>{if(!o.isMesh)return;for(const v of o.geometry.attributes.position.array)assert(Number.isFinite(v));records.push(window.ZAtlas.prepare({...o.userData,mesh:o,layer}))})}
const data=JSON.parse(execFileSync('node',['tools/extraer-datos.js','index.html'],{cwd:new URL('.',root),encoding:'utf8'}));const old=JSON.parse(execFileSync('node',['tools/extraer-datos.js','tools/atlas-base.txt'],{cwd:new URL('.',root),encoding:'utf8'}));
for(const original of old.V){const now=data.V.find(v=>v.id===original.id);assert(now,'Ficha perdida: '+original.id);for(const field of ['n','en','ta','ab','curso','drena','us','clin'])assert.equal(now[field],original[field],original.id+' '+field)}
for(const v of data.V){assert(records.some(r=>r.id===v.id));assert(meta.anchors[v.id]?.every(Number.isFinite))}
assert.equal(meta.manifest.valvesAdded,false);assert.equal(meta.manifest.junctionUpdates.length,15);
const Z={body:(kind,y)=>window.ZAtlas.hull(records.filter(r=>r.kind===kind).flatMap(r=>window.ZAtlas.cut(r,y).flatMap(c=>c.points)))};
const pStart=html.indexOf('const PRESETS=['),pEnd=html.indexOf('\n];',pStart)+3,presets=vm.runInNewContext(html.slice(pStart,pEnd)+';PRESETS');
const frameCode=html.slice(html.indexOf('function frame(){'),html.indexOf('function updateSlice('));const profCode=html.match(/function prof[^\n]+/)[0];
const cases=[];for(const p of presets){const cuts=window.ZAtlas.cutMany(records.filter(r=>r.kind==='vein'||r.kind==='art'),p.y).filter(c=>c.ids.includes(p.sel)&&c.closed);assert(cuts.length,p.id+' no corta su vena');const F=vm.runInNewContext('const PT=profiles;'+profCode+';'+frameCode+';frame()',{profiles:meta.profiles,Z,S:{lvl:p.y,phi:p.phi},DEG:Math.PI/180});const projected=cuts.map(c=>{const dx=c.center[0]-F.Sx,dz=c.center[1]-F.Sz;return{l:dx*F.tx+dz*F.tz,d:dx*F.nx+dz*F.nz}});const visible=projected.some(v=>Math.abs(v.l)<p.depth*2/3&&v.d>=0&&v.d<p.depth);cases.push({preset:p.id,selected:p.sel,contours:cuts.length,visible,positions:projected.map(q=>({l:+q.l.toFixed(2),d:+q.d.toFixed(2)}))})}
console.log(JSON.stringify({fichas:data.V.length,originalFichasPreserved:old.V.length,meshCount:records.length,allPositionsFinite:true,noValves:true,presets:cases},null,2));
fs.writeFileSync(new URL('revision-z-resultados.json',root),JSON.stringify({release:meta.manifest.release,fichas:data.V.length,originalFichasPreserved:old.V.length,meshCount:records.length,presets:cases,junctionUpdates:meta.manifest.junctionUpdates},null,2));

assert(cases.every(c=>c.visible),'Hay cortes que necesitan reajustar su ventana');

