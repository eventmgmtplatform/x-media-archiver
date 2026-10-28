# XMA-CLI-001 — Plan de implementación

**Versión:** 0.1.0  
**Estado:** ACTIVE / Q2 CLOSED / B03-REWORK-002 WAITING VALIDATION
**Método:** Engineering OS + Scrum/Accelerate proporcional al riesgo

## Objetivo de entrega

Producir `xma` v0.1.0 capaz de inspeccionar un perfil público, catalogar videos disponibles y descargarlos con documentación normalizada, reanudación e idempotencia.

## Roles y fuente de verdad

- Leonel: Product Owner y human gate; autoriza transiciones y releases.
- ChatGPT/dot: Solution Architect, Scrum Master y DevOps Accelerate; gobierna alcance, arquitectura, DoD, prompts y validación.
- Codex: Engineering execution; modifica código, prueba y produce handoff.
- Git: verdad de código, cambios y releases.
- CI: verdad de verificaciones automatizadas.
- Biblioteca: verdad canónica de prompts, planes y PKC.

## Backlog por gates

| Bloque | Resultado | Actividades | Gate/DoD |
|---|---|---|---|
| B00 | Baseline de diseño | arquitectura, ADR, plan, gobierno | Q0 aprobado |
| B01 | Foundation | repositorio, `pyproject`, layout, CLI `--help`, lint/test/CI | Q1: build y tests PASS |
| B02 | Contratos | entidades, schemas, puertos, migración SQLite inicial | Q2: contract tests PASS |
| B03 | Discovery | adapter gallery-dl, inspect/sync, fixtures, cobertura | Q3: perfil controlado catalogado |
| B04 | Download | yt-dlp, FFmpeg, staging, hash, sidecars | Q4: descarga reproducible PASS |
| B05 | Operación CLI | selección, progreso, retry, status, export, doctor | Q5 funcional PASS |
| B06 | Hardening | errores, seguridad, secret scan, rollback, docs | Q5 seguridad PASS |
| B07 | Release | package, changelog, SBOM/provenance cuando aplique | Q6 y `v0.1.0` aprobada |

Cada bloque contiene de 3 a 6 validaciones, se ejecuta en una rama aislada y termina con handoff. No se inicia el siguiente bloque por iniciativa de Codex.

## Métricas Accelerate adaptadas

- Lead time: autorización de bloque a handoff validable.
- Deployment/release frequency: releases certificadas, no número de commits.
- Change failure rate: bloques reabiertos o revertidos / bloques cerrados.
- Mean time to recovery: detección de regresión a restauración de baseline verde.
- Flow efficiency: tiempo activo / tiempo total del bloque.
- Desviación: actividades fuera del alcance aprobado / actividades ejecutadas; objetivo `0`.

No se fijan estimaciones de calendario sin medir B01 y B02. Se usarán tamaños `S/M/L`, dependencias y evidencia de ciclo real.

## Definition of Done común

1. Alcance aprobado y sin cambios laterales.
2. Branch y commits identificados.
3. Tests requeridos PASS; resultados negativos documentados.
4. No secretos, binarios descargados ni repositorio audiovisual en Git.
5. Evidencia y handoff Markdown trazables.
6. README, CHANGELOG y decisiones actualizados.
7. Rollback o reversión definida.
8. ChatGPT valida; Leonel autoriza transición.

## Siguiente paso autorizado

Ejecutar exclusivamente `XMA-CLI-001-DOT-PRM-0005 v0.1.0` para auditar B03-REWORK-002. El smoke
anónimo conserva el bloqueo `AuthRequired`; no se autorizan cookies, otro extractor ni B04.

B03-REWORK-001 aplicó las correcciones autorizadas por PRM-0004; B03-REWORK-002 aplica únicamente
RW-01/R-05 de AUD-0003 v0.1.1. El rework B02 permanece separado y no integrado. Q3 espera la
auditoría del nuevo snapshot; el ejecutor entrega `WAITING_VALIDATION` con evidencia.
Los recordatorios corporativos ajenos no cambian este plan ni autorizan B04.

PRM-0005 se consumió una sola vez para cerrar RW-01/R-05. AUD-0003 v0.1.1 permanece como origen
canónico del rework; la decisión de Q3 corresponde ahora a dot mediante DOT-PRM-0005.
