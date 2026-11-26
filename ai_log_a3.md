# Registro de uso de IA · Actividad 3

**Cesar Eduardo Valdez Pinto · MajesDo63**

## Herramientas que utilicé

Utilicé ChatGPT como apoyo para preparar el código, organizar las pruebas y redactar el informe. Ejecuté los scripts en PowerShell y guardé los resultados. También contrasté el trabajo con una revisión en Claude y una propuesta de diseño en Gemini.

Partí del motor del Avance 1 del equipo. En esta actividad trabajé en la autenticación, el endpoint específico y las tres versiones del login.

## Decisiones sobre la propuesta

Guardé la consulta de Gemini en `bitacora/a3/propuesta_20261126T024927Z/`, junto con el prompt, la respuesta y sus capturas. Evalué los siguientes puntos:

| Propuesta | Decisión y motivo |
| --- | --- |
| PBKDF2 con sal, HMAC y SQLite parametrizado | Acepté estas bases para la autenticación. |
| Secreto de respaldo escrito en el código, L10 | Lo rechacé y exigí configurar TOKEN_SECRET. |
| Token sin iat, L29–36 | Conservé sub, iat y exp para verificar emisión, duración y expiración. |
| Contador sin caducidad ni commit explícito, L39 | Definí ventana de 900 segundos, reinicio tras éxito y persistencia de los intentos. |
| compare_digest como mejora de eficiencia, L57 | Lo traté como un control de seguridad. Medí la eficiencia con los mismos límites del ciclo de vida. |
| Tiempos idénticos como resultado esperado, L72 | Usé mensajes, estados y efectos observables como criterios de prueba. |
| Entrada genérica, L84–87 | Utilicé un modelo estricto y retiré la ruta que aceptaba archivos. |

El prompt me sirvió para establecer el contexto, los seis requisitos, el contrato HTTP y las pruebas esperadas. Al comparar la respuesta con esos requisitos encontré decisiones que necesitaban ajustes. Desarrollé la evaluación en `a3/propuesta_y_evaluacion.md`.

## Comprobación del resultado

Retiré `/v1/variante` y actualicé el cliente para utilizar `/v1/revisor`. Añadí pruebas con rutas relativas, absolutas e inexistentes, además de un archivo sintético. Verifiqué que esas peticiones no llegaran al motor.

En V2 reutilicé recursos y procesé los intentos uno a uno. Para comparar las versiones incluí el arranque, las solicitudes y el cierre, con una y diez solicitudes por ciclo.

Obtuve 163 pruebas aprobadas, de las cuales 57 corresponden a la A3. Guardé las capturas de Swagger y las dos entradas enviadas a Gemini en `bitacora/a3/revision_20261126T025924Z/`. Conservé también el 503 temporal y el reintento que permitió completar limites.py.

Relacioné el resultado con las fuentes ejecutadas mediante sus firmas y guardé los comandos y el entorno de ejecución en la bitácora. Las llaves y los tokens de sesión quedaron fuera de los archivos de entrega.
