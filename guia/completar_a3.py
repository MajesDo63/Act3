"""Ejecuta pruebas, comparación y evidencias A3 sin mostrar credenciales.

Usar desde PowerShell normal cuando el entorno restringido no permite loopback.
No publica en GitHub ni modifica archivos del repositorio anterior del equipo.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from contextlib import contextmanager
from unittest.mock import patch
import argparse
import hashlib
import html
import json
import os
import platform
import secrets
import shutil
import socket
import statistics
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET

RAIZ = Path(__file__).resolve().parents[1]
for carpeta in (RAIZ, RAIZ/'src', RAIZ/'herramientas_pruebas', RAIZ/'herramientas_a3'):
    sys.path.insert(0, str(carpeta))
sys.stdout.reconfigure(encoding='utf8')
CLAVES_OCULTAS = {'token', 'contrasena', 'password', 'gemini_api_key', 'token_secret', 'authorization'}


def guardar(ruta, valor):
    ruta.write_text(json.dumps(valor, ensure_ascii=False, indent=2)+'\n', encoding='utf8')


def sanear(valor):
    if isinstance(valor, dict):
        return {k: '<oculto>' if k.lower() in CLAVES_OCULTAS else sanear(v) for k,v in valor.items()}
    if isinstance(valor, list): return [sanear(x) for x in valor]
    return valor


def pytest_grupo(destino, nombre, argumentos):
    comando = [sys.executable, '-m', 'pytest', *argumentos, '-q', '--junitxml='+str(destino/(nombre+'.xml'))]
    entorno = dict(os.environ, PYTEST_DISABLE_PLUGIN_AUTOLOAD='1', PYTHONIOENCODING='utf-8', LLM_PROVIDER='fake', EMB_PROVIDER='hash')
    inicio = time.monotonic()
    proceso = subprocess.run(comando, cwd=RAIZ, env=entorno, capture_output=True, text=True, encoding='utf8', timeout=360)
    salida = proceso.stdout+'\n'+proceso.stderr
    (destino/(nombre+'.txt')).write_text(salida, encoding='utf8')
    raiz = ET.parse(destino/(nombre+'.xml')).getroot()
    casos = list(raiz.iter('testcase'))
    resumen = dict(nombre=nombre, comando=comando, directorio=str(RAIZ), codigo_salida=proceso.returncode,
                   segundos=round(time.monotonic()-inicio,3), pruebas=len(casos),
                   aprobadas=sum(not any(c.find(t) is not None for t in ('failure','error','skipped')) for c in casos),
                   omitidas=sum(c.find('skipped') is not None for c in casos),
                   fallos=sum(c.find('failure') is not None or c.find('error') is not None for c in casos))
    print(nombre, resumen['aprobadas'], 'aprobadas;', resumen['omitidas'], 'omitidas', flush=True)
    if proceso.returncode: raise RuntimeError('Fallaron pruebas; consultar '+str(destino/(nombre+'.txt')))
    return resumen


def comparar_versiones(destino):
    from api.auth import Autenticador
    from a3 import login_original, login_seguridad, login_eficiencia, login_mantenible
    os.environ.setdefault('TOKEN_SECRET', secrets.token_hex(32))
    registros=[]
    with tempfile.TemporaryDirectory(prefix='a3_benchmark_') as tmp:
        db=str(Path(tmp)/'usuarios.db')
        auth=Autenticador(db)
        auth.registrar('ana@finnorte.mx','Segura123!')
        eficiente=login_eficiencia.LoginEficiente(db)
        mantenible=login_mantenible.ServicioLogin(auth)
        funciones={
            'original':lambda:login_original.login('admin','1234'),
            'seguridad':lambda:login_seguridad.login('ana@finnorte.mx','Segura123!',ruta_db=db),
            'eficiencia':lambda:login_eficiencia.login('ana@finnorte.mx','Segura123!',servicio=eficiente),
            'mantenible':lambda:login_mantenible.login('ana@finnorte.mx','Segura123!',servicio=mantenible),
        }
        try:
            for nombre, funcion in funciones.items():
                funcion()
                tiempos=[]
                original=hashlib.pbkdf2_hmac
                with patch('hashlib.pbkdf2_hmac', wraps=original) as derivaciones:
                    for _ in range(10):
                        inicio=time.perf_counter_ns();r=funcion();tiempos.append((time.perf_counter_ns()-inicio)/1e6)
                        assert r=='access granted' if nombre=='original' else r['acceso']
                registros.append(dict(version=nombre,repeticiones=10,mediana_ms=round(statistics.median(tiempos),4),
                                       minimo_ms=round(min(tiempos),4),maximo_ms=round(max(tiempos),4),
                                       llamadas_pbkdf2=derivaciones.call_count,tiempos_ms=tiempos))
        finally:
            eficiente.cerrar();auth.cerrar()
    guardar(destino/'comparacion_versiones.json',dict(metodo='10 logins exitosos por version despues de un calentamiento. Inicializacion de servicios reutilizados fuera del intervalo; V1 abre y cierra por solicitud. No es una prueba de carga HTTP.',resultados=registros))
    return registros


@contextmanager
def servidor(destino, proveedor):
    import requests
    with socket.socket() as s:
        s.bind(('127.0.0.1',0));puerto=s.getsockname()[1]
    base='http://127.0.0.1:'+str(puerto)
    temporal=tempfile.TemporaryDirectory(prefix='a3_api_',ignore_cleanup_errors=True)
    env=dict(os.environ, LLM_PROVIDER=proveedor, EMB_PROVIDER='gemini' if proveedor=='gemini' else 'hash',
             AUTH_DB=str(Path(temporal.name)/'usuarios.db'),TOKEN_SECRET=secrets.token_hex(32),
             PYTHONPATH=os.pathsep.join(str(RAIZ/p) for p in ('.','src','herramientas_a3','herramientas_pruebas')),
             PYTHONIOENCODING='utf-8', FINNORTE_DIR_TRAZAS=str(destino/('trazas_'+proveedor)))
    log=(destino/('servidor_'+proveedor+'.txt')).open('w',encoding='utf8')
    # En Windows el lanzador de venv puede dejar un hijo vivo si se termina al padre.
    # Se controla directamente el intérprete real, con los mismos módulos en PYTHONPATH.
    comando=[getattr(sys,'_base_executable',sys.executable),'-m','uvicorn','api.producto:app','--host','127.0.0.1','--port',str(puerto),'--log-level','warning']
    proc=subprocess.Popen(comando,cwd=RAIZ,env=env,stdout=log,stderr=subprocess.STDOUT,
                          creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    try:
        for _ in range(100):
            if proc.poll() is not None: raise RuntimeError('No inicio el servidor; consultar registro')
            try:
                if requests.get(base+'/salud',timeout=1).status_code==200:break
            except requests.RequestException:pass
            time.sleep(.15)
        else:raise RuntimeError('El servicio no respondio a /salud')
        yield base,env,comando
    finally:
        proc.terminate()
        try:proc.wait(timeout=10)
        except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=5)
        log.close();temporal.cleanup()


def evidencias_api(destino, proveedor, incluir_seguridad=False):
    import requests
    eventos=[]
    with servidor(destino,proveedor) as (base,env,comando):
        token=None
        def pedir(etiqueta, metodo, ruta, cuerpo=None, autorizado=True, token_distinto=None):
            pase=token_distinto if token_distinto is not None else token
            headers={'Authorization':'Bearer '+pase} if autorizado and pase else {}
            inicio=time.perf_counter()
            r=requests.request(metodo,base+ruta,json=cuerpo,headers=headers,timeout=240)
            try:datos=r.json()
            except ValueError:datos={'texto':r.text[:500]}
            eventos.append(dict(etiqueta=etiqueta,proveedor=proveedor,fecha_utc=datetime.now(timezone.utc).isoformat(),
                                metodo=metodo,ruta=ruta,solicitud=sanear(cuerpo),estado_http=r.status_code,
                                tipo_contenido=r.headers.get('content-type'),retry_after=r.headers.get('retry-after'),
                                duracion_ms=round((time.perf_counter()-inicio)*1000,2),respuesta=sanear(datos)))
            guardar(destino/('http_'+proveedor+'.json'),dict(base_url=base,comando=comando,eventos=eventos))
            print(proveedor,etiqueta,r.status_code,flush=True)
            return r,datos
        pedir('salud','GET','/salud',autorizado=False)
        cred={'email':'ana@finnorte.mx','contrasena':'Segura123!'}
        if incluir_seguridad:
            r,_=pedir('sin_token','POST','/v1/revisor',{'codigo':'x=1'},False);assert r.status_code==401
        r,_=pedir('registro','POST','/auth/registro',cred,False);assert r.status_code==201
        r,datos=pedir('login_exitoso','POST','/auth/login',cred,False);assert r.status_code==200
        token=datos['token']
        if incluir_seguridad:
            r,_=pedir('correo_duplicado','POST','/auth/registro',cred,False);assert r.status_code==409
            r,a=pedir('contrasena_incorrecta','POST','/auth/login',{**cred,'contrasena':'Incorrecta123'},False)
            r,b=pedir('usuario_inexistente','POST','/auth/login',{'email':'nadie@finnorte.mx','contrasena':'Incorrecta123'},False)
            assert a['detail']==b['detail'] and a['status']==b['status']==401
            alterado=token[:-1]+('A' if token[-1]!='A' else 'B')
            r,_=pedir('token_alterado','POST','/v1/revisor',{'codigo':'x=1'},token_distinto=alterado);assert r.status_code==401
            from api.auth import emitir_token
            previo=os.environ.get('TOKEN_SECRET');os.environ['TOKEN_SECRET']=env['TOKEN_SECRET']
            try:expirado=emitir_token(cred['email'],ahora=time.time()-901)
            finally:
                if previo is None:os.environ.pop('TOKEN_SECRET',None)
                else:os.environ['TOKEN_SECRET']=previo
            r,_=pedir('token_expirado','POST','/v1/revisor',{'codigo':'x=1'},token_distinto=expirado);assert r.status_code==401
            r,_=pedir('entrada_invalida','POST','/v1/revisor',{'codigo':' '});assert r.status_code==422
            bloqueado={'email':'bloqueo@finnorte.mx','contrasena':'Segura123!'}
            pedir('registro_para_bloqueo','POST','/auth/registro',bloqueado,False)
            for intento in range(5):
                r,_=pedir('fallo_'+str(intento+1),'POST','/auth/login',{**bloqueado,'contrasena':'Incorrecta123'},False)
                assert r.status_code==401
            r,_=pedir('bloqueo','POST','/auth/login',bloqueado,False);assert r.status_code==429
        for nombre in ('usuarios.py','limites.py'):
            codigo=(RAIZ/'datos/v2-revisor/codigo'/nombre).read_text(encoding='utf8')
            r,salida=pedir('revisor_'+nombre,'POST','/v1/revisor',{'codigo':codigo})
            if r.status_code!=200:raise RuntimeError('No se completo la entrada '+nombre+' con '+proveedor+'; se guardo el resultado HTTP')
            if proveedor=='gemini' and salida.get('demo',True):raise RuntimeError('La respuesta no acredita el motor real con Gemini')
    return eventos


def capturas(destino, grupos):
    edge=next((p for p in [Path(r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'),Path(r'C:\Program Files\Google\Chrome\Application\chrome.exe')] if p.exists()),None)
    if edge is None:return []
    def tomar(nombre,titulo,contenido):
        pagina=destino/(nombre+'.html')
        pagina.write_text('<!doctype html><meta charset="utf-8"><style>body{font:16px Arial;margin:35px;background:#f4f6fa;color:#172434}h1{font-size:25px}section{background:white;padding:20px;border:1px solid #ccd3df;margin:15px 0}pre{white-space:pre-wrap;font:13px Consolas;line-height:1.4}small{color:#465565}.grid{display:grid;grid-template-columns:1fr 1fr;gap:15px}</style><h1>'+html.escape(titulo)+'</h1><small>Registro de ejecuciones reales · Cesar Eduardo Valdez Pinto · '+html.escape(destino.name)+'</small>'+contenido,encoding='utf8')
        png=destino/(nombre+'.png')
        with tempfile.TemporaryDirectory(prefix='a3_captura_',ignore_cleanup_errors=True) as perfil:
            r=subprocess.run([str(edge),'--headless','--disable-gpu','--no-first-run','--user-data-dir='+perfil,'--window-size=1400,1100','--virtual-time-budget=2000','--screenshot='+str(png),pagina.as_uri()],capture_output=True,timeout=45,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        return png.name if r.returncode==0 and png.exists() else None
    resultados=[]
    if (destino/'http_fake.json').exists():
        eventos=json.loads((destino/'http_fake.json').read_text(encoding='utf8'))['eventos']
        seleccion=[e for e in eventos if e['etiqueta'] in ('sin_token','token_alterado','entrada_invalida','bloqueo')]
        tarjetas=''.join('<section><b>'+html.escape(e['etiqueta'])+' · HTTP '+str(e['estado_http'])+'</b><pre>'+html.escape(json.dumps(e['respuesta'],ensure_ascii=False,indent=2))+'</pre></section>' for e in seleccion)
        resultados.append(tomar('captura_errores','A3 · Evidencias HTTP de autenticación y validación','<div class="grid">'+tarjetas+'</div>'))
    secciones=''
    for grupo in grupos[:3]:
        texto=(destino/(grupo['nombre']+'.txt')).read_text(encoding='utf8')
        secciones+='<section><b>'+html.escape(grupo['nombre'])+'</b><pre>'+html.escape(texto[-1800:])+'</pre></section>'
    resultados.append(tomar('captura_pruebas','A3 · Resultados de pytest',secciones))
    return [r for r in resultados if r]


def limpiar_servidor_anterior(destino):
    """Detiene solo el ayudante uvicorn del puerto documentado por esta ejecución."""
    previo=destino/'http_fake.json'
    if os.name!='nt' or not previo.exists():return
    from urllib.parse import urlparse
    puerto=urlparse(json.loads(previo.read_text(encoding='utf8'))['base_url']).port
    assert isinstance(puerto,int) and 1024<=puerto<=65535
    orden=("$r=@(); Get-NetTCPConnection -State Listen -LocalPort "+str(puerto)+" -ErrorAction SilentlyContinue | ForEach-Object { "
           "$p=Get-CimInstance Win32_Process -Filter ('ProcessId='+$_.OwningProcess); "
           "if($p.CommandLine -match 'uvicorn api[.]producto:app' -and $p.CommandLine -match '--port "+str(puerto)+"(?: |$)'){ "
           "$r+=$p.ProcessId; Stop-Process -Id $p.ProcessId -Force -ErrorAction Stop }}; ConvertTo-Json -InputObject @($r) -Compress")
    r=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',orden],capture_output=True,text=True,timeout=30,
                     creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    guardar(destino/'limpieza_servidor_anterior.json',dict(codigo_salida=r.returncode,puerto_documentado=puerto,procesos=r.stdout.strip()))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--sin-gemini',action='store_true');parser.add_argument('--reanudar',action='store_true');args=parser.parse_args()
    os.chdir(RAIZ)
    from finnorte.config import _cargar_env
    _cargar_env()
    destino=Path(json.loads((RAIZ/'bitacora/a3/ultima_ejecucion.json').read_text(encoding='utf8'))['directorio']) if args.reanudar else RAIZ/'bitacora/a3'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    destino.mkdir(parents=True,exist_ok=True)
    estado=dict(estado='iniciado',fecha_utc=datetime.now(timezone.utc).isoformat(),python=sys.version,
                plataforma=platform.platform(),directorio=str(RAIZ),destino=str(destino))
    anterior=json.loads((destino/'estado.json').read_text(encoding='utf8')) if args.reanudar else None
    if anterior and not (destino/'estado_interrupcion_original.json').exists():
        shutil.copy2(destino/'estado.json',destino/'estado_interrupcion_original.json')
    guardar(RAIZ/'bitacora/a3/ultima_ejecucion.json',{'directorio':str(destino)})
    medidos={}
    for carpeta in ('api','a3','src','tests','prompts','corpus'):
        for p in (RAIZ/carpeta).rglob('*'):
            if p.is_file() and p.suffix in ('.py','.md','.json'):
                medidos[p.relative_to(RAIZ).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
    if anterior:
        firma=json.loads((destino/'firma_fuentes.json').read_text(encoding='utf8'))
        assert all(hashlib.sha256((RAIZ/n).read_bytes()).hexdigest()==h for n,h in firma.items()),'Cambio de fuentes desde la ejecución anterior'
        medidos=firma
        guardar(destino/'reanudacion.json',dict(fecha_utc=datetime.now(timezone.utc).isoformat(),motivo='Corrección del cierre del lanzador Windows; fuentes de API y pruebas conservadas',
                sha256_script=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),pruebas_anteriores_preservadas=True))
    else:guardar(destino/'firma_fuentes.json',medidos)
    grupos=anterior['grupos'] if anterior else []
    try:
        if not anterior:
            grupos.append(pytest_grupo(destino,'checkpoint_auth',['tests/test_lab_producto.py','-k','mensaje or alterado or bloqueo or texto_plano']))
            grupos.append(pytest_grupo(destino,'laboratorio',['tests/test_lab_producto.py']))
            grupos.append(pytest_grupo(destino,'actividad3',['tests/test_a3_auth.py','tests/test_a3_api.py','tests/test_a3_versiones.py']))
            grupos.append(pytest_grupo(destino,'regresion',['tests']))
            comparar_versiones(destino)
            evidencias_api(destino,'fake',True)
        else:
            assert len(grupos)==4 and all(g['codigo_salida']==0 and not g['fallos'] for g in grupos)
            limpiar_servidor_anterior(destino)
            print('Resultados aprobados conservados. Reanudando Gemini.',flush=True)
        if not args.sin_gemini:
            import requests
            clave=os.getenv('GEMINI_API_KEY','')
            acceso=requests.get('https://generativelanguage.googleapis.com/v1beta/models',headers={'x-goog-api-key':clave},timeout=30)
            disponibles=[m['name'].removeprefix('models/') for m in acceso.json().get('models',[]) if 'generateContent' in m.get('supportedGenerationMethods',[])] if acceso.status_code==200 else []
            solicitado=os.getenv('LLM_MODEL','gemini-3.1-flash-lite')
            seleccionado=solicitado if solicitado in disponibles else next((x for x in ('gemini-flash-lite-latest','gemini-3.1-flash-lite','gemini-2.5-flash-lite') if x in disponibles),None)
            guardar(destino/'acceso_gemini.json',dict(estado_http=acceso.status_code,modelo_solicitado=solicitado,modelo_elegido=seleccionado))
            if acceso.status_code!=200 or not seleccionado:raise RuntimeError('No se confirmo acceso a un modelo Gemini; ver acceso_gemini.json')
            os.environ['LLM_MODEL']=seleccionado
            evidencias_api(destino,'gemini')
        assert all(hashlib.sha256((RAIZ/n).read_bytes()).hexdigest()==h for n,h in medidos.items()),'Cambio de codigo durante la ejecucion'
        estado.update(estado='completo' if not args.sin_gemini else 'local_completo_gemini_pendiente',grupos=grupos)
    except Exception as error:
        estado.update(estado='interrumpido',error=type(error).__name__,detalle=str(error)[:300],grupos=grupos)
        print('Proceso interrumpido; consultar registros en',destino,flush=True)
    finally:
        try:estado['capturas']=capturas(destino,grupos)
        except Exception as error:estado['capturas_error']=type(error).__name__
        estado['cierre_utc']=datetime.now(timezone.utc).isoformat()
        guardar(destino/'estado.json',estado)
        print('ESTADO:',estado['estado'],'EVIDENCIAS:',destino,flush=True)
    return 0 if estado['estado']=='completo' else 1


if __name__=='__main__':raise SystemExit(main())
