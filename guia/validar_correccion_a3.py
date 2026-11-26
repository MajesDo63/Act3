"""Valida y documenta la nueva revisión, conservando las corridas anteriores."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import importlib
import json
import os
import platform
import sys
import time
import traceback

ROOT=Path(__file__).resolve().parents[1]
for p in (ROOT,ROOT/'src',ROOT/'guia',ROOT/'herramientas_a3',ROOT/'herramientas_pruebas'):sys.path.insert(0,str(p))
sys.stdout.reconfigure(encoding='utf8')
import completar_a3 as ejecucion
from benchmark_a3 import medir
from finnorte.config import _cargar_env

def guardar(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def firma():
    out={}
    for folder in ('api','a3','src','tests','prompts','corpus'):
        for p in (ROOT/folder).rglob('*'):
            if p.is_file() and p.suffix in ('.py','.json','.md') and not (folder=='a3' and p.suffix=='.md'):
                out[p.relative_to(ROOT).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
    return out

def main():
    args=argparse.ArgumentParser();args.add_argument('--continuar',action='store_true');opt=args.parse_args()
    os.chdir(ROOT)
    secreto=ROOT/'.env'
    if not secreto.exists():secreto=ROOT.parents[2]/'actividad3_cesar/.env'
    _cargar_env(secreto)
    pointer=ROOT/'bitacora/a3/ultima_revision.json'
    if opt.continuar:
        dest=Path(json.loads(pointer.read_text(encoding='utf8'))['directorio'])
        state=json.loads((dest/'estado.json').read_text(encoding='utf8'))
        assert firma()==json.loads((dest/'firma_fuentes.json').read_text(encoding='utf8')),'Las fuentes ejecutables cambiaron; crear una corrida nueva'
    else:
        dest=ROOT/'bitacora/a3'/('revision_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
        dest.mkdir(parents=True);guardar(pointer,{'directorio':str(dest)})
        state={'estado':'iniciado','fecha_utc':datetime.now(timezone.utc).isoformat(),'python':sys.version,'plataforma':platform.platform(),'directorio':str(ROOT),'grupos':[]}
        guardar(dest/'firma_fuentes.json',firma())
    def checkpoint(estado):
        state['estado']=estado;state['actualizado_utc']=datetime.now(timezone.utc).isoformat();guardar(dest/'estado.json',state)
    checkpoint('pruebas')
    try:
        grupos=[('checkpoint_auth',['tests/test_lab_producto.py','-k','mensaje or alterado or bloqueo or texto_plano']),
                ('laboratorio',['tests/test_lab_producto.py']),
                ('actividad3',['tests/test_a3_auth.py','tests/test_a3_api.py','tests/test_a3_versiones.py']),
                ('regresion',['tests'])]
        for nombre,argumentos in grupos:
            if not any(g['nombre']==nombre and g['codigo_salida']==0 for g in state['grupos']):
                state['grupos'].append(ejecucion.pytest_grupo(dest,nombre,argumentos));checkpoint('pruebas')
        actuales={g['nombre']:g for g in state['grupos']}
        assert actuales['actividad3']['aprobadas']==57 and actuales['regresion']['aprobadas']==163
        assert all(g['omitidas']==0 and g['fallos']==0 for g in state['grupos'])
        if not (dest/'comparacion_ciclo_completo.json').exists():
            checkpoint('benchmark');guardar(dest/'comparacion_ciclo_completo.json',medir())
        if not (dest/'http_fake_completo.json').exists():
            checkpoint('http_fake');ejecucion.evidencias_api(dest,'fake',True);guardar(dest/'http_fake_completo.json',{'completo':True})
        if not (dest/'swagger_manifest.json').exists():
            import capturar_swagger_a3 as capturas
            propuesta=ROOT/'bitacora/a3'/Path(json.loads((ROOT/'bitacora/a3/ultima_propuesta.json').read_text(encoding='utf8'))['directorio']).name
            for intento in range(3):
                try:
                    checkpoint('capturas_swagger')
                    with ejecucion.servidor(dest,'fake') as (base,_,__):imagenes=capturas.capturar(base,dest,propuesta)
                    guardar(dest/'swagger_manifest.json',{'base_url':base,'capturas':imagenes});break
                except Exception as error:
                    state['captura_error']=type(error).__name__+': '+str(error)[:180]
                    (dest/'captura_error.txt').write_text(traceback.format_exc(),encoding='utf8')
                    checkpoint('capturas_pendientes')
                    print('La captura directa necesita ajuste; las pruebas aprobadas están guardadas. Esperando actualización del ayudante.',flush=True)
                    helper=ROOT/'guia/capturar_swagger_a3.py';stamp=helper.stat().st_mtime_ns
                    limite=time.monotonic()+600
                    while time.monotonic()<limite and helper.stat().st_mtime_ns==stamp:time.sleep(1)
                    if helper.stat().st_mtime_ns==stamp:raise RuntimeError('No llegó el ajuste de captura a tiempo') from error
                    importlib.invalidate_caches();capturas=importlib.reload(capturas)
            else:raise RuntimeError('No se pudieron completar las capturas directas')
        if not (dest/'http_gemini_completo.json').exists():
            for intento in range(3):
                checkpoint('gemini')
                try:
                    ejecucion.evidencias_api(dest,'gemini',continuar=True)
                    guardar(dest/'http_gemini_completo.json',{'completo':True});break
                except RuntimeError:
                    eventos=json.loads((dest/'http_gemini.json').read_text(encoding='utf8'))['eventos']
                    ultimo=eventos[-1]['estado_http']
                    if ultimo not in (429,500,502,503,504) or intento==2:raise
                    checkpoint('gemini_reintento')
                    print('Proveedor temporalmente no disponible. Se conservan las respuestas 200 y solo se reintenta la entrada pendiente.',flush=True)
                    time.sleep(30*(intento+1))
        assert firma()==json.loads((dest/'firma_fuentes.json').read_text(encoding='utf8')),'Las fuentes cambiaron durante la corrida'
        incidencias={k:state.pop(k) for k in ('error','detalle','captura_error') if k in state}
        if incidencias:state.setdefault('incidencias_resueltas',[]).append(incidencias)
        checkpoint('completo');print('REVISION COMPLETA: '+str(dest),flush=True)
        return 0
    except Exception as error:
        state['error']=type(error).__name__;state['detalle']=str(error)[:250];checkpoint('interrumpido')
        print('REVISION INTERRUMPIDA: '+str(dest),flush=True);return 1

if __name__=='__main__':raise SystemExit(main())
