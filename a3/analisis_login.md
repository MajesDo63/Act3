# Análisis del login oficial

Fuente: Presentacion_Actividades_A3_A4.pptx, diapositiva 4. Código conservado en login_original.py.

| Problema | Explicación técnica | Impacto | Mejora y evidencia |
| --- | --- | --- | --- |
| Identidad y contraseña fijas en el código | Las cadenas admin y 1234 sustituyen un almacén de usuarios. Son el ejemplo inseguro del enunciado, no cuentas del servicio. | Quien accede al código conoce la contraseña del ejemplo. No existe administración de cuentas. | SEC-01 y SEC-06: usuarios y hashes con sal en SQLite; test_no_contrasena_ni_token_en_registros. |
| Contraseña sin hash ni sal | La comprobación usa una cadena literal. | No existe protección del material de autenticación almacenado. | PBKDF2-HMAC-SHA256 y sal aleatoria: test_hash_sal_aleatoria_y_comprobacion_constante. |
| Comparación mediante == | No usa una operación de comparación de secretos en tiempo constante. | El diseño no contempla canales temporales. | hmac.compare_digest para hashes y firmas; api/auth.py. |
| Mensajes diferentes | wrong password y user not found distinguen cuentas existentes. | Permite enumerar usuarios mediante el resultado. | 401 uniforme y hash ficticio: test_credenciales_incorrectas_mensaje_uniforme. |
| Espacio final y cadenas sueltas | user not found incluye un espacio final y las salidas carecen de un contrato estructurado. | Comparaciones frágiles e integración más difícil. | ResultadoLogin tipado y problem+json en la API. |
| Sin bloqueo ni bitácora | Los intentos pueden repetirse sin control ni registro. | Facilita ataques de adivinación y dificulta investigar. | Cinco fallos, registro sin contraseña, persistencia y prueba concurrente. |
| Sin token ni expiración | El retorno de texto no define una sesión verificable. | No puede proteger de manera consistente los demás endpoints. | Token firmado de máximo 900 s: pruebas de expiración, firma y formato. |

## Tres versiones y trazabilidad

| Versión | Qué cambia | Por qué | Evidencia |
| --- | --- | --- | --- |
| login_seguridad.py | Usa el componente criptográfico y el almacén persistente. Abre y cierra la conexión en cada solicitud. | Primera sustitución segura del ejemplo; hace explícito el ciclo de vida de recursos. | Tres escenarios parametrizados en test_a3_versiones.py y pruebas de auth. |
| login_eficiencia.py | Reutiliza el Autenticador, la conexión y el hash ficticio. Conserva la derivación de contraseña en cada login. | Evita repetir trabajo de inicialización; no debilita la verificación. | Comparación de diez logins y conteo de llamadas PBKDF2 en comparacion_versiones.json. |
| login_mantenible.py | Introduce Protocol, ResultadoLogin y un servicio con dependencia inyectada. | Permite probar presentación y orquestación sin una base real y evita acoplarlas al HTTP. | test_mantenible_admite_proveedor_inyectado_sin_base_real y los mismos tres escenarios. |

Las tres versiones comparten las primitivas revisadas de api/auth.py. No son tres criptografías distintas. El servicio HTTP utiliza el componente integrado; los archivos a3/ explican y comparan las decisiones de refactorización.

## Cinco criterios de comparación

| Criterio | Original | Seguridad | Eficiencia | Mantenibilidad |
| --- | --- | --- | --- | --- |
| Seguridad | Credenciales fijas, sin hash, bloqueo ni sesión. | PBKDF2, sal, token y bloqueo. | Conserva las mismas garantías. | Conserva las garantías del proveedor inyectado. |
| Eficiencia | Muy rápido porque no realiza controles suficientes. | Inicializa conexión y hash ficticio por llamada. | Amortiza la inicialización; verifica siempre el hash. | Reutiliza el proveedor y añade una capa de presentación. |
| Legibilidad | Corto, pero usa mensajes inconsistentes. | Flujo explícito y errores uniformes. | Explicita el ciclo de vida del servicio reutilizado. | Contratos y resultados con tipos descriptivos. |
| Mantenibilidad | Credenciales y lógica mezcladas. | Separa autenticación del ejemplo original. | Requiere gestionar el cierre de la instancia reutilizada. | Permite sustituir proveedor y probarlo de forma aislada. |
| Manejo de errores y pruebas | Tres retornos de texto, incluido un espacio final. | Estados y mensajes uniformes. | Mantiene el contrato de la versión segura. | ResultadoLogin centraliza la salida; prueba de inyección. |

Los tiempos de comparación son mediciones locales, no una prueba de carga de la API ni una afirmación de rendimiento en producción. El menor tiempo del original no lo convierte en una solución aceptable.
