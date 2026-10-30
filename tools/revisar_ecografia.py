"""Reviewed educational ultrasound presentation; applies after Z-Anatomy integration."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parent.parent
DATA=json.loads((ROOT/'tools/ecografia-revisada.json').read_text(encoding='utf-8'))
def apply_ultrasound_review(s):
    note='''<div class="eco-scope" role="note"><strong>Esquema anatómico para orientación ecográfica</strong><p>Generado desde el modelo 3D. No es una ecografía clínica ni simula Doppler, velocidades, reflujo o diagnóstico de trombosis.</p><p>Los planos tisulares son aproximados; el modelo no reproduce la fascia safena ni todos los canales de las venas pares.</p><a href="revision-ecografia.html" target="_blank" rel="noopener">Qué se revisó y fuentes médicas ↗</a></div>'''
    s=s.replace('<div class="us-screen">',note+'<div class="us-screen">',1)
    s=s.replace('</head>','<style>.eco-scope{padding:12px;margin-bottom:12px;border-left:3px solid #567589;background:var(--tint);font-size:12px;line-height:1.55}.eco-scope strong{display:block;font-size:14px}.eco-scope p{margin:6px 0}.eco-scope a{color:var(--accent)}.eco-evidence{display:flex;gap:7px;flex-wrap:wrap;margin-top:12px;font-size:11px}</style></head>',1)
    for a,b in [('Simulación de corte ecográfico transversal en modo B','Corte anatómico esquemático; no es una ecografía clínica'),('>Doppler color</button>','>Color anatómico</button>'),('>Simular trombo</button>','>Ejemplo sin colapso</button>'),('>Comprimir</button>','>Compresión ilustrativa</button>'),('Cortes de referencia</div>','Ventanas del modelo</div>'),('L 12–5 MHz · TRANSV','ESQUEMA · TRANSVERSAL'),("'DOPPLER COLOR'","'COLOR ANATÓMICO · NO DOPPLER'"),('simulador de ecografía en modo B','cortes anatómicos para orientación ecográfica'),('simulación de ecografía en modo B','representación anatómica para orientación ecográfica'),('ecografía en modo B, evaluación','orientación ecográfica, evaluación'),('Anatomía venosa del miembro inferior y ecografía Doppler venosa','Anatomía venosa del miembro inferior y orientación anatómica para ecografía')]:s=s.replace(a,b)
    data=json.dumps(DATA['fichaUltrasoundUpdates'],ensure_ascii=False)
    s=s.replace('const byId=',f'const ECO_FICHA_REVIEW={data};for(const v of V)if(ECO_FICHA_REVIEW[v.id])v.us=ECO_FICHA_REVIEW[v.id];\nconst byId=',1)
    for id,p in DATA['presets'].items():
        pattern=r"(\{id:'"+id+r"'.*?\bs:)'[^']*'(.*?\n  tip:)'[^']*'"
        s,n=re.subn(pattern,lambda m:m[1]+json.dumps(p['s'],ensure_ascii=False)+m[2]+json.dumps(p['tip'],ensure_ascii=False),s,count=1,flags=re.S)
        assert n==1,id
    sources={r['id']:r for r in DATA['sources']}
    refs={id:'<div class="eco-evidence">'+''.join(f'<a href="{sources[k]["url"]}" target="_blank" rel="noopener">{sources[k]["label"]} ↗</a>' for k in p['evidence'])+'</div>' for id,p in DATA['presets'].items()}
    s=s.replace('function setTip(html)', 'const ECO_EVIDENCE='+json.dumps(refs,ensure_ascii=False)+';\nfunction setTip(html)',1)
    s=s.replace('${p.tip}${refChips(p.refs)}','${p.tip}${ECO_EVIDENCE[p.id]}')
    s=s.replace('S.depth=p.depth;S.compT=0;',"S.depth=p.depth;S.compT=0;S.comp=0;S.thr=false;setTog('tThr',false);")
    # Remove synthetic echotexture. This is a diagram, not simulated acoustic acquisition.
    a=s.index('function noiseTex(');b=s.index('function resizeUS()',a);s=s[:a]+s[b:]
    s=s.replace('TEX={fat:noiseTex(w,h,10,85,70,.45,40),mus:noiseTex(w,h,30,150,320,.22,26)}','TEX=true')
    s=s.replace('ctx.save();poly(skin);ctx.clip();ctx.drawImage(TEX.fat,0,0);poly(fas);ctx.clip();ctx.drawImage(TEX.mus,0,0);ctx.restore();',"poly(skin);ctx.fillStyle='#303942';ctx.fill();poly(fas);ctx.fillStyle='#46525e';ctx.fill();")
    s=s.replace('const cy=(y0+y1)/2;ctx.fillStyle=\'#000\';ctx.fillRect(x0,cy,x1-x0,H);poly(pts);ctx.fill();',"const cy=H;ctx.fillStyle='#adb7bf';poly(pts);ctx.fill();")
    s=s.replace('const cf=1-.9*S.comp','const cf=1-S.comp')
    s=s.replace('const pulse=1+.09*Math.max(0,Math.sin(now/1000*2*Math.PI*1.15));','const pulse=1;')
    s=s.replace("const lum=thr?'#585858':S.dop?(isV?(sq>.5?'#2b6cff':'#000'):'#e2382f'):'#030303';", "const lum=S.dop?(isV?'#2b6cff':'#e2382f'):'#10161c';")
    a=s.index('    const g=ctx.createLinearGradient(0,Y+R');b=s.index('    poly(ps);ctx.fillStyle=lum;',a);s=s[:a]+s[b:]
    a=s.index('    if(thr){ctx.save();ctx.clip();');b=s.index('    shapes.push(',a);s=s[:a]+s[b:]
    a=s.index('  // Ganancia en profundidad');b=s.index('  // Rótulos',a);s=s[:a]+s[b:]
    s=s.replace("ctx.fillText('ESQUEMA · TRANSVERSAL',8*DPR,8*DPR);","ctx.fillText('ESQUEMA · NO CLÍNICO',8*DPR,8*DPR);")
    s=s.replace("if(S.dop){ctx.fillStyle", "if(S.thr){ctx.textBaseline='bottom';ctx.fillStyle='#ffbf67';ctx.fillText('SIN COLAPSO: EJEMPLO, NO DIAGNÓSTICO',8*DPR,H-25*DPR)}\n  if(S.dop){ctx.fillStyle")
    s=s.replace("+' · Doppler '+(S.dop?'activo':'inactivo')", "+' · Color anatómico '+(S.dop?'activo':'inactivo')")
    s=s.replace('Ecografía calculada sobre las mallas visibles','Esquema anatómico; no ecografía clínica')
    s=s.replace('Modelo 3D y cortes ecográficos actualizados','Modelo 3D · orientación ecográfica revisada')
    s=s.replace('${refChips(PRESETS[0].refs)}','${ECO_EVIDENCE[PRESETS[0].id]}')
    s=s.replace("if(location.hash==='#paciente')", "if(location.hash==='#eco')setTab('eco');\nif(location.hash==='#paciente')")
    extra_refs=[{'n':24,'a':'AIUM Practice Parameter for the Performance of a Peripheral Venous Ultrasound Examination, 2024 Revision. J Ultrasound Med. 2026;45:E1-E9.','u':'https://doi.org/10.1002/jum.70049'},{'n':25,'a':'Gloviczki P, et al. SVS/AVF/AVLS clinical practice guidelines for varicose veins, 2023. Part II. J Vasc Surg Venous Lymphat Disord. 2024;12:101670.','u':'https://pmc.ncbi.nlm.nih.gov/articles/PMC11523430/'}]
    a=s.index('const REFS=[');b=s.index('\n];',a);s=s[:b]+',\n'+',\n'.join(json.dumps(x,ensure_ascii=False) for x in extra_refs)+s[b:]
    s=s.replace('const byId=',"for(const v of V){if(['vie','vpt'].includes(v.id))v.refs=[...new Set([...(v.refs||[]),24])];if(['vfc','pdodd','pcock'].includes(v.id))v.refs=[...new Set([...(v.refs||[]),25])]};\nconst byId=",1)
    s=s.replace('shapes.push({id:ve.id,kind:ve.kind,X,Y,R,ab:ve.ab});',"shapes.push({id:ve.id,kind:ve.kind,X,Y,R,ab:[...new Set(it.section.records.map(r=>r.ab))].join(' / ')});")
    return s
