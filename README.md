# Actividad 3 · Cesar Eduardo Valdez Pinto

Entrega individual de LSCA2318, variante v2-revisor. Repositorio: **https://github.com/MajesDo63/Act3**. Etiqueta: **a3-MajesDo63**.

## Revisión corregida

Se eliminó completamente `POST /v1/variante`, su modelo `EntradaVariante` y el fallback demo. La API del revisor solo admite `POST /v1/revisor` con `{"codigo": "..."}`. Enviar `archivo` al endpoint propio produce 422; la ruta retirada produce 404 incluso con token válido. El cliente de ejemplo utiliza el endpoint propio.

Una prueba crea un archivo sintético y falla si cualquier petición intenta leerlo o enviar su contenido al motor. Otros cinco casos cubren rutas relativas, traversal, absolutas e inexistentes. La lectura de archivos del motor compartido permanece disponible para CLI; no se publica mediante HTTP.

## Entregables y resultados actuales

| Elemento | Ruta / resultado |
| --- | --- |
| Informe PDF y Word editable | `entrega/Actividad3_Cesar_Informe.pdf` y `.docx` |
| Autenticación | `api/auth.py` |
| Servicio específico | `api/producto.py`: `/v1/revisor` |
| Tres versiones | `a3/login_seguridad.py`, `login_eficiencia.py`, `login_mantenible.py` |
| Evaluación de una respuesta literal | `a3/propuesta_y_evaluacion.md` |
| Registro de IA | `ai_log.md` |
| Checkpoint / laboratorio | 4 / 12 aprobadas, sin omitidas |
| Pruebas propias de A3 | **57 aprobadas**: 23 auth + 19 API + 15 versiones |
| Suite completa actual | **163 aprobadas**, sin omitidas |
| Evidencias vigentes | `bitacora/a3/ultima_revision.json` identifica la corrida de esta revisión |

Los grupos se solapan; no se suman. Las cifras 159 y 155 son históricas. Los resultados actuales, firmas, comandos y fechas se conservan en la carpeta `revision_*` señalada por el índice. La corrección tiene nuevas pruebas y dos solicitudes nuevas a Gemini; no se afirma que conserve los bytes de la API anterior.

## Evidencia de IA y capturas

`bitacora/a3/propuesta_20261126T024927Z/` conserva un prompt nuevo, la solicitud sin credenciales, el JSON original de Gemini 3.1 Flash-Lite, el texto íntegro y capturas del texto abierto en el navegador. Esta consulta posterior subsana la falta de una respuesta verificable; no se presenta como la conversación original.

La evaluación cita líneas concretas: secreto de respaldo, token sin iat, ambigüedad del desbloqueo, clasificación errónea de eficiencia y un oráculo de tiempos idénticos. El bloque propuesto no se ejecutó ni se copió al servicio.

Las capturas `swagger_*.png` de la revisión actual proceden directamente de Server response en Swagger UI: 401 sin token, token alterado, ambos errores de credenciales, 422 y 429. Los JSON HTTP y JUnit son los registros completos. Los paneles de la primera corrida se conservan como antecedentes y no se usan como si fueran capturas directas.

## Eficiencia y comparación

V2 reutiliza el autenticador y procesa un iterable de intentos de forma perezosa. El contexto cierra la conexión incluso si falla el productor. Cada intento conserva la verificación criptográfica.

El benchmark usa cinco repeticiones para N=1 y N=10. **Todas las versiones incluyen inicialización + N logins + cierre en el total**. Se guardan muestras, medianas y conteos PBKDF2 en `comparacion_ciclo_completo.json`. V0 ya es O(1) para una cuenta y omite seguridad; no se presenta como una solución aceptable ni se afirma una mejora asintótica frente a él. La amortización se compara con V1 bajo los mismos controles.

## Instalación y reproducción

Python 3.11 o posterior; la evidencia local utiliza Python 3.14.7. Desde la raíz:

```powershell
python -m venv .venv
& '.\.venv\Scripts\python.exe' -m pip install -r requirements.txt
& '.\.venv\Scripts\python.exe' -m pip install -e .
Copy-Item '.env.example' '.env'
& '.\.venv\Scripts\python.exe' -c "import secrets; print(secrets.token_hex(32))"
```

Guarda el valor generado como `TOKEN_SECRET` en `.env`. Para pruebas sin red usa `LLM_PROVIDER=fake` y `EMB_PROVIDER=hash`. Para integración real configura tu `GEMINI_API_KEY`, `LLM_PROVIDER=gemini`, `LLM_MODEL=gemini-3.1-flash-lite`, `EMB_PROVIDER=gemini` y `EMB_MODEL=gemini-embedding-001`. La llave y `.env` no se publican.

```powershell
& '.\.venv\Scripts\python.exe' -m pytest tests -q
& '.\.venv\Scripts\python.exe' -m uvicorn api.producto:app --host 127.0.0.1 --port 8000
```

Abre `http://127.0.0.1:8000/docs`, registra una cuenta de prueba, inicia sesión, usa Authorize y llama a `/v1/revisor`. Los archivos y rutas del servidor no son entradas válidas del endpoint.

El script `guia/validar_correccion_a3.py` genera otra corrida con pruebas, benchmark, HTTP, Swagger y Gemini. No sobrescribe la primera corrida. `--continuar` solo reanuda si las fuentes ejecutables no cambiaron. El script puede usar `.env` local; las rutas absolutas de los registros identifican el equipo donde se produjo la evidencia original. Las copias de dependencias en `herramientas_a3/` conservan versión, procedencia y licencias; la instalación normal usa requirements.txt.

## Alcance y procedencia

El motor de cuatro etapas pertenece al equipo del Avance 1 y su origen se reconoce en `PROCEDENCIA_BASE.md`. La A3 añade autenticación, endpoint y refactorizaciones del login. Las entregas de otras actividades se excluyen; el caso guía del kit se conserva como dependencia y referencia.

El token es un formato HMAC educativo, no JWT ni OAuth 2.0 completo. El límite por usuario es local a un proceso. El prototipo usa HTTP en loopback; un despliegue externo requiere HTTPS y gestión de secretos apropiada. Las respuestas 200 de Gemini prueban integración, no exactitud exhaustiva; los parches propuestos no se aplicaron ni ejecutaron.

El manual y las presentaciones proporcionadas fueron la base de la entrega. El Word oficial de instrucciones no estuvo disponible.
