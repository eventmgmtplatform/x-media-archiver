# XMA-CLI-001 — HND-0005 B05 Durable Archive Slice v0.1.1

**Fecha:** 2026-10-29  
**Estado:** `REWORK_REQUIRED`  
**Autoridad:** `XMA-CLI-001-PRM-0028 B05-EXISTING-STATE-RECONCILIATION v0.1.0`

## Baseline

- Baseline: `d49deadd429493407c46904c1e972a47445e8c35`, tree
  `b5d28f2682e73e21b10beb16cd371eb62673c7b0`.
- Funcional previo: `32aa2a6fc5ad8baa5bb531c71f176b1db10f070e`.
- CI baseline: [40843726827](https://github.com/eventmgmtplatform/x-media-archiver/actions/runs/40843726827),
  `SUCCESS`, 332 pruebas, 90.82 %.
- B04: `VALIDATED_WITH_OBSERVATIONS`; PR #5 permaneció abierto, draft y apilado.

## Causa y rework

PRM-0027 creó el run con conteo cero, calculó página absoluta 2 y dejó `RUNNING` tras el conflicto.
La regresión de PRM-0028 parte de cinco artifacts, run defectuoso y checkpoint cero; antes del
arreglo solicitaba `[2, 7, 9, 10]`. Después solicita `[7, 9, 10]`, preserva `existing_before=5`,
termina página 3 y no sobrescribe artifacts.

El rework usa `DownloadService.verified_total()` sobre catálogo/filesystem verificados y acotados
al handle. Repara un run `RUNNING` como `INTERRUPTED_PREVIOUS_RUN`, reconcilia checkpoints detrás,
rechaza checkpoints adelantados y persiste `PAUSED`/`FAILED` antes de propagar errores. Se cubrieron
errores de discovery, download, dominio, interrupción y fallo inesperado sanitizado.

- Commit funcional: `9fe73ede675b36f693546ced26845a0221230fba`.
- Tree funcional: `c09819d321c05f7834b5e2c63c90dc9e0dd38270`.
- Archivos: `src/xma/application/archive.py`, `src/xma/application/download.py`,
  `tests/application/test_archive_service.py`.
- CI funcional: [40893335540](https://github.com/eventmgmtplatform/x-media-archiver/actions/runs/40893335540),
  `SUCCESS`, 340 pruebas, cobertura 90.71 %.

## Reanudación pública única

Preflight: cinco videos, sidecars, artifacts/jobs `COMPLETED` e identidades; integridad `ok`, hashes
coherentes y cero residuos. `status` confirmó offline el run defectuoso sin modificarlo.

| Paso | Total absoluto | Resultado |
|---|---:|---|
| inicio reconciliado | 5 | cinco hashes originales verificados |
| página 1 | 7 | dos nuevos confirmados |
| página 2 | 9 | dos nuevos confirmados; cooldown aplicado |
| página 3 | 10 | un nuevo confirmado; `COMPLETED` |

El único comando terminó código 0 en 14 segundos. Resultado inmediato: `existing_before=5`,
`downloaded_total=10`, `page_number=3`, `remaining=0`, `complete=true`. No hubo retry.

Verificación final: diez videos, diez sidecars, diez artifacts/jobs `COMPLETED`, diez identidades,
checkpoint `known_identity_count=10 / last_completed_page=3`, manifest completo, integridad `ok` y
cero `.part`/`.tmp`. Los cinco hashes B04 permanecieron idénticos. Hashes nuevos permitidos:

- `0b7612da62b6c9783ec6b0accbf06169fa0eecb8108e44cff6db83713ed1acc5`
- `3b1d636c00b53f90d85d8e5a322e9e0b0feae7cec6bdd16cc67490876a6d8fea`
- `6c45e2e00effa9932fa35bfbe39e146f48ed2f24b6ae04072d6d2eb74a0c411a`
- `76540cf718f90baa47aed53efb3ddccc43165591e0e49cafc93ff23fc5992b1b`
- `df8b8cab3274414b9366c30cfc66f9ac45ea4c06b0c559ad5bb29ef1fcc70d27`

## Desviación durable

El `status` offline posterior reprodujo estado `COMPLETED`, total 10, página 3 y remaining 0, pero
leyó `existing_before=0`. El resultado inmediato sí contenía 5. Causa: el UPSERT de `archive_runs`
no actualiza `existing_before`; conservó el valor defectuoso histórico. La aceptación no cumple
todos los criterios y queda `REWORK_REQUIRED`. No se alteró retroactivamente la evidencia ni se
repitió el comando.

## Validaciones y seguridad

- Local: `uv sync`, Ruff format/check, mypy, 340 pruebas, cobertura 90.33 %, build y diff PASS.
- CI funcional: 340 pruebas, cobertura 90.71 %, build PASS.
- `uv.lock` byte-idéntico: `7a7e7215a354abefde9351de1691a651ea6c37fcc7f9326125642068433c0788`.
- Ningún medio, SQLite, manifest privado, log o cookie fue rastreado.
- No se persistieron cookies, URLs firmadas, headers, tokens, selector o rutas personales.

## Riesgo y rollback

El próximo rework debe actualizar `existing_before` de forma durable y probar la reconciliación sin
nueva red. El rollback revierte `9fe73ed`; los diez assets íntegros y tablas v2 deben conservarse.
No hubo retry, otro target/perfil, dot, merge, tag, release, límite superior a diez ni descarga
masiva.
