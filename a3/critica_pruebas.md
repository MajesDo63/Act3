# Evaluación de las pruebas

Tomé como punto de partida los tres casos del login oficial: acceso concedido, contraseña incorrecta y usuario inexistente. Los utilicé para comparar el comportamiento del ejemplo y de las versiones que desarrollé.

En las versiones seguras cambié el resultado esperado de los dos errores: exigí el mismo mensaje y comprobé que no se devolviera un token. Añadí pruebas para los requisitos que el ejemplo inicial no contempla:

- Sal aleatoria y registro de intentos sin contraseñas ni tokens.
- Token alterado, expiración exacta, reloj cero, emisión futura y formato inválido.
- Bloqueo tras cinco fallos, caducidad, reinicio de la racha y persistencia al reabrir SQLite.
- Intentos concurrentes e inyección SQL.
- Endpoint protegido, campos extra, límites de uso y errores sin detalles internos.
- Sustitución del proveedor en la versión mantenible.
- Consumo de un intento a la vez y cierre de recursos en la versión eficiente.

## Criterios que utilicé

Al revisar la propuesta de Gemini encontré dos sugerencias que ajusté. Conservé los tres casos oficiales y añadí bloqueo y expiración como casos propios. También usé estados, mensajes y efectos observables como criterios de comparación, en lugar de exigir tiempos idénticos entre ejecuciones.

Para probar el contrato de la API sustituí el motor por un doble en casos controlados. Después envié dos entradas al motor con Gemini y guardé sus respuestas en http_gemini.json. Usé fake/hash en la suite para mantener las pruebas reproducibles.

## Acceso a archivos

Probé cinco rutas relativas, absolutas e inexistentes con un token válido. Verifiqué que /v1/variante devolviera 404 y que esas peticiones no invocaran el motor.

También creé un archivo sintético y preparé una prueba que falla si se intenta leerlo. En /v1/revisor comprobé el rechazo de archivo y de los campos adicionales con 422. Revisé OpenAPI para confirmar que la ruta genérica y EntradaVariante ya no estuvieran publicados.

## Resultados

Obtuve 57 pruebas propias de A3 y 163 en la regresión completa, todas aprobadas y sin omitidas. Guardé los XML, las salidas y las capturas de Swagger en bitacora/a3/revision_20261126T025924Z/. Las capturas incluyen los dos errores de credenciales con el mismo mensaje.
