# XMA-CLI-001 — HND-0004 B04 Download Slice

**Versión:** 0.2.0  
**Fecha:** 2026-10-28 (America/Mexico_City)  
**Estado:** `PARTIAL_PUBLIC_DOWNLOAD / BLOCKED`  
**Prompt:** `XMA-CLI-001-PRM-0017 B04-PUBLIC-DOWNLOAD-RECOVERY v0.1.0`

## Baseline y commits

- Baseline: `6761e2301c63beac04acd8ac8a73d04dcd2a4197`.
- Tree baseline: `d17f9d770f860d7ac41fb8fde765502c5fed5b86`.
- Rama: `feature/xma-b04-download-slice`.
- PR draft apilado: #4, base `feature/xma-b03-discovery`.
- Diagnóstico: `aaf517d1003a614a9227c8a92d21bafa65648719`.
- Tree del diagnóstico: `96a7df6a41e50190904148f0862c5fae6ee4f4a4`.
- CI #46 / run `40824364282`: `SUCCESS` antes del smoke.
- El commit que contiene este handoff es la publicación documental posterior a la recuperación.

## Diagnóstico sanitizado

La frontera clasifica timeout, conexión, HTTP 502, HTTP 503, rate limit, restricción y contrato con
mensajes constantes. Conserva códigos públicos 8, 4, 3 y 5 según el contrato preexistente. Pruebas
sintéticas verifican que cookies, URLs, rutas, excepciones y marcadores sensibles no aparecen en
stdout, stderr o mensajes públicos. No se añadió una captura general fuera de la frontera existente.

La primera falla observada durante esta recuperación fue `PROVIDER_TIMEOUT` en Reuters límite 2.

## Matriz pública sanitizada

Se usaron repositorios independientes bajo `<LOCAL_SMOKE_ROOT>` y el mecanismo `FIREFOX`. El perfil
real no se publica. `COOKIE_FILE` no se generó ni utilizó porque Firefox funcionó en límite 1.

| Orden | Target | Límite | Mecanismo | Código | Videos | Sidecars | Manifest | SQLite | Resultado |
|---:|---|---:|---|---:|---:|---:|---:|---:|---|
| 1 | Reuters | 1 | FIREFOX | 0 | 1 | 1 | 1 | 1 | PASS |
| 2 | Reuters | 2 | FIREFOX | 8 | 0 | 0 | 0 | 0 | `PROVIDER_TIMEOUT` |
| 3 | Reuters | 5 | FIREFOX | no ejecutado | 0 | 0 | 0 | 0 | detenido por contrato |
| — | Reuters | 1 | COOKIE_FILE | no usado | 0 | 0 | 0 | 0 | fallback no habilitado |

No hubo retry adicional. Total descargado: un video `.mp4`, 55,616,220 bytes agregados.

## Integridad

Para límite 1: `PRAGMA integrity_check = ok`; un artifact; un `download_job` `COMPLETED`; una
identidad `post_id:media_index` distinta. SHA-256 y tamaño coinciden entre video, sidecar, manifest y
catálogo. No existen `.part` o `.tmp`; sidecar, manifest y SQLite no contienen cookies ni URLs con
query string. Para límite 2 no quedó archivo alguno. Límite 5 no fue creado por la CLI.

Los medios, sidecars, manifest y SQLite permanecen exclusivamente en `<LOCAL_SMOKE_ROOT>` fuera de
Git. No se publican hashes de medios, IDs, URLs, perfil o rutas locales.

## Validación offline

| Comando | Antes y después del smoke |
|---|---|
| `uv sync --locked --all-groups` | PASS |
| `uv run ruff format --check .` | PASS, 100 archivos |
| `uv run ruff check .` | PASS |
| `uv run mypy` | PASS, 34 archivos fuente |
| `uv run pytest` | PASS, 250 pruebas |
| cobertura local | PASS, 92.86 % |
| `uv build` | PASS, sdist y wheel |
| `git diff --check` | PASS |
| `uv.lock` byte-idéntico | PASS |
| archivos prohibidos rastreados | cero |

La CI final se registra en el cuerpo canónico del PR #4 después de publicar este handoff.

## Archivos modificados

- `src/xma/adapters/discovery/gallery_dl.py`.
- `tests/adapters/test_gallery_dl_discovery.py`.
- `tests/test_cli.py`.
- README, CHANGELOG, ADR-0004, Gate Register, Implementation Plan y este handoff.

## Deuda v2, riesgo y rollback

Deuda v2: eliminar o endurecer `--cookies-file`; inicio de sesión guiado Firefox; almacenamiento
seguro del sistema; paginación durable; reanudación; rate limiting; operación para miles;
`retry/status/export/doctor`; y auditoría independiente.

El timeout impide demostrar 2 y 5, por lo que B04 no queda validado. Rollback: revertir los commits
de PRM-0017 o cerrar el PR draft; la rama B03 no fue modificada. Conservar temporalmente el lote
local exacto para una auditoría autorizada.

No hubo retry adicional, merge, tag, release, descarga masiva, B05, dot ni exposición de secretos.
Cualquier nueva ejecución pública requiere decisión humana.
