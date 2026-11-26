"""Compone el informe editable y PDF a partir de evidencia real de A3."""
from pathlib import Path
import hashlib
import json
from xml.sax.saxutils import escape

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'entrega'
EVI = Path(json.loads((ROOT/'bitacora/a3/ultima_ejecucion.json').read_text(encoding='utf8'))['directorio'])
state = json.loads((EVI/'estado.json').read_text(encoding='utf8'))
assert state['estado'] == 'completo', 'Se requieren las evidencias completas antes de componer la entrega'
fingerprint = json.loads((EVI/'firma_fuentes.json').read_text(encoding='utf8'))
cleanup_path=ROOT/'bitacora/a3/limpieza_entrega.json'
removed=json.loads(cleanup_path.read_text(encoding='utf8'))['archivos_retirados'] if cleanup_path.exists() else {}
assert all((not (ROOT/n).exists() and n in removed) or hashlib.sha256((ROOT/n).read_bytes()).hexdigest() == h for n,h in fingerprint.items())
gemini = json.loads((EVI/'http_gemini.json').read_text(encoding='utf8'))['eventos']
real = [e for e in gemini if e['etiqueta'].startswith('revisor_')]
assert len(real) == 2 and all(e['estado_http']==200 and e['respuesta']['demo'] is False for e in real)
bench = json.loads((EVI/'comparacion_versiones.json').read_text(encoding='utf8'))['resultados']
OUT.mkdir(exist_ok=True)

# Un único contenido para ambos formatos. Cada elemento es un párrafo, tabla o imagen.
pages = []
def page(title, subtitle=''):
    content=[]; pages.append((title,subtitle,content)); return content
def p(c,text): c.append(('p',text))
def table(c,headers,rows,widths=None): c.append(('table',headers,rows,widths))
def picture(c,name,caption,width=6.45): c.append(('image',str(EVI/name),caption,width))

c=page('Actividad 3 · Servicio con autenticación','FinNorte | v2-revisor | Cesar Eduardo Valdez Pinto | MajesDo63')
p(c,'Desarrollé la capa de autenticación del revisor de código y un endpoint propio para utilizar el motor del Avance 1. Comparé el login oficial con tres versiones enfocadas en seguridad, eficiencia y mantenibilidad. La entrega reúne el código, las decisiones de revisión y los registros de las pruebas realizadas.')
table(c,['Dato','Identificación'],[
 ['Asignatura','LSCA2318 · IA generativa aplicada a ingeniería de software'],
 ['Repositorio de esta actividad','https://github.com/MajesDo63/Act3'],
 ['Etiqueta de entrega','a3-MajesDo63'],
 ['Ejecución','Windows 11 · Python 3.14.7 · PowerShell local'],
 ['Fecha local de las pruebas','25 de noviembre de 2026 (registros conservados en UTC)'],
 ['Modelo real','Gemini 3.1 Flash-Lite · embeddings gemini-embedding-001'],
 ['Evidencias','bitacora/a3/20261126T020719Z/'],
], [1.55,4.95])
p(c,'Partí del motor compartido del equipo en alanrivera066/Project_v2_TSTI, commit 81a1dd0bec2a6350d750f9440fbdcbaa2af05b63. Documenté su origen y autoría en PROCEDENCIA_BASE.md. La entrega conserva el motor y sus recursos y pruebas relacionados, y excluye los informes y bitácoras de actividades anteriores.')
table(c,['Componente','Responsabilidad'],[
 ['api/auth.py','Registro, PBKDF2, emisión y validación de tokens, intentos y bloqueo.'],
 ['api/producto.py','POST /v1/revisor, validación, autenticación, límite y errores HTTP.'],
 ['src/finnorte/variante.py','Motor del equipo: detectar, explicar, parche y dictamen.'],
 ['a3/','Login oficial, tres versiones, prompt, crítica y reflexión.'],
 ['tests/ y bitacora/a3/','Pruebas reproducibles, HTTP real, mediciones y capturas.'],
], [1.7,4.8])
p(c,'El alcance es un prototipo local de clase. Los componentes de referencia del kit para agentes se conservaron como material de apoyo; la implementación individual de la Actividad 4 queda fuera de esta entrega.')

c=page('1. Diseño asistido y revisión crítica','Prompt utilizado, reglas y decisiones de aceptación')
p(c,'El prompt completo está en a3/prompt_diseno.md. Solicité conservar las firmas del kit, utilizar bibliotecas estándar para autenticación y conectar el endpoint a variante.sistema(). Este es el núcleo del encargo registrado:')
p(c,'«Diseña la autenticación REST del revisor de código de FinNorte en Python, manteniendo las firmas del kit v2. Incluye registro, login, tokens y un endpoint POST /v1/revisor conectado a variante.sistema(). Aplica PBKDF2-HMAC-SHA256 con sal, compare_digest, expiración máxima de 15 minutos, mensaje uniforme para credenciales incorrectas y bloqueo temporal tras cinco fallos».')
p(c,'Consideré útil la arquitectura propuesta, pero incompleta para integrar sin cambios. Relacioné sus ambigüedades con las reglas del material y comprobé las correcciones mediante casos de prueba:')
table(c,['Falla o ambigüedad','Regla','Corrección y evidencia'],[
 ['Duración configurable sin máximo.','SEC-06; ing-07','Validé 1–900 segundos y la expiración exacta del token.'],
 ['Usar ahora or time.time() pierde el cero.','SEC-04; SEC-10','Diferencié None de 0; prueba de reloj cero y emisión futura.'],
 ['Lanzar el error dentro de la transacción puede revertir el intento.','SEC-05; SEC-06','Confirmé el intento antes de lanzar ErrorAuth; prueba de persistencia al reabrir.'],
 ['Mensaje uniforme sin trabajo equivalente para cuentas inexistentes.','SEC-06','Verifiqué un hash ficticio; no afirmo eliminar todos los canales temporales.'],
 ['Entrada genérica con archivo o rutas del servidor.','SEC-04; SEC-08','Modelo CodigoRevisor con codigo y extra="forbid"; rechazo 422.'],
 ['Exponer str(error) del proveedor.','SEC-05; ing-02; ing-07','Respuesta 503 genérica; registro solo de la clase y prueba con marcador sintético.'],
], [2.25,1.0,3.25])
p(c,'Acepté PBKDF2 con sal, SQLite parametrizado, HMAC y errores estructurados. Modifiqué reloj, vigencia, transacciones y contrato de entrada. Rechacé las credenciales fijas del ejemplo, sustituir el motor real por demo y acelerar mediante caché de contraseñas o tokens. El registro de asistencia conserva estas decisiones; las consultas de Gemini están identificadas por separado.')

c=page('2. Implementación y contrato HTTP','Autenticación, autorización y validación del endpoint propio')
table(c,['Requisito','Aplicación y comprobación'],[
 ['Hash con sal','PBKDF2-HMAC-SHA256, 200 000 iteraciones y sal aleatoria de 16 bytes. No se almacena la contraseña.'],
 ['Expiración ≤15 minutos','Token payload.firma con sub, iat y exp; vigencia máxima de 900 segundos. Rechazo de token expirado, futuro o modificado.'],
 ['Mensaje uniforme','401: “Correo o contraseña incorrectos” en los dos casos. Hash ficticio para identidad desconocida.'],
 ['Comparación de secretos','hmac.compare_digest para derivaciones y firmas; parseo estricto de los formatos.'],
 ['Bloqueo','Cinco fallos consecutivos dentro de 900 segundos; intento posterior 429. Un éxito reinicia la racha.'],
 ['Bitácora sin contraseña','Registro de intentos en SQLite; las evidencias HTTP ocultan contraseña y token.'],
], [1.48,5.02])
p(c,'POST /v1/revisor recibe {"codigo": "..."}, exige Authorization: Bearer y llama al motor real. CodigoRevisor rechaza texto vacío, caracteres nulos, más de 20 000 caracteres y campos extra. El código recibido se analiza; no se ejecuta. El límite por usuario es 30 solicitudes por minuto. Los errores incluyen type, title, status, detail y trace_id en application/problem+json; 429 incorpora Retry-After.')
picture(c,'captura_errores.png','Figura 1. Captura del panel de evidencias HTTP reales: 401, token alterado, 422 y bloqueo 429. Archivo fuente: http_fake.json.',5.0)
p(c,'El secreto se obtiene de TOKEN_SECRET; no se incluye en Git. El token es un formato HMAC propio del kit, no JWT ni una implementación completa de OAuth 2.0. Para exposición externa se requiere HTTPS y un diseño de autenticación y secretos apropiado para ese entorno.')

c=page('3. Login oficial y tres versiones','Problema → mejora → versión → evidencia')
p(c,'Conservé el login oficial en a3/login_original.py como ejemplo inseguro. Sus cadenas admin/1234 son datos didácticos del enunciado, no cuentas de la API. El análisis completo está en a3/analisis_login.md.')
table(c,['Problema e impacto','Mejora / versión','Evidencia'],[
 ['Credenciales fijas y contraseña sin hash: el acceso depende del código fuente.','V1 seguridad: almacén SQLite con hash y sal.','Pruebas de sal, registro y ausencia de contraseña en bitácora.'],
 ['Comparación == de secretos: el diseño omite protección temporal.','V1 y primitivas compartidas: compare_digest.','Verificación de contraseña y firma; rechazo de token alterado.'],
 ['Errores distintos: facilitan identificar cuentas.','V1–V3: mensaje uniforme y hash ficticio.','Mismo 401 para cuenta desconocida y contraseña mala.'],
 ['Sin bloqueo ni sesión: permite repetir intentos y no protege otros endpoints.','V1–V3: registro de fallos, bloqueo y token.','Persistencia, ventana, concurrencia y caducidad del token.'],
 ['Inicializar recursos cada vez agrega trabajo.','V2 eficiencia: reutilizar conexión y hash ficticio.','10 logins medidos y conteo real de derivaciones.'],
 ['Texto suelto y espacio final: contrato frágil y lógica acoplada.','V3 mantenible: Protocol, ResultadoLogin y dependencia inyectable.','Tres escenarios comunes y prueba de proveedor sustituible.'],
], [2.25,2.15,2.1])
table(c,['Archivo','Cambio principal y motivo'],[
 ['login_seguridad.py','Abre y cierra el autenticador por solicitud. Sustituye el ejemplo por verificaciones y almacenamiento seguro.'],
 ['login_eficiencia.py','Reutiliza el servicio sin omitir PBKDF2. Evita repetir inicialización; exige cerrar la instancia al terminar.'],
 ['login_mantenible.py','Separa presentación y autenticación mediante tipos e inyección. Facilita cambiar y probar el proveedor.'],
], [1.7,4.8])
p(c,'Las tres versiones comparten las primitivas de api/auth.py. Esta decisión evita mantener tres implementaciones criptográficas sensibles. La API integra el componente de autenticación; los archivos separados permiten observar cada objetivo de refactorización. La respuesta asistida fue suficiente para orientar el diseño, pero ambigua en los límites y la transacción del bloqueo; por eso requirió las correcciones de la sección 1.')

c=page('4. Pruebas y evidencias de ejecución','Resultados locales conservados y dos entradas reales con Gemini')
table(c,['Grupo','Aprobadas','Omitidas','Qué comprueba'],[
 ['Checkpoint de autenticación','4','0','Mensaje, token alterado, bloqueo y texto plano.'],
 ['Laboratorio','12','0','Contrato del kit y caso guía.'],
 ['Actividad 3','49','0','Autenticación, endpoint propio y tres versiones.'],
 ['Regresión completa','159','0','Suite completa; incluye los grupos anteriores.'],
], [1.5,.75,.75,3.5])
p(c,'Los grupos se solapan: no se suman como pruebas distintas. Los 159 casos son la regresión original: al excluir cuatro casos exclusivos del ejemplo A2 quedan 155. Los 49 de A3 se conservan. Las tres pruebas oficiales verifican acceso, contraseña incorrecta y usuario inexistente. Añadí sal aleatoria, token expirado/alterado, bloqueo persistente, SQL malicioso, concurrencia, campos extra y errores sin datos internos.')
picture(c,'captura_pruebas.png','Figura 2. Captura del registro real de pytest. Los XML y la salida completa de cada grupo acompañan la entrega.',4.85)
table(c,['Entrada real','HTTP / tiempo','Resultado observado'],[
 ['usuarios.py',f"200 / {real[0]['duracion_ms']/1000:.2f} s",'3 hallazgos SEC-06: MD5, random y comparación ==; fuente sec-06#0.'],
 ['limites.py',f"200 / {real[1]['duracion_ms']/1000:.2f} s",'sin hallazgos; sin citas por no identificar infracciones.'],
], [1.25,1.2,4.05])
p(c,'Ambas respuestas registraron demo=false y abstuvo=false. HTTP 200 demuestra ejecución y respuesta, no exactitud exhaustiva. El parche sugerido para usuarios.py introduce bcrypt: no lo apliqué ni lo presento como validado. Las pruebas usan fake/hash; las dos peticiones reales se conservan completas en http_gemini.json y trazas_gemini/.')

c=page('5. Comparación y evaluación de las pruebas','Cinco criterios para cuatro versiones del login')
table(c,['Criterio','Original','Seguridad','Eficiencia','Mantenible'],[
 ['Seguridad','Credenciales fijas; sin sesión ni bloqueo.','PBKDF2, sal, token y bloqueo.','Conserva controles; sin caché de secretos.','Conserva controles del proveedor inyectado.'],
 ['Eficiencia','Hace menos controles; su rapidez no es aceptable.','Abre conexión y crea hash ficticio por llamada.','Amortiza inicialización; verifica cada contraseña.','Reutiliza proveedor y agrega presentación.'],
 ['Legibilidad','Breve; cadenas y espacio final inconsistentes.','Flujo y errores explícitos.','Ciclo de vida del servicio visible.','Tipos y resultado con nombres claros.'],
 ['Mantenibilidad','Credenciales y lógica mezcladas.','Separa el ejemplo del componente seguro.','Requiere cerrar instancia reutilizada.','Protocol permite sustituir proveedor.'],
 ['Errores / pruebas','Tres retornos de texto.','Mensaje uniforme y estados.','Mantiene el mismo contrato seguro.','ResultadoLogin y prueba de inyección.'],
], [1.1,1.35,1.35,1.35,1.35])
table(c,['Versión','Mediana (ms)','Derivaciones / 10 logins'],[
 [b['version'],f"{b['mediana_ms']:.4f}",str(b['llamadas_pbkdf2'])] for b in bench
], [2.2,1.6,2.7])
p(c,'Medí diez logins exitosos por versión después de un calentamiento. La inicialización de V2/V3 queda fuera del intervalo; V1 la realiza por solicitud. Las medianas son locales y no representan carga HTTP ni rendimiento de producción. La versión eficiente realiza una derivación por login en lugar de dos; conserva la comprobación de cada contraseña. El original solo sirve como contraste inseguro.')
p(c,'Acepté las tres situaciones funcionales propuestas, pero rechacé usarlas como única prueba de seguridad: el ejemplo vulnerable también las aprueba. Cambié el contrato esperado de las versiones nuevas para exigir el mismo mensaje en los dos errores y ausencia de token cuando falla el login. Añadí límites del reloj, formatos no canónicos y persistencia de intentos para detectar fallas que los ejemplos simples no cubren.')
p(c,'Las pruebas con un doble del motor comprueban la conexión y el manejo de errores del endpoint; las solicitudes a Gemini prueban la integración real con el proveedor. Mantengo ambos registros separados. Los parches generados son propuestas del revisor y no forman parte del código autenticador que pasó las 159 pruebas.')

c=page('6. Reflexión y reproducción','Conclusiones, límites y fuentes de la actividad')
ref=(ROOT/'a3/reflexion.md').read_text(encoding='utf8').split('\n\n')[1:]
for text in ref:p(c,text.strip())
table(c,['Comprobación','Archivo o comando'],[
 ['Pruebas locales','python -m pytest tests -q (con dependencias instaladas).'],
 ['Proceso completo','python guia/completar_a3.py; --reanudar conserva las pruebas de la corrida indicada.'],
 ['Levantar servicio','python -m uvicorn api.producto:app --host 127.0.0.1 --port 8000'],
 ['Interfaz de API','http://127.0.0.1:8000/docs · registrar, login, Authorize y /v1/revisor.'],
 ['Registro de dónde y cómo','estado.json: directorio, Python, plataforma y comandos; http_*.json: URL, solicitud saneada y respuesta.'],
], [1.6,4.9])
p(c,'El primer intento terminó al limpiar una base temporal bloqueada por el lanzador de Windows. Corregí el cierre y reanudé solo Gemini, conservando los grupos aprobados. Las firmas registran los 108 archivos medidos. La posterior limpieza retiró únicamente materiales ajenos a la A3; limpieza_entrega.json identifica las exclusiones. La API y el motor mantienen los mismos bytes que en las pruebas y consultas reales.')
p(c,'Fuentes: MANUAL_ALUMNO.md, sección 4, y Presentacion_Actividades_A3_A4.pptx, diapositivas 3–7, del kit lsca2318-lab-a3-a4-main.zip; reglas SEC del corpus e ing-02/ing-07. Base del equipo: Project_v2_TSTI, commit 81a1dd0bec2a6350d750f9440fbdcbaa2af05b63. El registro ai_log_a3.md identifica el apoyo de IA. El Word oficial de instrucciones no estuvo disponible; seguí el manual y las presentaciones entregadas.')

pdfmetrics.registerFont(TTFont('ArialA3',r'C:\Windows\Fonts\arial.ttf'))
pdfmetrics.registerFont(TTFont('ArialA3Bold',r'C:\Windows\Fonts\arialbd.ttf'))
style=ParagraphStyle('a3',fontName='ArialA3',fontSize=9.1,leading=12.4,spaceAfter=8,textColor=colors.HexColor('#24344a'))
small=ParagraphStyle('small',parent=style,fontSize=8,leading=10.1,spaceAfter=0)
head=ParagraphStyle('head',parent=style,fontName='ArialA3Bold',fontSize=20,leading=24,spaceAfter=10,textColor=colors.HexColor('#153655'))
sub=ParagraphStyle('sub',parent=style,fontSize=9,leading=12,spaceAfter=15,textColor=colors.HexColor('#486c85'))
story=[]
doc=Document();sec=doc.sections[0];sec.top_margin=Inches(.65);sec.bottom_margin=Inches(.65);sec.left_margin=Inches(.7);sec.right_margin=Inches(.7)
sec.page_width=Inches(8.5);sec.page_height=Inches(11)
normal=doc.styles['Normal'];normal.font.name='Arial';normal.font.size=Pt(9);normal.paragraph_format.space_after=Pt(7)
normal.paragraph_format.line_spacing=1.08
doc.styles['Title'].font.size=Pt(20);doc.styles['Title'].font.color.rgb=RGBColor.from_string('153655')
footer=sec.footer.paragraphs[0];footer.text='Cesar Eduardo Valdez Pinto · Actividad 3 · FinNorte';footer.style='Caption'
def para(t,st=style):return Paragraph(escape(str(t)).replace('\n','<br/>'),st)
for idx,(title,subtitle,items) in enumerate(pages):
    if idx:story.append(PageBreak());doc.add_page_break()
    story.extend([para(title,head),para(subtitle,sub)])
    doc.add_paragraph(title,'Title');doc.add_paragraph(subtitle,'Subtitle')
    for item in items:
        if item[0]=='p':story.append(para(item[1]));doc.add_paragraph(item[1])
        elif item[0]=='table':
            _,headers,rows,widths=item
            grid=[[para(v,small) for v in row] for row in [headers,*rows]]
            widths=[w*72 for w in widths] if widths else None
            t=Table(grid,colWidths=widths,hAlign='LEFT',repeatRows=1)
            t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e3edf4')),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#b7c7d3')),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6)]))
            story.extend([t,Spacer(1,10)])
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
        else:
            _,path,caption,w=item
            iw,ih=ImageReader(path).getSize();story.extend([Image(path,width=w*72,height=w*72*ih/iw),para(caption,small),Spacer(1,7)])
            doc.add_picture(path,width=Inches(w));doc.add_paragraph(caption,'Caption')
def foot(canvas,document):
    canvas.setStrokeColor(colors.HexColor('#b7c7d3'));canvas.line(50,39,562,39);canvas.setFont('ArialA3',8);canvas.setFillColor(colors.HexColor('#486c85'))
    canvas.drawString(50,27,'Cesar Eduardo Valdez Pinto · Actividad 3 · FinNorte');canvas.drawRightString(562,27,str(document.page))
pdf=OUT/'Actividad3_Cesar_Informe.pdf';word=OUT/'Actividad3_Cesar_Informe.docx'
SimpleDocTemplate(str(pdf),pagesize=(612,792),rightMargin=50,leftMargin=50,topMargin=44,bottomMargin=49,title='Actividad 3 - Cesar Eduardo Valdez Pinto',author='Cesar Eduardo Valdez Pinto').build(story,onFirstPage=foot,onLaterPages=foot)
doc.core_properties.title='Actividad 3 - Servicio de variante con autenticación';doc.core_properties.author='Cesar Eduardo Valdez Pinto';doc.save(word)
print(json.dumps({'pdf':str(pdf),'word':str(word)},ensure_ascii=False))
