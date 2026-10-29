# XMA-CLI-001 — HND-0005 B05 Durable Archive Slice v0.1.2

**Fecha:** 2026-10-29  
**Estado:** `B05_LIMIT_10_VALIDATED / WAITING_CHAT_VALIDATION`  
**Autoridad:** `XMA-CLI-001-PRM-0029 B05-DURABLE-EXISTING-BEFORE-REPAIR v0.1.0`

## Baseline y causa

- Baseline: `8aa6e319677d8f8a9fa20d8634226825b7fa16b8`, tree
  `8643e313a190d1cd4afde9f855a225f058c47a4f`.
- CI baseline: [40894341159](https://github.com/eventmgmtplatform/x-media-archiver/actions/runs/40894341159),
  `SUCCESS`, 340 pruebas, 90.71 %.
- Handoff precedente: HND-0005 v0.1.1, `REWORK_REQUIRED`.

PRM-0028 completó `5 → 7 → 9 → 10`; el resultado inmediato contenía `existing_before=5`, pero
`SQLiteArchiveStore.put()` omitía esa columna en `ON CONFLICT DO UPDATE`, por lo que status retenía
el cero histórico.

## Corrección y regresión

Se añadió únicamente `existing_before=excluded.existing_before` al UPSERT. La regresión inserta
cero, escribe cinco sobre el mismo run y comprueba run/created_at estables, total 10, página 3,
estado `COMPLETED` y checkpoint 10/3. Un trigger sintético fuerza fallo en la segunda escritura y
demuestra rollback completo.

- Commit funcional: `98d7d6d20af15a954122e82821c2b23574392299`.
- Tree funcional: `2dad810a391e2eee566b4c8c0dc948adf7d523b9`.
- Archivos: `src/xma/adapters/archive.py`, `tests/application/test_archive_service.py`.
- CI funcional: [40903082249](https://github.com/eventmgmtplatform/x-media-archiver/actions/runs/40903082249),
  `SUCCESS`, 341 pruebas, cobertura 90.71 %.

## Reparación transaccional local

Precondición offline: estado `COMPLETED`, solicitado 10, `existing_before=0`, total 10, página 3,
remaining 0, checkpoint 10/3, diez artifacts/jobs/sidecars/identidades, integridad `ok`, hashes y
tamaños válidos, cero residuos.

La única transacción condicionada cambió exclusivamente `existing_before: 0 → 5`. Preservó run,
created/completed timestamps, estado, total, página, checkpoint, artifacts, manifest y archivos.

- SHA-256 catálogo previo: `8ad1e17a82ae75832911b2f45ce67572eecefbad087d8576eb80f54943631bae`.
- SHA-256 catálogo posterior: `b64d64617efa0ada39f4ae5da48e432b93e30860f4a530139baac2d74d72af31`.
- Status posterior: `existing_before=5`, total 10, remaining 0, página 3, `COMPLETED`, complete true.
- Checkpoint: known identity 10, página 3; `PRAGMA integrity_check=ok`.
- Los diez hashes multimedia publicados en HND v0.1.1 permanecieron idénticos.
- Cero `.part`/`.tmp`; lock liberado; no se modificaron medios, sidecars o manifest.

## Validación

| Comando | Resultado |
|---|---|
| `uv sync --locked --all-groups` | PASS |
| `ruff format --check` | PASS |
| `ruff check` | PASS |
| `mypy` | PASS |
| `pytest` | 341 PASS |
| cobertura local | 90.33 % |
| `uv build` | PASS |
| `git diff --check` | PASS |
| `uv.lock` | byte-idéntico; `7a7e7215a354abefde9351de1691a651ea6c37fcc7f9326125642068433c0788` |

No se rastrearon SQLite, medios, manifests privados, logs o cookies. No hubo acceso a X ni ejecución
de `archive`, `download`, `inspect` o `sync`.

## Decisión de versión y rollback

B05 actual admite como máximo diez videos y `RESCAN_DEDUP_V1` es suficiente para ese corte. No se
afirma soporte para cientos o miles. Cursor remoto, scheduler, automatización masiva y optimización
de escala quedan en backlog posterior.

Rollback de código: revertir el commit funcional. La reparación local puede revertirse únicamente
mediante una transacción gobernada que restaure el catálogo previo; no se borra evidencia. No hubo
dot, merge, tag, release ni elevación del límite.
