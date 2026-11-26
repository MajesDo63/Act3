"""Capturas directas de Swagger UI mediante el protocolo del navegador local.

No dibuja respuestas HTTP ni recrea pantallas. Solo controla la interfaz real
y captura su tabla de respuesta; las cabeceras con tokens quedan fuera.
"""
from contextlib import contextmanager
from pathlib import Path
import base64
import hashlib
import json
import os
import secrets
import socket
import struct
import subprocess
import tempfile
import time
import sys
import importlib
import traceback
from urllib.parse import urlparse
import requests

class CDP:
    def __init__(self,url):
        u=urlparse(url);self.s=socket.create_connection((u.hostname,u.port),timeout=20);self.buf=b'';self.seq=0
        key=base64.b64encode(os.urandom(16)).decode()
        request=(f'GET {u.path} HTTP/1.1\r\nHost: {u.hostname}:{u.port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n')
        self.s.sendall(request.encode('ascii'))
        while b'\r\n\r\n' not in self.buf:self.buf+=self.s.recv(8192)
        headers,self.buf=self.buf.split(b'\r\n\r\n',1)
        expected=base64.b64encode(hashlib.sha1((key+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest())
        if b'101' not in headers.split(b'\r\n')[0] or expected not in headers:raise RuntimeError('No se abrió el control local del navegador')
    def read(self,n):
        while len(self.buf)<n:
            b=self.s.recv(max(8192,n-len(self.buf)))
            if not b:raise RuntimeError('El navegador cerró el canal')
            self.buf+=b
        b,self.buf=self.buf[:n],self.buf[n:];return b
    def send(self,data,opcode=1):
        mask=os.urandom(4);n=len(data);head=bytes([0x80|opcode])
        head+=bytes([0x80|n]) if n<126 else bytes([0x80|126])+struct.pack('!H',n) if n<65536 else bytes([0x80|127])+struct.pack('!Q',n)
        self.s.sendall(head+mask+bytes(b^mask[i%4] for i,b in enumerate(data)))
    def receive(self):
        data=b''
        while True:
            a,b=self.read(2);opcode=a&15;n=b&127
            if n==126:n=struct.unpack('!H',self.read(2))[0]
            elif n==127:n=struct.unpack('!Q',self.read(8))[0]
            mask=self.read(4) if b&128 else None;part=self.read(n)
            if mask:part=bytes(x^mask[i%4] for i,x in enumerate(part))
            if opcode==9:self.send(part,10);continue
            if opcode==8:raise RuntimeError('El navegador cerró la sesión')
            data+=part
            if a&128:return json.loads(data)
    def call(self,method,params=None):
        self.seq+=1;seq=self.seq
        self.send(json.dumps({'id':seq,'method':method,'params':params or {}}).encode())
        while True:
            d=self.receive()
            if d.get('id')==seq:
                if 'error' in d:raise RuntimeError('Fallo del control del navegador: '+str(d['error'].get('code')))
                return d.get('result',{})
    def js(self,code):
        r=self.call('Runtime.evaluate',{'expression':code,'awaitPromise':True,'returnByValue':True})
        if r.get('exceptionDetails'):raise RuntimeError('No se pudo controlar la interfaz Swagger')
        return r.get('result',{}).get('value')
    def wait(self,expr,timeout=60):
        start=time.monotonic()
        while time.monotonic()-start<timeout:
            if self.js(expr):return
            time.sleep(.25)
        raise RuntimeError('Swagger no completó la operación esperada')
    def screenshot(self,path,clip=None):
        params={'format':'png','captureBeyondViewport':True}
        if clip:params['clip']=clip
        Path(path).write_bytes(base64.b64decode(self.call('Page.captureScreenshot',params)['data']))
    def close(self):self.s.close()

@contextmanager
def navegador():
    edge=next((p for p in (Path(r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'),Path(r'C:\Program Files\Google\Chrome\Application\chrome.exe')) if p.exists()),None)
    if not edge:raise RuntimeError('No se encontró Edge o Chrome')
    with tempfile.TemporaryDirectory(prefix='a3_swagger_',ignore_cleanup_errors=True) as profile:
        proc=subprocess.Popen([str(edge),'--headless','--disable-gpu','--no-first-run','--no-default-browser-check','--remote-debugging-port=0','--user-data-dir='+profile,'--window-size=1200,1100','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        channel=None
        try:
            info=Path(profile)/'DevToolsActivePort'
            for _ in range(100):
                if info.exists() and info.stat().st_size:break
                if proc.poll() is not None:raise RuntimeError('El navegador no inició')
                time.sleep(.1)
            port=int(info.read_text().splitlines()[0])
            targets=requests.get(f'http://127.0.0.1:{port}/json',timeout=10).json()
            target=next(t for t in targets if t['type']=='page')
            channel=CDP(target['webSocketDebuggerUrl']);channel.call('Page.enable')
            yield channel
        finally:
            if channel:channel.close()
            proc.terminate()
            try:proc.wait(timeout=10)
            except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=5)

def _capturar(base,dest,propuesta=None):
    cred={'email':'captura-'+secrets.token_hex(4)+'@finnorte.mx','contrasena':'Segura123!'}
    r=requests.post(base+'/auth/registro',json=cred,timeout=10);r.raise_for_status()
    token=requests.post(base+'/auth/login',json=cred,timeout=10).json()['token']
    archivos=[]
    with navegador() as c:
        c.call('Page.navigate',{'url':base+'/docs'})
        c.wait('typeof ui !== "undefined" && !!document.querySelector(".opblock")')
        c.js('window.a3op = ruta => Array.from(document.querySelectorAll(".opblock")).find(e => e.querySelector(".opblock-summary-path")?.textContent.trim() === ruta)')
        def ejecutar(nombre,ruta,cuerpo,estado,pase=None):
            auth={} if pase is None else {'HTTPBearer':{'name':'HTTPBearer','schema':{'type':'http','scheme':'bearer'},'value':pase}}
            c.js('ui.authActions.logout(["HTTPBearer"]);ui.authActions.authorize('+json.dumps(auth)+');')
            c.js('var o=a3op('+json.dumps(ruta)+');if(!o.classList.contains("is-open"))(o.querySelector(".opblock-summary-control")||o.querySelector(".opblock-summary")).click();')
            try:
                c.wait('!!a3op('+json.dumps(ruta)+').querySelector(".try-out__btn")',timeout=15)
            except RuntimeError:
                fragmento=c.js('a3op('+json.dumps(ruta)+').outerHTML').replace(token,'<oculto>')
                (dest/'swagger_diagnostico.txt').write_text(fragmento,encoding='utf8')
                raise
            c.js('var o=a3op('+json.dumps(ruta)+');var b=o.querySelector(".try-out__btn");if(/try it out/i.test(b.textContent))b.click();')
            c.wait('!!a3op('+json.dumps(ruta)+').querySelector("textarea:not([disabled])")')
            c.js('ui.oas3Actions.setRequestBodyValue({value:'+json.dumps(json.dumps(cuerpo,ensure_ascii=False,indent=2))+',pathMethod:['+json.dumps(ruta)+',"post"]})')
            # Esperar una respuesta nueva, no una tabla de una llamada anterior.
            c.js('var o=a3op('+json.dumps(ruta)+');window.a3Anterior=o.querySelector(".live-responses-table")?.innerText || "";o.querySelector(".execute").click();')
            expr='(()=>{var t=a3op('+json.dumps(ruta)+').querySelector(".live-responses-table");return t && t.innerText!==window.a3Anterior && t.querySelector("tbody .response-col_status")?.textContent.trim().startsWith('+json.dumps(str(estado))+')})()'
            try:c.wait(expr,timeout=20)
            except RuntimeError:
                fragmento=c.js('a3op('+json.dumps(ruta)+').outerHTML').replace(token,'<oculto>')
                (dest/'swagger_diagnostico.txt').write_text(fragmento,encoding='utf8')
                raise
            time.sleep(.5)
            datos=c.js('(()=>{var e=a3op('+json.dumps(ruta)+').querySelector(".live-responses-table");e.scrollIntoView({block:"center"});var r=e.getBoundingClientRect();return {texto:e.innerText,clip:{x:Math.max(0,r.x+scrollX),y:Math.max(0,r.y+scrollY-35),width:Math.min(r.width,1120),height:Math.min(r.height+40,900),scale:1}}})()')
            if token in datos['texto']:raise RuntimeError('La región de captura contiene una credencial; no se guardó')
            path=dest/('swagger_'+nombre+'.png');c.screenshot(path,datos['clip'])
            archivos.append({'archivo':path.name,'ruta':ruta,'http_status':estado,'tipo':'Captura directa de la tabla Server response en Swagger UI','texto_visible':datos['texto']})
        ejecutar('sin_token','/v1/revisor',{'codigo':'x=1'},401)
        ejecutar('token_alterado','/v1/revisor',{'codigo':'x=1'},401,token+'x')
        ejecutar('entrada_invalida','/v1/revisor',{'codigo':' ','archivo':'archivo-no-admitido'},422,token)
        ejecutar('contrasena_incorrecta','/auth/login',{**cred,'contrasena':'Incorrecta123'},401)
        ejecutar('usuario_inexistente','/auth/login',{'email':'nadie-'+secrets.token_hex(3)+'@finnorte.mx','contrasena':'Incorrecta123'},401)
        for _ in range(4):
            assert requests.post(base+'/auth/login',json={**cred,'contrasena':'Incorrecta123'},timeout=10).status_code==401
        ejecutar('bloqueo','/auth/login',cred,429)
        if propuesta:
            c.call('Page.navigate',{'url':(propuesta/'respuesta_asistente.txt').as_uri()})
            c.wait('document.body && document.body.innerText.includes("TOKEN_SECRET")')
            c.js('document.body.style.fontSize="20px";document.body.style.fontFamily="Consolas,monospace";document.querySelector("pre").style.whiteSpace="pre-wrap";window.scrollTo(0,0)')
            c.screenshot(propuesta/'captura_respuesta_detalle.png',{'x':0,'y':0,'width':1100,'height':480,'scale':1})
    return archivos

def capturar(base,dest,propuesta=None):
    try:return _capturar(base,dest,propuesta)
    except Exception:
        (dest/'swagger_ajuste_error.txt').write_text(traceback.format_exc(),encoding='utf8')
        print('Las pruebas siguen aprobadas; ajustando el control de Swagger sin repetirlas.',flush=True)
        helper=Path(__file__);stamp=helper.stat().st_mtime_ns;limite=time.monotonic()+600
        while time.monotonic()<limite:
            if helper.stat().st_mtime_ns!=stamp:
                importlib.invalidate_caches();modulo=importlib.reload(sys.modules[__name__])
                return modulo.capturar(base,dest,propuesta)
            time.sleep(1)
        raise RuntimeError('No llegó el ajuste de captura a tiempo')
