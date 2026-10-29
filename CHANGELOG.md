# Changelog

## Unreleased

- Añade el corte vertical B04 `xma download` para lotes de 1–5 activos.
- Incorpora staging `.part`, movimiento atómico, SHA-256, sidecars, manifest e idempotencia.
- Permite autenticación Firefox o archivo Netscape local mutuamente excluyentes.
- Registra GOV-DEC-0020 y la deuda técnica de operación masiva para v2.
- Registra HND-0004 y el bloqueo público: Reuters límite 1 terminó con código 8, sin retry ni
  ejecución de los límites 2/5.

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
- Autenticación B03 opcional mediante lectura directa de una sesión local de Firefox, sin exportar
  cookies y conservando modo anónimo por defecto.

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
- La aceptación controlada autenticada acreditó exactamente dos activos distintos sin descargar
  medios; Q3-Público queda en `WAITING_VALIDATION` hasta la auditoría independiente.

### Known Limitations

- B02 no incluye discovery, acceso a X ni descarga de medios.
- El modo anónimo permanece restringido por `AuthRequired`; la evidencia autenticada espera
  auditoría independiente y no autoriza B04.
- La arquitectura sigue en validación incremental y el producto no está certificado.
