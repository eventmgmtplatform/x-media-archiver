# Changelog

## [Unreleased]

### Added

- Baseline de arquitectura `XMA-CLI-001`.
- ADR-0001 para CLI local y monolito modular hexagonal.
- Plan incremental B00–B07 y gates Q0–Q6.
- Gobierno inicial de Git, releases y prompt PRM-0001.
- Scaffold Python instalable con comandos `xma --help` y `xma version`.
- Pruebas unitarias, Ruff, mypy, pre-commit y workflow de CI.
- Prompts gobernados de ejecución Codex y auditoría dot para B02.
- Entidades y validadores de dominio para perfiles, publicaciones, medios, ejecuciones, trabajos y
  artefactos.
- Contratos tipados de catálogo, unidad de trabajo y reloj.
- Catálogo SQLite v1 con migración monotónica, integridad referencial, transacciones e idempotencia.
- Matriz documentada y probada de transiciones de trabajos de descarga.
- Auditoría y cierre humano Q2 en el commit `b2bdca7`.
- Prompts gobernados de ejecución y auditoría para B03 discovery.
- Registro versionado de gates, autorizaciones, alertas y rework.

### Known Limitations

- B02 no incluye discovery, acceso a X ni descarga de medios.
- La arquitectura sigue en validación incremental y el producto no está certificado.
