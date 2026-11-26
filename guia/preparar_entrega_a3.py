"""Copia y comprueba la entrega; excluye credenciales, entornos y caches."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT.parent/'output/actividad3_entrega/Act3'
DEST.mkdir(parents=True,exist_ok=True)
secretos=[]
for linea in (ROOT/'.env').read_text(encoding='utf8').splitlines():
    if '=' in linea:
        k,v=linea.split('=',1)
        if k.strip() in ('GEMINI_API_KEY','TOKEN_SECRET') and v.strip():secretos.append(v.strip().strip('\"\'').encode())
assert len(secretos)==2
omitir={'.git','.venv','__pycache__','.pytest_cache','privado','tmp'}
excluidas={'.env','swagger_diagnostico.txt','swagger_ajuste_error.txt','captura_error.txt'}
ext={'.pyc','.pyo','.db','.sqlite','.sqlite3','.npy','.pem','.key'}
manifest={}
excluir_raices={'Actividad 2','avance1','entregables','README_BASE_AVANCE1.md'}
excluir_guias={'a2_dictamen.py','a2_flujo_variante.py','s2_flujo_cambios.py','av1_reanudar_gemini31.py','verificar_evidencias.py'}
for src in sorted(ROOT.rglob('*')):
    if not src.is_file():continue
    rel=src.relative_to(ROOT)
    if rel.parts[0] in excluir_raices:continue
    if rel.parts[0]=='bitacora' and (len(rel.parts)<2 or rel.parts[1]!='a3'):continue
    if rel.parts[0]=='guia' and src.name in excluir_guias:continue
    if rel.parts[:2]==('datos','lab2_complemento'):continue
    if rel.as_posix()=='tests/test_a2_pipeline.py':continue
    if rel.parts[0]=='prompts' and src.name.startswith('cambio_'):continue
    if any(p in omitir or p.endswith('.egg-info') for p in rel.parts):continue
    if src.name in excluidas or src.suffix.lower() in ext or '.db-' in src.name:continue
    if src.name.startswith('.env.') and not src.name.endswith('example'):continue
    # Los experimentos previos se conservan en el equipo; la entrega señala la corrida completa.
    if rel.parts[:2]==('bitacora','a3') and len(rel.parts)==3 and src.suffix in ('.xml',):continue
    data=src.read_bytes()
    assert not any(s in data for s in secretos),f'Credencial detectada en {rel}'
    dst=DEST/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
    manifest[rel.as_posix()]=hashlib.sha256(data).hexdigest()
expected=set(manifest)
for p in DEST.rglob('*'):
    if not p.is_file():continue
    if any(part in omitir or part.endswith('.egg-info') for part in p.relative_to(DEST).parts):continue
    if p.suffix.lower() in ext:continue
    if p.name in excluidas:continue
    name=p.relative_to(DEST).as_posix()
    assert name in expected or name=='CONTENIDO_SHA256.json',f'Archivo adicional de una preparación anterior: {name}'
(DEST/'CONTENIDO_SHA256.json').write_text(json.dumps({'destino_github':'https://github.com/MajesDo63/Act3.git','archivos':manifest},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
archive=DEST.parent/'Actividad3_Cesar_Entrega.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for nombre in [*manifest,'CONTENIDO_SHA256.json']:
        z.write(DEST/nombre,'Act3/'+nombre)
    helper=DEST.parent/'PUBLICAR_ACT3.ps1'
    if helper.exists():z.write(helper,helper.name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for name in z.namelist():
        assert not any(p in ('.git','.venv','__pycache__') for p in Path(name).parts)
        assert Path(name).name!='.env'
        assert not any(s in z.read(name) for s in secretos),name
print(json.dumps({'archivos':len(manifest),'zip_bytes':archive.stat().st_size,'zip':str(archive),'carpeta':str(DEST),'credenciales_en_paquete':False},ensure_ascii=False))
