"""V2: reutiliza conexión, índices y hash ficticio; no cachea contraseñas ni tokens."""
from api.auth import Autenticador, ErrorAuth


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


def login(user: str, password: str, *, servicio: LoginEficiente) -> dict:
    return servicio.login(user, password)
