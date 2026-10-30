/* ================= Ruta de aprendizaje (lectura, sin chat ni seguimiento de avance) ================= */
const lmsList=document.getElementById('lmsList'),lmsMain=document.getElementById('lmsMain');
const lmsEsc=t=>String(t).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const levelInfo=id=>LEVELS.find(l=>l.id===id)||LEVELS[0];
const progressKey='imf-learning-20261029-v1';
let learningProgress={done:[],best:{}};
try{const p=JSON.parse(localStorage.getItem(progressKey)||'null');if(p&&Array.isArray(p.done)&&p.best&&typeof p.best==='object')learningProgress={done:p.done.filter(id=>ROUTE.some(m=>m.id===id)),best:p.best}}catch(e){}
function saveLearning(){try{localStorage.setItem(progressKey,JSON.stringify(learningProgress))}catch(e){}}
function evidenceLinks(keys=[]){return keys.length?`<div class="evidence"><b>Evidencia de esta lección o pregunta</b>${keys.map(k=>{const s=LEARNING_SOURCES[k];return `<p><a href="${s.url}" target="_blank" rel="noopener">${lmsEsc(s.title)} ↗</a><small>${lmsEsc(s.section)}</small></p>`}).join('')}</div>`:''}
let lmsCur=-1;
const lmsFirst=t=>String(t).split(/(?<=[.!?])\s/)[0];
function lmsOutline(){
  lmsList.innerHTML='';
  const add=(i,num,title,sub)=>{const li=document.createElement('li'),b=document.createElement('button');b.type='button';
    b.innerHTML=`<span class="lms-n">${num}</span><span>${title}<small>${sub}</small></span>`;
    if(i===lmsCur)b.setAttribute('aria-current','step');b.onclick=()=>lmsShow(i);li.appendChild(b);lmsList.appendChild(li)};
  add(-1,'i','Introducción','Cómo funciona esta ruta');
  const sep=document.createElement('li');sep.className='sep';lmsList.appendChild(sep);
  ROUTE.forEach((m,i)=>add(i,i+1,m.t,levelInfo(m.level).label+(learningProgress.done.includes(m.id)?' · ✓ Revisada':' · ≈ '+m.minutes+' min')));
}
function lmsTerms(m){
  const seen=new Set(),rows=[];
  (m.terms||[]).forEach(id=>{const v=byId[id];seen.add(v.ab);rows.push([v.ab,v.n,v.en,v.abSource])});
  (m.codes||[]).forEach(code=>{if(seen.has(code))return;const t=MAP2023.find(t=>t[0]===code);if(t)rows.push([t[0],t[1],t[2],'Mapeo latinoamericano 2023 · tabla VI'])});
  if(!rows.length)return '';
  return `<div class="learn-table-wrap" tabindex="0" role="region" aria-label="Nombres y siglas del módulo"><table class="learn-table"><caption>Nombres de este módulo: español, inglés y fuente</caption><thead><tr><th scope="col">Nombre y sigla</th><th scope="col">Inglés y referencia</th></tr></thead><tbody>${rows.map(([ab,es,en,source])=>`<tr><td><b>${lmsEsc(es)}</b><span class="learn-badge">${lmsEsc(ab)}</span></td><td><span lang="en">${lmsEsc(en)}</span><small>${lmsEsc(source)}</small></td></tr>`).join('')}</tbody></table></div>`;
}
function lmsIntro(){
  const how=[['Caso','Parte de un problema clínico o de interpretación.'],['Explora','Relaciona el nombre con el modelo y la ecografía.'],['Reto','Responde y compara la explicación.'],['Para llevar','Identifica la fuente y evita confusiones.']];
  return `<div class="lms-in lms-hero">
    <p class="lms-eyebrow">IMF · De la primera consulta al razonamiento avanzado</p>
    <h2>Aprende flebología, paso a paso</h2>
    <p class="lead">${ROUTE.length} lecciones para médicos: empieza por orientación y retorno venoso, aprende a interpretar hallazgos y termina con casos que requieren integrar información. No necesitas conocer las siglas para comenzar.</p>
    <div class="level-shortcuts" role="group" aria-label="Empezar un nivel">${LEVELS.map(l=>`<button type="button" data-go="${ROUTE.findIndex(m=>m.level===l.id)}">${l.label}<small>4 lecciones</small></button>`).join('')}</div>
    <div class="learning-progress"><b>${learningProgress.done.length} de ${ROUTE.length} lecciones revisadas</b><progress max="${ROUTE.length}" value="${learningProgress.done.length}" aria-label="Lecciones marcadas como revisadas"></progress><small>Avance guardado solo en este navegador. Marcar lectura no acredita competencia clínica.</small><button type="button" class="mini" data-reset-progress>Reiniciar mi avance</button></div>
    <button class="cta-btn" type="button" data-go="0">Comenzar con el módulo 1 →</button>
    <div class="learn-convention"><b>Español en el nombre; inglés en la sigla.</b><p>GSV y SSV corresponden a safena mayor y menor. Para ejes profundos indicamos CEAP 2020; otras leyendas inglesas se identifican como editoriales. AAGSV (2023) y ASV (2024) se explican con su fuente y fecha.</p><a href="/anatomia-venosa-miembros-inferiores/#consenso-2023">Consultar la guía y sus referencias →</a></div>
    <h3 class="lms-h">Cómo funciona cada módulo</h3>
    <ol class="how">${how.map((h,i)=>`<li><b>${i+1}</b><strong>${h[0]}</strong><span>${h[1]}</span></li>`).join('')}</ol>
    ${LEVELS.map(l=>`<section class="level-section"><h3 class="lms-h">${l.label}</h3><p>${l.description}</p><div class="mods">${ROUTE.map((m,i)=>m.level===l.id?`<button class="mod-card" type="button" data-go="${i}"><span class="lms-n">${learningProgress.done.includes(m.id)?'✓':i+1}</span><div><strong>${lmsEsc(m.t)}</strong><span>${lmsEsc(lmsFirst(m.obj))}</span><small>≈ ${m.minutes} min · caso y reto</small></div></button>`:'').join('')}</div></section>`).join('')}
    <p class="lms-note">Todos los niveles están disponibles. «Leyenda» es un reto docente, no un título ni una certificación de especialista. Revisión documental: 29 de octubre de 2026; pendiente de validación docente por el equipo médico del IMF.</p><a class="learn-guide" href="revision-aprendizaje.html">Qué se revisó, fuentes y límites →</a>
  </div>`;
}
function lmsLesson(i){
  const m=ROUTE[i],prev=ROUTE[i-1],next=ROUTE[i+1];
  const acts=m.act.map((a,k)=>`<button class="act" type="button" data-k="${k}">${lmsEsc(a.l==='Explorar estructura en 3D'?byId[a.v].n:a.l)}<small>${a.p?'Abrir esquema en Ecografía →':'Abrir en el modelo 3D →'}</small></button>`).join('');
  const sec=(id,n,t,body)=>`<section class="les-sec" id="les-${id}"><h3><b>${n}</b>${t}</h3>${body}</section>`;
  return `<div class="lms-in">
    <div class="les-top"><span>${levelInfo(m.level).label} · Lección ${i+1} de ${ROUTE.length}</span><span>≈ ${m.minutes} min + práctica</span></div>
    <h2 class="les-title">${lmsEsc(m.t)}</h2>
    <div class="steps" role="navigation" aria-label="Partes del módulo">${[['caso','Caso'],['obj','Objetivo'],['explora','Explora'],['reto','Reto'],['llevar','Para llevar']].map(([id,l],k)=>`<button type="button" data-s="${id}"><b>${k+1}</b>${l}</button>`).join('')}</div>
    ${sec('caso',1,'Situación de partida',`<div class="callout case">${lmsEsc(m.prob)}</div>`)}
    ${sec('obj',2,'Objetivo y nombres del módulo',`<p>${lmsEsc(m.obj)}</p>${lmsTerms(m)}`)}
    ${sec('explora',3,'Explora y relaciona',`<p class="hint">Los botones abren la estructura o el corte de referencia. Para volver a este módulo, usa «Aprender» en el menú.</p><div class="acts">${acts}</div><div class="learn-concepts">${m.concepts.map(([h,p])=>`<h4>${lmsEsc(h)}</h4><p>${lmsEsc(p)}</p>`).join('')}</div><a class="learn-guide" href="/anatomia-venosa-miembros-inferiores/#${m.guide}">Ampliar este tema en la guía anatómica →</a>`)}
    ${sec('reto',4,'Reto',`<div class="reto"><p>${lmsEsc(m.q)}</p><button class="mini" type="button" data-x="ans" aria-expanded="false" aria-controls="lesson-answer">Ver respuesta</button><div class="ans" id="lesson-answer" hidden><b>Respuesta:</b> ${lmsEsc(m.a)}</div></div>`)}
    ${sec('llevar',5,'Para llevar a tu práctica',`<div class="callout perla"><b>Idea clave</b>${lmsEsc(m.perla)}</div><div class="callout error"><b>Error frecuente</b>${lmsEsc(m.error)}</div>${refChips(m.refs)}${evidenceLinks(m.sourceRefs)}<button type="button" class="primary learn-quiz" data-test="lesson">Practicar esta lección →</button><button type="button" class="mini" data-complete aria-pressed="${learningProgress.done.includes(m.id)}">${learningProgress.done.includes(m.id)?'✓ Lección revisada':'Marcar como revisada'}</button>`)}
    <div class="les-nav">${prev?`<button type="button" data-go="${i-1}"><small>← Módulo ${i}</small>${lmsEsc(prev.t)}</button>`:`<button type="button" data-go="-1"><small>← Inicio</small>Introducción</button>`}${next?`<button type="button" class="nx" data-go="${i+1}"><small>Módulo ${i+2} →</small>${lmsEsc(next.t)}</button>`:''}</div>
  </div>`;
}
function lmsShow(i){
  lmsCur=i;lmsMain.innerHTML=i<0?lmsIntro():lmsLesson(i);lmsOutline();lmsMain.scrollTop=0;
  lmsMain.querySelectorAll('[data-go]').forEach(b=>b.onclick=()=>lmsShow(+b.dataset.go));
  const reset=lmsMain.querySelector('[data-reset-progress]');if(reset)reset.onclick=()=>{if(reset.dataset.confirm!=='yes'){reset.dataset.confirm='yes';reset.textContent='Confirmar reinicio de lecturas y resultados';return}learningProgress={done:[],best:{}};saveLearning();lmsShow(-1)};
  if(i>=0){const m=ROUTE[i];
    lmsMain.querySelectorAll('.act').forEach(b=>b.onclick=()=>{const a=m.act[+b.dataset.k];if(a.p){setTab('eco');applyPreset(a.p)}else{setTab('ficha');select(a.v,{focus:true})}});
    lmsMain.querySelector('[data-x="ans"]').onclick=e=>{const an=lmsMain.querySelector('.ans');an.hidden=!an.hidden;e.target.textContent=an.hidden?'Ver respuesta':'Ocultar respuesta';e.target.setAttribute('aria-expanded',String(!an.hidden))};
    lmsMain.querySelector('[data-test]').onclick=()=>{quizMode='clinical';quizLevel=m.level;quizModule=m.id;setTab('quiz')};
    lmsMain.querySelector('[data-complete]').onclick=()=>{learningProgress.done=learningProgress.done.includes(m.id)?learningProgress.done.filter(id=>id!==m.id):[...learningProgress.done,m.id];saveLearning();lmsShow(i)};
    lmsMain.querySelectorAll('.steps button').forEach(b=>b.onclick=()=>document.getElementById('les-'+b.dataset.s).scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'}));
  }
  const cur=lmsList.querySelector('[aria-current="step"]');if(cur&&cur.scrollIntoView)cur.scrollIntoView({block:'nearest',inline:'nearest'});
}
lmsShow(-1);

/* ================= Autoevaluación ================= */
const quiz=document.getElementById('quiz');let Q=null,QS=null,quizMode='clinical',quizLevel='principiante',quizModule=null;const TOTAL=10;
const shuffle=a=>{for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a};
const pool=()=>V.filter(v=>S.active.has(v.sys));
const termPool=()=>NOMEN_QUIZ.filter(q=>q.level===quizLevel&&(!quizModule||q.module===quizModule)&&(quizMode!=='names'||q.kind==='names')&&(quizMode==='clinical'||!q.sys.length||q.sys.some(s=>S.active.has(s))));
const questionById=Object.fromEntries(NOMEN_QUIZ.map(q=>[q.id,q]));
const quizIdentity=v=>`<span class="quiz-name">${lmsEsc(v.n)} <span class="learn-badge">${lmsEsc(v.ab)}</span></span><small lang="en">${lmsEsc(v.en)}</small>`;
function modeButtons(){return `<label class="difficulty">Dificultad<select id="quiz-level" aria-label="Dificultad">${LEVELS.map(l=>`<option value="${l.id}" ${quizLevel===l.id?'selected':''}>${l.label}</option>`).join('')}</select></label><p class="quiz-hint">${levelInfo(quizLevel).description}${quizLevel==='leyenda'?' Reto docente; no acredita especialidad.':''}</p><div class="quiz-mode" role="group" aria-label="Tipo de evaluación"><button type="button" data-quiz-mode="clinical" aria-pressed="${quizMode==='clinical'}">Por nivel</button><button type="button" data-quiz-mode="mixed" aria-pressed="${quizMode==='mixed'}">Con 3D</button><button type="button" data-quiz-mode="names" aria-pressed="${quizMode==='names'}">Siglas</button></div>${quizModule?`<p class="quiz-hint">Práctica: ${lmsEsc(ROUTE.find(m=>m.id===quizModule).t)} <button class="mini" data-clear-module>Todo el nivel</button></p>`:''}`}
function bindQuizModes(){quiz.querySelectorAll('[data-quiz-mode]').forEach(b=>b.onclick=()=>{if(quizMode===b.dataset.quizMode)return;quizMode=b.dataset.quizMode;quizModule=null;startQuiz()});const level=quiz.querySelector('#quiz-level');if(level)level.onchange=()=>{quizLevel=level.value;quizModule=null;startQuiz()};const clear=quiz.querySelector('[data-clear-module]');if(clear)clear.onclick=()=>{quizModule=null;startQuiz()}}
function reviewLesson(id){const i=ROUTE.findIndex(m=>m.id===id);if(i>=0){setView('tutor',{push:true});lmsShow(i)}}
function bindReview(){quiz.querySelectorAll('[data-review]').forEach(b=>b.onclick=()=>reviewLesson(b.dataset.review))}
function startQuiz(){
  const pl=pool(),terms=shuffle(termPool().map(q=>({kind:'terms',id:q.id})));
  let order=[];
  if(quizMode!=='mixed')order=terms.slice(0,TOTAL);
  else{
    const anatomy=shuffle(pl.map(v=>({kind:'anatomy',id:v.id}))).slice(0,Math.min(5,pl.length));
    const names=terms.slice(0,TOTAL-anatomy.length);
    for(let i=0;i<Math.max(anatomy.length,names.length);i++){if(anatomy[i])order.push(anatomy[i]);if(names[i])order.push(names[i])}
  }
  if(!order.length){Q=null;QS=null;S.marks={};paint();quiz.innerHTML=modeButtons()+'<p class="fb">No hay preguntas de este tipo con estos filtros. Elige «Por nivel» para practicar los casos o cambia la dificultad.</p>';bindQuizModes();return}
  QS={i:0,score:0,order,answers:[]};setRotate(quizMode==='mixed');nextQ();
}
function nextQ(){
  S.marks={};if(QS.i>=QS.order.length)return finishQ();
  const item=QS.order[QS.i];
  if(item.kind==='terms'){
    const question=questionById[item.id];Q={type:'terms',question,done:false};
    Q.opts=shuffle(question.options.map((_,i)=>String(i)));
  }else{
    const id=item.id,type=Math.random()<.5?'senala':'nombra';Q={id,type,done:false};
    if(type==='nombra'){Q.opts=shuffle([id,...shuffle(pool().filter(v=>v.id!==id).map(v=>v.id)).slice(0,3)]);S.marks[id]='sel'}
  }
  paint();
  let body='';
  if(Q.type==='terms')body=`<div class="qprompt"><p class="quiz-instruction">${levelInfo(Q.question.level).label} · ${Q.question.kind==='clinical'?'Razonamiento y aplicación':'Anatomía y nomenclatura'} · elige una respuesta</p><h2 class="quiz-question" id="quiz-question">${lmsEsc(Q.question.prompt)}</h2></div><div class="opts" role="group" aria-labelledby="quiz-question">${Q.opts.map(o=>`<button type="button" class="opt" data-id="${o}">${lmsEsc(Q.question.options[+o])}</button>`).join('')}</div>`;
  else if(Q.type==='senala')body=`<div class="qprompt"><p class="quiz-instruction">Haz clic en el modelo 3D; puedes girarlo</p><h2 class="quiz-question" id="quiz-question">Señala en el modelo:<span class="quiz-target">${lmsEsc(byId[Q.id].n)} <span class="learn-badge">${lmsEsc(byId[Q.id].ab)}</span></span></h2><p class="quiz-question-english" lang="en">${lmsEsc(byId[Q.id].en)}</p></div>`;
  else body=`<div class="qprompt"><p class="quiz-instruction">Reconocimiento anatómico · elige una respuesta</p><h2 class="quiz-question" id="quiz-question">¿Qué estructura está resaltada en naranja?</h2></div><div class="opts" role="group" aria-labelledby="quiz-question">${Q.opts.map(o=>`<button type="button" class="opt" data-id="${o}">${quizIdentity(byId[o])}</button>`).join('')}</div>`;
  quiz.innerHTML=`${modeButtons()}<p class="quiz-hint">${quizMode==='mixed'?'Incluye reconocimiento 3D de repaso general (no graduado), según sistemas activos.':quizMode==='names'?'Abreviaturas del nivel, según sistemas activos.':'Casos y conceptos del nivel; independiente de las capas visibles.'} Cambiar nivel o tipo inicia otra ronda.</p><div class="qtop"><span>Pregunta ${QS.i+1} de ${QS.order.length}</span><span id="qsc">Aciertos ${QS.score}</span></div><div class="bar"><b style="width:${QS.i/QS.order.length*100}%"></b></div>${body}<div class="fb" id="qfb" role="status" aria-live="polite"></div><div id="qnx"></div>`;
  quiz.querySelectorAll('.opt').forEach(b=>b.onclick=()=>answer(b.dataset.id));bindQuizModes();
}
function answer(id){
  if(!Q||Q.done)return;
  const isTerm=Q.type==='terms',correct=isTerm?String(Q.question.correct):Q.id;
  // Descartar valores que no pertenecen a las opciones o al catálogo del modelo.
  if(Q.type==='senala'?!byId[id]:!Q.opts.includes(id))return;
  Q.done=true;const ok=id===correct;if(ok)QS.score++;
  S.marks={};if(!isTerm){S.marks[Q.id]='ok';if(!ok&&Q.type==='senala')S.marks[id]='bad'}paint();
  quiz.querySelectorAll('.opt').forEach(b=>{b.disabled=true;if(b.dataset.id===correct)b.classList.add('ok');else if(b.dataset.id===id)b.classList.add('bad')});
  let explanation='';
  if(isTerm){const q=Q.question;
    explanation=`<b class="${ok?'ok':'bad'}">${ok?'Correcto.':'Incorrecto.'}</b><p><b>Respuesta:</b> ${lmsEsc(q.options[q.correct])}</p><p>${lmsEsc(q.explain)}</p>${refChips(q.refs)}${evidenceLinks(q.sourceRefs)}<button class="mini" type="button" data-review="${q.module}">Repasar este tema en Aprender →</button>`;
    QS.answers.push({kind:'terms',ok,module:q.module,id:q.id});
  }else{const v=byId[Q.id];
    explanation=`<b class="${ok?'ok':'bad'}">${ok?'Correcto.':'Incorrecto.'}</b>${!ok&&Q.type==='senala'?`<p>Seleccionaste: ${lmsEsc(byId[id].n)} (${lmsEsc(byId[id].ab)}).</p>`:''}<div class="quiz-answer">${quizIdentity(v)}</div><p>${lmsEsc(v.abNote)}</p><small class="quiz-source">${lmsEsc(v.abSource)}</small>${refChips(v.refs)}<a class="quiz-guide" href="/anatomia-venosa-miembros-inferiores/#v-${v.id}">Ver la explicación anatómica →</a>`;
    QS.answers.push({kind:'anatomy',ok,id:Q.id});
  }
  document.getElementById('qfb').innerHTML=explanation;bindReview();
  document.getElementById('qsc').textContent='Aciertos '+QS.score;QS.i++;
  const b=document.createElement('button');b.type='button';b.className='primary';b.textContent=QS.i>=QS.order.length?'Ver resultado':'Siguiente pregunta';b.onclick=nextQ;document.getElementById('qnx').appendChild(b);
}
function finishQ(){
  S.marks={};paint();const pct=QS.score/QS.order.length;
  const bestKey=quizLevel+':'+quizMode+':'+(quizModule||'all');if(!QS.retry)learningProgress.best[bestKey]=Math.max(Number(learningProgress.best[bestKey])||0,Math.round(pct*100));saveLearning();
  const breakdown=[['anatomy','Reconocimiento anatómico'],['terms','Conceptos y casos del nivel']].map(([kind,label])=>{const a=QS.answers.filter(a=>a.kind===kind);return a.length?`<li>${label}: <b>${a.filter(a=>a.ok).length} / ${a.length}</b></li>`:''}).join('');
  const review=[...new Set(QS.answers.filter(a=>!a.ok&&a.module).map(a=>a.module))];
  quiz.innerHTML=`${modeButtons()}<div class="qtop"><span>Resultado de esta ronda</span><span>${QS.order.length} preguntas</span></div><div class="bar"><b style="width:100%"></b></div><div class="big">${QS.score}<span style="font-size:24px;color:var(--muted)"> / ${QS.order.length}</span></div><p class="fb">${pct>=.9?'Muy buen resultado en esta ronda.':pct>=.7?'Revisa las diferencias de nombres y las estructuras que fallaste.':'Repasa los módulos y las fichas antes de repetir.'}</p><ul class="quiz-breakdown">${breakdown}</ul>${review.length?`<div class="quiz-review"><b>Temas para repasar</b>${review.map(id=>`<button type="button" class="mini" data-review="${id}">${lmsEsc(ROUTE.find(m=>m.id===id).t)} →</button>`).join('')}</div>`:''}<button class="primary" id="again" type="button">Nueva ronda</button><p class="fb"><a href="/anatomia-venosa-miembros-inferiores/#nomenclatura">Consultar la tabla bilingüe →</a></p><p class="quiz-hint">Resultado de práctica, sin acreditación ni seguimiento de avance.</p><p class="fb"><a href="https://flebo.mx/oferta-educativa/" target="_blank" rel="noopener">Aprende flebología en el IMF</a>.</p>`;
  quiz.innerHTML=quiz.innerHTML.replace('sin acreditación ni seguimiento de avance.','sin acreditación. Mejor resultado en este nivel y modalidad: '+learningProgress.best[bestKey]+'%. Guardado en este navegador; no equivale a competencia clínica.');
  const missed=QS.answers.filter(a=>!a.ok&&a.id).map(a=>({kind:a.kind,id:a.id}));
  if(missed.length){const retry=document.createElement('button');retry.type='button';retry.className='primary';retry.textContent='Repetir preguntas falladas';retry.onclick=()=>{QS={i:0,score:0,order:shuffle([...missed]),answers:[],retry:true};nextQ()};quiz.appendChild(retry)}
  document.getElementById('again').onclick=startQuiz;bindQuizModes();bindReview();
}


