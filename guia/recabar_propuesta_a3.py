"""Conserva una propuesta nueva y real de Gemini para la revisión de A3.

Se ejecuta fuera del entorno restringido; no copia ni ejecuta código del modelo.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
sys.stdout.reconfigure(encoding='utf8')
from finnorte.config import _cargar_env
_cargar_env()

PROMPT='''Actúa como ingeniero de seguridad de una fintech. Diseña en Python, sin dependencias externas de criptografía, hash_contrasena, verificar_contrasena, emitir_token y validar_token, más un login SQLite con bloqueo después de cinco fallos. Requisitos: PBKDF2-HMAC-SHA256 con sal aleatoria; compare_digest; token firmado con vigencia máxima de 900 segundos; secreto tomado de TOKEN_SECRET; el mismo mensaje para cuenta inexistente y contraseña incorrecta; bitácora que no registre contraseña ni token. Incluye pseudocódigo suficiente para revisar transacciones, reloj, límites e inicialización. No necesito un programa completo; explica las decisiones y los riesgos pendientes.

El servicio de la A3 usa FastAPI y debe tener POST /v1/revisor, protegido, entrada propia {"codigo": "..."}, límite por usuario y errores problem+json. El motor de equipo también permite leer entradas desde archivo cuando se usa desde su CLI. Explica cómo impedir que la API exponga esa lectura de archivos, incluyendo el riesgo de dejar un segundo endpoint genérico.

Analiza este login oficial, que se conserva solo como ejemplo inseguro:
def login(user,password):
    if user=="admin":
        if password=="1234": return "access granted"
        else: return "wrong password"
    return "user not found "

Propón tres refactorizaciones separadas: seguridad, eficiencia y mantenibilidad. Relaciona cada una con un problema concreto del original. Evita presentar omitir controles de seguridad como optimización. Explica cómo comparar la inicialización y las llamadas de manera justa. Propón tres pruebas oficiales y al menos tres adicionales con sus oráculos. Señala qué partes de tu propuesta requieren comprobación. Máximo 1000 palabras; no afirmes haber ejecutado pruebas.'''

def save(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def main():
    import requests
    key=os.getenv('GEMINI_API_KEY','')
    if not key:raise RuntimeError('Falta la configuración local de Gemini; no se imprimirá ninguna credencial')
    model=os.getenv('LLM_MODEL','gemini-3.1-flash-lite')
    dest=ROOT/'bitacora/a3'/('propuesta_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    dest.mkdir(parents=True)
    request={'contents':[{'role':'user','parts':[{'text':PROMPT}]}],'generationConfig':{'temperature':0.2}}
    (dest/'prompt.txt').write_text(PROMPT,encoding='utf8');save(dest/'solicitud.json',request)
    before={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ('api/auth.py','api/producto.py','a3/login_original.py','a3/login_seguridad.py','a3/login_eficiencia.py','a3/login_mantenible.py')}
    start=time.perf_counter()
    r=requests.post('https://generativelanguage.googleapis.com/v1beta/models/'+model+':generateContent',headers={'x-goog-api-key':key},json=request,timeout=180)
    meta={'fecha_utc':datetime.now(timezone.utc).isoformat(),'modelo':model,'http_status':r.status_code,'duracion_s':round(time.perf_counter()-start,3),'tipo':'Propuesta nueva para revisión de la versión corregida; no es la respuesta original de la primera entrega.','sha256_antes_de_revision':before}
    save(dest/'meta.json',meta)
    if r.status_code!=200:raise RuntimeError('La consulta no terminó con HTTP 200; revisar meta.json sin publicar credenciales')
    data=r.json();text=''.join(p.get('text','') for p in data.get('candidates',[{}])[0].get('content',{}).get('parts',[]) if not p.get('thought'))
    if not text.strip():raise RuntimeError('El modelo no devolvió una propuesta de texto')
    if key in text:raise RuntimeError('La respuesta no es apta para evidencia pública')
    save(dest/'respuesta_api.json',data);(dest/'respuesta_asistente.txt').write_text(text,encoding='utf8')
    save(ROOT/'bitacora/a3/ultima_propuesta.json',{'directorio':str(dest)})
    edge=next((p for p in (Path(r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'),Path(r'C:\Program Files\Google\Chrome\Application\chrome.exe')) if p.exists()),None)
    if edge:
        with tempfile.TemporaryDirectory(prefix='a3_propuesta_',ignore_cleanup_errors=True) as profile:
            result=subprocess.run([str(edge),'--headless','--disable-gpu','--no-first-run','--user-data-dir='+profile,'--window-size=1500,1400','--screenshot='+str(dest/'captura_respuesta_asistente.png'),(dest/'respuesta_asistente.txt').as_uri()],capture_output=True,timeout=45,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        meta['captura_respuesta_real']=result.returncode==0 and (dest/'captura_respuesta_asistente.png').exists()
    save(dest/'meta.json',meta)
    print('PROPUESTA REAL GUARDADA: '+str(dest))
    print('La respuesta no se ejecutó ni se incorporó al servicio. Se revisará antes de cerrar la corrección.')

if __name__=='__main__':main()
