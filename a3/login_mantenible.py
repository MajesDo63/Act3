"""V3: separa presentación y autenticación mediante un contrato inyectable."""
from dataclasses import asdict, dataclass
from typing import Protocol

from api.auth import ErrorAuth


class ProveedorAutenticacion(Protocol):
    def login(self, email: str, contrasena: str, ahora: float | None = None) -> str: ...


@dataclass(frozen=True)
class ResultadoLogin:
    acceso: bool
    status: int
    mensaje: str
    token: str | None = None

    def como_dict(self) -> dict:
        resultado = asdict(self)
        if self.token is None:
            resultado.pop("token")
        return resultado


class ServicioLogin:
    def __init__(self, autenticador: ProveedorAutenticacion):
        self.autenticador = autenticador

    def autenticar(self, usuario: str, contrasena: str) -> ResultadoLogin:
        try:
            token = self.autenticador.login(usuario, contrasena)
            return ResultadoLogin(True, 200, "Acceso concedido", token)
        except ErrorAuth as error:
            return ResultadoLogin(False, error.status, str(error))


def login(user: str, password: str, *, servicio: ServicioLogin) -> dict:
    return servicio.autenticar(user, password).como_dict()
