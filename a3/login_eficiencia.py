"""V2: reutiliza conexión, índices y hash ficticio; no cachea contraseñas ni tokens."""
from api.auth import Autenticador, ErrorAuth
from collections.abc import Iterable, Iterator


class LoginEficiente:
    def __init__(self, ruta_db: str):
        self.autenticador = Autenticador(ruta_db)

    def login(self, user: str, password: str) -> dict:
        try:
            token = self.autenticador.login(user, password)
            return {"acceso": True, "status": 200, "mensaje": "Acceso concedido", "token": token}
        except ErrorAuth as error:
            return {"acceso": False, "status": error.status, "mensaje": str(error)}

    def cerrar(self):
        self.autenticador.cerrar()

    def __enter__(self):
        return self

    def __exit__(self, tipo, valor, traza):
        self.cerrar()
        return False

    def autenticar_lote(self, intentos: Iterable[tuple[str, str]]) -> Iterator[dict]:
        """Procesa un intento a la vez sin construir una lista de credenciales."""
        for usuario, contrasena in intentos:
            yield self.login(usuario, contrasena)


def login(user: str, password: str, *, servicio: LoginEficiente) -> dict:
    return servicio.login(user, password)
