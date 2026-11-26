# Registro de IA · Actividad 3, revisión corregida

**Cesar Eduardo Valdez Pinto · MajesDo63 · MajesDo63/Act3.**

## Intervenciones y fuentes

ChatGPT ayudó a preparar la implementación, las pruebas y el informe. El estudiante ejecutó los scripts en PowerShell normal. El motor procede del Avance 1 del equipo; no se atribuye a la A3 todo su desarrollo.

Una revisión externa en Claude identificó que /v1/variante seguía exponiendo la entrada archivo del motor. Acepté el hallazgo: validar solo /v1/revisor era insuficiente. Se retiraron ruta, modelo y fallback y se actualizó el cliente. Se añadieron regresiones con token válido y un archivo sintético que nunca debe abrirse.

## Propuesta nueva verificable

La consulta Gemini de `propuesta_20261126T024927Z` conserva el prompt real, la solicitud sin credenciales, la respuesta original, HTTP 200 y una captura del texto recibido. Es posterior a la primera entrega; no reemplaza ni reconstruye la conversación original. No se ejecutó ni copió el código de la propuesta.

| Elemento de la respuesta | Decisión y fundamento |
| --- | --- |
| PBKDF2, sal, HMAC y separación de responsabilidades | Aceptados; se conservan los controles implementados y probados. |
| Secreto de respaldo literal, L10 | Rechazado: vulnera el requisito de secreto externo; la falta de configuración debe fallar. |
| Token sin iat, L29–36 | Modificado: se conserva sub/iat/exp y validación de duración y emisión futura. |
| Contador sin expiración/commit explícito, L39 | Modificado: ventana de 900 s, reinicio y persistencia confirmada. |
| compare_digest como eficiencia, L57 | Rechazado: es seguridad, no una medición de velocidad. |
| Tiempos idénticos como oráculo, L72 | Rechazado: no es reproducible; se comprueban mensajes y efectos observables. |
| payload: dict y ausencia de cierre de ruta genérica, L84–87 | Modificado: entrada estricta y ruta alternativa eliminada. |

El prompt resultó útil por delimitar rol, requisitos, motor compartido, riesgos y pruebas; aun así el modelo incumplió condiciones explícitas. La evaluación completa cita líneas del archivo íntegro en a3/propuesta_y_evaluacion.md.

## Eficiencia y pruebas

V2 incorpora lote perezoso y cierre mediante contexto. La comparación actual incluye inicialización, N logins y cierre para todas las versiones, N=1/10 y cinco repeticiones. No atribuye a la ausencia de controles de V0 una ventaja aceptable. No se cachean contraseñas ni tokens para evitar verificaciones.

La suite actual tiene 163 pruebas, 57 propias de A3, sin omitidas. Las 159 y 155 anteriores se conservan como historia. La revisión actual tiene firma de fuentes y dos llamadas nuevas a Gemini: no se afirma que el código cambiado sea idéntico al de las llamadas anteriores. Los parches generados por el revisor no se ejecutan ni se incorporan automáticamente.

Las nuevas capturas se toman directamente de la tabla Server response de Swagger UI. Incluyen ambos errores de credenciales, cuyo detail debe ser igual. Las capturas de la propuesta muestran el texto real de Gemini en el navegador, no una interfaz ficticia de chat. Los paneles antiguos no se presentan como capturas directas. Las credenciales de configuración y los tokens de sesión quedan fuera del paquete.
