import io
import re
import json
from datetime import datetime
from urllib.parse import quote
import pandas as pd
import streamlit as st
from docx import Document

st.set_page_config(page_title='INNOVA-VT | Proyectos de Ingeniería', page_icon='🔎', layout='wide')
st.title('🔎 INNOVA-VT')
st.caption('Asistente académico para estado del arte y vigilancia tecnológica · Prototipo funcional sin credenciales')

STOP = set('de la el los las en con para por del al un una unos unas que se su sus y o a e es son como sobre mediante basado basada sistema diseño desarrollo implementar realizar permitir proyecto objetivo general específicos especificos problema ingeniería ingenieria'.split())
SUGGESTIONS = {
    'agua': ['water','water management'], 'fugas':['leak detection','water leakage'], 'flujo':['flow monitoring','flow sensor'],
    'aire':['air quality','air monitoring'], 'calidad':['quality monitoring'], 'lluvia':['rainwater harvesting'],
    'carro':['smart cart','automated shopping cart'], 'mercado':['shopping cart','retail automation'],
    'inteligente':['smart system','intelligent monitoring'], 'sensor':['sensors','sensor network'],
    'monitoreo':['monitoring','remote sensing'], 'control':['control system','automatic control'],
    'energia':['energy management','energy efficiency'], 'energía':['energy management','energy efficiency'],
    'pintura':['paint booth','automotive painting'], 'automotriz':['automotive industry','vehicle painting'],
    'temperatura':['temperature monitoring','thermal sensor'], 'humedad':['humidity monitoring','humidity sensor'],
    'residuos':['waste management','waste collection'], 'riego':['smart irrigation','irrigation control'],
    'esp32':['ESP32','microcontroller'], 'iot':['internet of things','IoT'],
}

def keywords(text):
    words = re.findall(r'[a-záéíóúñü0-9]+', text.lower())
    seen=[]
    for w in words:
        if len(w)>3 and w not in STOP and w not in seen:
            seen.append(w)
    return seen[:12]

def terms(text):
    kw=keywords(text)
    en=[]
    for w in kw:
        en.extend(SUGGESTIONS.get(w,[]))
    en=list(dict.fromkeys(en))
    return kw,en

def make_queries(kw,en):
    base=en[:6] if en else kw[:6]
    if not base: return []
    a=base[:2]; b=base[2:4]; c=base[4:6]
    grp=lambda xs:'('+' OR '.join('"'+x+'"' for x in xs)+')'
    wide=grp(a) if not b else grp(a)+' AND '+grp(b)
    focused=wide+(' AND '+grp(c) if c else '')
    emergent=wide+' AND ("machine learning" OR "IoT" OR "automation")'
    return [('Amplia',wide),('Específica',focused),('Emergente',emergent)]

def report_doc(project, kw, en, queries, papers, patents, notes):
    d=Document();d.add_heading('INNOVA-VT | Informe de investigación formativa',0)
    d.add_paragraph('Generado: '+datetime.now().strftime('%Y-%m-%d %H:%M'))
    for title,val in project.items():
        d.add_heading(title,level=2);d.add_paragraph(val or 'No diligenciado')
    d.add_heading('Términos de búsqueda',level=1)
    d.add_paragraph('Español: '+', '.join(kw));d.add_paragraph('Inglés sugerido (verificar): '+', '.join(en))
    d.add_heading('Ecuaciones de búsqueda',level=1)
    for name,q in queries:
        d.add_heading(name,level=2);d.add_paragraph('Scopus: TITLE-ABS-KEY('+q+')');d.add_paragraph('Búsqueda conceptual para patentes (adaptar sintaxis por plataforma): '+q)
    d.add_heading('Matriz de publicaciones',level=1)
    add_table(d,papers)
    d.add_heading('Matriz de patentes',level=1)
    add_table(d,patents)
    d.add_heading('Análisis crítico del estudiante',level=1)
    d.add_paragraph(notes or 'Pendiente de diligenciar con base en las fuentes verificadas.')
    d.add_paragraph('Nota metodológica: las ecuaciones son propuestas. La aplicación no ha verificado automáticamente fuentes ni estados jurídicos. Validar metadatos y documentos originales.')
    buf=io.BytesIO();d.save(buf);return buf.getvalue()

def add_table(doc,df):
    if df.empty:
        doc.add_paragraph('Sin registros cargados.');return
    subset=df.iloc[:100,:8].fillna('').astype(str)
    table=doc.add_table(rows=1,cols=len(subset.columns));table.style='Table Grid'
    for i,col in enumerate(subset.columns):table.rows[0].cells[i].text=col
    for row in subset.itertuples(index=False,name=None):
        cells=table.add_row().cells
        for i,val in enumerate(row):cells[i].text=str(val)[:500]

if 'papers' not in st.session_state:st.session_state.papers=pd.DataFrame(columns=['Título','Autores','Año','DOI/URL','Metodología','Resultados','Limitaciones','Aporte al proyecto','Verificado'])
if 'patents' not in st.session_state:st.session_state.patents=pd.DataFrame(columns=['Número de publicación','Título','Solicitante','Fecha de prioridad','IPC/CPC','URL','Solución técnica','Estado jurídico verificado','Aporte al proyecto'])

with st.sidebar:
    st.header('Proyecto')
    name=st.text_input('Nombre del proyecto',placeholder='Sistema de detección de fugas de agua')
    program=st.text_input('Programa académico',value='Ingeniería')
    team=st.text_input('Integrantes')
    st.info('Esta versión no realiza búsquedas automáticas ni genera referencias ficticias. Utilice los enlaces y cargue los resultados verificados.')

p_tab,q_tab,art_tab,pat_tab,rep_tab=st.tabs(['1 · Formulación','2 · Estrategias de búsqueda','3 · Estado del arte','4 · Patentes','5 · Informe'])
with p_tab:
    problem=st.text_area('Planteamiento del problema',height=180,placeholder='Describa la situación, causas, efectos, contexto y población afectada.')
    question=st.text_area('Pregunta de investigación',height=75)
    general=st.text_area('Objetivo general',height=90)
    specifics=st.text_area('Objetivos específicos (uno por línea)',height=120)
    scope=st.text_area('Alcance y tecnologías previstas',height=90)
    st.caption('Sugerencia: formule objetivos verificables y asegure coherencia entre problema, objetivo general y objetivos específicos.')
project={'Proyecto':name,'Programa':program,'Integrantes':team,'Planteamiento del problema':problem,'Pregunta de investigación':question,'Objetivo general':general,'Objetivos específicos':specifics,'Alcance y tecnologías':scope}
kw,en=terms(' '.join([name,problem,question,general,specifics,scope]));queries=make_queries(kw,en)
with q_tab:
    st.subheader('Palabras clave extraídas y traducciones sugeridas')
    st.write('**Español (extracción automática):** '+(', '.join(kw) or 'Ingrese primero el proyecto.'))
    st.write('**Inglés (diccionario inicial):** '+(', '.join(en) or 'No hay traducciones en el diccionario; añada términos manualmente.'))
    extra=st.text_input('Términos adicionales en inglés (separados por comas)',key='extra')
    if extra.strip():
        en=list(dict.fromkeys(en+[x.strip() for x in extra.split(',') if x.strip()]));queries=make_queries(kw,en)
    if not en:st.warning('Revise los términos en inglés antes de utilizar las ecuaciones.')
    for title,q in queries:
        st.markdown('#### '+title)
        st.code('TITLE-ABS-KEY('+q+')',language='text')
        st.caption('Scopus: consulta de títulos, resúmenes y palabras clave. Ajuste filtros en la plataforma.')
        st.code(q,language='text')
        st.caption('Ecuación conceptual para patentes; verifique operadores y campos en cada plataforma.')
    search=' '.join(en[:4] or kw[:4])
    if search:
        st.markdown('**Acceso a plataformas (búsqueda manual y validación):**')
        st.markdown(f'[Google Scholar](https://scholar.google.com/scholar?q={quote(search)}) · [Scopus](https://www.scopus.com/) · [Espacenet](https://worldwide.espacenet.com/) · [PATENTSCOPE](https://patentscope.wipo.int/) · [The Lens](https://www.lens.org/)')
    st.warning('Las búsquedas para Scopus, Google Scholar y plataformas de patentes no son sintácticamente intercambiables. Las ecuaciones son borradores que deben probarse y documentarse.')
with art_tab:
    st.subheader('Matriz verificable de publicaciones')
    up=st.file_uploader('Importar CSV de publicaciones (se incorporarán las columnas disponibles)',type=['csv'],key='up_p')
    if up is not None:
        try:
            df=pd.read_csv(up,sep=None,engine='python',encoding='utf-8-sig')
            if st.button('Incorporar CSV de artículos'):
                st.session_state.papers=pd.concat([st.session_state.papers,df],ignore_index=True);st.rerun()
        except Exception as e:st.error('No se pudo leer el CSV: '+str(e))
    st.session_state.papers=st.data_editor(st.session_state.papers,num_rows='dynamic',use_container_width=True,key='papers_editor')
    st.caption('Cada fila debe corresponder a una publicación real. Consigne DOI/URL y complete los hallazgos a partir del documento original.')
with pat_tab:
    st.subheader('Matriz verificable de patentes')
    up2=st.file_uploader('Importar CSV de patentes',type=['csv'],key='up_pat')
    if up2 is not None:
        try:
            df2=pd.read_csv(up2,sep=None,engine='python',encoding='utf-8-sig')
            if st.button('Incorporar CSV de patentes'):
                st.session_state.patents=pd.concat([st.session_state.patents,df2],ignore_index=True);st.rerun()
        except Exception as e:st.error('No se pudo leer el CSV: '+str(e))
    st.session_state.patents=st.data_editor(st.session_state.patents,num_rows='dynamic',use_container_width=True,key='patents_editor')
    st.caption('El estado jurídico es territorial y temporal: consulte el registro oficial correspondiente.')
with rep_tab:
    st.subheader('Síntesis crítica y exportación')
    notes=st.text_area('Análisis del estudiante: tecnologías, limitaciones, brechas y aporte propuesto',height=200)
    st.metric('Publicaciones registradas',len(st.session_state.papers))
    st.metric('Patentes registradas',len(st.session_state.patents))
    xls=io.BytesIO()
    with pd.ExcelWriter(xls,engine='openpyxl') as writer:
        st.session_state.papers.to_excel(writer,sheet_name='Estado del arte',index=False)
        st.session_state.patents.to_excel(writer,sheet_name='Vigilancia tecnológica',index=False)
        pd.DataFrame(queries,columns=['Tipo','Ecuación conceptual']).to_excel(writer,sheet_name='Estrategias',index=False)
    st.download_button('📊 Descargar matrices Excel',xls.getvalue(),file_name='INNOVA_VT_Matrices.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    st.download_button('📄 Descargar informe Word',report_doc(project,kw,en,queries,st.session_state.papers,st.session_state.patents,notes),file_name='INNOVA_VT_Informe.docx',mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    st.download_button('💾 Guardar ficha de proyecto JSON',json.dumps({'proyecto':project,'palabras_clave':kw,'terminos_ingles':en,'ecuaciones':queries,'analisis':notes},ensure_ascii=False,indent=2).encode(),file_name='INNOVA_VT_Proyecto.json',mime='application/json')
