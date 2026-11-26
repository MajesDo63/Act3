# Reflexión

Al desarrollar esta actividad entendí que proteger un endpoint también implica revisar las otras rutas del servicio. Un modelo de entrada estricto resulta útil, pero pierde parte de su efecto si todavía existe otro acceso que acepta datos más amplios. Por eso revisé las rutas del kit, retiré la entrada genérica y añadí pruebas para comprobar que los archivos del servidor no llegaran al motor.

La propuesta de Gemini me sirvió para contrastar el diseño. Al leerla encontré un secreto de respaldo escrito en el código, una explicación incompleta del desbloqueo y una confusión entre seguridad y eficiencia. Tener el texto completo me permitió señalar cada punto y justificar mis decisiones con las reglas del manual. Acepté las bases que correspondían al ejercicio y ajusté lo que no cumplía el contrato del servicio.

La comparación de las versiones fue otro aprendizaje. El login original es corto y rápido porque resuelve una sola cuenta y omite controles necesarios. Para comparar las versiones seguras medí el arranque, las solicitudes y el cierre dentro del mismo ciclo. Con una solicitud observé el costo inicial; con diez pude ver el efecto de reutilizar la conexión y el autenticador. También comprobé que el procesamiento por lotes siguiera verificando cada intento.

Las pruebas me ayudaron a separar el comportamiento esperado de las suposiciones. Comprobar estados HTTP, mensajes, expiración y efectos sobre los archivos me dio criterios claros para aceptar el resultado. Guardar los comandos, las capturas y las firmas de las fuentes también me facilitó relacionar cada cifra del informe con su ejecución.

Me quedo con una forma de trabajo más ordenada: partir de requisitos concretos, revisar las propuestas, comparar con los mismos criterios y conservar evidencias de lo que ejecuté. Esa combinación me permitió entender mejor las decisiones del login y explicar por qué elegí cada mejora.
