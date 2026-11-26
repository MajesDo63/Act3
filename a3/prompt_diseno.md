# Prompt de diseño

Para organizar la actividad partí de este encargo:

Diseña la autenticación REST del revisor de código de FinNorte en Python, manteniendo las firmas del kit v2. Incluye registro, login, tokens y un endpoint POST /v1/revisor conectado a variante.sistema(). Aplica PBKDF2-HMAC-SHA256 con sal, compare_digest, expiración máxima de 15 minutos, mensaje uniforme para credenciales incorrectas y bloqueo temporal tras cinco fallos. El secreto se obtiene de TOKEN_SECRET y no debe aparecer en respuestas, código versionado ni bitácoras. Los errores HTTP usan application/problem+json con trace_id. Propón pruebas de casos correctos, límites y abuso, y explica qué riesgos quedan.

Además, analiza el login oficial de la diapositiva 4 y desarrolla tres variantes separadas enfocadas en seguridad, eficiencia y mantenibilidad. Conserva el código oficial para poder comparar su comportamiento, sin utilizarlo en el servicio.

## Contexto que utilicé

- Kit v2 de lsca2318-lab-a3-a4-main.zip, SHA-256: 935b1c8bc183546e55af5725d8f4c67f39ea2393460e903563cb7e41fa30a9ac.
- Manual del alumno, sección 4, y presentación de Actividades A3/A4.
- Motor v2-revisor del equipo en Project_v2_TSTI, commit 81a1dd0bec2a6350d750f9440fbdcbaa2af05b63.
- Reglas SEC-01, SEC-04, SEC-05, SEC-06, SEC-08, SEC-10, ing-02 e ing-07.

## Consulta que evalué

Consulté Gemini 3.1 Flash-Lite y guardé el prompt exacto y la respuesta en bitacora/a3/propuesta_20261126T024927Z/. En esa carpeta incluí prompt.txt, solicitud.json, respuesta_api.json, respuesta_asistente.txt y las capturas.

En a3/propuesta_y_evaluacion.md relacioné los pasajes de la respuesta con las decisiones que tomé. El contexto y los requisitos del prompt me permitieron identificar las diferencias entre lo solicitado y lo propuesto.
