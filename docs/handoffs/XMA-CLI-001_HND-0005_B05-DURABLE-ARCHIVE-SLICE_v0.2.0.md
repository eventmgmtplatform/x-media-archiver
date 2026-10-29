# XMA-CLI-001 — HND-0005 B05 Durable Archive Slice v0.2.0

**Fecha:** 2026-10-29  
**Estado:** `OFFLINE_DEPENDENCY_CACHE_UNAVAILABLE`  
**Gate B05:** `VALIDATED_WITH_OBSERVATIONS`  
**Autoridad:** `XMA-CLI-001-PRM-0030 B05-LOCAL-OPERABILITY-CLOSURE v0.1.0`

## Baseline y decisión

- Baseline: `5416fc0841702fe44a5e9a0b793a4d67fa77b979`, tree
  `23f8e18710cbf72b040f24bc5bdaf876d15592d5`.
- CI baseline: [40903392681](https://github.com/eventmgmtplatform/x-media-archiver/actions/runs/40903392681),
  `SUCCESS`, 341 pruebas, 90.71 %.
- PR #5 permaneció abierto, draft y apilado sobre B04.
- Leonel cierra B05 como `VALIDATED_WITH_OBSERVATIONS`, con máximo diez.

El runbook `docs/operations/XMA-CLI-001_LOCAL-CLI-RUNBOOK_v0.1.0.md` documenta preparación,
download 1/2/5, archive 10, SINGLE_POST, status offline, reanudación, códigos, estructura,
integridad, respaldo, diagnóstico, limpieza y seguridad.

## Matriz offline

| Interfaz | Evidencia sintética/offline |
|---|---|
| download 1 | PASS, un artifact sintético |
| download 2 | PASS, dos artifacts sintéticos |
| download 5 | PASS, cinco artifacts sintéticos |
| archive 10 | PASS, `COMPLETED`, checkpoint reproducible |
| SINGLE_POST | PASS, URL canónica y un artifact sintético |
| status | PASS, salida humana/JSON sin red |
| reanudación | PASS, artifacts íntegros no sobrescritos |

La suite usa filesystem/SQLite/proveedores/bytes sintéticos; no abre Firefox, no usa cookies reales
y no accede a red.

## Paquete local

- Versión: `0.1.0.dev0`; Python requerido: `>=3.11`.
- Entry point: `xma = xma.cli:app`.
- Wheel: `x_media_archiver-0.1.0.dev0-py3-none-any.whl`, 51,866 bytes,
  SHA-256 `7426b535ed235225d53d46d43df8e33fa24020bc85fdef35bb31b6bbd53ab9f6`.
- sdist: `x_media_archiver-0.1.0.dev0.tar.gz`, 269,762 bytes,
  SHA-256 `b550f7ffb0ec5989b870f530461688b002fa6c8072582ce6a8b275c6243ec975`.

El wheel contiene módulos XMA, esquemas SQLite y metadata/entry point. No contiene cookies,
catálogos locales, manifests privados, medios, logs, rutas personales, `.part` o `.tmp`. El sdist
añade fuentes, documentación, configuración y fixtures exclusivamente sintéticos. Ningún artifact
de `dist/` se rastrea o publica.

## Instalación aislada

La verificación obligatoria Python 3.12 no pudo crear el entorno en modo offline: el intérprete
3.12 no está instalado ni disponible en la caché administrada. Una comprobación suplementaria con
Python 3.14 tampoco pudo resolver `gallery-dl` desde la caché local. No se habilitó red, no se
modificaron dependencias y no se presenta esa comprobación como PASS. Clasificación:
`OFFLINE_DEPENDENCY_CACHE_UNAVAILABLE`.

## Validación y límites

- CLI del entorno de desarrollo: help/version y help de inspect/sync/download/archive/status PASS.
- Suite: 341 PASS; cobertura local 90.33 %, CI baseline 90.71 %.
- Ruff, mypy, build y `git diff --check`: PASS; `uv.lock` byte-idéntico.
- No hubo acceso a X, descargas, Firefox, cookies ni cambios funcionales.

B05 admite hasta diez. `RESCAN_DEDUP_V1` es adecuado para este corte, no para soporte masivo
certificado. Cientos/miles, cursor remoto, scheduler, automatización desatendida, optimización de
escala, tag y release quedan diferidos.

Rollback documental: revertir el commit de cierre; no altera código funcional ni repositorios
locales. Para completar la comprobación de instalación se requiere disponer previamente, sin
cambiar dependencias, de Python 3.12 y todas las ruedas bloqueadas en una caché offline confiable.
