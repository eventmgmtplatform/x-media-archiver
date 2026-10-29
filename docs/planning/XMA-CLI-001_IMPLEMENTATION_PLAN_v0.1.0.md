# XMA-CLI-001 — Plan de implementación

**Versión:** 0.1.0  
**Estado:** ACTIVE / Q2 CLOSED / B03-AUTH-BOUNDARY REWORK_COMPLETED / WAITING_VALIDATION
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
| B03 | Discovery | adapter gallery-dl, inspect/sync, fixtures, cobertura | Q3-Técnico: implementación auditada; Q3-Público: exactamente 2 activos públicos distintos catalogados con `--limit 2` antes de B04; 0 o 1 no pasan |
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

B03-AUTH-BOUNDARY-REWORK-001 queda `REWORK_COMPLETED / WAITING_VALIDATION` bajo PRM-0010 y
HND-0003 v0.2.1. PRM-0009 se consumió una vez y no se repitió el smoke ni se accedió a X. La
evidencia SQLite original no estaba disponible de forma inequívoca; no se reconstruyó.

El modo anónimo continúa por defecto. La lectura autenticada es infraestructura local, contenida,
solo lectura y limitada a X; no almacena, exporta, copia, imprime ni versiona cookies o
credenciales. CI continúa completamente offline.

Q3-Público permanece `BLOCKED` hasta auditoría y decisión humana. La siguiente acción es que dot
ejecute DOT-PRM-0012 sobre el HEAD final. Siguen prohibidos merge, B04, descargas, otros
extractores, API X, tags, releases y certificación.

El rework B02 permanece separado y no integrado.
