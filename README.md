# Actividad 3 · Cesar Eduardo Valdez Pinto

Entrega individual de LSCA2318: servicio del revisor de código con autenticación, revisión del login oficial y tres versiones comparadas.

Destino: **https://github.com/MajesDo63/Act3**. Etiqueta de entrega: **a3-MajesDo63**.

## Qué revisar

| Elemento | Ruta |
| --- | --- |
| Informe de siete páginas | `entrega/Actividad3_Cesar_Informe.pdf` |
| Informe editable | `entrega/Actividad3_Cesar_Informe.docx` |
| Autenticación completa | `api/auth.py` |
| Endpoint propio protegido | `api/producto.py`: `POST /v1/revisor` |
| Tres versiones | `a3/login_seguridad.py`, `login_eficiencia.py`, `login_mantenible.py` |
| Prompt y crítica | `a3/prompt_diseno.md`, `propuesta_y_evaluacion.md`, `critica_pruebas.md` |
| Análisis y reflexión | `a3/analisis_login.md`, `a3/reflexion.md` |
| Asistencia de IA | `ai_log_a3.md` |
| Evidencias de esta entrega | `bitacora/a3/20261126T020719Z/` |

## Resultados comprobados

- Checkpoint de autenticación: **4 aprobadas, 0 omitidas**.
- Laboratorio: **12 aprobadas, 0 omitidas**.
- A3: **49 aprobadas, 0 omitidas**.
- Regresión completa: **159 aprobadas, 0 omitidas**. Incluye las anteriores; no se suman los grupos.
- HTTP real con proveedor `fake`: registro 201, login 200, rechazo 401, validación 422 y bloqueo 429; dos entradas del revisor 200.
- HTTP real con Gemini 3.1 Flash-Lite: `usuarios.py` 200, tres hallazgos SEC-06; `limites.py` 200, sin hallazgos. Ambas respuestas: `demo=false` y `abstuvo=false`.

Las pruebas de la suite emplean fake/hash; la integración real con Gemini está identificada en `http_gemini.json`. Un HTTP 200 no demuestra exactitud exhaustiva de los hallazgos o de los parches sugeridos. No se aplicaron ni ejecutaron los parches generados.

## Instalar y reproducir

Python 3.11 o posterior. La evidencia entregada se obtuvo con Python 3.14.7 y Windows 11. Desde la raíz del repositorio, en PowerShell:

```powershell
python -m venv .venv
& '.\.venv\Scripts\python.exe' -m pip install -r requirements.txt
& '.\.venv\Scripts\python.exe' -m pip install -e .
Copy-Item '.env.example' '.env'
& '.\.venv\Scripts\python.exe' -c "import secrets; print(secrets.token_hex(32))"
```

En tu `.env` local agrega el valor generado como `TOKEN_SECRET`. Para ejecutar sin proveedor externo, configura `LLM_PROVIDER=fake` y `EMB_PROVIDER=hash`. Para las consultas reales configura `LLM_PROVIDER=gemini`, `LLM_MODEL=gemini-3.1-flash-lite`, `EMB_PROVIDER=gemini`, `EMB_MODEL=gemini-embedding-001` y tu `GEMINI_API_KEY`. El archivo `.env` no se publica.

```powershell
& '.\.venv\Scripts\python.exe' -m pytest tests -q
& '.\.venv\Scripts\python.exe' -m uvicorn api.producto:app --host 127.0.0.1 --port 8000
```

Abre `http://127.0.0.1:8000/docs`, registra una cuenta de prueba, inicia sesión, pega solo el token en **Authorize** y llama a `/v1/revisor` con `{"codigo":"..."}`. El modelo solo recibe el código de prueba; nunca envíes secretos en esa entrada.

Para otra corrida completa con JUnit, HTTP real y capturas:

```powershell
& '.\.venv\Scripts\python.exe' '.\guia\completar_a3.py'
```

`--sin-gemini` permite la comprobación local y marca explícitamente Gemini pendiente. `--reanudar` conserva los grupos aprobados de la corrida indicada por `bitacora/a3/ultima_ejecucion.json`; exige que sus fuentes medidas sigan intactas. Los registros originales contienen las rutas del equipo donde se ejecutaron; el script generará rutas nuevas si se ejecuta desde otra carpeta.

`herramientas_a3/` conserva copias verificadas de dependencias y licencias empleadas en este equipo; `PROCEDENCIA.json` identifica sus repositorios y versiones. La instalación normal y GitHub Actions utilizan `requirements.txt`. Esas copias no sustituyen Python ni todas las dependencias binarias y no se anuncian como instalación portátil universal.

## Alcance, procedencia y límites

La base del equipo procede de `alanrivera066/Project_v2_TSTI`, commit `81a1dd0bec2a6350d750f9440fbdcbaa2af05b63`. `README_BASE_AVANCE1.md`, los registros del Avance 1 y las autorías se conservan como antecedentes. No son nuevas mediciones de A3. El motor compartido mantiene detectar, explicar, parche y dictamen. La autenticación, el endpoint específico, las tres versiones y su documentación corresponden a esta entrega.

El token HMAC del kit es `payload.firma`, no JWT ni OAuth 2.0 completo. La vigencia máxima es 900 s. Tras cinco fallos consecutivos se bloquea temporalmente el login; las rutas protegidas tienen un límite local de 30 solicitudes por minuto y usuario. Este límite vive en memoria. El prototipo local utiliza HTTP; una exposición externa requiere HTTPS y gestión de secretos adecuada. Los componentes de referencia de A4 se conservan, pero no se presenta una A4 individual terminada.

Se siguieron el manual y las presentaciones proporcionadas. El Word oficial de instrucciones no estuvo disponible.

## Publicación

Ver `guia/PUBLICAR_ACT3.md`. El informe y los resultados están preparados localmente. Crear el repositorio, un commit o una etiqueta local no los publica automáticamente: verifica que el contenido y `a3-MajesDo63` se vean en GitHub antes de entregar el enlace.
