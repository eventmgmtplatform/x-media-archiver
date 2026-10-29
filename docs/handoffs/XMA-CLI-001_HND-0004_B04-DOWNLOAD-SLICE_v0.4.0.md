# XMA-CLI-001 — HND-0004 B04 Download Slice

**Versión:** 0.4.0  
**Fecha:** 2026-10-29 (America/Mexico_City)  
**Estado:** `PARTIAL_PROGRESS_PRESERVED / BLOCKED`  
**Prompt:** `XMA-CLI-001-PRM-0019 B04-INCREMENTAL-RESUMABLE-DOWNLOAD v0.1.0`

## Baseline, commit y CI

- Baseline: `869732623a797276ab32abad3f22f623a19306d9`.
- Tree baseline: `351d0e1aa875aa3170cbc3efc7c6a21f4219c71c`.
- Rama: `feature/xma-b04-download-slice`; PR #4 draft sobre B03.
- Commit funcional: `40e67d269b06ab87d5eede543bcf234aebc2f179`.
- Tree funcional: `d7e2d7d2fa02dd9837acca3ca3c872c9d07cf73c`.
- CI #53 / run `40829160311`: `SUCCESS` antes de la prueba pública.
- El commit que contiene este handoff es la publicación documental posterior.

## Diseño entregado

`--limit N` significa asegurar un total de hasta N activos válidos del target. Antes de red, el
servicio enumera jobs/artifacts, verifica estado `COMPLETED`, media asset, archivo, tamaño, SHA-256,
sidecar y perfil. Solo el catálogo respalda el conteo. Si el total ya satisface N, termina sin red.

Un worker Linux hijo contiene gallery-dl y lectura de autenticación. Recibe identidades públicas
existentes, nunca cookies. Emite perfil, metadata y URL efímera por queue local en memoria. El padre
descarga y persiste cada candidato de inmediato. La URL no entra en SQLite, sidecar, manifest o log.

Cada worker dura máximo 30 s. El padre aplica terminate, join breve, kill si sigue vivo y join final.
`--discovery-attempts` admite 1–2, predeterminado 2. El segundo worker solo comienza si falta total.
No existe retry HTTP de medios. El rango `--discovery-timeout` vuelve a 5–60 s.

## Progreso parcial y manifest

El manifest incluye `requested_total`, `existing_before`, `downloaded_this_run`, `total_after` y
`complete`. Candidatos duplicados se omiten; jobs completados, archivos y sidecars válidos no se
sobrescriben. Un timeout conserva artifacts terminados y elimina únicamente staging incompleto.

## Matriz pública

El repositorio original límite 1 no se modificó. Se copió localmente a `<LOCAL_RESUME_ROOT>` y se
verificó antes del comando.

| Fase | Total antes | Petición | Timeout | Progreso | Total después | Código/clasificación |
|---|---:|---:|---:|---|---:|---|
| copia inicial | 1 | — | — | evidencia íntegra | 1 | PASS |
| `--limit 2` | 1 | 1/2 | 30 s | ningún candidato | 1 | `PROVIDER_TIMEOUT` |
| `--limit 2` | 1 | 2/2 | 30 s | ningún candidato | 1 | `PROVIDER_TIMEOUT`, código 8 |
| `--limit 5` | 1 | no ejecutada | — | requiere total 2 | 1 | detenido por contrato |

Duración total sanitizada del comando límite 2: 61 s. Salida de progreso: `discovery attempt 1/2`,
`discovery attempt 2/2`. No hubo descarga nueva.

## Conteos e integridad

- `existing_before=1`, `downloaded_this_run=0`, `total_after=1`, `complete=false`.
- Un video, un sidecar, un artifact, un job `COMPLETED` y una identidad distinta.
- `PRAGMA integrity_check = ok`.
- Hash y tamaño del video existente coinciden con catálogo.
- Cero `.part` y `.tmp`.
- Cero cookies o URLs con query string persistidas.
- El original límite 1 permanece sin modificar; toda prueba usó una copia fuera de Git.

## Validación offline

| Comando | Resultado |
|---|---|
| `uv sync --locked --all-groups` | PASS |
| `uv run ruff format --check .` | PASS, 106 archivos |
| `uv run ruff check .` | PASS |
| `uv run mypy` | PASS, 38 archivos fuente |
| `uv run pytest` | PASS, 276 pruebas |
| cobertura local | PASS, 90.46 % |
| `uv build` | PASS, sdist y wheel |
| `git diff --check` | PASS |
| `uv.lock` byte-idéntico | PASS |
| archivos prohibidos rastreados | cero |

La CI final del commit documental se registra en el cuerpo canónico del PR #4.

## Archivos y deuda

Cambios: catálogo listable, puerto incremental, worker gallery-dl, servicio acumulado/reanudable,
CLI, resumen/manifest y pruebas de worker, servicio y CLI; más documentación gobernada.

Deuda B05: paginación/cursor durable, operación para miles, scheduling, progreso persistente entre
hosts, `retry/status/export/doctor`, portabilidad del worker y auditoría independiente.

No hubo cookies exportadas, dot, merge, tag, release, B05, descarga masiva ni exposición de
secretos. Cualquier repetición pública requiere nueva decisión humana.
