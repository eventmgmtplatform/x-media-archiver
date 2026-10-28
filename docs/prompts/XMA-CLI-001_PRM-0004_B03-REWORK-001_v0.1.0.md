# XMA-CLI-001-PRM-0004 — B03 Rework 001

**Versión:** 0.1.0

**Estado:** APPROVED FOR ONE EXECUTION

**Ejecutor:** Codex localhost

**Supervisión humana:** Leonel Galindo

**Repositorio:** `https://github.com/eventmgmtplatform/x-media-archiver.git`

**Rama:** `feature/xma-b03-discovery`

**Baseline del rework:** HEAD de PR #3 que contenga AUD-0003 y estos prompts.

## 1. Objetivo

Corregir exclusivamente R-01 a R-07 de `XMA-CLI-001-AUD-0003 v0.1.0` sin ampliar B03.
El resultado debe dejar como único impedimento posible el `AuthRequired` de la prueba pública
anónima. Este rework no autoriza cookies, autenticación, otro extractor ni B04.

## 2. Precondiciones

1. Consultar PR #3 y verificar que AUD-0003, PRM-0004 y DOT-PRM-0004 estén versionados.
2. Verificar rama, upstream, worktree limpio, HEAD y CI de la baseline del rework.
3. Trabajar sobre `feature/xma-b03-discovery`; no reescribir historia ni usar force-push.
4. Si GitHub cambió desde la autorización o falta evidencia canónica, detenerse con estado
   `BLOCKED`.

## 3. Rework obligatorio

### R-01 — Evidencia y handoff

- Crear addendum `HND-0003` v0.1.1 o un handoff de rework equivalente y trazable.
- Registrar comandos exactos, orden, timestamps, cuenta, salida y motivo de fallback para Reuters,
  AP y BBCWorld.
- Registrar conteos de perfiles, posts, activos y runs. Si el fallo ocurrió antes de crear el
  catálogo, indicar explícitamente `N/A — fallo previo a persistencia` y demostrar que no existe
  SQLite que consultar.
- Recuperar evidencia existente cuando sea posible. No inventar salidas.
- Si la evidencia no existe, se autoriza repetir una sola prueba pública, anónima, de metadatos y
  limitada a dos activos por cuenta, en el orden Reuters → AP → BBCWorld. Sin cookies, login,
  secretos, descarga ni archivos multimedia.
- Incluir inventario de archivos, métricas disponibles, limitaciones, rollback integral de B03 y
  ausencia de medios rastreados.

### R-02 — Estado del PR y documentación

- Actualizar README, CHANGELOG, Gate Register e Implementation Plan al estado real
  `B03 REWORK_REQUIRED`; conservar por separado el bloqueo externo `AuthRequired`.
- Preparar una descripción actualizada del PR con commits, HND, AUD, CI y estado. Si no existe
  acceso autenticado para modificar el cuerpo del PR, entregar el texto al gobernante y marcarlo
  como acción pendiente; no falsificar el cambio.

### R-03 — Rework B02

- Conciliar documentalmente AUD-0002 v0.1.2 y la rama de rework B02 con la baseline `b2bdca7`.
- Registrar que esos fixes no están integrados en `main` ni en B03, su estado y su impacto.
- No importar indiscriminadamente el rework B02. Cualquier cambio funcional de B02 requiere
  demostrar que es indispensable para los casos `inspect`/`sync` de B03 y mantener el diff mínimo.
- Eliminar afirmaciones de que no existe rework B02 cuando Git demuestra lo contrario.

### R-04 — JSON estable

- Emitir JSON por una salida cruda que no interprete markup, estilos ni wrapping de Rich.
- Mantener `ensure_ascii=False`, orden determinista y una sola representación parseable.
- Añadir regresiones con corchetes/markup, Unicode y cadenas largas; validar con `json.loads`.

### R-05 — Errores y persistencia

- Completar la taxonomía al menos para not-found, restricted/auth, rate limit, cambio de contrato y
  fallo transitorio, sin exponer respuesta cruda ni secretos.
- Normalizar errores esperables de catálogo, SQLite, creación de directorios y filesystem.
- Mover operaciones locales fallables dentro de límites de captura deliberados.
- Documentar códigos de salida y añadir pruebas CLI para conflicto de catálogo, ruta no escribible
  y fallo externo. No capturar indiscriminadamente `BaseException`.

### R-06 — Idempotencia y variantes efímeras

- Definir qué parte de una variante es estable y cuál es efímera/sensible.
- Evitar que query strings, firmas o rotación equivalente rompan la identidad estable del activo.
- No imprimir URLs firmadas. La persistencia debe ser sanitizada o tener una política de actualización
  explícita y probada.
- Añadir dos sync del mismo activo con variantes rotadas y comprobar ausencia de conflicto/duplicado.

### R-07 — Límite y cursor

- Añadir defensa en aplicación: el resultado no puede exceder el límite solicitado y debe ser
  coherente con el contrato de entrada.
- Probar un proveedor que devuelve más activos o un límite inconsistente.
- Documentar y probar `cursor=None` como limitación observada mientras no exista paginación real.

## 4. Restricciones

- No cookies, login, tokens de usuario, contraseñas ni sesiones autenticadas.
- No `yt-dlp`, FFmpeg, Twikit, `twscrape` ni otro extractor.
- No descargar videos, audio, thumbnails o sidecars.
- No implementar `download`, `retry`, `status`, `export` o `doctor`.
- No GUI, API, servidor, ORM, Redis, Docker, scheduler, tags o releases.
- No bases, medios, secretos, respuestas reales ni evidencias locales en Git.
- Tests automatizados sin red; solamente el smoke manual acotado puede usar red.
- No merge, no B04 y no declarar el producto certificado.

## 5. Validación

Ejecutar y registrar:

```bash
uv sync --locked --all-groups
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest
uv build
git diff --check
git status --short
```

Cobertura total mínima: 90 %. Confirmar que el wheel contiene lo requerido, el lockfile permanece
íntegro y no existen archivos prohibidos rastreados. Publicar commits acotados y esperar CI verde
sobre el HEAD final.

## 6. Entregables y parada

- Código y pruebas para R-04 a R-07.
- Documentación y evidencia para R-01 a R-03.
- Handoff/addendum de rework con commits, tree, CI, resultados, limitaciones y rollback.
- PR #3 permanece draft.

Detenerse tras publicar el handoff y obtener CI. No crear AUD-0003 v0.1.1, no fusionar y no
autorizar B04. La única clasificación aceptable al entregar es `WAITING_VALIDATION`,
`BLOCKED` o `FAILED`, sustentada por evidencia.
