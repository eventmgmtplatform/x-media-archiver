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
- Contrato de discovery independiente del proveedor y adaptador `gallery-dl` sin descarga.
- Casos de uso y comandos `inspect` y `sync`, con JSON seguro, dry-run y códigos de salida.
- Fixtures offline, pruebas de mapeo y sincronización idempotente para B03.

### Changed

- B03 `REWORK_REQUIRED`: JSON crudo, errores normalizados y códigos 6–8, defensa de target/límite.
- Persistencia B03 de variantes como `metadata-only`, con regresión de firmas rotadas.
- Rework B02 separado, no integrado; aceptación pública y nueva auditoría B03 pendientes.
- B03-REWORK-002 normaliza metadatos numéricos inválidos como error de contrato sanitizado y
  difiere la creación del catálogo hasta después de discovery.
- B03-REWORK-003 rechaza duraciones negativas antes de redondear, incluidas cadenas con magnitud
  subnormal, y conserva el redondeo histórico de cero y duraciones positivas submilisegundo.
- B03-REWORK-004 restaura exactamente el redondeo positivo histórico después de validar el signo,
  sin retirar las regresiones de duraciones negativas ni alterar los límites SQLite.
- B03-REWORK-005 elimina el límite decimal de exponente mediante validación léxica del significando,
  preservando cadenas compatibles con `float()` y el rechazo de negativos que subdesbordan.

### Known Limitations

- B02 no incluye discovery, acceso a X ni descarga de medios.
- El smoke B03 anónimo está bloqueado por `AuthRequired` de X en Reuters, AP y BBCWorld.
- La arquitectura sigue en validación incremental y el producto no está certificado.
