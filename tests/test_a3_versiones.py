"""Tres escenarios oficiales y comparación del contrato de las tres mejoras."""
import pytest

from a3 import login_original, login_seguridad, login_eficiencia, login_mantenible
from api.auth import Autenticador, validar_token


def test_oficial_login_exitoso():
    assert login_original.login("admin", "1234") == "access granted"


def test_oficial_contrasena_incorrecta():
    assert login_original.login("admin", "incorrecta") == "wrong password"


def test_oficial_usuario_inexistente():
    assert login_original.login("no-existe", "1234") == "user not found "


@pytest.fixture(params=["seguridad", "eficiencia", "mantenible"])
def login_mejorado(request, tmp_path, monkeypatch):
    monkeypatch.setenv("TOKEN_SECRET", "s" * 64)
    ruta = str(tmp_path / "version.db")
    auth = Autenticador(ruta)
    auth.registrar("ana@finnorte.mx", "Segura123!")
    if request.param == "seguridad":
        funcion = lambda user, password: login_seguridad.login(user, password, ruta_db=ruta)
    elif request.param == "eficiencia":
        servicio = login_eficiencia.LoginEficiente(ruta)
        funcion = lambda user, password: login_eficiencia.login(user, password, servicio=servicio)
    else:
        servicio = login_mantenible.ServicioLogin(auth)
        funcion = lambda user, password: login_mantenible.login(user, password, servicio=servicio)
    yield funcion
    if request.param == "eficiencia":
        servicio.cerrar()
    auth.cerrar()


def test_versiones_login_exitoso(login_mejorado):
    r = login_mejorado("ana@finnorte.mx", "Segura123!")
    assert r["acceso"] and r["status"] == 200
    assert validar_token(r["token"]) == "ana@finnorte.mx"


def test_versiones_contrasena_incorrecta(login_mejorado):
    r = login_mejorado("ana@finnorte.mx", "Incorrecta123")
    assert not r["acceso"] and r["status"] == 401 and "token" not in r


def test_versiones_usuario_inexistente(login_mejorado):
    r = login_mejorado("no-existe@finnorte.mx", "Segura123!")
    assert not r["acceso"] and r["status"] == 401
    assert r["mensaje"] == login_mejorado("ana@finnorte.mx", "Incorrecta123")["mensaje"]


def test_mantenible_admite_proveedor_inyectado_sin_base_real():
    class ProveedorPrueba:
        def login(self, email, contrasena, ahora=None):
            assert email == "identidad" and contrasena == "entrada"
            return "token-simulado-del-proveedor"
    resultado = login_mantenible.login("identidad", "entrada", servicio=login_mantenible.ServicioLogin(ProveedorPrueba()))
    assert resultado["acceso"] and resultado["token"] == "token-simulado-del-proveedor"


def test_eficiencia_lote_perezoso_verifica_cada_intento(tmp_path, monkeypatch):
    from unittest.mock import patch
    monkeypatch.setenv("TOKEN_SECRET", "s" * 64)
    with login_eficiencia.LoginEficiente(str(tmp_path / "lote.db")) as servicio:
        servicio.autenticador.registrar("ana@finnorte.mx", "Segura123!")
        with patch.object(servicio.autenticador, "login", wraps=servicio.autenticador.login) as verificar:
            resultados = servicio.autenticar_lote(iter([
                ("ana@finnorte.mx", "Segura123!"), ("ana@finnorte.mx", "Incorrecta123")]))
            assert verificar.call_count == 0
            correcto = next(resultados)
            assert verificar.call_count == 1 and validar_token(correcto["token"]) == "ana@finnorte.mx"
            incorrecto = next(resultados)
            assert verificar.call_count == 2 and incorrecto["status"] == 401 and "token" not in incorrecto
            assert list(resultados) == []


def test_eficiencia_cierra_conexion_si_falla_iterador(tmp_path, monkeypatch):
    import sqlite3
    monkeypatch.setenv("TOKEN_SECRET", "s" * 64)
    def intentos():
        yield "nadie@finnorte.mx", "Incorrecta123"
        raise ValueError("Fallo sintético del productor")
    servicio = login_eficiencia.LoginEficiente(str(tmp_path / "cierre.db"))
    with pytest.raises(ValueError, match="productor"):
        with servicio:
            list(servicio.autenticar_lote(intentos()))
    with pytest.raises(sqlite3.ProgrammingError):
        servicio.autenticador.db.execute("SELECT 1")
