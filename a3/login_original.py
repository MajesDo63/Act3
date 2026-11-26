"""Código oficial del enunciado: se conserva para análisis, no se usa en la API.

Fuente: Presentacion_Actividades_A3_A4.pptx, diapositiva 4 del ZIP del curso.
Las credenciales de juguete de este ejemplo no son cuentas del servicio.
"""


def login(user, password):
    if user == "admin":
        if password == "1234":
            return "access granted"
        else:
            return "wrong password"
    return "user not found "
