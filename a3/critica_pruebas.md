# Evaluación de las pruebas propuestas

Las tres pruebas del login oficial comprueban sus salidas reales: acceso concedido, contraseña incorrecta y usuario inexistente. Son una referencia de comportamiento, pero no prueban seguridad: pueden aprobar incluso cuando las credenciales están escritas en el código. Por eso mantuve ese ejemplo separado del servicio.

Acepté probar esas tres situaciones también en cada versión mejorada. Cambié el contrato esperado: en las versiones seguras, usuario inexistente y contraseña incorrecta producen el mismo mensaje y no devuelven token.

Las pruebas adicionales cubren propiedades que las tres iniciales omiten:

- Sal aleatoria y ausencia de contraseñas o tokens en la bitácora.
- Token alterado, expiración exacta, tiempo cero, emisión futura y codificación no canónica.
- Bloqueo después de cinco fallos, caducidad de la ventana, reinicio de la racha y persistencia al reabrir SQLite.
- Intentos concurrentes e inyección SQL.
- Endpoint protegido, rechazo de campos extra y rutas de archivo, límite de solicitudes y errores sin detalles internos.
- Dependencia inyectable en la versión mantenible.

Las pruebas del endpoint que sustituyen variante.sistema por un doble verifican el contrato de conexión y los errores, no la calidad del modelo. Las dos entradas enviadas al servicio con el motor real se registran por separado en http_gemini.json. Las pruebas automatizadas de la suite utilizan fake/hash para ser reproducibles y no consumir cuota.

No se sustituye una prueba fallida por un skipped. Los resultados finales se toman de los XML y registros completos de la ejecución correspondiente.

## Correcciones tras revisar una respuesta real

La nueva respuesta Gemini confundió las tres pruebas oficiales con bloqueo y expiración, y propuso tiempos idénticos como oráculo. Rechacé esos cambios: las oficiales siguen siendo acceso, contraseña incorrecta y usuario inexistente; bloqueo y expiración se añaden como pruebas propias. El estado y el mensaje son oráculos reproducibles; la igualdad literal de tiempos no lo es.

La primera suite solo probaba el rechazo de archivos en /v1/revisor. Era insuficiente porque /v1/variante seguía expuesto. Retiré esa ruta y añadí cinco casos de rutas con token válido más una prueba con archivo sintético real que falla si alguien intenta leerlo o invocar el motor. La nueva verificación obtiene 404 en la ruta retirada y 422 al enviar archivo al endpoint propio. OpenAPI ya no publica la ruta ni EntradaVariante. Las nuevas capturas corresponden directamente a Server response de Swagger UI, incluyendo ambos 401 con el mismo mensaje.
