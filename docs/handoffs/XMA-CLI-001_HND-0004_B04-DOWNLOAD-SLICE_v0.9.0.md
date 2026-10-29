# XMA-CLI-001 — HND-0004 B04 Download Slice

**Versión:** 0.9.0  
**Fecha:** 2026-10-29 (America/Mexico_City)  
**Estado:** `SINGLE_POST_DOWNLOAD_VALIDATED / WAITING_CHAT_VALIDATION`  
**Prompt:** `XMA-CLI-001-PRM-0025 B04-SINGLE-POST-INSPECT-PARITY-AND-DOWNLOAD v0.1.0`

## Baseline, autorización y alcance

- Baseline: `3a0e70cf3795d16e4fa98a930c1220a6ac3e4e3d`; tree `225f2305c5414a00d930d8bf0002a06fc7733600`.
- Commit funcional: `5852f62ddaca6c257c2c7f66f2081fe70c46372f`; tree `4167bf43f64b5e51632a0bff0289ff02dd1e9103`.
- Rama `feature/xma-b04-download-slice`; PR #4 abierto, draft, mergeable y sin merge.
- CI baseline #63/run `40836310657`: `SUCCESS`, 302 pruebas, cobertura 90.57 %.
- CI funcional #64/run `40837243538`: `SUCCESS` sobre `5852f62`.
- Leonel autorizó corregir exclusivamente la selección de URL del adaptador principal, ejecutar un
  `inspect` y, solo después de su PASS completo, una descarga del mismo post.

No cambiaron autenticación, cookies, mapper numérico, esquema, downloader, timeouts, IPC, spawn,
dependencias, `uv.lock` o workflows. No se ejecutó el post usado por PRM-0024.

## Corrección funcional

El adaptador principal selecciona ahora la URL del job mediante una función pura y explícita:

- `PROFILE` conserva `https://x.com/<handle>/timeline`.
- `SINGLE_POST` usa `https://x.com/<handle>/status/<post_id>`.

La ruta incremental importa la misma selección sin cambiar su comportamiento observable. Ambos
adaptadores aplican la misma validación fail-closed de post y autor. Las pruebas offline cubren
canonicalización, ausencia de `/timeline` en SINGLE_POST, límite y discrepancias de identidad.

## Matriz pública sanitizada

Target permitido: host `x.com`, handle `great_almightyG`, post ID `2115507112214462643`; la query de
entrada fue descartada antes de discovery y no aparece en salida o persistencia.

| Fase | Código | Duración | Resultado |
|---|---:|---:|---|
| `inspect`, límite 1 | 0 | 2 s | un perfil, un post exacto y un activo `VIDEO`; JSON válido; cero persistencia |
| `download`, límite 1 | 0 | 2 s | `0 → 1`, completo; un MP4, sidecar, artifact, job e identidad |

Inspect no creó SQLite, manifest, sidecar o medio y no mostró traceback. La descarga emitió
`WORKER_STARTED`, `AUTH_LOADED`, `EXTRACTOR_STARTED`, `PROFILE_SEEN` y `VIDEO_SEEN`.

## Conteos, integridad y artifact

- Manifest: `requested_total=1`, `existing_before=0`, `downloaded_this_run=1`, `total_after=1`, `complete=true`.
- Catálogo: un perfil, post, activo, discovery run, job y artifact; una identidad distinta.
- Job: `COMPLETED`; `PRAGMA integrity_check=ok`.
- Video: `.mp4`, 2,397,441 bytes.
- SHA-256 permitido: `8d262cc984e77c2dbb2f43644783854dc8d43699768b49ce02a8e00b5becf8d5`.
- Hash y tamaño coinciden entre archivo, sidecar, manifest y SQLite.
- Residuos `.part`/`.tmp`: cero.
- Variantes multimedia, URLs firmadas, query de entrada, cookies, headers, tokens, perfil o rutas
  personales persistidos: cero en la comprobación sanitizada.

El repositorio de descarga y los logs permanecen exclusivamente locales, separados y fuera de Git.

## Validaciones offline

| Comando | Resultado |
|---|---|
| `uv sync --locked --all-groups` | PASS |
| `uv run ruff format --check .` | PASS, 112 archivos |
| `uv run ruff check .` | PASS |
| `uv run mypy` | PASS, 38 archivos fuente |
| `uv run pytest` | PASS, 306 pruebas |
| cobertura local | PASS, 90.32 % |
| `uv build` | PASS, sdist y wheel |
| `git diff --check` | PASS |
| `uv.lock` byte-idéntico | PASS (`847ee02394976ad7a72b906e0e3bb994b2061307`) |
| evidencia privada/prohibida rastreada | cero |

## Riesgo, rollback y siguiente decisión

La aceptación demuestra un único video público por URL de estado; no demuestra descarga masiva,
recorrido de cuenta ni cierre general de B04. La decisión de gate permanece humana.

Rollback funcional: revertir `5852f62`; esto restaura la selección histórica del adaptador principal
sin tocar esquema ni datos. Los medios locales no forman parte de Git.

No hubo retry, cookie file, exportación de cookies, otro perfil/post, recorrido de cuenta,
gallery-dl directo, curl, wget, dot, merge, tag, release, B05 o descarga masiva.
