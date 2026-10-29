# XMA-CLI-001-PRM-0003 — B03 Discovery

**Versión:** 0.1.0

**Estado:** APPROVED FOR ONE EXECUTION

**Ejecutor:** Codex localhost

**Repositorio:** `https://github.com/eventmgmtplatform/x-media-archiver.git`

**Baseline obligatoria:** `main` en `b2bdca7961f00d54f2465a4f8d26b2003340c3b9`

**Rama de trabajo:** `feature/xma-b03-discovery`

## 1. Objetivo

Implementar discovery de contenido audiovisual público de X mediante un adaptador reemplazable de
`gallery-dl`, los casos de uso `inspect` y `sync`, y persistencia idempotente en el catálogo B02.
B03 descubre y cataloga; no descarga ningún medio.

## 2. Resultado esperado

- `xma inspect @perfil --limit N [--json]` enumera publicaciones y activos audiovisuales sin
  modificar el catálogo.
- `xma sync @perfil --limit N --repository RUTA [--dry-run]` registra perfil, publicaciones,
  activos y `DiscoveryRun` en `RUTA/catalog.sqlite3`.
- Una ejecución controlada y anónima cataloga hasta dos activos de video de una organización
  periodística pública, sin crear archivos de medios.
- Fixtures offline y pruebas de contrato protegen el mapeo frente a cambios del extractor.

## 3. Precondiciones

1. Actualizar referencias y verificar que `main` coincide exactamente con la baseline.
2. Confirmar worktree limpio; no sobrescribir trabajo ajeno.
3. Crear o reutilizar solamente `feature/xma-b03-discovery` desde la baseline.
4. Ejecutar todos los gates B02 antes de modificar; deben pasar.
5. Confirmar que `HND-0002`, `AUD-0002` y el merge Q2 existen en GitHub.
6. No iniciar si el prompt gobernado no está presente en la rama.

Ante cualquier incumplimiento, producir `HND-0003` con estado `BLOCKED` y detenerse.

## 4. Alcance obligatorio

### 4.1 Contrato de discovery

Definir modelos de entrada/salida y un puerto tipado que expresen:

- objetivo normalizado (`@handle`, handle o URL de perfil);
- perfil observado;
- publicaciones audiovisuales;
- activos con índice, tipo, variantes, dimensiones y duración cuando estén disponibles;
- cursor o cobertura observada, advertencias y errores normalizados;
- límite solicitado y conteo realmente observado.

El dominio y la aplicación no importan `gallery_dl` ni tipos propios del proveedor.

### 4.2 Adaptador `gallery-dl`

- Añadir `gallery-dl` como dependencia versionada y bloqueada; no copiar extractores.
- Encapsularlo en `src/xma/adapters/discovery/`.
- Usar API Python o proceso con lista de argumentos; nunca `shell=True`.
- Activar explícitamente modo de metadatos/simulación que impida escribir medios.
- No aceptar contraseñas, tokens, cabeceras arbitrarias ni cookies en B03.
- Normalizar errores: objetivo inválido, perfil no encontrado, restringido, rate limit, cambio de
  contrato y fallo transitorio.
- No registrar URLs firmadas completas, cabeceras ni datos sensibles.
- Aplicar límite temprano cuando el proveedor lo permita y límite defensivo en aplicación.

### 4.3 Casos de uso

- `inspect`: consulta y presenta resultados; no crea catálogo, base, manifiesto ni medios.
- `sync`: con transacción, crea/actualiza `Profile`, `Post`, `MediaAsset` y `DiscoveryRun`.
- `sync --dry-run`: muestra el cambio previsto sin persistir.
- Repetir el mismo `sync` no crea duplicados ni cambia identidades estables.
- El handle observado puede cambiar sin sustituir `profile_id`.
- Nunca declarar cobertura total; reportar proveedor, límite y limitaciones observadas.

### 4.4 CLI

Implementar como mínimo:

```text
xma inspect TARGET [--limit N] [--json]
xma sync TARGET [--limit N] [--repository PATH] [--dry-run] [--json]
```

Requisitos:

- `1 <= N <= 100` y valor por defecto conservador;
- salida humana clara y JSON estable para automatización;
- códigos de salida documentados para éxito, entrada inválida, acceso/restricción y fallo externo;
- ruta de repositorio explícita o default local documentado, nunca dentro del paquete fuente;
- mensajes sin traceback salvo modo de depuración explícito.

## 5. Prueba controlada pública

Después de que pruebas offline y CI local pasen:

1. Ejecutar anónimamente `inspect` y `sync --limit 2` contra `@Reuters`.
2. Si no ofrece dos videos accesibles o el extractor no resuelve el perfil, intentar en orden
   `@AP` y `@BBCWorld`; registrar el motivo exacto del fallback.
3. Usar un directorio temporal o `evidence/local-b03/` ignorado por Git.
4. Verificar por consulta SQLite que existen como máximo dos activos de tipo video, su perfil,
   posts y un `DiscoveryRun` terminado.
5. Confirmar que no se creó ningún archivo multimedia.
6. Registrar en el handoff cuenta, comandos, conteos, IDs públicos, versión de `gallery-dl` y
   resultado. No incluir URLs firmadas, cookies ni respuesta cruda completa.

Si X o el proveedor exige autenticación/cookies, clasificar `BLOCKED`. No introducir cookies ni
cambiar de extractor dentro de este bloque.

## 6. Pruebas obligatorias

Mantener B02 verde y añadir pruebas sin red para:

1. normalización y rechazo de targets;
2. mapeo de fixtures de perfil, post y video;
3. publicación con múltiples medios e índices estables;
4. campos opcionales y claves desconocidas;
5. contrato cambiado o payload malformado;
6. clasificación de errores externos;
7. límite y paginación/cursor observados;
8. `inspect` sin efectos laterales;
9. `sync`, `--dry-run`, rollback e idempotencia;
10. salida JSON y códigos de salida CLI.

La suite automatizada no realiza tráfico real. Cobertura total `>= 90 %`; mapeadores y casos de
uso críticos, `100 %` de ramas cuando sea razonable.

## 7. Fuera de alcance — prohibiciones

- No usar cookies, login, contraseña, token ni sesión autenticada.
- No integrar `yt-dlp`, FFmpeg, Twikit, `twscrape` ni otro extractor.
- No descargar thumbnails, videos, audio ni archivos de medios.
- No implementar `download`, `retry`, `status`, `export` o `doctor`.
- No crear repositorio documental, sidecars, hashes de medios ni staging B04.
- No crear GUI, API, servidor, ORM, Redis, Docker o servicio programado.
- No rastrear bases SQLite, respuestas reales, medios, secretos ni evidencias locales.
- No fusionar a `main`, crear tags/releases o comenzar B04.

## 8. Validaciones de cierre

Registrar:

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

Verificar además el wheel, el lockfile, ausencia de medios/bases/secretos rastreados, y que CI
remota termine en verde después de publicar.

## 9. Entregables y handoff

- contrato, aplicación y adaptador de discovery;
- comandos `inspect` y `sync`;
- fixtures sintéticos/sanitizados y pruebas offline;
- README con ejemplos exclusivamente B03 y códigos de salida;
- CHANGELOG actualizado;
- handoff `docs/handoffs/XMA-CLI-001_HND-0003_B03-<RUN-ID>_v0.1.0.md`.

El handoff incluye baseline, rama, commits/tree, archivos, decisiones, comandos/resultados,
cobertura, CI, evidencia pública controlada, defectos, limitaciones, riesgos, rollback, métricas y
estado `WAITING_VALIDATION`, `BLOCKED` o `FAILED`.

## 10. Condición de parada

Publicar commits en la rama y actualizar el PR draft de B03. Detenerse después de `HND-0003` y
CI. No fusionar, no autorizar B04 y no afirmar que el producto descarga videos.
