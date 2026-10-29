// Comprueba el banco, el reparto por sistemas, la puntuación y los enlaces de repaso.
// Uso: node tools/verificar-aprendizaje.cjs
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert'),{execFileSync}=require('child_process');
const root=path.resolve(__dirname,'..'),html=fs.readFileSync(path.join(root,'index.html'),'utf8');
const data=JSON.parse(fs.readFileSync(path.join(__dirname,'aprendizaje.json'),'utf8'));
const mapping=JSON.parse(fs.readFileSync(path.join(__dirname,'guia-fuentes.json'),'utf8')).mapping2023;
const {V,REFS}=JSON.parse(execFileSync(process.execPath,[path.join(__dirname,'extraer-datos.js'),path.join(root,'index.html')],{encoding:'utf8'}));
const guide=fs.readFileSync(path.join(root,'anatomia-venosa-miembros-inferiores/index.html'),'utf8');
const refs=new Set(REFS.filter(r=>r.n).map(r=>r.n)),ids=new Set(V.map(v=>v.id));
assert.equal(data.modules.length,8);assert.equal(data.questions.length,32);assert.equal(mapping.length,17);
assert.equal(new Set(data.questions.map(q=>q.id)).size,data.questions.length);
assert(html.includes('8 módulos · unos 10 minutos cada uno'));
for(const m of data.modules){
 assert(m.concepts.length>0&&m.refs.every(r=>refs.has(r)),m.id);
 assert(guide.includes('id="'+m.guide+'"'),m.id+' guide');
 for(const id of m.terms)assert(ids.has(id),m.id+' term '+id);
 for(const code of m.codes)assert(mapping.some(t=>t[0]===code),m.id+' code '+code);
 for(const a of m.act){if(a.v)assert(ids.has(a.v));if(a.p)assert(html.includes("id:'"+a.p+"',refs:"))}
}
for(const q of data.questions){
 assert.equal(q.options.length,4,q.id);assert.equal(new Set(q.options).size,4,q.id);
 assert(q.correct>=0&&q.correct<4,q.id);assert(q.explain&&q.refs.every(r=>refs.has(r)),q.id);
 assert(guide.includes('id="'+q.guide+'"'),q.id+' guide');assert(data.modules.some(m=>m.id===q.module),q.id);
}
// La guía y las lecciones usan el mismo repertorio; las respuestas se revisan contra esa convención.
for(const code of mapping.map(t=>t[0]))assert(data.modules.some(m=>m.codes.includes(code)),code);
assert.equal(data.questions.find(q=>q.id==='aagsv').options[0],'AAGSV');
assert(data.questions.find(q=>q.id==='pv').options[0].startsWith('Perforating'));
assert(data.questions.find(q=>q.id==='popv').explain.includes('CEAP'));
const elements=new Map();
function el(){return {innerHTML:'',textContent:'',querySelectorAll:()=>[],appendChild(){},onclick:null,classList:{add(){}}}}
const quiz=el();elements.set('quiz',quiz);
const document={getElementById(id){if(!elements.has(id))elements.set(id,el());return elements.get(id)},createElement:el};
const context={V,byId:Object.fromEntries(V.map(v=>[v.id,v])),S:{active:new Set(['sup','deep','perf','pel']),marks:{}},document,paint(){},setRotate(){},lmsEsc:String,refChips:()=>'',setView(){},lmsShow(){},console};
vm.createContext(context);
vm.runInContext(html.slice(html.indexOf('const MAP2023='),html.indexOf('/* ================= Ruta de aprendizaje (lectura, sin chat')),context);
vm.runInContext(html.slice(html.indexOf('const quiz=document.getElementById'),html.indexOf('/* ================= Modo paciente:')),context);
let rounds=0;
for(let mask=1;mask<16;mask++)for(const mode of ['mixed','names'])for(const allCorrect of [true,false]){
 context.active=['sup','deep','perf','pel'].filter((_,i)=>mask&(1<<i));context.mode=mode;context.allCorrect=allCorrect;
 vm.runInContext(`S.active=new Set(active);quizMode=mode;startQuiz();`,context);
 const order=vm.runInContext('QS.order',context);assert.equal(order.length,10);assert.equal(new Set(order.map(q=>q.kind+q.id)).size,10);
 if(mode==='mixed')assert(order.some(q=>q.kind==='anatomy')&&order.some(q=>q.kind==='terms'));
 for(const item of order){
  if(item.kind==='anatomy')assert(context.active.includes(V.find(v=>v.id===item.id).sys));
  else{const q=data.questions.find(q=>q.id===item.id);assert(!q.sys.length||q.sys.some(s=>context.active.includes(s)))}
 }
 for(let i=0;i<10;i++){
  // Entrada inválida y doble respuesta no pueden sumar aciertos ni avanzar dos preguntas.
  assert.equal(vm.runInContext('QS.i',context),i);
  vm.runInContext("answer('__invalida__')",context);assert.equal(vm.runInContext('QS.i',context),i);
  vm.runInContext(`var answerId=Q.type==='terms'?(allCorrect?String(Q.question.correct):Q.opts.find(o=>o!==String(Q.question.correct))):(allCorrect?Q.id:Q.type==='nombra'?Q.opts.find(o=>o!==Q.id):V.find(v=>v.id!==Q.id).id);answer(answerId);answer(answerId);`,context);
  assert.equal(vm.runInContext('QS.i',context),i+1);
  assert(elements.get('qfb').innerHTML.includes('guía')||elements.get('qfb').innerHTML.includes('explicación anatómica'));
  vm.runInContext('nextQ()',context);
 }
 assert.equal(vm.runInContext('QS.score',context),allCorrect?10:0);
 assert(quiz.innerHTML.includes('Resultado de esta ronda'));rounds++;
}
// Todas las preguntas, incluso las que el reparto aleatorio no eligió en una ronda concreta.
for(const q of data.questions){context.question=q;vm.runInContext("QS={i:0,score:0,order:[{kind:'terms',id:question.id}],answers:[]};nextQ();answer(String(question.correct));nextQ();",context);assert.equal(vm.runInContext('QS.score',context),1)}
console.log(JSON.stringify({modules:data.modules.length,questions:data.questions.length,mapping_terms:mapping.length,system_combinations:15,rounds,answers_checked:rounds*10+data.questions.length,passed:true}));
