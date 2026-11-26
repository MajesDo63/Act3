"""Genera el PDF y el Word de la revisión corregida usando solo resultados reales."""
from pathlib import Path
from xml.sax.saxutils import escape
import hashlib
import json
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, Flowable

ROOT=Path(__file__).resolve().parents[1]

def main():
    dest=Path(json.loads((ROOT/'bitacora/a3/ultima_revision.json').read_text(encoding='utf8'))['directorio'])
    state=json.loads((dest/'estado.json').read_text(encoding='utf8'))
    assert state['estado']=='completo','Faltan evidencias de la revisión corregida'
    fingerprint=json.loads((dest/'firma_fuentes.json').read_text(encoding='utf8'))
    assert all(hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h for n,h in fingerprint.items())
    grupos={g['nombre']:g for g in state['grupos']}
    assert all(g['fallos']==0 and g['omitidas']==0 for g in grupos.values())
    propuesta=ROOT/'bitacora/a3'/Path(json.loads((ROOT/'bitacora/a3/ultima_propuesta.json').read_text(encoding='utf8'))['directorio']).name
    gemini=[e for e in json.loads((dest/'http_gemini.json').read_text(encoding='utf8'))['eventos'] if e['etiqueta'].startswith('revisor_') and e['estado_http']==200]
    assert len(gemini)==2 and all(e['estado_http']==200 and e['respuesta']['demo'] is False for e in gemini)
    benchmark=json.loads((dest/'comparacion_ciclo_completo.json').read_text(encoding='utf8'))
    swagger=json.loads((dest/'swagger_manifest.json').read_text(encoding='utf8'))['capturas']
    assert len(swagger)==6
    pages=[]
    def page(title,sub):c=[];pages.append((title,sub,c));return c
    def p(c,t):c.append(('p',t))
    def tab(c,headers,rows,widths):c.append(('table',headers,rows,widths))
    def img(c,path,caption,width):c.append(('image',str(path),caption,width))
    def pair(c,a,b,caption):c.append(('pair',str(dest/a),str(dest/b),caption))

    c=page('Actividad 3 · Servicio con autenticación','Cesar Eduardo Valdez Pinto · MajesDo63 · LSCA2318 · v2-revisor')
    p(c,'Implementé la autenticación del revisor de código de FinNorte y su endpoint específico. Comparé el login oficial con versiones de seguridad, eficiencia y mantenibilidad. Esta revisión corrige el acceso alternativo por la ruta genérica del kit y presenta pruebas y consultas nuevas que corresponden al código entregado.')
    tab(c,['Identificación','Entrega'],[
        ['Repositorio','https://github.com/MajesDo63/Act3'],
        ['Etiqueta','a3-MajesDo63'],
        ['Autor','Cesar Eduardo Valdez Pinto'],
        ['Estado de esta revisión',f"{grupos['regresion']['aprobadas']} pruebas aprobadas; {grupos['actividad3']['aprobadas']} propias de A3; cero omitidas."],
        ['Ejecución','Windows 11 · Python 3.14.7 · PowerShell local'],
        ['Modelo de las dos entradas','Gemini 3.1 Flash-Lite; ambas respuestas con demo=false.'],
        ['Carpeta de evidencia','bitacora/a3/'+dest.name+'/'],
    ],[1.55,4.95])
    p(c,'Reutilicé el motor compartido del Avance 1, como requiere la actividad: Project_v2_TSTI, commit 81a1dd0bec2a6350d750f9440fbdcbaa2af05b63. PROCEDENCIA_BASE.md reconoce al equipo. Conservé el motor y sus recursos; los informes y bitácoras de otras actividades están excluidos.')
    tab(c,['Pieza','Responsabilidad'],[
        ['api/auth.py','Registro, hash, tokens, intentos y bloqueo persistente.'],
        ['api/producto.py','POST /v1/revisor: entrada propia, token, límite y problem+json.'],
        ['src/finnorte/','Motor del equipo: detectar, explicar, parche y dictamen; no ejecuta el código recibido.'],
        ['a3/','Login oficial, tres versiones, evaluación de una respuesta real y reflexión.'],
        ['tests/ y bitacora/a3/','Casos reproducibles, firmas, registros íntegros y capturas directas.'],
    ],[1.6,4.9])
    p(c,'La revisión anterior validaba el rechazo de archivos solo en /v1/revisor. Eso era insuficiente: /v1/variante seguía aceptando un diccionario que el motor podía interpretar como una ruta. Retiré por completo esa ruta, su modelo y el fallback demo. El cliente de ejemplo también utiliza ahora /v1/revisor.')

    c=page('1. Prompt y evaluación de la propuesta','Consulta real nueva, sin reconstruir la conversación original')
    p(c,'Guardé una consulta nueva a Gemini antes de cerrar esta corrección. La respuesta literal de la primera conversación no estaba conservada; no atribuyo a ese intercambio las capturas nuevas. El prompt, la solicitud sin credenciales, el JSON del proveedor y el texto íntegro están en bitacora/a3/'+propuesta.name+'/.')
    p(c,'Prompt (extracto): «Actúa como ingeniero de seguridad de una fintech. Diseña en Python […] hash_contrasena, verificar_contrasena, emitir_token y validar_token, más un login SQLite con bloqueo después de cinco fallos». A continuación enumeré los seis requisitos, el contrato HTTP, el login oficial y el riesgo de conservar un endpoint genérico. Pedí separar arranque y llamadas en la comparación.')
    p(c,'El rol y el contexto delimitan el problema; los requisitos y oráculos permiten comprobar el resultado. Aun así, la respuesta incumplió condiciones explícitas. La rechacé como implementación lista para copiar y evalué estos pasajes reales:')
    tab(c,['Pasaje de la respuesta','Evaluación y decisión'],[
        ['L10: secreto de respaldo literal.','SEC-01/06, ing-02: rechacé el respaldo; la configuración ausente debe fallar.'],
        ['L29–36: exp sin iat.','SEC-06, ing-07: no prueba vigencia máxima; conservé sub/iat/exp y límites estrictos.'],
        ['L39: contador >=5.','SEC-05/06: no concreta caducidad ni commit; mantuve ventana, reinicio y persistencia.'],
        ['L57: compare_digest = eficiencia.','Es seguridad, no prueba de velocidad. V2 se evalúa por reutilización y ciclo completo.'],
        ['L72: tiempos idénticos.','Rechacé ese oráculo; el ruido de ejecución impide exigir igualdad literal.'],
        ['L84–87: payload: dict.','SEC-04/08, ing-07: omite el modelo estricto y la ruta alternativa; retiré la genérica.'],
    ],[2.05,4.45])
    img(c,propuesta/'captura_respuesta_detalle.png','Figura 1. Captura de la respuesta real de Gemini API, abierta como texto en el navegador. El respaldo mostrado es una propuesta insegura del modelo; no se incorporó al servicio.',6.1)
    p(c,'Acepté PBKDF2 con sal, HMAC y separación de responsabilidades. Modifiqué validación, reloj, desbloqueo y transacciones. Rechacé el secreto de respaldo y las afirmaciones no demostradas sobre eficiencia. El análisis completo, con líneas verificables, está en a3/propuesta_y_evaluacion.md.')

    c=page('2. Autenticación y superficie HTTP','Seis requisitos y cierre de la ruta alternativa')
    tab(c,['Requisito','Implementación y oráculo'],[
        ['Hash con sal','PBKDF2-HMAC-SHA256, 200 000 iteraciones y sal aleatoria de 16 bytes; pruebas de sal y registro sin contraseña.'],
        ['Vigencia <=15 minutos','Token HMAC payload.firma con sub/iat/exp, máximo 900 s; rechazo de modificación, expiración y emisión futura.'],
        ['Mensaje uniforme','Cuenta inexistente y contraseña incorrecta: 401, mismo detail; hash ficticio para no omitir la derivación.'],
        ['Comparación de secretos','compare_digest para derivados y firmas; formato y tipos comprobados.'],
        ['Bloqueo','Cinco fallos consecutivos en 900 s; siguiente intento 429; éxito reinicia la racha.'],
        ['Bitácora sin contraseña','SQLite parametrizado y confirmación del intento antes del error; capturas sin tokens.'],
    ],[1.45,5.05])
    p(c,'POST /v1/revisor exige Bearer y acepta solo codigo: no vacío, sin NUL y hasta 20 000 caracteres. Rechaza archivo y campos extra con 422. El límite local es 30 solicitudes/minuto por usuario; 429 incluye Retry-After. Los errores contienen type, title, status, detail y trace_id. /v1/variante ya no existe ni aparece en OpenAPI: con token válido y cualquier ruta de entrada responde 404.')
    c.append(('crop',str(dest/'swagger_contrasena_incorrecta.png'),'Figura 2. Contraseña incorrecta: fragmento de Server response en Swagger UI. El PNG íntegro acompaña la entrega.'))
    c.append(('crop',str(dest/'swagger_usuario_inexistente.png'),'Figura 3. Usuario inexistente: mismo 401 y detail; trace_id distinto. Captura directa, con recorte de maquetación.'))
    p(c,'Se conservan también las capturas directas de 401 sin token, token alterado, 422 y 429. La prueba de archivo real falla si se intenta abrir un marcador sintético o invocar el motor; no lee el .env real. La capacidad de archivos permanece en CLI, sin ruta HTTP que la reciba. El token educativo no es JWT ni OAuth 2.0 completo; una exposición externa requiere HTTPS y gestión de secretos adecuada.')

    c=page('3. Login oficial y tres mejoras','Problema, explicación técnica, impacto y trazabilidad')
    p(c,'Conservé el ejemplo oficial en a3/login_original.py: admin/1234 concede acceso; otra contraseña devuelve wrong password; otra identidad devuelve user not found con un espacio final. Son datos sintéticos del enunciado, no cuentas de la API.')
    tab(c,['Problema / impacto','Mejora y versión','Evidencia'],[
        ['Identidad fija y contraseña literal: conocer el código revela el acceso.','V1: usuarios persistentes y PBKDF2 con sal.','Hash diferente con misma contraseña; registro sin texto plano.'],
        ['== no contempla comparación de secretos en tiempo constante.','V1–V3: primitivas compartidas con compare_digest.','Firma y contraseña comprobadas; token alterado rechazado.'],
        ['Errores distintos revelan si existe la cuenta.','V1–V3: mismo 401 y hash ficticio.','Prueba y capturas de ambos mensajes.'],
        ['Sin bloqueo ni sesión verificable.','V1–V3: ventana, bitácora persistente y token.','Caducidad, reinicio, concurrencia y persistencia al reabrir.'],
        ['Cuenta y lógica mezcladas: no hay un servicio reutilizable para varios intentos.','V2: almacén indexado compartido, ciclo de vida reutilizable y lote perezoso.','Dos pruebas nuevas de consumo por intento y cierre ante error.'],
        ['Retornos de texto y espacio final: contrato frágil.','V3: Protocol, ResultadoLogin e inyección del proveedor.','Mismos tres escenarios y prueba de proveedor sustituible.'],
    ],[2.15,2.25,2.1])
    tab(c,['Archivo','Qué cambió y por qué'],[
        ['login_seguridad.py','Abre, autentica y cierra por solicitud. Da prioridad a controles y persistencia.'],
        ['login_eficiencia.py','Reutiliza conexión, índices y hash ficticio. autenticar_lote entrega un resultado por intento sin construir una lista; el contexto cierra recursos incluso ante errores.'],
        ['login_mantenible.py','Separa presentación y autenticación con un contrato inyectable; facilita sustituir y probar el proveedor.'],
    ],[1.6,4.9])
    p(c,'V0 ya hace un trabajo constante para una única cuenta; no afirmo una mejora asintótica ni que V2 sea más rápida que omitir seguridad. Comparo V2 con V1 bajo los mismos controles, contabilizando también el arranque. Las tres versiones comparten el componente criptográfico: son refactorizaciones de responsabilidades, no tres criptografías distintas.')

    c=page('4. Pruebas de la revisión entregada','Conteos actuales y consultas reales con el código corregido')
    tab(c,['Grupo','Aprobadas','Omitidas','Alcance'],[
        ['Checkpoint',str(grupos['checkpoint_auth']['aprobadas']),'0','Mensaje, token, bloqueo y texto plano.'],
        ['Laboratorio',str(grupos['laboratorio']['aprobadas']),'0','Contrato original del kit.'],
        ['Actividad 3',str(grupos['actividad3']['aprobadas']),'0','23 de auth, 19 de API y 15 de versiones.'],
        ['Regresión actual',str(grupos['regresion']['aprobadas']),'0','Suite completa de esta revisión.'],
    ],[1.3,.75,.75,3.7])
    p(c,'Los grupos se solapan y no se suman. Las cifras 159 y 155 corresponden a corridas anteriores; no son el resultado actual. La nueva firma de fuentes acompaña a los XML y registros completos de esta revisión.')
    tab(c,['Casos','Oráculo utilizado'],[
        ['Tres oficiales','Éxito, contraseña incorrecta y usuario inexistente; V0 conserva sus salidas y las versiones seguras unifican los dos errores.'],
        ['Seguridad adicional','Token alterado/expirado/futuro, secreto ausente, bloqueo persistente, sal aleatoria, SQL malicioso y ausencia de secretos en registros.'],
        ['Ruta alternativa','Cinco rutas absolutas/relativas/inexistentes con token válido: 404 y motor no invocado. Archivo sintético real: ninguna lectura; 422 en revisor.'],
        ['Eficiencia adicional','El lote no adelanta intentos, cada contraseña se verifica y la conexión se cierra si falla el productor.'],
    ],[1.4,5.1])
    rows=[]
    for e in gemini:
        s=e['respuesta'];arte=s.get('artefacto',{});d=arte.get('dictamen',{})
        detail=str(d.get('estado',s.get('respuesta','')))[:70]+f"; {len(arte.get('hallazgos',[]))} hallazgos; abstuvo={s.get('abstuvo')}"
        rows.append([e['etiqueta'].removeprefix('revisor_'),f"200 / {e['duracion_ms']/1000:.2f} s",detail])
    tab(c,['Entrada real','HTTP / duración','Resultado observado'],rows,[1.1,1.2,4.2])
    p(c,'Las dos solicitudes nuevas utilizan /v1/revisor con Gemini y demo=false. HTTP 200 prueba la integración, no exactitud exhaustiva. No ejecuté ni incorporé los parches sugeridos por el motor. Las pruebas de la suite usan fake/hash; los registros Gemini se distinguen en http_gemini.json y trazas_gemini/.')
    p(c,'El proveedor devolvió temporalmente 503 al procesar limites.py. El intento fallido se conserva; la reanudación mantiene usuarios.py aprobado y repite solo la entrada pendiente con las mismas fuentes. No se reemplazó el fallo por una respuesta inventada.')
    p(c,'Comandos: python -m pytest tests -q y python guia/validar_correccion_a3.py. El directorio real, Python, plataforma, comandos por grupo y fechas UTC están en estado.json. Cada petición HTTP registra URL, solicitud saneada, duración y respuesta. Los PNG nuevos proceden de Swagger UI; los paneles generados de la corrida anterior no se usan como si fueran capturas directas.')
    p(c,'Rechacé dos sugerencias de pruebas de la propuesta nueva: reemplazar las tres oficiales por bloqueo/expiración y exigir tiempos idénticos. Mantuve estados, mensajes, firmas y efectos observables como oráculos. La revisión externa puso de manifiesto que cubrir una sola ruta era insuficiente; los seis casos de regresión nuevos cubren el acceso alternativo.')

    c=page('5. Comparación y eficiencia','Cinco criterios, cuatro versiones y una frontera de medida común')
    tab(c,['Criterio','Original','Seguridad','Eficiencia','Mantenible'],[
        ['Seguridad','Credenciales fijas y sin sesión.','PBKDF2, token y bloqueo.','Mismos controles; sin caché de secretos.','Mismos controles del proveedor.'],
        ['Eficiencia','O(1) para una cuenta; omite controles.','Inicializa recursos por solicitud.','Reutiliza servicio y procesa lotes perezosos.','Reutiliza proveedor más presentación.'],
        ['Legibilidad','Breve, cadenas inconsistentes.','Flujo y errores explícitos.','Ciclo de vida visible con contexto.','Tipos y resultado descriptivos.'],
        ['Mantenibilidad','Cuenta y lógica mezcladas.','Componente seguro separado.','Cierre explícito y ante errores.','Proveedor inyectable.'],
        ['Errores/pruebas','Tres textos y espacio final.','Mensajes uniformes y estados.','Mismo contrato y pruebas de lote.','Resultado tipado y prueba aislada.'],
    ],[.95,1.35,1.35,1.4,1.45])
    br=[]
    for b in benchmark['resumen']:
        br.append([b['version'],str(b['n']),f"{b['mediana_total_ms']:.3f}",f"{b['mediana_inicio_ms']:.3f}",str(b['derivaciones'])])
    tab(c,['Versión','N','Total mediano ms','Inicio mediano ms','PBKDF2/ciclo'],br,[1.25,.4,1.65,1.7,1.5])
    p(c,'Método: cinco repeticiones para N=1 y N=10. El total abarca inicializar + N logins + cerrar en todas las versiones. Registrar el usuario es una precondición común fuera del intervalo. En V1 la inicialización ocurre dentro de cada llamada; el inicio separado aparece cercano a cero porque su costo ya está en solicitudes. Se conservan todas las muestras y componentes, no solo medianas.')
    p(c,'Para diez intentos, V1 realiza veinte derivaciones; V2/V3 realizan once incluyendo el hash ficticio inicial y una verificación por intento. Para un intento los costos criptográficos son equivalentes. Esto evita atribuir a V2 una ganancia artificial por omitir el arranque. El lote permite consumir intentos uno a uno sin guardar la lista completa, y no evita verificar contraseñas.')
    p(c,'La propuesta de Gemini confundía compare_digest con eficiencia. Lo mantuve como control de seguridad. Los tiempos locales no son un ensayo de carga, no demuestran tiempo constante de toda la aplicación y no se generalizan a producción. La rapidez de V0 no compensa la ausencia de controles.')

    c=page('6. Reflexión y trazabilidad','Qué corregí y qué demuestran las evidencias')
    for text in (ROOT/'a3/reflexion.md').read_text(encoding='utf8').split('\n\n')[1:]:
        if text.strip():p(c,text.strip())
    tab(c,['Comprobación','Referencia'],[
        ['Propuesta literal','bitacora/a3/'+propuesta.name+'/; líneas citadas y JSON original.'],
        ['Revisión actual','bitacora/a3/'+dest.name+'/; firmas, JUnit, HTTP, Swagger y benchmark.'],
        ['Procedencia y asistencia','PROCEDENCIA_BASE.md, ai_log.md y a3/propuesta_y_evaluacion.md.'],
        ['Entrega','entrega/Actividad3_Cesar_Informe.pdf y .docx; etiqueta a3-MajesDo63.'],
    ],[1.5,5.0])
    p(c,'Fuentes: MANUAL_ALUMNO.md, sección 4; Presentacion_Actividades_A3_A4.pptx, diapositivas 3–7 y 12; reglas SEC del corpus e ing-02/ing-07 del kit proporcionado. El Word oficial de instrucciones no estuvo disponible. Se distingue la respuesta nueva de Gemini de la revisión inicial; no se reconstruyeron capturas históricas.')
    render(pages,ROOT/'entrega')

def render(pages,out):
    out.mkdir(exist_ok=True)
    pdfmetrics.registerFont(TTFont('ArialA3',r'C:\Windows\Fonts\arial.ttf'))
    pdfmetrics.registerFont(TTFont('ArialA3Bold',r'C:\Windows\Fonts\arialbd.ttf'))
    style=ParagraphStyle('a3',fontName='ArialA3',fontSize=9,leading=12,spaceAfter=7,textColor=colors.HexColor('#24344a'))
    small=ParagraphStyle('small',parent=style,fontSize=7.8,leading=9.8,spaceAfter=0)
    head=ParagraphStyle('head',parent=style,fontName='ArialA3Bold',fontSize=20,leading=24,spaceAfter=9,textColor=colors.HexColor('#153655'))
    sub=ParagraphStyle('sub',parent=style,fontSize=9,leading=12,spaceAfter=12,textColor=colors.HexColor('#486c85'))
    def para(t,st=style):return Paragraph(escape(str(t)).replace('\n','<br/>'),st)
    def picture(path,width):
        iw,ih=ImageReader(path).getSize();return Image(path,width=width*72,height=width*72*ih/iw)
    class Recorte(Flowable):
        def __init__(self,path):
            Flowable.__init__(self);self.path=path;self.iw,self.ih=ImageReader(path).getSize()
            self.cw=min(650,self.iw);self.ch=min(170,self.ih-80);self.width=6.4*72;self.scale=self.width/self.cw;self.height=self.ch*self.scale
        def draw(self):
            cv=self.canv;cv.saveState();rect=cv.beginPath();rect.rect(0,0,self.width,self.height);cv.clipPath(rect,stroke=0,fill=0)
            cv.drawImage(self.path,0,-(self.ih-80-self.ch)*self.scale,width=self.iw*self.scale,height=self.ih*self.scale);cv.restoreState()
    story=[];doc=Document();sec=doc.sections[0]
    sec.top_margin=Inches(.6);sec.bottom_margin=Inches(.6);sec.left_margin=Inches(.7);sec.right_margin=Inches(.7);sec.page_width=Inches(8.5);sec.page_height=Inches(11)
    normal=doc.styles['Normal'];normal.font.name='Arial';normal.font.size=Pt(9);normal.paragraph_format.space_after=Pt(6);normal.paragraph_format.line_spacing=1.05
    doc.styles['Title'].font.size=Pt(20);doc.styles['Title'].font.color.rgb=RGBColor.from_string('153655')
    sec.footer.paragraphs[0].text='Cesar Eduardo Valdez Pinto · Actividad 3 · Revisión corregida'
    for idx,(title,subtitle,items) in enumerate(pages):
        if idx:story.append(PageBreak());doc.add_page_break()
        story.extend([para(title,head),para(subtitle,sub)]);doc.add_paragraph(title,'Title');doc.add_paragraph(subtitle,'Subtitle')
        for item in items:
            if item[0]=='p':story.append(para(item[1]));doc.add_paragraph(item[1])
            elif item[0]=='table':
                _,headers,rows,widths=item;grid=[[para(v,small) for v in row] for row in [headers,*rows]]
                t=Table(grid,colWidths=[w*72 for w in widths],hAlign='LEFT',repeatRows=1)
                t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e3edf4')),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#b7c7d3')),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5)]));story.extend([t,Spacer(1,8)])
                dt=doc.add_table(rows=1,cols=len(headers));dt.style='Light Shading Accent 1'
                for cell,text in zip(dt.rows[0].cells,headers):cell.text=str(text)
                for row in rows:
                    for cell,text in zip(dt.add_row().cells,row):cell.text=str(text)
                for row in dt.rows:
                    for cell in row.cells:
                        for par in cell.paragraphs:
                            par.paragraph_format.space_after=Pt(2)
                            for run in par.runs:run.font.size=Pt(8)
                doc.add_paragraph('')
            elif item[0]=='image':
                _,path,caption,w=item;story.extend([picture(path,w),para(caption,small),Spacer(1,6)]);doc.add_picture(path,width=Inches(w));doc.add_paragraph(caption,'Caption')
            elif item[0]=='crop':
                _,path,caption=item;rec=Recorte(path);story.extend([rec,para(caption,small),Spacer(1,6)])
                inline=doc.add_paragraph().add_run().add_picture(path,width=Inches(6.4),height=Pt(rec.height))
                crop=OxmlElement('a:srcRect');crop.set('l','0');crop.set('r',str(round((rec.iw-rec.cw)/rec.iw*100000)));crop.set('t',str(round(80/rec.ih*100000)));crop.set('b',str(round((rec.ih-80-rec.ch)/rec.ih*100000)))
                inline._inline.graphic.graphicData.pic.blipFill.insert(1,crop);doc.add_paragraph(caption,'Caption')
            else:
                _,a,b,caption=item
                t=Table([[picture(a,3.16),picture(b,3.16)]],colWidths=[3.25*72,3.25*72],hAlign='LEFT')
                t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),2)]));story.extend([t,para(caption,small),Spacer(1,6)])
                dt=doc.add_table(rows=1,cols=2)
                for cell,path in zip(dt.rows[0].cells,[a,b]):cell.paragraphs[0].add_run().add_picture(path,width=Inches(3.12))
                doc.add_paragraph(caption,'Caption')
    def footer(canvas,document):
        canvas.setStrokeColor(colors.HexColor('#b7c7d3'));canvas.line(50,39,562,39);canvas.setFont('ArialA3',8);canvas.setFillColor(colors.HexColor('#486c85'));canvas.drawString(50,27,'Cesar Eduardo Valdez Pinto · Actividad 3 · Revisión corregida');canvas.drawRightString(562,27,str(document.page))
    pdf=out/'Actividad3_Cesar_Informe.pdf';word=out/'Actividad3_Cesar_Informe.docx'
    SimpleDocTemplate(str(pdf),pagesize=(612,792),rightMargin=50,leftMargin=50,topMargin=42,bottomMargin=49,title='Actividad 3 - Revisión corregida',author='Cesar Eduardo Valdez Pinto').build(story,onFirstPage=footer,onLaterPages=footer)
    doc.core_properties.title='Actividad 3 - Revisión corregida';doc.core_properties.author='Cesar Eduardo Valdez Pinto';doc.save(word)
    print(json.dumps({'pdf':str(pdf),'word':str(word)},ensure_ascii=False))

if __name__=='__main__':main()
