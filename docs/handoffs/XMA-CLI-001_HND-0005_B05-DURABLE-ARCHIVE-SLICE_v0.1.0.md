# XMA-CLI-001 — HND-0005 B05 Durable Archive Slice v0.1.0

**Fecha:** 2026-10-29  
**Estado:** `REWORK_REQUIRED`  
**Autoridad:** `XMA-CLI-001-PRM-0027 B05-DURABLE-ARCHIVE-SLICE v0.1.0`

## Baseline y cierre B04

- Baseline B04: `a745f3ce1ea637aca04917da1a9aabb7d05414a8`, tree
  `5021335b5574a33d1fbd2e261578f9b250ddf84c`, CI #67 verde.
- Cierre: `be5b533`, HND-0004 v1.0.1, CI
  [40839678549](https://github.com/eventmgmtplatform/x-media-archiver/actions/runs/40839678549) verde.
- Gate B04: `VALIDATED_WITH_OBSERVATIONS`.
- Rama B05: `feature/xma-b05-durable-archive`; PR
  [#5](https://github.com/eventmgmtplatform/x-media-archiver/pull/5), draft y apilado sobre B04.

## Entrega B05

- Commit funcional: `32aa2a6fc5ad8baa5bb531c71f176b1db10f070e`.
- Tree funcional: `a31c909c73093b94c37fb84461243aea4ae5886f`.
- CI funcional:
  [40842011770](https://github.com/eventmgmtplatform/x-media-archiver/actions/runs/40842011770), `SUCCESS`.
- Se añadieron `archive`, `status`, `ArchiveRequest`, `ArchiveRun`, `RESCAN_DEDUP_V1`, bloqueo
  `flock`, checkpoints y migración SQLite v2.
- `status` es offline; el cooldown combina reloj monotónico y `next_allowed_at` durable. No se
  añadió dependencia ni cambió `uv.lock`.

La migración controlada pasó `PRAGMA integrity_check=ok`. Permanecieron cinco videos, sidecars,
artifacts/jobs `COMPLETED` e identidades. Los hashes permitidos permanecieron idénticos:

- `2da39c6ed2b3fa5705283d83b2188ee22ed29323fc7f54e29332a50a45b4bff3`
- `ef8200d3e53e841ad8960f98fd4d6acc6d8d973bc5abce06a7a47293ad5fb627`
- `80bcf8b5b90e09d83fe86f67ed0ad9372bd0ede25eac99abb097cc469314a997`
- `42738f6a21cbd350788689c8be2a17aee2def3e6dd0fb8dc7534c59e9cb980b3`
- `13d32def90a1d582a09cd82b00826cb576f9e283fec232f175e1d77b0bb24582`

## Aceptación pública única

El único comando autorizado `archive @BBCWorld --limit 10 --batch-size 2` terminó código `9` en
menos de un segundo, antes de discovery o descarga. No se repitió.

| Campo | Resultado |
|---|---|
| assets existentes preservados | 5 |
| nuevos descargados | 0 |
| total íntegro posterior | 5 |
| run status | `RUNNING` (defecto) |
| page number | 0 |
| checkpoint avanzado | no |
| integrity_check | `ok` |
| `.part` / `.tmp` | 0 / 0 |

Causa reproducida offline: el run inicializó `downloaded_total=0`. La primera página calculó un
total absoluto de `2`; `DownloadService` observó cinco artifacts y rechazó correctamente
`existing_before > request.limit`. El error no fue convertido a `PAUSED` o `FAILED`, por lo que
status quedó `RUNNING`. Ningún checkpoint declaró artifacts inexistentes ni se sobrescribió
evidencia.

## Validaciones

| Comando | Resultado |
|---|---|
| `uv sync --locked --all-groups` | PASS |
| `ruff format --check` | PASS, 123 archivos |
| `ruff check` | PASS |
| `mypy` | PASS, 44 archivos |
| `pytest` | PASS, 332 pruebas |
| cobertura local | 90.44 % |
| `uv build` | PASS, sdist y wheel |
| `git diff --check` | PASS |
| `uv.lock` | byte-idéntico; SHA-256 `7a7e7215a354abefde9351de1691a651ea6c37fcc7f9326125642068433c0788` |

No se rastrearon medios, SQLite, manifests privados, logs, cookies ni rutas locales. La evidencia
publicada no contiene cookie, selector, URL firmada, header ni token.

## Riesgo, rollback y siguiente decisión

`RESCAN_DEDUP_V1` es ineficiente para miles. Antes de otra aceptación se requiere un rework
gobernado que inicialice desde artifacts existentes, calcule páginas contra el total absoluto
correcto y lleve conflictos a un estado terminal sanitizado. El rollback de código revierte el
commit funcional; las tablas v2 se conservan para no borrar evidencia.

No hubo retry, cookie file/exportación, otro perfil/target, dot, merge, tag, release, elevación del
límite, descarga masiva ni segunda operación pública.
