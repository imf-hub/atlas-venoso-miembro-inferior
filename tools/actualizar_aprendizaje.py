"""Sincroniza las lecciones, preguntas y siglas compartidas con la guía en index.html."""
from pathlib import Path
import json,re

def sync_learning(root):
    root=Path(root)
    data=json.loads((root/'tools/aprendizaje.json').read_text(encoding='utf-8'))
    glossary=json.loads((root/'tools/guia-fuentes.json').read_text(encoding='utf-8'))['mapping2023']
    for q in data['questions']:
        assert len(q['options'])==4 and len(set(q['options']))==4, q['id']
        assert 0 <= q['correct'] < 4, q['id']
        assert q['module'] in [m['id'] for m in data['modules']],q['id']
    content=(root/'index.html').read_text(encoding='utf-8')
    start=content.index('/* ================= Ruta de aprendizaje ================= */')
    end=content.index('/* ================= Ruta de aprendizaje (lectura, sin chat',start)
    block='/* ================= Ruta de aprendizaje ================= */\n// Generado desde tools/aprendizaje.json y tools/guia-fuentes.json.\n'
    for name,value in [('MAP2023',glossary),('LEVELS',data['levels']),('LEARNING_SOURCES',data['sources']),('ROUTE',data['modules']),('NOMEN_QUIZ',data['questions'])]:
        block+='const '+name+'='+json.dumps(value,ensure_ascii=False,indent=1)+';\n'
    result=content[:start]+block+content[end:]
    result=re.sub(r'(<p class="lms-meta">).*?(</p>)',lambda m:m[1]+str(len(data['modules']))+' lecciones · 5 niveles · a tu ritmo'+m[2],result,count=1)
    ui_start=result.index('/* ================= Ruta de aprendizaje (lectura, sin chat')
    ui_end=result.index('/* ================= Modo paciente:',ui_start)
    result=result[:ui_start]+(root/'assets/aprendizaje-ui.js').read_text(encoding='utf-8')+'\n\n'+result[ui_end:]
    if 'assets/aprendizaje.css' not in result:
        result=result.replace('</head>','<link rel="stylesheet" href="assets/aprendizaje.css?v=20261029-niveles">\n</head>')
    result=result.replace("if(location.hash==='#eco')setTab('eco');", "if(location.hash==='#evaluacion')setTab('quiz');\nif(location.hash==='#eco')setTab('eco');") if "if(location.hash==='#evaluacion')setTab('quiz');" not in result else result
    (root/'index.html').write_text(result,encoding='utf-8',newline='\n')

if __name__=='__main__':sync_learning(Path(__file__).resolve().parent.parent)
