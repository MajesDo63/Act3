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
excluidas={'.env'}
ext={'.pyc','.pyo','.db','.sqlite','.sqlite3','.npy','.pem','.key'}
manifest={}
for src in sorted(ROOT.rglob('*')):
    if not src.is_file():continue
    rel=src.relative_to(ROOT)
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
    if not p.is_file() or '.git' in p.relative_to(DEST).parts:continue
    name=p.relative_to(DEST).as_posix()
    assert name in expected or name=='CONTENIDO_SHA256.json',f'Archivo adicional de una preparación anterior: {name}'
(DEST/'CONTENIDO_SHA256.json').write_text(json.dumps({'destino_github':'https://github.com/MajesDo63/Act3.git','archivos':manifest},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
archive=DEST.parent/'Actividad3_Cesar_Entrega.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(DEST.rglob('*')):
        if p.is_file() and '.git' not in p.relative_to(DEST).parts:z.write(p,'Act3/'+p.relative_to(DEST).as_posix())
    helper=DEST.parent/'PUBLICAR_ACT3.ps1'
    if helper.exists():z.write(helper,helper.name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for name in z.namelist():
        assert not any(p in ('.git','.venv','__pycache__') for p in Path(name).parts)
        assert Path(name).name!='.env'
        assert not any(s in z.read(name) for s in secretos),name
print(json.dumps({'archivos':len(manifest),'zip_bytes':archive.stat().st_size,'zip':str(archive),'carpeta':str(DEST),'credenciales_en_paquete':False},ensure_ascii=False))
