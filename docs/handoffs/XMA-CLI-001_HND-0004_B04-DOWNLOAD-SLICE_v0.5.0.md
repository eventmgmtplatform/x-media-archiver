# XMA-CLI-001 — HND-0004 B04 Download Slice

**Versión:** 0.5.0  
**Fecha:** 2026-10-29 (America/Mexico_City)  
**Estado:** `PARTIAL_PROGRESS_PRESERVED / PROVIDER_BLOCKED`  
**Prompt:** `XMA-CLI-001-PRM-0020 B04-INCREMENTAL-IPC-RECOVERY v0.1.0`

## Baseline y publicación funcional

- Baseline: `027cafb28455cb5fa82fe167f1a4a2c2c4d2ead0`.
- Tree baseline: `77bfc4811e850cf3abe26d37bc07d1b44cf29744`.
- Rama: `feature/xma-b04-download-slice`; PR #4 abierto, draft y sin merge.
- Commit funcional: `49b0b68aef3d895f2ff28472e92428401a0aef6d`.
- CI funcional: run `40831328407`, `SUCCESS`, antes del acceso público.
- El commit documental que contiene este handoff se publica después de la aceptación y recibe CI
  sobre su mismo tree.

## Cambio IPC y evidencia offline

Queue fue sustituida por `multiprocessing.Pipe(duplex=False)`. Padre e hijo cierran inmediatamente
el extremo no usado; `Connection.send` serializa síncronamente; el padre usa `poll` con deadline y
clasifica timeout vivo, agotamiento limpio, falla de worker, falla de serialización y EOF sin
terminal. `terminate`, kill de respaldo y join ocurren en `finally`.

Los mensajes v1 contienen únicamente primitivas finitas: telemetría constante con contadores,
candidato con perfil/post seleccionados y terminal. `datetime` se convierte a ISO-8601 antes de
enviar; campos adicionales no serializables se ignoran; campos requeridos inválidos fallan sin
publicar tipo, representación o contenido. La URL fuente existe solo en memoria del flujo.

La suite reprodujo candidatos enviados antes de `COMPLETED`, StopExtraction esperado, duplicados,
EOF, timeout, terminales, cierre de extremos y terminación del worker. No reprodujo pérdida por el
feeder de Queue: esa explicación queda descartada como causa demostrada y conservada solo como
inferencia histórica plausible.

## Matriz pública sanitizada

Se reutilizó exclusivamente la copia incremental local; el repositorio original límite 1 no se
abrió ni modificó. Se ejecutó una sola vez Reuters `--limit 2`, Firefox `<LOCAL_PROFILE>`, dos
workers internos máximos de 30 s. No hubo retry manual.

| Petición | Eventos observados | Candidatos | Terminal |
|---|---|---:|---|
| 1/2 | `WORKER_STARTED`, `AUTH_LOADED`, `EXTRACTOR_STARTED` | 0 | `PROVIDER_TIMEOUT` |
| 2/2 | `WORKER_STARTED`, `AUTH_LOADED`, `EXTRACTOR_STARTED` | 0 | `PROVIDER_TIMEOUT` |

Resultado del comando: código 8. No aparecieron `PROFILE_SEEN`, `VIDEO_SEEN`,
`DUPLICATE_SKIPPED` ni `CANDIDATE_SENT`. Esta es una observación pública; no demuestra una causa
interna del proveedor. Como el total no alcanzó dos, límite 5 no se ejecutó.

## Conteos e integridad

- Antes/después: `1 → 1`; `complete=false`; cero descargas nuevas.
- Un video, un sidecar, un artifact, un job `COMPLETED` y una identidad distinta.
- `PRAGMA integrity_check = ok`; SHA-256 y tamaño del video existente siguen respaldados por el
  catálogo.
- Cero `.part`, `.tmp`, cookies o URL firmada persistida.
- El paquete permanece fuera de Git bajo `<LOCAL_RESUME_ROOT>`.

## Validaciones

| Comando | Resultado |
|---|---|
| `uv sync --locked --all-groups` | PASS |
| `uv run ruff format --check .` | PASS, 107 archivos |
| `uv run ruff check .` | PASS |
| `uv run mypy` | PASS, 38 archivos fuente |
| `uv run pytest` | PASS, 287 pruebas |
| cobertura local | PASS, 90.30 % |
| `uv build` | PASS, sdist y wheel |
| `git diff --check` | PASS |
| `uv.lock` byte-idéntico | PASS (`847ee02394976ad7a72b906e0e3bb994b2061307`) |
| archivos prohibidos rastreados | cero nuevos |

## Riesgo, rollback y siguiente decisión

La frontera IPC queda verificable y sanitizada, pero el proveedor no produjo perfil o candidato en
la ventana autorizada. El progreso válido no se perdió. Rollback: revertir los commits PRM-0020;
no reescribir historia ni borrar evidencia local. Cualquier nueva prueba pública o ampliación exige
otra decisión humana.

No hubo exportación de cookies, dot, merge, tag, release, B05 ni descarga masiva.
