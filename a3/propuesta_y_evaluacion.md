# Propuesta real del asistente y evaluación crítica

La respuesta completa de Gemini 3.1 Flash-Lite está en `bitacora/a3/propuesta_20261126T024927Z/respuesta_asistente.txt`. Se conserva el JSON original del proveedor, la solicitud sin credenciales, el prompt, metadatos HTTP 200 y una captura del texto recibido. Es una **consulta nueva de revisión**, posterior a la primera entrega; no la presento como la conversación original, cuya respuesta literal no quedó conservada.

La respuesta nueva se recibió antes de cerrar la corrección. No ejecuté ni copié su bloque de autenticación. Contrasté sus afirmaciones con el manual y con el componente existente. Las líneas siguientes corresponden al texto íntegro, sin editar.

| Pasaje real del modelo | Falla o ambigüedad | Regla y decisión |
| --- | --- | --- |
| L10: `os.environ.get("TOKEN_SECRET", "secreto-muy-seguro")` | El respaldo conocido permite firmar tokens si falta configuración; contradice exigir secreto externo. | SEC-01, SEC-06, ing-02: rechacé el respaldo; `_secreto()` falla si falta o mide menos de 32 caracteres. Prueba del secreto ausente. |
| L29–36: solo firma y `exp`, sin `iat`. | No comprueba duración máxima entre emisión y expiración ni emisión futura. | SEC-06, ing-07: conservé sub/iat/exp y límites estrictos; pruebas de reloj cero, expiración exacta y fechas futuras. |
| L39: rechazar si `intentos_fallidos >= 5`. | Menciona `bloqueado_hasta` pero no define expiración ni transacción; puede bloquear indefinidamente o perder intentos. | SEC-05, SEC-06: ventana 900 s, reinicio tras éxito y commit antes de ErrorAuth; pruebas de persistencia y caducidad. |
| L57: llama «eficiencia» a cambiar a `compare_digest`. | Es seguridad, no prueba de una mejora de rendimiento. | SEC-06, SEC-10: rechacé la clasificación. V2 reutiliza recursos y procesa lotes perezosos; benchmark del ciclo completo. |
| L72: el tiempo «debe ser idéntico». | La igualdad exacta depende de ruido del sistema y no es un oráculo reproducible. | SEC-06: rechazo la igualdad literal. Mensaje uniforme y verificación también para cuentas desconocidas, sin afirmar inmunidad temporal. |
| L84–87: `payload: dict` y token por `Header`. | Omite modelo propio, campos extra prohibidos, límite y problem+json. No retira explícitamente otra ruta genérica. | SEC-04, SEC-08, ing-07: CodigoRevisor y HTTPBearer; retiro de `/v1/variante`, su modelo y fallback demo. Pruebas de 404 y archivo sintético nunca abierto. |

Corregí las «pruebas oficiales» enumeradas por el modelo: el login oficial tiene éxito, contraseña incorrecta y usuario inexistente. Bloqueo y expiración son pruebas adicionales, no sustituyen las tres oficiales. No acepté como autoridad la afirmación de que 100 000 iteraciones sea «el estándar actual»: no aporta fuente ni medición. El parámetro del prototipo no se presenta como configuración universal de producción.

## Decisiones

- Acepté PBKDF2 con sal, HMAC, SQLite parametrizado, separación de presentación y autenticación y registro de eventos sin contraseñas ni tokens.
- Modifiqué el contrato del token, las reglas del reloj, la transacción de intentos, el desbloqueo y el modelo HTTP.
- Rechacé el secreto de respaldo, `except` sin tipo como contrato de errores, tiempos idénticos como oráculo y atribuir eficiencia a `compare_digest`.
- Conservé el motor compartido, como requiere la A3: se invoca únicamente con `{"codigo": ...}` desde HTTP. La capacidad de lectura de archivos sigue disponible internamente/CLI; la ruta genérica que la exponía se elimina.

## Utilidad del prompt

El prompt identifica rol y contexto, enumera seis requisitos comprobables, describe el contrato HTTP y aporta el login oficial. Explica la lectura de archivos en CLI, pide revisar la ruta genérica y exige separar inicialización de llamadas. Así permite contrastar respuestas concretas con reglas y pruebas. Aun con ese contexto, el modelo incumplió requisitos explícitos: el prompt no sustituye la revisión.

## Versiones y evidencias

La corrida de 159 pruebas y la entrega depurada de 155 se mantienen como antecedentes. La corrección modifica la superficie HTTP, V2 y sus pruebas; tiene una nueva corrida, firma de fuentes y dos solicitudes nuevas a Gemini. No afirmo que el código corregido tenga los mismos bytes que la versión anterior.
