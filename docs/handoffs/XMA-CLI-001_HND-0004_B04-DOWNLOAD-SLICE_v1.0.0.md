# XMA-CLI-001 — HND-0004 B04 Download Slice

**Versión:** 1.0.0  
**Fecha:** 2026-10-29 (America/Mexico_City)  
**Estado:** `B04_LIMIT_5_VALIDATED / WAITING_CHAT_VALIDATION`  
**Prompt:** `XMA-CLI-001-PRM-0026 B04-FIFTH-ASSET-RECOVERY v0.1.0`

## Baseline y alcance

- Baseline: `765885edf9c0a92850c788ffd9367062e243c90a`; tree `ad9f67ba518d357e5e98f4fe6881b39a8499bf61`.
- Commit funcional: `cb42abb3a7ccfe8f2854c48ee63af16a61b25b91`; tree `968c437f3e436d769aaaddc26d821b78a4820e86`.
- Rama `feature/xma-b04-download-slice`; PR #4 abierto, draft, mergeable y sin merge.
- CI baseline #65/run `40837563589`: `SUCCESS`, 306 pruebas, cobertura 90.67 %.
- CI funcional #66/run `40838827903`: `SUCCESS`, 309 pruebas, cobertura 90.68 %.
- Repositorio local original de PRM-0022 localizado inequívocamente fuera de Git y verificado antes
  de código o red: cuatro videos, sidecars, artifacts, jobs `COMPLETED` e identidades; manifest
  incompleto `total_after=4`; `integrity_check=ok`; cero residuos.

No cambiaron autenticación, cookies, downloader, esquema, dependencias, `uv.lock`, workflows,
timeouts, spawn, Pipe síncrono, DTOs, persistencia inmediata o semántica de deduplicación.

## Causa reproducida y rework

Una prueba sintética reprodujo el defecto antes del arreglo: después de entregar el último candidato
válido solicitado, EOF/cierre del Pipe o un terminal tardío de fallo se clasificaban todavía como
`WORKER_FAILED`. La regresión falló con `invalid provider response [WORKER_FAILED]`.

El cambio mínimo cuenta únicamente batches mapeados, validados y entregados. Si esos batches
alcanzan `remaining`, EOF, muerte posterior o terminal tardío se normalizan como `COMPLETED`.
Antes del último candidato, EOF, Pipe cerrado, timeout, serialización o mapping siguen fallando
cerrados. La aplicación solo vuelve a pedir el siguiente mensaje después de persistir el candidato;
un candidato inválido o no persistido no se contabiliza como éxito.

La prueba fallida pasó después del arreglo. También pasan candidato seguido de `COMPLETED`, terminal
tardío, cierre temprano del consumidor, `StopExtraction`, timeout, join/cleanup y la secuencia
sintética exacta `4 → 5`, con una sola persistencia del quinto artifact/job.

## Reanudación pública única

- Target: `@BBCWorld`; un comando, `--limit 5`, dos workers internos acotados permitidos.
- Código de salida: 0; duración redondeada: 3 s.
- `existing_before=4`, `downloaded_this_run=1`, `total_after=5`, `complete=true`.
- Cinco videos `.mp4`, cinco sidecars, artifacts, jobs `COMPLETED` e identidades distintas.
- `PRAGMA integrity_check=ok`; hashes y tamaños coinciden entre archivos, sidecars, manifest y SQLite.
- Los cuatro hashes originales permanecen idénticos:
  - `ef8200d3e53e841ad8960f98fd4d6acc6d8d973bc5abce06a7a47293ad5fb627`
  - `80bcf8b5b90e09d83fe86f67ed0ad9372bd0ede25eac99abb097cc469314a997`
  - `42738f6a21cbd350788689c8be2a17aee2def3e6dd0fb8dc7534c59e9cb980b3`
  - `13d32def90a1d582a09cd82b00826cb576f9e283fec232f175e1d77b0bb24582`
- Quinto video: `2da39c6ed2b3fa5705283d83b2188ee22ed29323fc7f54e29332a50a45b4bff3`.
- SQLite final: `08fd8398d9c76eac88b47d38e2ec48095005166df56511012597b4c99b928140`.
- Manifest final: `d90e9749038be53eb83b4725083e9a37acb8adad38e9faa8b41c85581c81c42d`.
- `.part`/`.tmp`: cero; no se sobrescribieron los cuatro activos anteriores.
- Cookies, URL firmada, token, header, selector o ruta personal persistidos: cero.

Repositorio y logs permanecen exclusivamente locales y fuera de Git.

## Validaciones offline finales

| Comando | Resultado |
|---|---|
| `uv sync --locked --all-groups` | PASS |
| `uv run ruff format --check .` | PASS, 113 archivos |
| `uv run ruff check .` | PASS |
| `uv run mypy` | PASS, 38 archivos fuente |
| `uv run pytest` | PASS, 309 pruebas |
| cobertura local | PASS, 90.33 % |
| `uv build` | PASS, sdist y wheel |
| `git diff --check` | PASS |
| `uv.lock` byte-idéntico | PASS (`847ee02394976ad7a72b906e0e3bb994b2061307`) |
| evidencia privada/prohibida rastreada | cero |

## Riesgo y rollback

La aceptación valida el total incremental cinco para BBCWorld en este repositorio local; no
autoriza descarga masiva, otro target, merge ni B05. El gate final corresponde a Leonel.

Rollback: revertir `cb42abb`. Esto restaura la clasificación anterior de EOF/terminal posterior al
candidato sin tocar esquema o evidencia local. Los medios y catálogos no forman parte de Git.

No hubo retry manual, cookie file, exportación de cookies, otro perfil/target, inspect, gallery-dl
directo, curl, wget, dot, merge, tag, release, B05 o descarga masiva.
