# X Media Archiver CLI

CLI local para descubrir el contenido audiovisual público de un perfil de X, catalogarlo y descargarlo en un repositorio normalizado con metadatos y evidencia de integridad.

## Estado

- Workstream: `XMA-CLI-001`
- Madurez: `DESIGN`
- Baseline de arquitectura: `v0.1.0`
- Implementación: `B02 VALIDATED / B03 EVIDENCE GOVERNED / B04 VALIDATED_WITH_OBSERVATIONS / B05 REWORK_REQUIRED`
- Certificación de producto: `NOT CERTIFIED`

## Objetivo del MVP

1. Recibir un `@usuario`, URL de perfil o URL de publicación.
2. Descubrir publicaciones con video, GIF animado, broadcast o Space soportado.
3. Presentar un resumen y permitir descarga masiva desde la terminal.
4. Descargar mediante `yt-dlp` y `ffmpeg`.
5. Crear una carpeta normalizada por publicación con video, `metadata.json`, `ficha.md`, miniatura y URL original.
6. Registrar catálogo, progreso, errores y deduplicación en SQLite.
7. Reanudar ejecuciones y sincronizar solamente contenido nuevo.

## Documentación

- [Arquitectura](docs/architecture/XMA-CLI-001_ARCHITECTURE_v0.1.0.md)
- [ADR-0001](docs/adr/ADR-0001-cli-modular-monolith.md)
- [Plan de actividades](docs/planning/XMA-CLI-001_IMPLEMENTATION_PLAN_v0.1.0.md)
- [Gobierno Git y releases](docs/governance/XMA-CLI-001_GIT_RELEASE_GOVERNANCE_v0.1.0.md)
- [Prompt inicial de Codex](docs/prompts/XMA-CLI-001_PRM-0001_FOUNDATION-BOOTSTRAP_v0.1.0.md)
- [Catálogo SQLite v1](docs/architecture/XMA-CLI-001_CATALOG-SCHEMA_v0.1.0.md)
- [Gate register](docs/governance/XMA-CLI-001_GATE-REGISTER_v0.1.0.md)
- [AUD-0005 v0.1.2](docs/audits/XMA-CLI-001_AUD-0005_B03-AUTH-BOUNDARY-REWORK-002_v0.1.2.md)
- [PRM-0012 — recuperación de evidencia A-06](docs/prompts/XMA-CLI-001_PRM-0012_A06-PUBLIC-EVIDENCE-RECOVERY_v0.1.0.md)
- [DOT-PRM-0014 — auditoría de evidencia A-06](docs/prompts/XMA-CLI-001_DOT-PRM-0014_A06-PUBLIC-EVIDENCE-AUDIT_v0.1.0.md)
- [Prompt B03 para Codex](docs/prompts/XMA-CLI-001_PRM-0003_B03-DISCOVERY_v0.1.0.md)
- [Prompt B03 para dot](docs/prompts/XMA-CLI-001_DOT-PRM-0003_B03-GOVERNANCE-AUDIT_v0.1.0.md)

## Principio de operación

`Leonel autoriza → ChatGPT diseña y gobierna → Codex ejecuta → Codex entrega handoff Markdown → ChatGPT valida → Leonel autoriza la transición`.

Codex no encadena fases ni publica releases sin un gate explícito.

## Desarrollo local

```bash
uv sync --all-groups
uv run xma --help
uv run xma version
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest
uv build
```

### Núcleo B02

`xma.domain` contiene entidades inmutables, validadores, estados y puertos sin dependencias de
CLI o persistencia. `xma.adapters.catalog` implementa el catálogo SQLite mediante una migración
monotónica, claves foráneas activas y límites transaccionales explícitos.

Los comandos de discovery no forman parte de B02 y se documentan abajo como B03. La descarga de
medios permanece reservada para bloques posteriores.

## Download B04 — corte vertical

`xma download` descarga entre uno y cinco activos a un repositorio local normalizado:

```bash
uv run xma download @Reuters --limit 1 --repository ./downloads
uv run xma download @Reuters --limit 2 --repository ./downloads \
  --auth-browser firefox --auth-profile <LOCAL_PROFILE>
uv run xma download @Reuters --limit 5 --repository ./downloads \
  --cookies-file <LOCAL_COOKIE_FILE> --json
```

Firefox y archivo de cookies son alternativas mutuamente excluyentes. La aplicación no copia,
exporta, imprime ni persiste cookies o URLs multimedia. Cada activo produce video, `metadata.json`,
registro SQLite y SHA-256; `manifests/latest.json` resume el lote. El corte no implementa retry,
paginación durable, paralelismo ni descarga masiva.

La implementación y sus pruebas offline están completas, pero la única prueba pública de límite 1
terminó con código 8 antes de crear el repositorio. PRM-0016 prohíbe reintentar y exige detener los
límites 2 y 5; HND-0004 registra el bloqueo sanitizado.

PRM-0017 añadió clasificación sanitizada del proveedor. La recuperación Firefox obtuvo exactamente
un video en el límite 1; el límite 2 terminó con código 8 y `PROVIDER_TIMEOUT`, sin residuos. Por
contrato no hubo retry, fallback de cookies ni ejecución del límite 5. HND-0004 v0.2.0 conserva la
matriz sanitizada; el gate permanece bloqueado.

PRM-0018 añadió `--discovery-timeout`: 30 s por defecto, rango 5–180 s en Linux, watchdog total y
timeout HTTP subordinado. Las ejecuciones autorizadas de límite 2 terminaron sin activos; la final
de 180 s devolvió código 8 / `PROVIDER_TIMEOUT` y cero residuos. Límite 1 no se repitió y límite 5
no se ejecutó. HND-0004 v0.3.0 mantiene B04 `BLOCKED_PUBLIC_DOWNLOAD`.

PRM-0019 cambió `--limit` a total deseado y añadió discovery incremental mediante worker Linux
terminable, hasta dos peticiones de 30 s, persistencia parcial y reanudación. La prueba reutilizó una
copia íntegra del lote límite 1; ambos workers expiraron sin candidato nuevo. El activo inicial se
conservó y HND-0004 v0.4.0 registra `PARTIAL_PROGRESS_PRESERVED / BLOCKED`.

PRM-0020 sustituyó la queue incremental por `multiprocessing.Pipe(duplex=False)`, DTOs primitivos
versionados y telemetría sanitizada. La reproducción offline no confirmó la hipótesis del feeder de
Queue. En la única aceptación Reuters límite 2, ambos workers cargaron autenticación e iniciaron el
extractor, pero no observaron perfil o video antes de `PROVIDER_TIMEOUT`; el activo inicial quedó
íntegro y límite 5 no se ejecutó. HND-0004 v0.5.0 mantiene
`PARTIAL_PROGRESS_PRESERVED / PROVIDER_BLOCKED`.

PRM-0021 probó una sola vez BBCWorld en un repositorio nuevo. Los dos workers cargaron autenticación
e iniciaron el extractor, pero no emitieron perfil, video o candidato antes de
`PROVIDER_TIMEOUT`. El manifest registra `0 → 0`, sin SQLite, medios o residuos; límite 5 no se
habilitó. HND-0004 v0.6.0 clasifica el resultado `PROVIDER_BLOCKED`.

PRM-0022 confirmó paridad en el proceso principal (`inspect`, un activo, 13 s) y sustituyó `fork`
por `spawn`. BBCWorld límite 2 pasó con dos activos íntegros; límite 5 preservó cuatro activos antes
de `WORKER_FAILED`. El cambio observable respalda `fork` como causa del bloqueo previo, pero no
explica el fallo del quinto activo. HND-0004 v0.7.0 registra
`B04_LIMIT_2_VALIDATED / LIMIT_5_BLOCKED`.

PRM-0023 añadió targets explícitos `PROFILE` y `SINGLE_POST`: las URLs HTTPS de estado admitidas se
canonicalizan sin query/fragment, el worker usa directamente el estado y valida post/autor. La
aceptación pública no alcanzó discovery porque la captura local ocupó el repositorio vacío y activó
el control de conflicto; no hubo red ni descarga. HND-0004 v0.8.0 registra `REWORK_REQUIRED` sin
repetir el comando.

PRM-0024 corrigió exclusivamente el arnés local y ejecutó una única aceptación con repositorio y
logs separados. El worker cargó autenticación e inició el extractor, pero el post exacto no produjo
ningún video/candidato y terminó `PROVIDER_EXHAUSTED`, código 8. El manifest quedó `0 → 0`, sin
SQLite, medios o residuos. HND-0004 v0.8.1 registra `SINGLE_POST_NO_VIDEO`.

PRM-0025 corrigió la paridad del adaptador principal: `PROFILE` conserva `/timeline` y
`SINGLE_POST` entrega al job la URL canónica directa. Un `inspect` read-only encontró el video
exacto y la única descarga posterior produjo un MP4 íntegro, sidecar, manifest y catálogo con un
job `COMPLETED`. HND-0004 v0.9.0 registra `SINGLE_POST_DOWNLOAD_VALIDATED /
WAITING_CHAT_VALIDATION`; esto no autoriza descarga masiva, merge o B05.

PRM-0026 reprodujo y corrigió una clasificación falsa: EOF o terminal tardío después del último
candidato entregado podía convertirse en `WORKER_FAILED`. La reanudación única BBCWorld preservó
los cuatro hashes originales y completó `4 → 5` descargando exactamente un activo nuevo. HND-0004
v1.0.0 registra `B04_LIMIT_5_VALIDATED / WAITING_CHAT_VALIDATION`; no habilita descarga masiva,
merge o B05.

Leonel cerró posteriormente B04 como `VALIDATED_WITH_OBSERVATIONS`: quedan demostrados los cortes
1/2/5, SINGLE_POST, integridad, deduplicación y reanudación. Operación masiva, paginación eficiente,
scheduler, release y certificación permanecen fuera de B04.

## Archive B05 — corte durable experimental

`xma archive` acepta únicamente perfiles, un total de 1–10, lotes de 1–5 y un intervalo entre
páginas de 1–60 segundos. `xma status` consulta el último run completamente offline:

```bash
uv run xma archive @BBCWorld --limit 10 --batch-size 2 \
  --repository ./repository --auth-browser firefox --auth-profile <LOCAL_PROFILE> \
  --request-interval 2 --discovery-timeout 30 --json
uv run xma status --repository ./repository
uv run xma status --repository ./repository --json
```

El repositorio normalizado contiene catálogo, artifacts, sidecars y manifests; nunca debe contener
cookies, selectores locales ni URLs multimedia firmadas. Los estados son `PENDING`, `RUNNING`,
`PAUSED`, `COMPLETED` y `FAILED`. `COMPLETED` confirma el total; `PAUSED` o `FAILED` conserva el
progreso y requiere diagnóstico antes de reanudar.

`RESCAN_DEDUP_V1` vuelve a recorrer el perfil, omite identidades catalogadas y confirma cada página
antes del checkpoint. Es adecuada para el corte gobernado de diez, pero no para miles.

La aceptación PRM-0027 no descargó ni alteró medios: con cinco activos B04, el servicio inició el
run con conteo cero y pidió un total absoluto de dos; el downloader rechazó correctamente que ya
existieran cinco. Terminó código 9 y el run quedó incorrectamente `RUNNING` en página cero. B05
queda `REWORK_REQUIRED`; no debe repetirse hasta reconciliar conteo y transición terminal.

PRM-0028 reconcilió el run desde los cinco artifacts verificados, corrigió los targets absolutos
`5 → 7 → 9 → 10` y garantizó estados terminales en la aplicación. La única reanudación descargó
cinco videos nuevos y dejó diez íntegros, checkpoint 10/página 3 y estado `COMPLETED`. Sin embargo,
el UPSERT durable no actualizó `existing_before`: el resultado del comando informó 5 pero `status`
leyó 0. La aceptación no se repitió y B05 continúa `REWORK_REQUIRED` por esa divergencia.

## Discovery B03

B03 añade inspección y catalogación de metadatos públicos. No descarga videos ni miniaturas.

```bash
# Inspección sin efectos laterales
uv run xma inspect @Reuters --limit 2
uv run xma inspect https://x.com/Reuters --limit 2 --json

# Vista previa: no crea directorios ni SQLite
uv run xma sync @Reuters --limit 2 --repository ./repository --dry-run

# Catálogo local; solo se ejecuta si X permite discovery anónimo
uv run xma sync @Reuters --limit 2 --repository ./repository

# Sesión local explícita; ambos parámetros son obligatorios
uv run xma sync @Reuters --limit 2 --repository ./repository \
  --auth-browser firefox --auth-profile <LOCAL_PROFILE>
```

La salida JSON omite las URLs de variantes multimedia. `inspect` no abre el catálogo;
`sync --dry-run` tampoco lo crea. El límite aceptado es de 1 a 100 activos de video.

### Códigos de salida B03

| Código | Significado |
|---|---|
| `0` | discovery completado |
| `2` | target o argumento inválido |
| `3` | perfil no disponible en modo anónimo |
| `4` | rate limit del proveedor |
| `5` | contrato o proveedor fallido |
| `6` | persistencia local no disponible o conflicto de catálogo |
| `7` | perfil no encontrado |
| `8` | fallo transitorio de transporte/proveedor |

En octubre de 2026, la prueba anónima histórica de Reuters, AP y BBCWorld recibió `AuthRequired`
de X. Posteriormente, ADR-0003 autorizó una sola aceptación controlada con sesión Firefox local.
El modo autenticado vigente es explícito, solo lectura y acotado; el modo anónimo sigue siendo el
predeterminado. Ninguna cookie se exporta, persiste, imprime ni cruza la frontera de infraestructura.

### Rework histórico B03-REWORK-001

AUD-0003 v0.1.1 clasificó B03-REWORK-001 como `REWORK_REQUIRED`. El bloqueo externo histórico
`AuthRequired` se evalúa por separado de las correcciones internas posteriores.

JSON usa salida cruda UTF-8 determinista, sin Rich. `cursor=null` significa que no existe
paginación implementada; no permite inferir completitud ni reanudación. La aplicación rechaza
resultados cuyo target, límite declarado o conteo no coincida con la solicitud.

La identidad del activo es `post_id:media_index`. En B03 las variantes son solo observaciones
efímeras del proveedor: no se usan como identidad ni se imprimen. El catálogo nuevo guarda
únicamente el marcador `metadata-only`; no conserva URLs, query strings, firmas ni rutas de
variantes. Una futura descarga requerirá resolver nuevamente sus fuentes en otro gate. Esta
política no migra catálogos previos; activos ya persistidos con variantes anteriores pueden
seguir produciendo conflicto (salida 6). No borrar automáticamente catálogos del usuario.

El rework B02 está separado en `feature/xma-b02-contracts`, auditoría v0.1.2 publicada en
`4b8bdab`. No está integrado en main ni B03; la baseline sigue siendo `b2bdca7`. Sus mejoras
de apertura excepcional, migración y contratos permanecen pendientes de integración gobernada.
B03 captura errores esperables en su CLI; esto no equivale a integrar ni certificar el rework B02.

### Rework B03-REWORK-002

PRM-0005 es el prompt vigente y AUD-0003 v0.1.1 es la auditoría que origina este rework. La
frontera `gallery-dl` rechaza booleanos, valores no finitos y enteros fuera del rango SQLite antes
de convertir `num`, dimensiones o duración. Estos casos producen salida 5 sanitizada y no crean
catálogo. El bloqueo público `AuthRequired` permanece separado; el smoke no se repitió.

### Rework B03-REWORK-003

AUD-0003 v0.1.2 demostró que B03-REWORK-002 todavía aceptaba duraciones negativas menores a un
milisegundo cuando el redondeo ocultaba su signo. PRM-0006 corrige esa frontera: valida la duración
en segundos con representación decimal antes de multiplicar o redondear. Toda duración
semánticamente negativa se rechaza con salida 5 sanitizada y sin crear catálogo.

Cero y las duraciones positivas menores a medio milisegundo siguen siendo válidas y se redondean
a cero milisegundos; las demás usan redondeo al entero par más cercano. Esto conserva la política
histórica de conversión y no introduce un límite de producto. No se repitió el smoke público.

### Rework B03-REWORK-004

AUD-0003 v0.1.3 detectó que REWORK-003 cambió involuntariamente los empates positivos de `float`
al usar `Decimal.from_float()`: `0.0005` y `0.0025` dejaron de producir `0 ms` y `2 ms`. PRM-0007
restaura la secuencia histórica `float(value)`, multiplicación por 1000 y `round()` después de la
validación semántica. Los cinco negativos siguen rechazándose antes del redondeo y los límites
SQLite y el mensaje sanitizado permanecen intactos. Esto corrige la afirmación incompatible de
HND v0.1.3 sobre compatibilidad positiva; no reescribe ese documento histórico ni repite el smoke.

### Rework B03-REWORK-005

AUD-0003 v0.1.4 detectó que `Decimal(value)` introducía un límite de exponente ausente en la
baseline: cadenas finitas no negativas que `float()` convierte a cero podían rechazarse. PRM-0008
reemplaza esa validación por inspección léxica del signo y significando, sin evaluar el exponente.
Así se aceptan exponentes extremos positivos y ceros con signo, mientras todo signo negativo con
significando no cero se rechaza antes de perderse como `-0.0`. La conversión histórica, los límites
SQLite y el mensaje sanitizado permanecen intactos; el smoke público no se repitió.

### Discovery autenticado controlado

PRM-0009 añade una selección explícita de sesión Firefox a `inspect` y `sync`; el modo anónimo
sigue siendo el predeterminado. Navegador y perfil deben proporcionarse juntos, solo se admite
Firefox y no se aceptan rutas de cookies. La aplicación resuelve el nombre exacto desde el
inventario Firefox autorizado y lee `cookies.sqlite` en modo inmutable y solo lectura. Solo carga
en memoria cookies de los dominios necesarios para X; mantiene caché en memoria y descarga
deshabilitada, y no copia, imprime, exporta ni persiste cookies o el identificador local.

La aceptación gobernada Reuters → AP → BBCWorld, siempre con `--limit 2`, obtuvo códigos 3, 3 y 0.
BBCWorld catalogó exactamente dos activos públicos distintos; el repositorio temporal contenía
solo `.sqlite3`, sin medios, miniaturas ni sidecars. AUD-0005 v0.1.1 clasificó el primer rework
como `REWORK_REQUIRED`: una sesión incompleta podía continuar como guest y un symlink circular
podía propagar un error de resolución. PRM-0011 implementó el fail-closed de `auth_token` y
`ct0`, y normalizó específicamente ese error. AUD-0005 v0.1.2 validó R-01–R-03 con
observaciones sobre los límites de la reproducción sintética y de CI.

La evidencia SQLite original permanece `EVIDENCE_NOT_AVAILABLE`. Leonel liberó PRM-0012 para
una única ejecución controlada de recuperación A-06; DOT-PRM-0014 continúa inactivo hasta que
existan HND-0003 v0.3.0, CI verde y el paquete local verificable. Q3-Público y la transición
general B03 permanecen `BLOCKED`; merge y B04 continúan sin autorización.
