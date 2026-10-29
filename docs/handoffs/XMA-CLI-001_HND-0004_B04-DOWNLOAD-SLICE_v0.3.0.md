# XMA-CLI-001 — HND-0004 B04 Download Slice

**Versión:** 0.3.0  
**Fecha:** 2026-10-29 (America/Mexico_City)  
**Estado:** `BLOCKED_PUBLIC_DOWNLOAD`  
**Prompt:** `XMA-CLI-001-PRM-0018 B04-BOUNDED-DISCOVERY-RECOVERY v0.1.0`

## Baseline, commits y CI

- Baseline: `75594b46945cf2d1f791da6e2d850a44a8785118`.
- Tree baseline: `e2ac5dba9e520b2748574fcb8f1c13f63edd5dd5`.
- Rama: `feature/xma-b04-download-slice`; PR #4 draft sobre `feature/xma-b03-discovery`.
- `4089b26`: watchdog inicial de discovery; CI #48 `SUCCESS`.
- `6eeb9a2`: señal de deadline no absorbible; CI #49 `SUCCESS`.
- `6d28633`: normalización y máximo 120 s; CI #50 `SUCCESS`.
- `9a72d33b26ca046d73e4b7655038d033d0b0e43f`: deadline/HTTP 180 s; tree
  `8bfa6167fc8dc823ecc6390caf6148df1271843e`; CI #51 `SUCCESS`.
- El commit que contiene este handoff es la publicación documental posterior al smoke.

## Implementación del timeout

`xma download --discovery-timeout N` usa 30 s por defecto. El rango Linux es 5–180 s tras las
ampliaciones humanas expresas de 120 y 180 s. Un watchdog `SIGALRM` cubre la fase completa; el
timeout HTTP de gallery-dl queda subordinado al mismo límite. La frontera cancela el timer y
restaura handler/timer previos en éxito o error. No crea threads o procesos. Fuera de Linux falla
cerrada. Timeout y contrato vacío al vencer se normalizan como código 8 / `PROVIDER_TIMEOUT`.

## Matriz completa sanitizada

El lote previo exitoso de límite 1 se conservó sin modificar y no se repitió. Se usaron repositorios
nuevos bajo `<LOCAL_SMOKE_ROOT>`. Los tiempos son duración total redondeada a segundos.

| Orden | Límite | Mecanismo | Deadline | Duración | Código | Clasificación | Videos | Residuos |
|---:|---:|---|---:|---:|---:|---|---:|---|
| evidencia previa | 1 | FIREFOX | — | — | 0 | PASS | 1 | ninguno |
| 1 | 2 | FIREFOX | 60 s | 159 s | 8 | `PROVIDER_TIMEOUT` | 0 | ninguno |
| 2 | 2 | COOKIE_FILE | 60 s | 60 s | 5 | contrato interno pre-corrección | 0 | ninguno |
| ampliación humana | 2 | COOKIE_FILE | 120 s | 121 s | 5 | perfil vacío al deadline | 0 | ninguno |
| ampliación humana final | 2 | COOKIE_FILE | 180 s | 180 s | 8 | `PROVIDER_TIMEOUT` | 0 | ninguno |
| detenido | 5 | — | — | — | no ejecutado | límite 2 no pasó | 0 | ninguno |

Las ampliaciones a 120 y 180 s fueron instrucciones humanas explícitas posteriores al mandato
inicial. No se efectuó ningún intento adicional después de 180 s.

## Conteos, integridad y privacidad

Las ejecuciones de límite 2 produjeron cero videos, sidecars, manifests, SQLite, `.part` y `.tmp`.
Por ello no existen hashes o integridad SQLite nuevos que comprobar. El lote histórico de límite 1
conserva un `.mp4`, un sidecar, un manifest, una SQLite íntegra y hashes/tamaños coincidentes según
HND v0.2.0; no fue abierto, modificado ni repetido.

Total exitoso acumulado gobernado: 1 video, no 8. El archivo COOKIE_FILE temporal tuvo permisos
0600, nunca se imprimió o versionó y fue eliminado al terminar. No se publican perfiles, cookies,
rutas, URLs, tokens, headers o medios.

## Validación offline posterior

| Comando | Resultado |
|---|---|
| `uv sync --locked --all-groups` | PASS |
| `uv run ruff format --check .` | PASS, 103 archivos |
| `uv run ruff check .` | PASS |
| `uv run mypy` | PASS, 36 archivos fuente |
| `uv run pytest` | PASS, 261 pruebas |
| cobertura local | PASS, 92.37 % |
| `uv build` | PASS, sdist y wheel |
| `git diff --check` | PASS |
| `uv.lock` byte-idéntico | PASS |
| archivos prohibidos rastreados | cero |

La CI final del commit documental se registra en el cuerpo canónico del PR #4.

## Archivos modificados

- `src/xma/adapters/discovery/bounded.py` y export del adaptador.
- `src/xma/adapters/discovery/gallery_dl.py`.
- `src/xma/cli.py`.
- pruebas del watchdog, gallery-dl y CLI download.
- README, CHANGELOG, ADR-0004, Gate Register, Implementation Plan y este handoff.

## Deuda v2, rollback y decisión

Deuda v2: sustituir señales por una frontera portable; eliminar o endurecer `--cookies-file`;
inicio de sesión guiado Firefox; almacenamiento seguro; paginación durable; reanudación; rate
limiting; operación para miles; `retry/status/export/doctor`; y auditoría independiente.

Rollback: revertir los commits PRM-0018 o cerrar el PR draft; B03 no cambió. B04 permanece
`BLOCKED_PUBLIC_DOWNLOAD`. No hubo merge, tag, release, masivo, dot, B05 ni exposición de secretos.
Cualquier nueva ejecución pública requiere otra autorización humana.
