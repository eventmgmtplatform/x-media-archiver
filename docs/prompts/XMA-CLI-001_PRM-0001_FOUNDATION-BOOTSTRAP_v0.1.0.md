# XMA-CLI-001-PRM-0001 — Foundation Bootstrap

**Versión:** 0.1.0  
**Fase:** B01 / Foundation  
**Estado:** DRAFT — NOT AUTHORIZED FOR EXECUTION  
**Predecesor:** XMA-CLI-001 Architecture v0.1.0

## Objetivo

Crear únicamente la base reproducible del proyecto Python CLI y su CI. No implementar acceso a X, discovery, descargas, cookies ni FFmpeg.

## Precondiciones

1. Repositorio remoto y rama por defecto identificados.
2. Baseline limpia o inventario de cambios entregado.
3. Leonel autoriza este prompt y el nombre del repositorio.
4. Python objetivo confirmado por Codex desde el entorno.

## Procedimiento

1. Ejecutar discovery read-only: `pwd`, estado Git, ramas, remotos, último commit y versiones de Python/Git.
2. Detenerse si existe trabajo ajeno o una identidad remota inesperada.
3. Crear rama `feature/xma-b01-foundation` desde la baseline confirmada.
4. Crear paquete `src/xma`, comando `xma --help` y `xma version`.
5. Configurar `pyproject.toml`, pytest, Ruff, mypy y pre-commit.
6. Agregar tests sin red para help/version.
7. Agregar CI mínima y plantillas de issue/PR.
8. Actualizar README y CHANGELOG.
9. Ejecutar validaciones y registrar comandos/resultados.
10. Generar handoff; no hacer merge, tag ni release.

## Validaciones B01

- V1 instalación editable en entorno limpio: PASS.
- V2 `xma --help`: PASS.
- V3 unit tests: PASS.
- V4 format/lint/typecheck: PASS.
- V5 secret scan y verificación de archivos ignorados: PASS.
- V6 CI definida y reproducible: PASS o PENDING si todavía no se ha publicado la rama.

## Handoff

Crear `docs/handoffs/XMA-CLI-001_HND-0001_<RUN-ID>_v0.1.0.md` con baseline inicial, rama, commits, archivos, comandos, resultados, riesgos, pendientes y rollback. Finalizar en `WAITING_VALIDATION`.

## Condición de parada

Detenerse después del handoff. Queda prohibido iniciar B02, integrar motores externos, publicar o cambiar protecciones de GitHub.
