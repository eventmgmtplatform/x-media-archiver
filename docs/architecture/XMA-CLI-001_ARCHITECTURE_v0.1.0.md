# XMA-CLI-001 — Architecture Baseline

**Versión:** 0.1.0  
**Fecha:** 2026-10-28 (America/Mexico_City)  
**Estado:** DESIGN BASELINE / IMPLEMENTATION PENDING  
**Decisión:** APPROVABLE  
**Certificación de producto:** NOT CERTIFIED

## 1. Propósito

Diseñar una aplicación CLI local, ligera y recuperable que descubra videos de perfiles públicos de X, mantenga un catálogo consultable y descargue cada publicación en un repositorio documental normalizado.

## 2. Requisitos trazables

| ID | Requisito | Componente | Evidencia futura |
|---|---|---|---|
| XMA-FR-001 | Aceptar perfil, handle o publicación | CLI | pruebas de comandos |
| XMA-FR-002 | Enumerar contenido audiovisual disponible | Discovery | fixtures y prueba controlada |
| XMA-FR-003 | Descargar lotes con progreso y reintentos | Download service | pruebas de integración |
| XMA-FR-004 | Crear repositorio normalizado | Storage | golden tree y esquema |
| XMA-FR-005 | Conservar JSON, Markdown, miniatura y URL | Documentation | validación de artefactos |
| XMA-FR-006 | Evitar duplicados y permitir reanudación | Catalog/Jobs | pruebas de idempotencia |
| XMA-NFR-001 | No guardar contraseñas ni cookies en Git | Auth boundary | secret scan |
| XMA-NFR-002 | Ser local-first y funcionar sin servidor | Runtime | smoke test CLI |
| XMA-NFR-003 | Fallar de forma segura ante cambios de X | Adapters | contract/error tests |
| XMA-NFR-004 | Trazar versión, origen, hash y estado | Evidence | manifest y SQLite |

## 3. Estilo arquitectónico

**Monolito modular CLI con arquitectura hexagonal ligera.** No se implementará MVC porque no existe una vista gráfica ni un controlador web. La CLI es un adaptador de entrada; los motores externos y el filesystem son adaptadores de salida.

```text
CLI (Typer + Rich)
  -> Application services
     -> Domain contracts
        -> Discovery adapter (gallery-dl)
        -> Download adapter (yt-dlp/ffmpeg)
        -> Catalog adapter (SQLite)
        -> Repository adapter (filesystem)
```

Regla de dependencia: `cli -> application -> domain`; `infrastructure` implementa puertos del dominio y nunca gobierna casos de uso.

## 4. Componentes

| Módulo | Responsabilidad | Dependencias permitidas |
|---|---|---|
| `cli` | comandos, preguntas, tablas y códigos de salida | application |
| `application` | orquestar inspect, sync, download, retry y export | domain ports |
| `domain` | entidades, estados, errores y contratos | biblioteca estándar |
| `adapters/discovery` | envolver `gallery-dl`; opcionalmente `twscrape` después | external tools |
| `adapters/download` | envolver API Python de `yt-dlp` y FFmpeg | yt-dlp |
| `adapters/catalog` | persistencia SQLite, migraciones y deduplicación | sqlite3 |
| `adapters/storage` | rutas seguras, escritura atómica, hashes y sidecars | filesystem |
| `observability` | logging estructurado, run ID y métricas locales | estándar |

No se copiarán extractores de terceros. Se consumirán como dependencias versionadas detrás de adaptadores reemplazables.

## 5. Comandos del MVP

```text
xma doctor
xma inspect @usuario [--limit N] [--json]
xma sync @usuario [--since DATE] [--dry-run]
xma download @usuario [--all | --select IDS] [--quality best]
xma retry [--run RUN_ID | --failed]
xma status [--run RUN_ID]
xma export @usuario --format json|csv
```

`inspect` no descarga. `sync` actualiza catálogo. `download` consume elementos catalogados. Esta separación permite revisar cobertura antes de escribir archivos grandes.

## 6. Modelo de dominio mínimo

- `Profile`: identidad estable, handle observado y fechas de sincronización.
- `Post`: ID de X, URL, autor, texto, fecha, tipo y métricas observadas.
- `MediaAsset`: ID compuesto, tipo, variantes, duración y dimensiones.
- `DownloadJob`: estado, intentos, timestamps, error normalizado y run ID.
- `Artifact`: ruta relativa, tamaño, SHA-256, MIME y fecha de creación.
- `DiscoveryRun`: estrategia, cursor, cobertura declarada y resultado.

Estados de trabajo: `DISCOVERED`, `QUEUED`, `DOWNLOADING`, `COMPLETED`, `FAILED_RETRYABLE`, `FAILED_FINAL`, `SKIPPED_DUPLICATE`, `RESTRICTED`.

## 7. Repositorio normalizado

```text
repository/
  catalog.sqlite3
  manifests/runs/<run-id>.json
  profiles/<handle>/profile.json
  profiles/<handle>/<yyyy>/<yyyy-mm-dd>_<post-id>/
    media_<index>.<ext>
    metadata.json
    ficha.md
    thumbnail.<ext>
    original.url
```

Las rutas utilizan IDs de X y no dependen exclusivamente del handle, que puede cambiar. Las escrituras se realizan a staging y se renombran atómicamente. `metadata.json` es canónico; `ficha.md` es una proyección regenerable.

## 8. Decisiones de seguridad

- Modo anónimo primero; cookies opcionales como archivo local con permisos restringidos.
- Nunca aceptar contraseña de X en argumentos ni configuración.
- Cookies, repositorio descargado y base SQLite quedan ignorados por Git.
- No intentar superar contenido privado, eliminado o controles de acceso.
- Sanitizar nombres, impedir path traversal y limitar concurrencia.
- Registrar URLs e IDs, pero nunca valores de cookies ni cabeceras sensibles.

## 9. Confiabilidad

- Idempotencia por `post_id + media_index + source_variant` y SHA-256 final.
- Reintentos acotados con backoff y clasificación retryable/final.
- Checkpoint de cursor por ejecución.
- Descarga a archivo temporal y promoción atómica.
- `doctor` valida Python, SQLite, FFmpeg, dependencias, rutas y permisos.
- La CLI nunca declara cobertura total: reporta fuente, rango y limitaciones observadas.

## 10. Límites del MVP

Fuera de alcance: GUI, servicio web, multiusuario, nube, evasión de controles, descarga de cuentas privadas, análisis ML, transcripción, búsqueda semántica y sincronización programada.

## 11. Gates de certificación

- `Q0` baseline y alcance aprobados.
- `Q1` scaffold reproducible y CI verde.
- `Q2` contratos y esquemas validados.
- `Q3` discovery con fixtures y prueba controlada.
- `Q4` descarga/normalización/idempotencia demostradas.
- `Q5` CLI E2E, seguridad y recuperación PASS.
- `Q6` release candidate reproducible y documentación completa.

Esta versión satisface únicamente el diseño de `Q0`; requiere autorización y ejecución del PRM-0001 para avanzar.
