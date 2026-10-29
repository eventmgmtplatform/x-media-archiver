# XMA-CLI-001 — HND-0004 B04 Download Slice

**Versión:** 0.7.0  
**Fecha:** 2026-10-29 (America/Mexico_City)  
**Estado:** `B04_LIMIT_2_VALIDATED / LIMIT_5_BLOCKED`  
**Prompt:** `XMA-CLI-001-PRM-0022 B04-PROVIDER-PARITY-AND-SPAWN-RECOVERY v0.1.0`

## Baseline y cambio

- Baseline: `e1c63b204cd0cfc892757bb9849ebdeaee8e76f7`.
- Tree baseline: `0eb27822bf2042a04207d621f2a818337db2cc42`.
- Rama: `feature/xma-b04-download-slice`; PR #4 abierto, draft y sin merge.
- CI baseline #57 / run `40832968358`: `SUCCESS`, 287 pruebas, 90.67 %.
- Commit funcional spawn: `0bfcddc68c7ca2e18690535ae42d52ec55df2d8d`.
- CI funcional: runs `40833785888` y `40833786782`, ambos `SUCCESS` antes del smoke.

El único cambio funcional selecciona `multiprocessing.get_context("spawn")` en lugar de `fork`.
El target permanece a nivel de módulo; BrowserAuthentication es serializable y no contiene valores
de cookies; Pipe/DTO, deadlines, cierres y terminate/kill/join conservan su contrato.

## Paridad read-only

`inspect @BBCWorld --limit 1` se ejecutó exactamente una vez en el proceso principal con timeout
externo de 35 s. Resultado: código 0, 13 s, perfil público y un activo observados, JSON válido,
traceback ausente y cero SQLite, manifest, sidecar o medio persistido.

La paridad pasó y spawn cambió el resultado público desde cero candidatos a descargas válidas. Esto
respalda a fork como causa del bloqueo previo en la frontera worker, sin atribuirle el fallo distinto
observado al buscar el quinto activo.

## Matriz spawn sanitizada

Se creó `<LOCAL_BBCWORLD_SPAWN_ROOT>/incremental` vacío. Firefox usó `<LOCAL_PROFILE>`; no se
exportaron cookies. Cada comando se ejecutó una sola vez.

| Prueba | Antes | Telemetría resumida | Descargados | Después | Resultado |
|---|---:|---|---:|---:|---|
| límite 2 | 0 | worker/auth/extractor/profile; 2 videos observados | 2 | 2 | código 0, `complete=true` |
| límite 5, worker 1 | 2 | 2 duplicados; nuevo video observado | 2 acumulados en ejecución | 4 | progreso preservado |
| límite 5, worker 2 | 4 efectivo | 3 duplicados; cuarto video observado | 0 adicional | 4 | código 5 / `WORKER_FAILED` |

No hubo retry manual. La ejecución límite 5 duró 130 s y quedó incompleta.

## Conteos e integridad

### Límite 2

- Manifest: `requested_total=2`, `existing_before=0`, `downloaded_this_run=2`, `total_after=2`,
  `complete=true`.
- Dos videos, sidecars, artifacts, jobs `COMPLETED` e identidades distintas.
- `PRAGMA integrity_check = ok`; hashes y tamaños: PASS; cero `.part`/`.tmp`.

### Estado final tras límite 5

- Manifest: `requested_total=5`, `existing_before=2`, `downloaded_this_run=2`, `total_after=4`,
  `complete=false`.
- Cuatro videos `.mp4`, cuatro sidecars `.json`, cuatro artifacts, cuatro jobs `COMPLETED` y cuatro
  identidades distintas; catálogo `.sqlite3` íntegro.
- Hashes y tamaños de artifacts completados: PASS; cero `.part`/`.tmp`, cookies o URLs firmadas
  persistidas.
- Los medios y catálogo permanecen exclusivamente fuera de Git.

## Validación offline

| Comando | Resultado |
|---|---|
| `uv sync --locked --all-groups` | PASS |
| `uv run ruff format --check .` | PASS, 109 archivos |
| `uv run ruff check .` | PASS |
| `uv run mypy` | PASS, 38 archivos fuente |
| `uv run pytest` | PASS, 288 pruebas |
| cobertura local | PASS, 90.30 % |
| `uv build` | PASS, sdist y wheel |
| `git diff --check` | PASS |
| `uv.lock` byte-idéntico | PASS (`847ee02394976ad7a72b906e0e3bb994b2061307`) |
| archivos prohibidos rastreados | cero nuevos |

## Riesgo, rollback y siguiente decisión

Límite 2 queda validado localmente. Límite 5 sigue bloqueado por un `WORKER_FAILED` sanitizado tras
preservar cuatro activos. Rollback: revertir el commit spawn; no reescribir historia ni borrar la
evidencia local. No se autoriza repetir, ampliar timeouts, cambiar autenticación ni iniciar B05.

No hubo cookies exportadas, retry manual, dot, merge, tag, release o descarga masiva.
