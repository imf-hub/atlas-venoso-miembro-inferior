import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
const source=await readFile(new URL('../worker/index.js',import.meta.url),'utf8');
const {default:worker}=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
class Bucket {
  text=null; version=0;
  async get(){const text=this.text,etag=String(this.version); return text===null?null:{etag,json:async()=>JSON.parse(text)};}
  async put(key,text,{onlyIf}){if(onlyIf.etagMatches && onlyIf.etagMatches!==String(this.version))return null;if(onlyIf.etagDoesNotMatch==='*' && this.text!==null)return null;this.text=text;this.version++;return {etag:String(this.version)};}
}
const env={BUCKET:new Bucket()};
const token=crypto.randomUUID();let revision=Date.now()-1000;
const send=(changes={},origin='https://anatomia.flebologiamexico.com')=>worker.fetch(new Request('https://test/api/vote',{method:'POST',headers:{Origin:origin,'Content-Type':'application/json'},body:JSON.stringify({token,like:true,rating:5,revision:++revision,...changes})}),env);
assert.equal((await send()).status,200);
assert.equal((await (await send()).json()).likes,1,'A repeated vote must not add likes');
let result=await (await send({rating:2,like:false})).json();
assert.equal(result.likes,0);assert.equal(result.average,2);assert.equal(result.ratings,1);
await send({revision:1});
result=await (await worker.fetch(new Request('https://test/api/summary'),env)).json();assert.equal(result.average,2,'Old retries cannot overwrite a newer vote');
assert.equal((await send({rating:8})).status,400);
assert.equal((await send({},'https://other.test')).status,403);
const parallel=await Promise.all([send({token:crypto.randomUUID()}),send({token:crypto.randomUUID()})]);
assert.ok(parallel.every(r=>r.status===200));
result=await (await worker.fetch(new Request('https://test/api/summary'),env)).json();assert.equal(result.likes,2);assert.equal(result.ratings,3,'Concurrent writes preserve both votes');
assert.equal((await send({rating:null,like:false})).status,200);
assert.equal((await worker.fetch(new Request('https://test/atlas/valoraciones-v1.json'),env)).status,404,'Raw records must not be public');
assert.equal((await worker.fetch(new Request('https://test/api/summary'),{})).status,503);
console.log('OK: persistence, duplicate prevention, change, stale retry, concurrent writes, validation, CORS and private records.');
