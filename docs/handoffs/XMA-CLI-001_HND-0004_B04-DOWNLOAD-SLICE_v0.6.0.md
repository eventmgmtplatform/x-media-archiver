# XMA-CLI-001 — HND-0004 B04 Download Slice

**Versión:** 0.6.0  
**Fecha:** 2026-10-29 (America/Mexico_City)  
**Estado:** `PROVIDER_BLOCKED`  
**Prompt:** `XMA-CLI-001-PRM-0021 B04-BBCWORLD-PUBLIC-ACCEPTANCE v0.1.0`  
**Autorización:** `GOV-AUTH-0026`

## Baseline y alcance

- Baseline/HEAD: `34a35d86062977c275f3ca4314c221d52d78a39f`.
- Tree: `c8a20fa6a0f24dbb3419df863346d97a1f76f162`.
- Rama: `feature/xma-b04-download-slice`; PR #4 abierto, draft, mergeable y sin merge.
- CI baseline #56 / run `40831713830`: `SUCCESS`, 287 pruebas, cobertura 90.67 %.
- HND precedente: v0.5.0, `PARTIAL_PROGRESS_PRESERVED / PROVIDER_BLOCKED`.
- Esta ejecución no modificó código, pruebas, esquema, dependencias, lockfile o workflow. El commit
  documental final y su tree se registran en el cuerpo canónico del PR #4.

## Matriz BBCWorld

Se creó `<LOCAL_BBCWORLD_ROOT>/incremental` vacío y separado de cualquier catálogo Reuters. Se usó
Firefox `<LOCAL_PROFILE>`; no se exportaron cookies. Hubo un solo comando límite 2 y cero retries.

| Prueba | Antes | Petición | Telemetría sanitizada | Descargados | Después | Resultado |
|---|---:|---:|---|---:|---:|---|
| BBCWorld `--limit 2` | 0 | 1/2 | `WORKER_STARTED`, `AUTH_LOADED`, `EXTRACTOR_STARTED` | 0 | 0 | `PROVIDER_TIMEOUT` |
| BBCWorld `--limit 2` | 0 | 2/2 | `WORKER_STARTED`, `AUTH_LOADED`, `EXTRACTOR_STARTED` | 0 | 0 | código 8 / `PROVIDER_TIMEOUT` |
| BBCWorld `--limit 5` | 0 | no ejecutada | requería total exacto 2 | — | 0 | detenido por contrato |

No se observaron `PROFILE_SEEN`, `VIDEO_SEEN`, `DUPLICATE_SKIPPED` o `CANDIDATE_SENT`.

## Conteos, integridad y extensiones

- Manifest: `requested_total=2`, `existing_before=0`, `downloaded_this_run=0`, `total_after=0`,
  `complete=false`.
- Videos: 0; sidecars: 0; artifacts: 0; jobs `COMPLETED`: 0; identidades: 0.
- SQLite no fue creado, por lo que `integrity_check` no aplica.
- Extensiones del repositorio: solamente `.json` para el manifest incompleto.
- Cero `.part`, `.tmp`, URLs firmadas o cookies persistidas.
- Todo el repositorio local permanece fuera de Git y no se publica.

## Validaciones offline posteriores

| Comando | Resultado |
|---|---|
| `uv sync --locked --all-groups` | PASS |
| `uv run ruff format --check .` | PASS, 108 archivos |
| `uv run ruff check .` | PASS |
| `uv run mypy` | PASS, 38 archivos fuente |
| `uv run pytest` | PASS, 287 pruebas |
| cobertura local | PASS, 90.30 % |
| `uv build` | PASS, sdist y wheel |
| `git diff --check` | PASS |
| `uv.lock` byte-idéntico | PASS (`847ee02394976ad7a72b906e0e3bb994b2061307`) |
| archivos prohibidos rastreados | cero nuevos |

## Riesgos y siguiente decisión

La implementación incremental no produjo candidatos de BBCWorld dentro de la ventana autorizada;
la observación no identifica por sí sola la causa interna del proveedor. No existe progreso que
reanudar y el criterio de límite 2 no se cumplió. Cualquier prueba adicional requiere nueva
autorización humana.

No hubo cambios funcionales, cookies exportadas, retry manual, dot, merge, tag, release, B05 ni
descarga masiva.
