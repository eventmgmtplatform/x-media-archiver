# XMA-CLI-001-PRM-0002 — B02 Domain, Contracts and Catalog

**Versión:** 0.1.0

**Estado:** APPROVED FOR ONE EXECUTION

**Ejecutor:** Codex localhost

**Repositorio:** `https://github.com/eventmgmtplatform/x-media-archiver.git`

**Baseline obligatoria:** `main` en `2acb88cb1644facc98f5e64253650a57df579e78`

**Rama de trabajo:** `feature/xma-b02-contracts`

## 1. Objetivo

Construir el núcleo determinista de dominio y persistencia de X Media Archiver: entidades, value objects, estados, puertos, esquema SQLite versionado y repositorios. B02 no accede a X ni descarga medios.

## 2. Resultado esperado

Una biblioteca interna tipada y probada que permita registrar perfiles, publicaciones, activos multimedia, ejecuciones de descubrimiento, trabajos de descarga y artefactos; garantice idempotencia y transiciones válidas; y persista todo en SQLite mediante migraciones reproducibles.

## 3. Precondiciones

1. Clonar o actualizar el repositorio remoto.
2. Verificar que `main` apunta exactamente a la baseline indicada.
3. Ejecutar `git status --short`; detenerse si existe trabajo ajeno.
4. Crear o reutilizar únicamente `feature/xma-b02-contracts` desde esa baseline.
5. Ejecutar la suite B01 antes de modificar; debe resultar PASS.
6. No usar cuentas, cookies, tokens ni tráfico real hacia X.

Si cualquier precondición falla, producir handoff `BLOCKED` y detenerse.

## 4. Alcance obligatorio

### 4.1 Dominio

Crear módulos equivalentes a:

```text
src/xma/domain/
  models.py
  enums.py
  errors.py
  ports.py
  identity.py
```

Modelar como mínimo:

- `Profile`: ID estable de X, handle observado, nombre y timestamps.
- `Post`: ID de X, perfil autor, URL canónica, texto, fecha y tipo.
- `MediaAsset`: identidad compuesta, índice, tipo, duración, dimensiones y variantes.
- `DiscoveryRun`: run ID, estrategia, inicio/fin, cursor, conteos y estado.
- `DownloadJob`: estado, intentos, error normalizado y timestamps.
- `Artifact`: ruta relativa, MIME, tamaño, SHA-256 y fecha.

Estados mínimos:

`DISCOVERED`, `QUEUED`, `DOWNLOADING`, `COMPLETED`, `FAILED_RETRYABLE`, `FAILED_FINAL`, `SKIPPED_DUPLICATE`, `RESTRICTED`.

Requisitos:

- dataclasses inmutables cuando sea razonable;
- timestamps conscientes de zona y normalizados a UTC;
- validación explícita de IDs, handles, índices, tamaños, hashes y rutas relativas;
- sin dependencias de `gallery-dl`, `yt-dlp`, Rich, Typer o SQLite dentro del dominio;
- errores propios, pequeños y accionables.

### 4.2 Puertos

Definir `Protocol` tipados para:

- `CatalogRepository`;
- `UnitOfWork` o límite transaccional equivalente;
- reloj inyectable si los tests lo requieren.

Los puertos describen operaciones necesarias, no una copia de SQL ni futuros motores todavía inexistentes.

### 4.3 Catálogo SQLite

Crear módulos equivalentes a:

```text
src/xma/adapters/catalog/
  sqlite.py
  migrations.py
  schema/
```

Requisitos:

- usar `sqlite3` de biblioteca estándar;
- activar `PRAGMA foreign_keys = ON` en cada conexión;
- transacciones explícitas y rollback ante error;
- migraciones monotónicas con tabla `schema_version`;
- constraints, claves foráneas e índices útiles;
- timestamps almacenados en formato UTC estable;
- ninguna interpolación de valores en SQL;
- SQLite temporal o en memoria para tests;
- cerrar conexiones de forma determinista.

### 4.4 Idempotencia e invariantes

- Un perfil lógico por ID estable de X; el handle puede cambiar.
- Un post por `post_id`.
- Un activo por identidad compuesta documentada, como `post_id + media_index`.
- Un artefacto no puede usar rutas absolutas ni `..`.
- SHA-256 válido: 64 caracteres hexadecimales.
- Reinsertar el mismo registro no crea duplicados ni cambios espurios.
- Conflictos de identidad producen un error de dominio o persistencia explícito.
- Las transiciones de `DownloadJob` se controlan mediante una matriz documentada y probada.

## 5. Fuera de alcance — prohibiciones

- No implementar `inspect`, `sync`, `download`, `retry`, `status`, `export` ni `doctor`.
- No integrar `gallery-dl`, `yt-dlp`, FFmpeg, Twikit ni `twscrape`.
- No efectuar tráfico de red.
- No crear GUI, API web, Redis, ORM, Docker ni servicios.
- No almacenar cookies, contraseñas o secretos.
- No fusionar a `main`, crear tags, releases o modificar protección del repositorio.
- No eliminar ni reescribir handoffs o prompts publicados.
- No cambiar arquitectura o alcance sin ADR y parada para autorización.

## 6. Pruebas obligatorias

Mantener B01 verde y añadir tests para:

1. construcción válida e inválida de cada entidad;
2. timestamps UTC;
3. identidad compuesta y deduplicación;
4. matriz de transiciones de trabajos;
5. migración desde base vacía y reaplicación idempotente;
6. integridad referencial y rollback;
7. CRUD mínimo de cada agregado requerido;
8. actualización de handle preservando identidad;
9. rechazo de rutas inseguras y hashes inválidos;
10. persistencia entre reaperturas de un archivo SQLite temporal.

Objetivo: cobertura total >= 90 %, y 100 % en validadores de invariantes y transiciones.

## 7. Validaciones de cierre

Ejecutar y registrar:

```bash
uv sync --locked --all-groups
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest
uv build
git diff --check
git status --short
```

Revisar además que no existan bases SQLite, descargas, cookies, secretos ni artefactos de build rastreados por Git.

## 8. Entregables

- código de dominio, puertos y adaptador SQLite;
- migración inicial y documentación del esquema;
- tests y fixtures sin red;
- actualización de README y CHANGELOG;
- ADR nuevo solo si surge una decisión no cubierta;
- commits Conventional Commits pequeños y trazables;
- handoff `docs/handoffs/XMA-CLI-001_HND-0002_<RUN-ID>_v0.1.0.md`.

## 9. Contrato del handoff

El handoff debe incluir:

- baseline, rama, commits y tree SHA;
- archivos creados/modificados;
- esquema y versión de migración;
- invariantes implementadas;
- comandos y resultados completos resumidos;
- cobertura;
- defectos encontrados y correcciones;
- riesgos, pendientes y rollback;
- confirmación explícita de que no hubo red hacia X;
- estado final `WAITING_VALIDATION`, `BLOCKED` o `FAILED`.

## 10. Condición de parada

Detenerse después de commit y handoff. No publicar PR si el remoto no está autorizado/configurado; si está disponible, publicar la rama y abrir PR sin fusionarlo. No comenzar B03.
