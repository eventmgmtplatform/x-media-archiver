# XMA-CLI-001 — Plan de implementación

**Versión:** 0.1.0  
**Estado:** ACTIVE / Q2 CLOSED / Q3-TÉCNICO VALIDATED WITH OBSERVATIONS / Q3-PÚBLICO BLOCKED
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
| B03 | Discovery | adapter gallery-dl, inspect/sync, fixtures, cobertura | Q3-Técnico: implementación auditada; Q3-Público: perfil controlado con hasta dos activos catalogados antes de B04 |
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

La única transición autorizada es documental: publicar AUD-0003 v0.1.5, ADR-0002, este plan,
el Gate Register y DOT-PRM-0009 en estado inactivo. Q3-Técnico queda
`VALIDATED_WITH_OBSERVATIONS` por decisión humana posterior a la auditoría; Q3-Público permanece
`BLOCKED` porque la prueba anónima no acreditó dos activos catalogados.

DOT-PRM-0009 puede ejecutarse únicamente con una autorización humana separada. No existe prompt
de implementación para Codex: AUD-0003 v0.1.5 no identifica un defecto técnico recuperable.

La división del gate no elimina ni difiere silenciosamente la aceptación pública. Mientras
Q3-Público no pase, quedan prohibidos merge, B04, cookies, autenticación, otro extractor,
descargas, tags, releases y cualquier afirmación de certificación. Una estrategia de acceso
distinta requerirá otra decisión versionada y un alcance expresamente autorizado.

El rework B02 permanece separado y no integrado. Los recordatorios corporativos ajenos no cambian
este plan ni autorizan fases posteriores.
