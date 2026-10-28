# XMA-CLI-001 — Catálogo SQLite v1

**Versión:** 0.1.0

**Fase:** B02

**Schema version:** 1

## Identidades y relaciones

- `profiles.profile_id`: ID estable de X. El `handle` observado es mutable.
- `posts.post_id`: ID estable de la publicación; referencia al perfil autor.
- `media_assets.asset_id`: identidad compuesta `<post_id>:<media_index>`; el par también es único.
- `discovery_runs.run_id`: identidad local de una ejecución de discovery.
- `download_jobs.job_id`: identidad local; referencia a un activo y una ejecución.
- `artifacts.artifact_id`: identidad local; referencia a un trabajo y usa una ruta relativa única.

Todos los timestamps se serializan como ISO 8601 UTC con seis dígitos de microsegundos y sufijo
`Z`. Las conexiones activan `PRAGMA foreign_keys = ON`. La tabla `schema_version` registra las
migraciones aplicadas, que se ejecutan de forma monotónica y transaccional.

## Matriz de estados de `DownloadJob`

| Origen | Destinos permitidos |
|---|---|
| `DISCOVERED` | `QUEUED`, `SKIPPED_DUPLICATE`, `RESTRICTED` |
| `QUEUED` | `DOWNLOADING`, `RESTRICTED` |
| `DOWNLOADING` | `COMPLETED`, `FAILED_RETRYABLE`, `FAILED_FINAL` |
| `FAILED_RETRYABLE` | `QUEUED`, `FAILED_FINAL` |
| `COMPLETED` | ninguno |
| `FAILED_FINAL` | ninguno |
| `SKIPPED_DUPLICATE` | ninguno |
| `RESTRICTED` | ninguno |

Los estados fallidos requieren código y mensaje normalizados. Cada transición a `DOWNLOADING`
incrementa `attempts`; cualquier transición fuera de esta matriz produce
`InvalidTransitionError`.

## Idempotencia y conflicto

Reinsertar una entidad idéntica no modifica filas. Los perfiles permiten actualizar handle,
nombre y timestamps sin cambiar `profile_id`; los trabajos permiten cambios de estado sin cambiar
su activo, ejecución o fecha de creación. Una reutilización incompatible de identidad produce
`IdentityConflictError` y la unidad de trabajo revierte la transacción.
