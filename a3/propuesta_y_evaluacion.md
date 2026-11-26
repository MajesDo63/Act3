# Diseño propuesto y evaluación crítica

Propuse conservar el servicio del kit y completar su autenticación con bibliotecas estándar. El usuario se registra en SQLite con un hash PBKDF2 y una sal aleatoria. Al iniciar sesión recibe un token payload.firma con sub, iat y exp; HMAC-SHA256 permite comprobar que no se modificó. El endpoint propio recibe únicamente código y utiliza el motor del Avance 1 del equipo.

La propuesta fue útil como arquitectura, pero incompleta como implementación. Estas decisiones exigieron revisión antes de integrar el código:

| Riesgo o ambigüedad del diseño inicial | Regla | Decisión aplicada y evidencia |
| --- | --- | --- |
| Confiar en TOKEN_VIGENCIA_S sin acotarlo permitiría una duración superior al máximo de la actividad. | SEC-06; ing-07 | Se rechazan valores fuera de 1–900 segundos. Las pruebas cubren expiración exacta y token emitido en el futuro. |
| La expresión ahora or time.time() del esqueleto pierde el valor cero, lo que dificulta probar límites del reloj. | SEC-04; SEC-10 | Se distingue None de cero en _hora. test_token_limites_de_expiracion_y_ahora_cero comprueba el límite. |
| Contar fallos y después propagar una excepción dentro de una transacción podría revertir el registro del intento. | SEC-05; SEC-06 | El resultado se registra y confirma antes de lanzar ErrorAuth. Se prueba que el bloqueo persista al reabrir la base. |
| El mensaje uniforme por sí solo no evita una diferencia evidente si un usuario inexistente omite la derivación de contraseña. | SEC-06 | Se verifica un hash ficticio creado al iniciar el servicio. No se afirma inmunidad total frente a canales temporales. |
| Reutilizar la entrada genérica de la variante permitiría campos archivo y lectura de rutas del servidor. | SEC-04; SEC-08 | CodigoRevisor solo acepta codigo y prohíbe campos extra. Las pruebas rechazan archivo y entradas vacías. |
| Reenviar str(error) de un proveedor puede publicar información interna. | SEC-05; ing-02; ing-07 | Se devuelve un 503 genérico y se registra solo la clase del error. Se prueba con un marcador confidencial sintético. |

## Aceptado, modificado y descartado

- **Acepté** PBKDF2 con sal, firma HMAC, secreto externo, SQLite parametrizado y errores estructurados, por corresponder al contrato del kit y las reglas SEC.
- **Modifiqué** la gestión del reloj, el límite de vigencia, las transacciones del bloqueo y el modelo de entrada específico. La decisión se verifica con pruebas reproducibles.
- **Descarté** el login oficial como autenticación del servicio, el motor demo como sustituto del endpoint real y el uso de mensajes de excepción completos en respuestas públicas.
- **Descarté** reutilizar tokens o contraseñas en caché para acelerar la versión eficiente. Solo se reutilizan conexión, índices y hash ficticio.

## Riesgos que permanecen

El servicio es un prototipo local de clase: su token firmado propio no implementa OAuth 2.0 completo. El límite por usuario del kit vive en memoria y no se comparte entre procesos. El bloqueo por cuenta puede utilizarse para causar denegación de acceso temporal. SQLite y un bloqueo por instancia simplifican este ejercicio, pero no sustituyen el diseño de autenticación de un despliegue distribuido. El cliente local usa HTTP según la ruta Windows del manual; un despliegue externo requiere HTTPS y gestión de secretos adecuada.

Las decisiones anteriores corresponden a la revisión asistida del diseño y el código de esta sesión. Los resultados de pruebas y las consultas de Gemini se conservan en archivos distintos, sin atribuir al modelo ejecuciones que no ocurrieron.
