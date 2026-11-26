"""V1: autenticación segura, con apertura y cierre de conexión por solicitud."""
from api.auth import Autenticador, ErrorAuth


def login(user: str, password: str, *, ruta_db: str) -> dict:
    servicio = Autenticador(ruta_db)
    try:
        token = servicio.login(user, password)
        return {"acceso": True, "status": 200, "mensaje": "Acceso concedido", "token": token}
    except ErrorAuth as error:
        return {"acceso": False, "status": error.status, "mensaje": str(error)}
    finally:
        servicio.cerrar()
