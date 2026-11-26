# Evaluación de la propuesta

Consulté Gemini 3.1 Flash-Lite para contrastar el diseño de autenticación. Guardé el prompt, la respuesta, el JSON del proveedor y las capturas en bitacora/a3/propuesta_20261126T024927Z/.

Comparé la propuesta con el manual y con el comportamiento que necesitaba para el servicio. En la siguiente tabla relacioné cada pasaje con su regla y con la decisión que tomé. Los números de línea corresponden a respuesta_asistente.txt.

| Pasaje real del modelo | Falla o ambigüedad | Regla y decisión |
| --- | --- | --- |
| L10: `os.environ.get("TOKEN_SECRET", "secreto-muy-seguro")` | El respaldo conocido permite firmar tokens si falta configuración; contradice exigir secreto externo. | SEC-01, SEC-06, ing-02: rechacé el respaldo; `_secreto()` falla si falta o mide menos de 32 caracteres. Prueba del secreto ausente. |
| L29–36: solo firma y `exp`, sin `iat`. | No comprueba duración máxima entre emisión y expiración ni emisión futura. | SEC-06, ing-07: conservé sub/iat/exp y límites estrictos; pruebas de reloj cero, expiración exacta y fechas futuras. |
| L39: rechazar si `intentos_fallidos >= 5`. | Menciona `bloqueado_hasta` pero no define expiración ni transacción; puede bloquear indefinidamente o perder intentos. | SEC-05, SEC-06: ventana 900 s, reinicio tras éxito y commit antes de ErrorAuth; pruebas de persistencia y caducidad. |
| L57: llama «eficiencia» a cambiar a `compare_digest`. | Es seguridad, no prueba de una mejora de rendimiento. | SEC-06, SEC-10: rechacé la clasificación. V2 reutiliza recursos y procesa lotes perezosos; benchmark del ciclo completo. |
| L72: el tiempo «debe ser idéntico». | La igualdad exacta depende de ruido del sistema y no es un oráculo reproducible. | SEC-06: rechazo la igualdad literal. Mensaje uniforme y verificación también para cuentas desconocidas, sin afirmar inmunidad temporal. |
| L84–87: `payload: dict` y token por `Header`. | Omite modelo propio, campos extra prohibidos, límite y problem+json. No retira explícitamente otra ruta genérica. | SEC-04, SEC-08, ing-07: CodigoRevisor y HTTPBearer; retiro de `/v1/variante`, su modelo y fallback demo. Pruebas de 404 y archivo sintético nunca abierto. |

Además, conservé los tres casos del login oficial: éxito, contraseña incorrecta y usuario inexistente. Añadí bloqueo y expiración como pruebas del componente seguro. Para el número de iteraciones mantuve explícito el parámetro del prototipo; la propuesta no aportaba una referencia que justificara su afirmación sobre un estándar actual.

## Decisiones que tomé

- Acepté PBKDF2 con sal, HMAC, SQLite parametrizado y la separación entre presentación y autenticación.
- Ajusté el contrato del token, las reglas del reloj, el registro de intentos, el desbloqueo y el modelo de entrada HTTP.
- Rechacé el secreto de respaldo y el uso de tiempos idénticos como criterio de prueba. Traté compare_digest como un control de seguridad.
- Reutilicé el motor del equipo y lo invoqué desde HTTP únicamente con codigo. Retiré la ruta que permitía enviar archivos.

## Utilidad del prompt

El prompt me ayudó a establecer el rol, los seis requisitos y el contrato HTTP. Incluí el login oficial, expliqué la lectura de archivos en CLI y pedí separar la inicialización de las solicitudes al comparar las versiones.

Con esa información pude evaluar la respuesta con criterios concretos. Identifiqué los puntos que coincidían con el manual y los que necesitaba corregir antes de incorporarlos al diseño.

## Evidencias

Relacioné el resultado con la ejecución de bitacora/a3/revision_20261126T025924Z/. Allí guardé las pruebas, las firmas de las fuentes y las respuestas de las dos entradas enviadas a Gemini. Utilicé esos registros para elaborar las tablas del informe.
