# Changelog

## Unreleased

- Añade el corte vertical B04 `xma download` para lotes de 1–5 activos.
- Incorpora staging `.part`, movimiento atómico, SHA-256, sidecars, manifest e idempotencia.
- Permite autenticación Firefox o archivo Netscape local mutuamente excluyentes.
- Registra GOV-DEC-0020 y la deuda técnica de operación masiva para v2.
- Registra HND-0004 y el bloqueo público: Reuters límite 1 terminó con código 8, sin retry ni
  ejecución de los límites 2/5.
- Clasifica fallos públicos como timeout, conexión, HTTP 502/503, rate limit, restricción o contrato
  sin exponer datos crudos; PRM-0017 recuperó límite 1 y se bloqueó en límite 2 por timeout.
- Añade watchdog Linux de discovery completo, `--discovery-timeout` 5–180 s y timeout HTTP alineado;
  PRM-0018 siguió bloqueado en Reuters límite 2 sin residuos ni ejecución de límite 5.
- Cambia download a semántica acumulada e incremental, worker terminable, dos peticiones acotadas y
  reanudación; PRM-0019 preservó el lote inicial pero no descubrió un segundo activo.
- Sustituye la Queue incremental por Pipe síncrono, DTO primitivo versionado, terminales explícitos y
  telemetría sanitizada; PRM-0020 preservó el activo inicial y quedó bloqueado por timeout externo.
- Registra la aceptación alternativa BBCWorld de PRM-0021: dos workers sin candidatos, total 0 y
  `PROVIDER_BLOCKED`; límite 5 no ejecutado y sin cambios funcionales.
- Cambia el worker incremental de `fork` a `spawn` tras una paridad principal exitosa; BBCWorld
  alcanzó dos activos y preservó cuatro al bloquearse la ampliación a cinco.
- Añade descarga acotada por URL canónica de un estado mediante target `SINGLE_POST`, con validación
  fail-closed de post/autor y eliminación de query; la aceptación PRM-0023 quedó `REWORK_REQUIRED`.
- Registra la repetición pública PRM-0024 con arnés corregido: el post exacto terminó
  `PROVIDER_EXHAUSTED` sin video, persistencia o residuos (`SINGLE_POST_NO_VIDEO`).
- Corrige la paridad SINGLE_POST del adaptador principal y valida un `inspect` seguido de una
  descarga exacta con integridad completa (`SINGLE_POST_DOWNLOAD_VALIDATED`).
- Evita clasificar como `WORKER_FAILED` el EOF/terminal posterior al último candidato válido y
  valida la reanudación BBCWorld `4 → 5` sin sobrescribir progreso.
- Cierra formalmente B04 como `VALIDATED_WITH_OBSERVATIONS`, conservando como límites la ausencia
  de operación masiva, paginación eficiente, scheduler, release y certificación.
- Añade B05 con `archive`, `status`, SQLite v2, checkpoints, lock local y `RESCAN_DEDUP_V1`. La
  aceptación única sobre cinco activos expuso una inicialización incorrecta del total y terminó
  código 9 sin redescarga ni pérdida; B05 queda `REWORK_REQUIRED`.

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
