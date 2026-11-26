"""Comparación con igual frontera: inicializar, N logins y cerrar."""
from pathlib import Path
import hashlib
import statistics
import tempfile
import time
from unittest.mock import patch

def medir():
    from api.auth import Autenticador
    from a3 import login_original, login_seguridad, login_eficiencia, login_mantenible
    muestras=[]
    with tempfile.TemporaryDirectory(prefix='a3_ciclo_') as tmp:
        db=str(Path(tmp)/'usuarios.db')
        semilla=Autenticador(db)
        semilla.registrar('ana@finnorte.mx','Segura123!');semilla.cerrar()
        for n in (1,10):
            for version in ('original','seguridad','eficiencia','mantenible'):
                for repeticion in range(1,6):
                    funcion_pbkdf2=hashlib.pbkdf2_hmac
                    with patch('hashlib.pbkdf2_hmac',wraps=funcion_pbkdf2) as derivaciones:
                        t0=time.perf_counter_ns();recurso=None
                        if version=='eficiencia':recurso=login_eficiencia.LoginEficiente(db)
                        elif version=='mantenible':recurso=Autenticador(db)
                        servicio=login_mantenible.ServicioLogin(recurso) if version=='mantenible' else None
                        t1=time.perf_counter_ns();latencias=[]
                        try:
                            for _ in range(n):
                                a=time.perf_counter_ns()
                                if version=='original':resultado=login_original.login('admin','1234')
                                elif version=='seguridad':resultado=login_seguridad.login('ana@finnorte.mx','Segura123!',ruta_db=db)
                                elif version=='eficiencia':resultado=recurso.login('ana@finnorte.mx','Segura123!')
                                else:resultado=servicio.autenticar('ana@finnorte.mx','Segura123!').como_dict()
                                latencias.append((time.perf_counter_ns()-a)/1e6)
                                assert resultado=='access granted' if version=='original' else resultado['acceso']
                            t2=time.perf_counter_ns()
                        finally:
                            if recurso is not None:recurso.cerrar()
                        t3=time.perf_counter_ns()
                        esperado=0 if version=='original' else 2*n if version=='seguridad' else n+1
                        assert derivaciones.call_count==esperado
                    muestras.append(dict(version=version,n=n,repeticion=repeticion,inicio_ms=(t1-t0)/1e6,
                        solicitudes_ms=(t2-t1)/1e6,cierre_ms=(t3-t2)/1e6,total_ms=(t3-t0)/1e6,
                        mediana_solicitud_ms=statistics.median(latencias),derivaciones=derivaciones.call_count))
    resumen=[]
    for n in (1,10):
        for version in ('original','seguridad','eficiencia','mantenible'):
            filas=[f for f in muestras if f['n']==n and f['version']==version]
            resumen.append(dict(version=version,n=n,repeticiones=len(filas),
                mediana_total_ms=round(statistics.median(f['total_ms'] for f in filas),4),
                mediana_inicio_ms=round(statistics.median(f['inicio_ms'] for f in filas),4),
                mediana_solicitud_ms=round(statistics.median(f['mediana_solicitud_ms'] for f in filas),4),
                derivaciones=filas[0]['derivaciones']))
    return {'metodo':'Cinco repeticiones por versión y N=1/10. Total incluye inicialización, N logins y cierre. El registro de usuario es precondición común y queda fuera. No se mide carga HTTP. V1 inicializa dentro de cada solicitud; V2/V3 una vez por ciclo. V0 es un contraste inseguro, no una optimización aceptable.',
            'resumen':resumen,'muestras':muestras}
