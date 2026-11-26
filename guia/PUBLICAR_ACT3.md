# Publicar la entrega en el repositorio nuevo

Destino único: **https://github.com/MajesDo63/Act3**.

El paquete contiene una sola carpeta `Act3`. Copia el contenido de esa carpeta dentro del clon local de **Act3**. No copies Documentos, OneDrive ni `Project_v2_TSTI`. Conserva `.git` del clon; el paquete no trae esa carpeta.

## GitHub Desktop

1. **File → Clone repository → URL**: pega `https://github.com/MajesDo63/Act3.git` y elige una carpeta local distinta del proyecto anterior.
2. Pulsa **Show in Explorer**. Copia ahí los archivos y carpetas que están dentro de `Act3` en el ZIP descomprimido. `README.md`, `api/`, `a3/` y `entrega/` deben quedar directamente en la raíz del clon.
3. Vuelve a Desktop y verifica que **Current repository** diga **Act3**. La lista debe contener el informe, código y registros, sin `.env`, `.venv` ni bases SQLite.
4. En Summary escribe `Completar Actividad 3 de Cesar` y pulsa **Commit to main**. Después **Push origin** o **Publish branch**, según aparezca.
5. En **History**, clic derecho sobre ese commit → **Create Tag** → `a3-MajesDo63`. Pulsa **Push origin** si indica una etiqueta pendiente. Si tu versión no ofrece esa opción, usa los comandos de abajo después de subir el commit.
6. Abre **View on GitHub** y verifica el PDF dentro de `entrega/` y la etiqueta en **Tags**. Solo entonces el repositorio y la etiqueta estarán publicados.

## Crear y subir la etiqueta desde PowerShell

Abre una terminal **en la carpeta del clon Act3**, después de subir el commit, y ejecuta una línea a la vez:

```powershell
git remote get-url origin
```

Debe mostrar `https://github.com/MajesDo63/Act3.git` (o el remoto SSH equivalente de esa misma cuenta y repositorio). Si muestra otro proyecto, abre el clon correcto antes de continuar.

```powershell
git tag -a a3-MajesDo63 -m 'Entrega Actividad 3 - Cesar Eduardo Valdez Pinto'
git push origin a3-MajesDo63
```

No uses `--force` para sustituir una etiqueta que ya exista.

## Entregar al docente

Adjunta `entrega/Actividad3_Cesar_Informe.pdf` en Canvas y en el correo. Incluye:

- Repositorio: `https://github.com/MajesDo63/Act3`
- Versión entregada: `https://github.com/MajesDo63/Act3/tree/a3-MajesDo63` (después de publicar la etiqueta).

El Word es editable y acompaña la entrega como respaldo. El código y las evidencias quedan en GitHub; no necesitas mandar el entorno `.venv` ni la llave de Gemini.
