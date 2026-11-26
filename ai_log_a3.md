# Registro de asistencia de IA · Actividad 3

**Estudiante:** Cesar Eduardo Valdez Pinto · **GitHub:** MajesDo63 · **Destino:** MajesDo63/Act3.

## Alcance de la asistencia

Utilicé ChatGPT para analizar el kit del profesor, diseñar y preparar la autenticación, el endpoint específico, tres refactorizaciones, pruebas y documentación. El prompt de diseño quedó registrado en `a3/prompt_diseno.md`. Los archivos de crítica documentan el juicio sobre las propuestas, sus límites y las decisiones; no son una transcripción inventada de una llamada al proveedor.

El motor de cuatro etapas pertenece al Avance 1 del equipo. Su copia y autoría están identificadas en `bitacora/a3/base_repositorio.json`; el informe no atribuye su desarrollo completo a esta actividad individual.

## Decisiones

| Propuesta | Decisión | Motivo y evidencia |
| --- | --- | --- |
| PBKDF2, sal aleatoria, HMAC y secreto por variable de entorno | Aceptada | Requisitos del manual; `api/auth.py` y pruebas de hash/token. |
| SQLite parametrizado y registro de intentos | Aceptada con correcciones | Confirmar el intento antes de lanzar la excepción; bloqueo persistente comprobado. |
| Vigencia configurable y manejo del reloj | Modificada | Rango 1–900; distinguir cero de None; probar expiración exacta y emisión futura. |
| Entrada genérica que acepta rutas del servidor | Rechazada para el endpoint propio | Solo `codigo`, con campos extra prohibidos. |
| Texto de errores internos en respuestas públicas | Rechazado | 503 genérico y solo clase del error en traza. |
| Acelerar omitiendo derivaciones o guardando tokens/contraseñas en caché | Rechazada | V2 reutiliza recursos y conserva PBKDF2 en cada login. |
| Tres escenarios funcionales como única evidencia de seguridad | Insuficiente | El ejemplo inseguro también los aprueba; se añaden pruebas de límites, abuso y persistencia. |
| Motor demo en lugar del revisor real | Rechazado | `/v1/revisor` llama al motor del equipo; respuesta Gemini `demo=false`. |

## Ejecución y revisión de resultados

Ejecuté el script preparado en PowerShell normal desde Windows. Los cuatro grupos aprobaron: 4, 12, 49 y 159 pruebas, sin omitidas. Son grupos solapados. Los comandos, entorno y duración quedaron registrados en `bitacora/a3/20261126T020719Z/estado.json` y sus JUnit XML.

La primera ejecución se interrumpió al limpiar un SQLite temporal mantenido abierto por un proceso hijo del lanzador de Windows. Se corrigió el script de ejecución y se reanudó solo la integración Gemini. Los 108 archivos de código, pruebas y documentación medidos conservaron sus SHA-256. El incidente se conserva en `estado_interrupcion_original.json` y `reanudacion.json`; no se borró un fallo de las evidencias.

Gemini 3.1 Flash-Lite respondió a dos entradas reales del endpoint protegido:

- `usuarios.py`: HTTP 200, tres hallazgos SEC-06, fuente `sec-06#0`, sin abstención y sin modo demo. Señaló MD5, uso de `random` y comparación mediante `==`.
- `limites.py`: HTTP 200, `sin hallazgos`, sin abstención y sin modo demo.

Las respuestas y las trazas se conservan completas. El parche de `usuarios.py` propone introducir `bcrypt`; no se incorporó ni ejecutó en esta entrega. Que el proveedor responda correctamente no valida automáticamente sus parches, ni demuestra cobertura completa de defectos. La autenticación implementada usa PBKDF2 de la biblioteca estándar y sus resultados se comprueban por separado.

Las capturas son del panel generado a partir de los registros reales de pytest y HTTP. Se identifican como panel de evidencias, no como capturas de Swagger ni de una conversación externa. La llave de Gemini, el secreto de los tokens y los tokens de sesión están excluidos de los archivos de entrega.
