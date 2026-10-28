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

### Fixed

- Validación de rutas de artefacto para rechazar el directorio actual `.`.
- Actualizaciones controladas del progreso y cierre de `DiscoveryRun`, preservando identidad,
  conteos monotónicos e inmutabilidad terminal.
- Cierre de la conexión SQLite cuando falla la entrada a una unidad de trabajo.
- Validación completa de la identidad compuesta de activos en `DownloadJob`.
- Timestamp UTC real y testeable para la aplicación de migraciones.

### Known Limitations

- B02 no incluye discovery, acceso a X ni descarga de medios.
- La arquitectura sigue en validación incremental y el producto no está certificado.
