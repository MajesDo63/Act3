# Actividad 3 · Cesar Eduardo Valdez Pinto

En esta actividad desarrollé el servicio de autenticación de FinNorte y lo conecté al revisor de código del equipo. Analicé el login del enunciado, preparé tres versiones y comparé sus resultados.

**Repositorio:** https://github.com/MajesDo63/Act3  
**Etiqueta de entrega:** `a3-MajesDo63`

## Organización de mi trabajo

| Apartado | Archivo |
| --- | --- |
| Informe y documento editable | `entrega/Actividad3_Cesar_Informe.pdf` y `.docx` |
| Autenticación | `api/auth.py` |
| Endpoint del revisor | `api/producto.py`: `POST /v1/revisor` |
| Tres versiones del login | `a3/login_seguridad.py`, `login_eficiencia.py`, `login_mantenible.py` |
| Análisis del ejemplo | `a3/analisis_login.md` |
| Prompt y evaluación | `a3/prompt_diseno.md`, `a3/propuesta_y_evaluacion.md` |
| Evaluación de pruebas y reflexión | `a3/critica_pruebas.md`, `a3/reflexion.md` |
| Registro de herramientas de IA | `ai_log.md` |
| Ejecución y evidencias | `bitacora/a3/revision_20261126T025924Z/` |

## Decisiones de implementación

Definí `/v1/revisor` con una entrada propia que acepta únicamente `codigo`. Incorporé autenticación Bearer, validación, un límite por usuario y errores `problem+json`. Retiré `/v1/variante` para impedir que una entrada genérica permitiera leer archivos del servidor. También adapté el cliente para utilizar el endpoint específico.

Comprobé las rutas con un token válido y con un archivo de prueba. La ruta retirada devuelve 404; enviar `archivo` a `/v1/revisor` devuelve 422. Conservé la lectura de archivos del motor para su uso desde CLI.

Para autenticar usé PBKDF2 con sal aleatoria, comparación con `compare_digest`, tokens HMAC de hasta 900 segundos y bloqueo tras cinco fallos consecutivos. Guardé los intentos en SQLite sin contraseñas ni tokens.

## Resultados

| Grupo | Aprobadas | Omitidas |
| --- | --- | --- |
| Checkpoint de autenticación | 4 | 0 |
| Laboratorio | 12 | 0 |
| Actividad 3 | **57** | 0 |
| Regresión completa | **163** | 0 |

Organicé las pruebas en grupos que se solapan: la regresión completa incluye los anteriores. Las 57 pruebas de A3 corresponden a 23 de autenticación, 19 de API y 15 de las versiones del login.

Envié `usuarios.py` y `limites.py` al endpoint con Gemini 3.1 Flash-Lite. Obtuve HTTP 200 en ambos casos. Conservé los resultados, tiempos, intentos y respuestas en `http_gemini.json`. Al recibir un 503 temporal para `limites.py`, reanudé esa entrada y conservé el resultado de `usuarios.py`.

Guardé los resultados de pytest en XML y texto, junto con la firma de las fuentes ejecutadas. Las capturas `swagger_*.png` muestran las respuestas de la API en Swagger: 401, 422, 429 y el mismo mensaje para los dos errores de credenciales.

## Evaluación de propuestas y eficiencia

Consulté Gemini para contrastar el diseño y guardé el prompt y la respuesta en `bitacora/a3/propuesta_20261126T024927Z/`. En `a3/propuesta_y_evaluacion.md` relacioné los pasajes que acepté, modifiqué o rechacé con las reglas del manual y sus pruebas.

Para comparar las versiones medí cinco ciclos con una y diez solicitudes. Incluí inicialización, autenticación y cierre en todas las versiones. Guardé cada muestra en `comparacion_ciclo_completo.json`.

En V2 reutilicé el autenticador y añadí un lote perezoso: cada intento produce un resultado sin construir una lista completa. Mantuve la verificación de cada contraseña y el cierre de la conexión ante errores. Comparé V2 con V1 porque ambas aplican los mismos controles de seguridad.

## Reproducir mi ejecución

Usé Windows 11 y Python 3.14.7. Para instalar el proyecto se necesita Python 3.11 o posterior. Desde la raíz:

```powershell
python -m venv .venv
& '.\.venv\Scripts\python.exe' -m pip install -r requirements.txt
& '.\.venv\Scripts\python.exe' -m pip install -e .
Copy-Item '.env.example' '.env'
& '.\.venv\Scripts\python.exe' -c "import secrets; print(secrets.token_hex(32))"
```

Coloca el valor generado en `TOKEN_SECRET`, dentro de `.env`. Para las pruebas locales configura `LLM_PROVIDER=fake` y `EMB_PROVIDER=hash`. Para Gemini agrega tu `GEMINI_API_KEY`, `LLM_PROVIDER=gemini`, `LLM_MODEL=gemini-3.1-flash-lite`, `EMB_PROVIDER=gemini` y `EMB_MODEL=gemini-embedding-001`.

```powershell
& '.\.venv\Scripts\python.exe' -m pytest tests -q
& '.\.venv\Scripts\python.exe' -m uvicorn api.producto:app --host 127.0.0.1 --port 8000
```

En `http://127.0.0.1:8000/docs` puedes registrar una cuenta de prueba, iniciar sesión y autorizar las peticiones a `/v1/revisor`. `guia/validar_correccion_a3.py` reúne las pruebas, mediciones y evidencias en una carpeta nueva. La opción `--continuar` retoma una ejecución si sus fuentes siguen intactas.

## Procedencia y alcance

Partí del motor compartido del Avance 1. En `PROCEDENCIA_BASE.md` identifiqué el repositorio, el commit y el trabajo del equipo. Conservé sus dependencias y licencias; utilicé el manual y las presentaciones del profesor como referencia.

Desarrollé un prototipo local con token HMAC y límite por usuario dentro de un proceso. Analicé las respuestas y los parches del revisor como propuestas de cambio. El alcance de mis pruebas es el descrito en el informe y sus evidencias.
