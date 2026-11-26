# Prompt de diseño de la A3

Diseña la autenticación REST del revisor de código de FinNorte en Python, manteniendo las firmas del kit v2. Incluye registro, login, tokens y un endpoint POST /v1/revisor conectado a variante.sistema(). Aplica PBKDF2-HMAC-SHA256 con sal, compare_digest, expiración máxima de 15 minutos, mensaje uniforme para credenciales incorrectas y bloqueo temporal tras cinco fallos. El secreto se obtiene de TOKEN_SECRET y no debe aparecer en respuestas, código versionado ni bitácoras. Los errores HTTP usan application/problem+json con trace_id. Propón pruebas de casos correctos, límites y abuso, y explica qué riesgos quedan.

Además, analiza el login oficial de la diapositiva 4 y desarrolla tres variantes separadas enfocadas en seguridad, eficiencia y mantenibilidad. Conserva el código oficial para poder comparar su comportamiento, sin utilizarlo en el servicio.

## Contexto entregado

- Kit v2 de lsca2318-lab-a3-a4-main.zip, SHA-256: 935b1c8bc183546e55af5725d8f4c67f39ea2393460e903563cb7e41fa30a9ac.
- Manual del alumno, sección 4; presentación Actividades A3/A4, diapositivas 3–7.
- Motor v2-revisor del equipo en Project_v2_TSTI, commit 81a1dd0bec2a6350d750f9440fbdcbaa2af05b63.
- SEC-01, SEC-04, SEC-05, SEC-06, SEC-08, SEC-10, ing-02 e ing-07.

Este archivo registra el encargo de diseño usado en la elaboración asistida de esta entrega. No representa una llamada adicional a Gemini; las llamadas de Gemini para las entradas del endpoint se registran aparte.

## Consulta nueva de revisión

El texto anterior conserva el encargo inicial, no una respuesta literal del asistente. La consulta real nueva y su respuesta están en bitacora/a3/propuesta_20261126T024927Z/: prompt.txt, solicitud.json, respuesta_api.json y respuesta_asistente.txt. Su evaluación cita líneas verificables y explica la utilidad del contexto y los oráculos. Esta consulta posterior no se presenta como la conversación original.
