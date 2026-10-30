from pathlib import Path
import re
ROOT=Path(__file__).resolve().parent.parent
source=(ROOT/'tools/atlas-base.txt').read_text(encoding='utf-8')
s=source
s=re.sub(r'/assets/beta-feedback\.css(?:\?[^"\s]*)?', '/assets/beta-feedback.css?v=20261030-votos', s)
s=re.sub(r'/assets/beta-feedback\.js(?:\?[^"\s]*)?', '/assets/beta-feedback.js?v=20261030-votos', s)
feedback=(ROOT/'assets/beta-feedback.html').read_text(encoding='utf-8').strip()
s=re.sub(r'<section class="beta-notice".*?</section>\s*<div class="beta-feedback".*?\n</div>', lambda _: feedback, s, count=1, flags=re.S)
s=s.replace('https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js','assets/vendor/three.min.js').replace('https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js','assets/vendor/OrbitControls.js')
s=s.replace('<script src="assets/vendor/OrbitControls.js"></script>','<script src="assets/vendor/OrbitControls.js"></script>\n<script src="assets/vendor/GLTFLoader.js"></script>\n<script src="assets/z-runtime.js"></script>')
s=s.replace('(function(){\nconst T=THREE, DEG=Math.PI/180;','''(async function(){
if(!window.THREE){document.getElementById('loading').textContent='No se pudo cargar el motor 3D local.';return}
const T=THREE, DEG=Math.PI/180;
let Z;try{document.getElementById('loading').textContent='Cargando anatomía Z-Anatomy…';Z=await ZAtlas.load(T)}catch(error){document.getElementById('loading').innerHTML='No se pudo cargar la anatomía. <button onclick="location.reload()">Reintentar</button>';console.error(error);return}
''')
s=re.sub(r'const PT=\[\[[^\n]+;', 'const PT=Z.meta.profiles;', s, count=1)
extra='''
// Afluentes presentes en Z-Anatomy: identificadores propios, sin renombrarlos como safena.
V.push(
{id:'epi',sys:'sup',r:.1,ab:'SEPi',n:'Vena epigástrica superficial',en:'Superficial epigastric vein',alt:'Superficial epigastric vein; SEPi',abSource:'Consenso latinoamericano 2023 · tabla VI',abNote:'Afluente superficial de la región del cayado.',ta:'Vena epigastrica superficialis',refs:[5,19,21],paths:[],curso:'Afluente superficial de la región inguinal representado por su malla original de Z-Anatomy.',drena:'Región del confluente safenofemoral.',us:'Identifica el vaso y su continuidad con el confluente en la región inguinal.',clin:'Su identificación permite describir los afluentes de la unión safenofemoral.'},
{id:'epud',sys:'sup',r:.1,ab:'EPV',n:'Venas pudendas externas',en:'External pudendal veins',alt:'External pudendal veins; EPV',abSource:'Consenso latinoamericano 2023 · tabla VI',abNote:'Distintas de la vena pudenda interna del sistema pélvico.',ta:'Venae pudendae externae',refs:[5,19,21],paths:[],curso:'Afluentes superficiales de la región inguinal representados por las mallas de Z-Anatomy.',drena:'Región del confluente safenofemoral.',us:'Sigue los afluentes de la región inguinal para distinguirlos de los troncos safenos.',clin:'Distinguir las pudendas externas de la pudenda interna evita confundir los territorios superficial y pélvico.'},
{id:'gen',sys:'deep',r:.1,ab:'GenV',n:'Venas geniculares',en:'Genicular veins',alt:'Genicular veins; red venosa genicular',abSource:'Leyenda editorial del atlas',abNote:'Grupo venoso de la rodilla representado por Z-Anatomy.',ta:'Venae genus',refs:[19],paths:[],curso:'Red venosa de la región de la rodilla, representada por la malla original de Z-Anatomy.',drena:'Territorio venoso profundo de la rodilla.',us:'Revisa las relaciones de la red con el eje poplíteo en los cortes de la rodilla.',clin:'Su identificación aporta contexto anatómico al eje profundo de la rodilla.'}
);
'''
idx=s.index('const byId=');s=s[:idx]+extra+s[idx:]
s=re.sub(r'<script type="application/json" id="bp3d">.*?</script>','',s,count=1,flags=re.S)
s=s.replace("const BP=JSON.parse(document.getElementById('bp3d').textContent);",'const BP={bone:[],mus:[]};')
start=s.index('LAY.skin.add(new T.Mesh(ringGeo(')
end=s.index('/* Corte ecográfico en 3D:',start)
s=s[:start]+'''
const musMat=new T.MeshStandardMaterial({roughness:.75,transparent:true,opacity:.25,depthWrite:false,side:T.DoubleSide});
const artMat=new T.MeshStandardMaterial({roughness:.48});
const VES=[],pickList=[];
V.forEach(v=>{v.mat=new T.MeshStandardMaterial({roughness:.42,metalness:.05});v.meshes=[];v.picks=[];v.curves=[];v.anchor=Z.meta.anchors[v.id]||null});
for(const rec of Z.records){const m=rec.mesh,d=rec;
 if(d.kind==='bone'||d.kind==='mus'){m.material=d.kind==='bone'?boneMat:musMat;m.userData.part=d.part;LAY[d.kind==='bone'?'bone':'mus'].add(m);if(d.kind==='mus')m.renderOrder=1;continue}
 if(d.kind==='skin'||d.kind==='fascia'){m.material=d.kind==='skin'?skinMat:fasciaMat;LAY[d.kind].add(m);continue}
 if(d.kind==='art'){m.material=artMat;m.userData.art={id:d.id,n:d.label,ab:d.ab};LAY.art.add(m);VES.push({...rec,ab:d.ab});continue}
 const v=byId[d.id];if(!v)throw Error('Estructura sin ficha: '+d.id);m.material=v.mat;m.userData.id=v.id;scene.add(m);v.meshes.push(m);v.picks.push(m);pickList.push(m);VES.push({...rec,ab:v.ab,sap:v.sap});v.geometrySource=d.source;
}
for(const v of V)if(!v.meshes.length)throw Error('Ficha sin geometría: '+v.id);
''' +s[end:]
s=s.replace("function anchorOf(v){const c=v.curves[0];return c.getPoint(v.t??.5)}",'function anchorOf(v){return v3(v.anchor)}')
s=s.replace("m.transparent=!on;m.opacity=on?1:.07;m.depthWrite=on;m.needsUpdate=true;", "m.transparent=false;m.opacity=1;m.depthWrite=true;v.meshes.forEach(mesh=>mesh.visible=on);m.needsUpdate=true;")
s=s.replace('<p class="f-nomen"><b>${v.abSource}</b>', '<p class="f-geometry">${v.geometrySource?.startsWith(\'IMF\')?\'Representación complementaria del IMF, adaptada al nuevo modelo.\':\'Geometría original de Z-Anatomy.\'}</p>\n   <p class="f-nomen"><b>${v.abSource}</b>')
s=s.replace('Miembro inferior derecho · huesos y músculos BodyParts3D','Actualizado · Z-Anatomy · 29/10/2026')
s=s.replace('<div class="app" id="app"', '<p class="atlas-update"><strong>Nueva versión · Z-Anatomy</strong><span>29 oct 2026 · Modelo 3D y cortes ecográficos actualizados</span></p>\n<div class="app" id="app"',1)
s=s.replace('Valora la compresibilidad de la CFV, las válvulas terminal y preterminal y el reflujo con Valsalva', 'Valora la compresibilidad de la CFV y el reflujo con Valsalva')
# The anatomic window changes with the geometry, while all existing ultrasound controls remain.
s=s.replace("y:85.9,phi:62,depth:4,sel:'vsm'", "y:84.6,phi:70,depth:4,sel:'vsm'")
s=s.replace("lvl:85.9,phi:62,depth:4", "lvl:84.6,phi:70,depth:4")
s=s.replace("y:68.2,phi:5,depth:3,sel:'vsm'", "y:68.2,phi:41,depth:4,sel:'vsm'")
s=s.replace("y:64.05,phi:12,depth:8,sel:'pdodd'", "y:64.05,phi:43,depth:8,sel:'pdodd'")
s=s.replace("y:45.3,phi:-90,depth:5,sel:'vsp'", "y:48.3,phi:-90,depth:6,sel:'vsp'")
s=s.replace("y:26.8,phi:-25,depth:6,sel:'vpt'", "y:26.8,phi:-40,depth:6,sel:'vpt'")
s=s.replace("s:'Dos venas por cada arteria'", "s:'Grupo venoso tibial posterior y su arteria'")
s=s.replace("La AAGSV se proyecta justo", "La representación complementaria de AAGSV se proyecta justo")
s=s.replace("La vena femoral común es la cabeza", "En la referencia anatómica, la vena femoral común es la cabeza")
s=s.replace("la arteria femoral común (lateral)", "la arteria femoral (lateral)")
s=s.replace("if(t==='eco'){resizeUS();updateSlice();}", "if(t==='eco'){resizeUS();updateSlice();}requestAnimationFrame(()=>{const aside=document.querySelector('.app aside');if(aside)aside.scrollTop=0});")
# Contact point and normal come from the same surface envelope shown in ultrasound.
s=s.replace('const Sx=p.cx+p.rx*Math.cos(a),Sz=p.cz+p.rz*Math.sin(a);', 'let Sx=p.cx+p.rx*Math.cos(a),Sz=p.cz+p.rz*Math.sin(a);')
needle='return{p,Sx,Sz,nx,nz,tx:-nz,tz:nx};'
s=s.replace(needle,'''const skin=Z.body('skin',S.lvl),dx=Math.cos(a),dz=Math.sin(a);let nearest=Infinity;
  for(let i=0;i<skin.length;i++){const A=skin[i],B=skin[(i+1)%skin.length],ex=B[0]-A[0],ez=B[1]-A[1],den=dx*ez-dz*ex;if(Math.abs(den)<1e-8)continue;const ax=A[0]-p.cx,az=A[1]-p.cz,t=(ax*ez-az*ex)/den,u=(ax*dz-az*dx)/den;if(t>=0&&u>=0&&u<=1&&t<nearest){nearest=t;Sx=p.cx+t*dx;Sz=p.cz+t*dz;nx=-ez;nz=ex;const l=Math.hypot(nx,nz);nx/=l;nz/=l;if(nx*dx+nz*dz>0){nx=-nx;nz=-nz}}}
  return{p,Sx,Sz,nx,nz,tx:-nz,tz:nx};''')
s=s.replace('const rp=[];for(let i=0;i<=72;i++){const a=i/72*Math.PI*2;rp.push(F.p.cx+F.p.rx*Math.cos(a),y,F.p.cz+F.p.rz*Math.sin(a))}', "const contour=Z.body('skin',y),rp=[];for(const pt of [...contour,contour[0]])if(pt)rp.push(pt[0],y,pt[1]);")
# Direct access to the approved region, within the full atlas.
s=s.replace('data-c="lat"', 'data-c="lat"',1)
pos=s.index('id="camSeg"');end=s.index('</div>',pos)
s=s[:end]+'<button type="button" data-c="usf" aria-pressed="false">Cayado</button>'+s[end:]
s=s.replace("const d={ant:[0,0,1]", "if(b.dataset.c==='usf'){setTab('ficha');select('vsm');const p=v3(Z.meta.landmarks.sfj);flyTo(p,p.clone().add(new T.Vector3(14,4,31)));return}const d={ant:[0,0,1]")
s=re.sub(r'(<input[^>]+id="lvl"[^>]+step=")[^"]+',r'\g<1>0.1',s)
# Surface and bone sections are taken from the very same meshes used by the 3D viewer.
s=s.replace('const P=F.p,skin=ell(P.cx,P.cz,P.rx,P.rz),fas=ell(P.cx,P.cz,P.rx*FASCIA,P.rz*FASCIA);', "const P=F.p;const skin3=Z.body('skin',S.lvl),fas3=Z.body('fascia',S.lvl);const skin=skin3.length>2?skin3.map(p=>map(...p)):ell(P.cx,P.cz,P.rx,P.rz),fas=fas3.length>2?fas3.map(p=>map(...p)):ell(P.cx,P.cz,P.rx*FASCIA,P.rz*FASCIA);")
a=s.index('  Object.values(SLICES).forEach(');b=s.index('  bones.forEach(pts=>',a)
s=s[:a]+"  Z.sections('bone',y).forEach(c=>bones.push(c.points.map(p=>map(...p))));\n"+s[b:]
a=s.index('  VES.forEach(ve=>');b=s.index('  // Ganancia en profundidad',a)
s=s[:a]+'''
  const visibleVessels=VES.filter(ve=>ve.kind==='vein'?S.active.has(byId[ve.id].sys):LAY.art.visible);
  for(const section of Z.cutMany(visibleVessels,y)){const ve=section.records.find(r=>r.id===S.sel)||section.records[0],pts=section.points.map(p=>map(...p));if(!section.closed){ctx.beginPath();pts.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));ctx.lineWidth=1.2*DPR;ctx.strokeStyle='rgba(200,200,200,.65)';ctx.stroke();continue}const m={x:section.center[0],z:section.center[1]},c=map(m.x,m.z);items.push({ve,m,section,c,pts})}
  items.sort((a,b)=>(a.ve.kind==='art')-(b.ve.kind==='art'));
  items.forEach(it=>{
    const ve=it.ve,isV=ve.kind==='vein',thr=isV&&S.thr&&ve.id===S.sel;
    const [X,Y]=it.c,R=Math.max(it.section.r*k,1.2*DPR),sq=isV&&!thr?cf:1,ps=it.pts.map(p=>[X+(p[0]-X)*(isV?1:pulse),Y+(p[1]-Y)*(isV?sq:pulse)]);
    if(Math.max(...ps.map(p=>p[0]))<0||Math.min(...ps.map(p=>p[0]))>W||Math.max(...ps.map(p=>p[1]))<0||Math.min(...ps.map(p=>p[1]))>H)return;
    const lum=thr?'#585858':S.dop?(isV?(sq>.5?'#2b6cff':'#000'):'#e2382f'):'#030303';
    const wall=isV?'rgba(200,200,200,.85)':'rgba(240,240,240,.95)',wl=(isV?1.4:2.4)*DPR;
    const g=ctx.createLinearGradient(0,Y+R,0,Y+R*6);g.addColorStop(0,'rgba(255,255,255,.12)');g.addColorStop(1,'rgba(255,255,255,0)');ctx.fillStyle=g;ctx.fillRect(X-R,Y+R,2*R,R*5);
    poly(ps);ctx.fillStyle=lum;ctx.fill();ctx.lineWidth=wl;ctx.strokeStyle=wall;ctx.stroke();
    if(thr){ctx.save();ctx.clip();for(let i=0;i<14;i++){ctx.fillStyle=`rgba(255,255,255,${.12+Math.random()*.15})`;ctx.fillRect(X-R+Math.random()*2*R,Y-R+Math.random()*2*R,1.5*DPR,1.5*DPR)}ctx.restore()}
    if(ve.sap){const e=Math.hypot((it.m.x-P.cx)/P.rx,(it.m.z-P.cz)/P.rz);if(e>FASCIA-.06&&e<1.04){const w=Math.max(R*4.6,14*DPR);ctx.lineWidth=1.6*DPR;ctx.strokeStyle='rgba(235,235,235,.9)';ctx.beginPath();ctx.moveTo(X-w,Y+R*1.3);ctx.bezierCurveTo(X-w*.45,Y-R*2.1,X+w*.45,Y-R*2.1,X+w,Y+R*1.3);ctx.stroke()}}
    shapes.push({id:ve.id,kind:ve.kind,X,Y,R,ab:ve.ab});
  });
''' +s[b:]
# No anatomical fallback is displayed silently: data source is shown in every ficha.
# Keep the denser source anatomy legible: one label per structure, with collision avoidance.
a=s.index('  if(S.lab){const seen=');b=s.index('  // Retícula y datos',a)
s=s[:a]+'''
  if(S.lab){
    ctx.font=`600 ${11*DPR}px "JetBrains Mono", monospace`;ctx.textBaseline='middle';
    const labels=[],unique=new Map();
    shapes.filter(q=>q.X>=0&&q.X<=W&&q.Y>22*DPR&&q.Y<H-18*DPR).forEach(q=>{if(!unique.has(q.id)||unique.get(q.id).R<q.R)unique.set(q.id,q)});
    const priority=q=>q.id===S.sel?0:q.id==='vfc'?1:q.kind==='art'?2:3;
    [...unique.values()].sort((a,b)=>priority(a)-priority(b)||b.R-a.R).forEach(q=>{
      const w=ctx.measureText(q.ab).width+8*DPR,h=17*DPR,px=q.X+q.R+5*DPR,py=q.Y-q.R-4*DPR;
      let box;for(const dy of [0,-20,20,-40,40,-60,60]){const x=Math.max(4*DPR,Math.min(px,W-w-27*DPR)),y=Math.max(30*DPR,Math.min(py+dy*DPR,H-h-20*DPR)),r={x,y,w,h};if(!labels.some(a=>r.x<a.x+a.w+3*DPR&&r.x+r.w+3*DPR>a.x&&r.y<a.y+a.h+3*DPR&&r.y+r.h+3*DPR>a.y)){box=r;break}}
      if(!box)return;labels.push(box);
      ctx.strokeStyle='rgba(215,226,234,.55)';ctx.lineWidth=.7*DPR;ctx.beginPath();ctx.moveTo(q.X,q.Y);ctx.lineTo(box.x,box.y+box.h/2);ctx.stroke();
      ctx.fillStyle='rgba(0,0,0,.65)';ctx.fillRect(box.x,box.y,box.w,box.h);
      ctx.fillStyle=q.kind==='vein'&&q.id===S.sel?'#ffb547':q.kind==='art'?'#ff9b93':'#d7e2ea';ctx.fillText(q.ab,box.x+4*DPR,box.y+box.h/2);
    });
  }
''' +s[b:]
s=s.replace('Modelo 3D: <a href="https://creativecommons.org/licenses/by-sa/2.1/jp/"', 'Modelo 3D: Z-Anatomy · <a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank" rel="noopener">CC BY-SA 4.0</a>; BodyParts3D · <a href="https://creativecommons.org/licenses/by-sa/2.1/jp/"')
s=s.replace('</head>', '<style>.f-geometry{font-size:11px;line-height:1.5;color:var(--muted);padding:9px 11px;background:var(--bg);border-left:2px solid var(--accent);margin:10px 0}.hud{max-width:90%}.atlas-update{max-width:1760px;margin:10px auto 0;padding:8px 16px;display:flex;gap:6px 18px;justify-content:center;flex-wrap:wrap;font:12px/1.4 var(--f-body);color:var(--fg);background:var(--bg);border-block:1px solid var(--line2)}.atlas-update strong{color:var(--accent)}.atlas-update span{color:var(--muted)}@media(max-width:640px){.atlas-update{font-size:11px;margin-top:0;padding:6px 12px;gap:2px 12px}.atlas-update span{font-size:10px}}</style></head>')
s=s.replace("${v.geometrySource?.startsWith('IMF')?'Representación complementaria del IMF, adaptada al nuevo modelo.':'Geometría original de Z-Anatomy.'}", "${v.geometrySource?.startsWith('IMF')?'Representación complementaria del IMF, adaptada al nuevo modelo.':'Geometría original de Z-Anatomy.'}${v.pair?' La malla representa el grupo venoso; no reproduce individualmente todas las venas acompañantes.':''}")
# Remove the large, obsolete embedded slice table; ultrasound uses live sections of the new meshes.
s=re.sub(r'const SLICES=\{[^\n]+;', 'const SLICES={};', s, count=1)
# A local capture of the running viewer for the review dossier.
capture='''
if(['127.0.0.1','localhost'].includes(location.hostname)){
const saveZView=document.createElement('button');saveZView.type='button';saveZView.textContent='↓';saveZView.setAttribute('aria-label','Guardar vista');saveZView.style.cssText='width:34px;min-width:34px;padding:0;font-size:20px';saveZView.title='Guardar imagen de esta vista local';document.getElementById('stageBar').append(saveZView);
saveZView.onclick=async()=>{renderer.render(scene,camera);const c=document.createElement('canvas');c.width=1400;c.height=1000;const x=c.getContext('2d');x.fillStyle='#f0f3f6';x.fillRect(0,0,1400,1000);x.fillStyle='#20364c';x.font='bold 30px Segoe UI';x.fillText('Atlas flebológico · Z-Anatomy',36,50);x.font='17px Segoe UI';x.fillStyle='#61758a';x.fillText('Web completa · Vista previa local · Sin publicar',36,82);
const draw=(img,xx,yy,w,h)=>{const q=Math.min(w/img.width,h/img.height),dw=img.width*q,dh=img.height*q;x.drawImage(img,xx+(w-dw)/2,yy+(h-dh)/2,dw,dh)};
draw(renderer.domElement,25,110,810,780);x.fillStyle='white';x.fillRect(855,110,515,780);x.fillStyle='#20364c';x.font='bold 23px Segoe UI';const v=byId[S.sel]||byId.vsm;x.fillText(v.n,878,150);x.font='16px Segoe UI';x.fillStyle='#61758a';x.fillText(S.tab==='eco'?'Ecografía calculada sobre las mallas visibles':v.geometrySource,878,181);
if(S.tab==='eco'){drawUS(performance.now());draw(us,875,210,470,400);x.fillText('Altura '+S.lvl.toFixed(1)+' cm · Profundidad '+S.depth+' cm',878,645);x.fillText('Compresión '+(S.compT?'activa':'inactiva')+' · Doppler '+(S.dop?'activo':'inactivo'),878,677)}else{let yy=220;for(const [title,text]of [['Trayecto',v.curso],['Drena en',v.drena]]){x.fillStyle='#20364c';x.font='bold 18px Segoe UI';x.fillText(title,878,yy);yy+=28;x.font='17px Segoe UI';x.fillStyle='#536c83';let line='';for(const word of text.split(' ')){if(x.measureText(line+word).width>445){x.fillText(line,878,yy);yy+=26;line=''}line+=word+' '}if(line)x.fillText(line,878,yy);yy+=45}}
x.font='16px Segoe UI';x.fillStyle='#61758a';x.fillText('30 fichas · Capas de piel, fascia, músculos, huesos y arterias · Sin válvulas añadidas',36,933);x.fillText('Z-Anatomy CC BY-SA 4.0 · BodyParts3D, DBCLS CC BY-SA 2.1 JP · IMF',36,965);const blob=await new Promise(r=>c.toBlob(r,'image/png'));const response=await fetch('/capture',{method:'POST',headers:{'Content-Type':'image/png'},body:blob});if(response.ok){saveZView.textContent='✓';setTimeout(()=>saveZView.textContent='↓',1800)}};
'''
capture+="\n}\n"
capture=capture.replace('Web completa · Vista previa local · Sin publicar','Nueva versión · Modelo 3D y ecografía actualizados')
s=s.replace("applyTheme();resize();renderIndex();select('vsm');",capture+"\napplyTheme();resize();renderIndex();select('vsm');")
s=s.replace('assets/z-runtime.js"','assets/z-runtime.js?v=20261029-z1"')

# Distinguish adapted receptor geometry from untouched Z-Anatomy meshes.
s=s.replace("'Geometría original de Z-Anatomy.'", "(v.geometrySource?.includes('uniones adaptadas')?'Geometría Z-Anatomy con uniones adaptadas por el IMF.':'Geometría original de Z-Anatomy.')")
s=s.replace('assets/z-runtime.js?v=20261029-z1','assets/z-runtime.js?v=20261029-uniones2')
from revisar_ecografia import apply_ultrasound_review
s=apply_ultrasound_review(s)
(ROOT/'index.html').write_text(s, encoding='utf-8')

print('Atlas completo integrado:',len(s.encode('utf-8')),'bytes HTML')
