Ejecuta una sola vez:

XMA-CLI-001-PRM-0016
B04-DOWNLOAD-VERTICAL-SLICE v0.1.0

OBJETIVO URGENTE

Implementar y demostrar una descarga real desde la CLI de:

- 1 video;
- 2 videos;
- 5 videos;

desde una sola cuenta pública periodística de X, con documentación JSON,
catálogo SQLite, SHA-256, staging atómico e idempotencia básica.

Prioriza una funcionalidad vertical mínima, ejecutable y comprobable.
No implementes todavía descarga masiva, paginación completa ni operación avanzada.

## 1. Autorización humana y decisión gobernada

Leonel autorizó:

- modo acelerado Chat → Codex;
- B04 limitado al corte vertical 1/2/5;
- autenticación Firefox local;
- uso opcional de un archivo local de cookies exportadas cuando facilite la ejecución;
- prueba pública controlada con un máximo acumulado de ocho descargas:
  1 + 2 + 5;
- documentación de deuda técnica para corregirla en v2.

Esta autorización no incluye:

- descarga de miles;
- paginación completa;
- paralelismo;
- retry automático;
- API X;
- GUI;
- servidor;
- Docker;
- release;
- merge automático;
- publicación de cookies o medios.

## 2. Baseline obligatoria

Repositorio:
eventmgmtplatform/x-media-archiver

PR anterior:
#3

Baseline de gobernanza:

HEAD:
bdef347ab83edba8ca63b9f13c8afa524178967e

Tree:
d57f9155e696a90f529641a2349fb694dcaa3d23

CI:
#41 / run 40820369121
SUCCESS
214 pruebas
94.74 % de cobertura

Snapshot funcional A-06:

HEAD:
7adb2f670ef20deff8b70aec0fad0037762ebb8b

Tree:
128c7cf7b8466848516e3b4223be4b40c73397d5

La discrepancia observada por AUD-0006 no representa cambios funcionales:
los tres commits posteriores son exclusivamente documentales.

No repitas A-06.

## 3. Rama y PR

1. Actualiza referencias remotas.
2. Confirma que `feature/xma-b03-discovery` está en el HEAD indicado.
3. Confirma worktree limpio.
4. Crea desde ese commit:

   feature/xma-b04-download-slice

5. Abre un PR draft apilado:
   - head: feature/xma-b04-download-slice
   - base: feature/xma-b03-discovery
   - título: feat: implement B04 download vertical slice

No modifiques main.
No hagas merge.

## 4. Decisión de gobernanza

Registra sin reescribir auditorías anteriores:

GOV-DEC-0020

- AUD-0006 mantiene su dictamen BLOCKED por discrepancia de HEAD.
- Los hashes del catálogo y manifest coincidieron.
- PRAGMA integrity_check fue `ok`.
- Se verificaron exactamente dos activos VIDEO con identidades distintas.
- Los commits entre 7adb2f6 y bdef347 son documentales.
- Leonel acepta el riesgo residual de que `protected=false` y parte de la
  secuencia provengan del manifest/HND y no de una columna independiente.
- Se permite avanzar a un corte vertical B04 sin declarar el producto
  certificado.
- Dot auditará el lote consolidado después de las pruebas 1/2/5.

Crea:

- `docs/adr/ADR-0004-expedited-v1-download-auth.md`
- `docs/prompts/XMA-CLI-001_PRM-0016_B04-DOWNLOAD-VERTICAL-SLICE_v0.1.0.md`

Actualiza proporcionalmente:

- Gate Register;
- Implementation Plan;
- README;
- CHANGELOG.

## 5. CLI requerida

Implementa:

xma download TARGET [OPTIONS]

Opciones mínimas:

- `--limit INTEGER`
  - mínimo 1;
  - máximo 5 para este corte vertical.
- `--repository PATH`
- `--auth-browser firefox`
- `--auth-profile PROFILE`
- `--cookies-file PATH`
- `--json`

Reglas de autenticación:

1. Sin opciones de autenticación:
   conservar el modo anónimo existente.

2. Firefox:
   `--auth-browser` y `--auth-profile` deben aparecer juntos.

3. Cookie file:
   `--cookies-file` es alternativo a Firefox.

4. Rechazar:
   - Firefox y cookies-file simultáneos;
   - navegador diferente de Firefox;
   - archivo inexistente;
   - directorio;
   - symlink;
   - archivo fuera del control local solicitado.

5. Nunca:
   - imprimir la ruta completa;
   - imprimir contenidos;
   - imprimir nombres o valores de cookies;
   - copiar el archivo;
   - persistirlo;
   - agregarlo a manifest o SQLite.

El archivo puede estar en formato Netscape compatible con gallery-dl.

Añade a `.gitignore` patrones suficientes para:

- cookies*.txt
- *.cookies
- cookies.json
- downloads/
- repository/
- *.part
- *.tmp
- archivos multimedia comunes producidos por el smoke, cuando estén dentro
  del árbol por error.

No generes ni exportes automáticamente cookies. Solamente acepta un archivo
que el operador proporcione localmente.

## 6. Arquitectura mínima

Conserva el monolito modular actual.

Añade una frontera tipada equivalente a:

- `MediaDownloadProvider`
- `DownloadRequest`
- `DownloadedArtifact`
- `DownloadService`

La aplicación no debe depender directamente de gallery-dl.

Implementa el adaptador usando preferentemente la dependencia `gallery-dl`
ya fijada. No añadas yt-dlp ni FFmpeg para este corte salvo que sea
técnicamente imprescindible y lo documentes como bloqueo antes de hacerlo.

No uses shell con texto no controlado.
No uses `shell=True`.

## 7. Flujo de descarga

Para cada activo:

1. Descubrir metadatos y URL efímera en memoria.
2. Crear un DownloadJob en estado DISCOVERED.
3. Transicionar a QUEUED.
4. Transicionar a DOWNLOADING.
5. Descargar a un archivo temporal con sufijo `.part`.
6. Rechazar respuestas vacías.
7. Calcular tamaño y SHA-256 durante o inmediatamente después de la descarga.
8. Crear sidecar JSON sanitizado.
9. Realizar movimiento atómico del archivo temporal al nombre final.
10. Registrar Artifact y completar el DownloadJob.
11. Nunca guardar la URL firmada o su query string.
12. Ante fallo:
    - eliminar `.part`;
    - registrar error normalizado sin secretos;
    - no crear Artifact;
    - no presentar el archivo como completo.

No hagas retry automático en este corte.

## 8. Estructura normalizada

Usa una estructura determinista equivalente a:

repository/
  catalog.sqlite3
  profiles/
    <handle-normalizado>/
      posts/
        <post-id>/
          <media-index>/
            video.<extension>
            metadata.json
  manifests/
    latest.json

No uses texto de la publicación como nombre de archivo.

La ruta registrada en SQLite debe ser relativa al repository.

## 9. Sidecar JSON

Cada `metadata.json` debe incluir como mínimo:

- schema_version;
- profile_handle;
- post_id;
- media_index;
- asset_id;
- canonical_post_url;
- published_at;
- post_type;
- text;
- media_type;
- duration_ms;
- width;
- height;
- provider;
- downloaded_at;
- relative_path;
- mime_type;
- size_bytes;
- sha256.

No incluir:

- cookies;
- auth_token;
- ct0;
- URL multimedia;
- query strings;
- headers;
- ruta personal;
- nombre del perfil Firefox;
- ruta del archivo de cookies.

## 10. Manifest

`manifests/latest.json` debe incluir:

- schema_version;
- target sanitizado;
- requested_limit;
- downloaded_count;
- skipped_count;
- failed_count;
- started_at;
- finished_at;
- run_id;
- lista de artefactos con:
  - asset_id;
  - relative_path;
  - size_bytes;
  - sha256;
  - sidecar_path.

Debe escribirse atómicamente.

## 11. Idempotencia mínima

Si el activo ya está COMPLETED y el archivo existe:

- comprobar tamaño y SHA-256;
- no volver a descargar;
- reportarlo como skipped;
- no crear un segundo Artifact.

Si catálogo y filesystem no coinciden:

- fallar cerrado;
- no sobrescribir silenciosamente;
- emitir error sanitizado.

## 12. Pruebas offline

No uses red en CI.

Añade pruebas para:

- validación de límite 1–5;
- opciones de auth mutuamente excluyentes;
- cookies-file inexistente;
- symlink rechazado;
- nombres y valores de cookies nunca impresos;
- descarga exitosa con proveedor falso;
- archivo `.part` durante escritura;
- movimiento atómico;
- SHA-256 correcto;
- sidecar correcto;
- manifest correcto;
- DownloadJob con transiciones válidas;
- Artifact persistido;
- fallo elimina `.part`;
- fallo no crea Artifact;
- segundo comando idempotente;
- conflicto catálogo/filesystem falla cerrado;
- salida JSON estable;
- conteo exacto 1, 2 y 5 con fixtures;
- regresión completa de B02/B03.

Mantén cobertura mínima 90 %.

## 13. Validaciones locales

Ejecuta:

- `uv sync --locked --all-groups`
- `uv run ruff format --check .`
- `uv run ruff check .`
- `uv run mypy`
- `uv run pytest`
- `uv build`
- `git diff --check`

Confirma:

- `uv.lock` intacto, salvo que una dependencia imprescindible haya sido
  previamente autorizada;
- ningún secreto rastreado;
- ningún video rastreado;
- ninguna SQLite local rastreada;
- ningún archivo de cookies rastreado.

## 14. Smoke público 1/2/5

Solo después de que las pruebas offline pasen.

Usa una única cuenta pública periodística autorizada.
Preferencia: Reuters.

Usa tres repositorios temporales independientes fuera de Git:

- `<LOCAL_SMOKE_ROOT>/limit-1`
- `<LOCAL_SMOKE_ROOT>/limit-2`
- `<LOCAL_SMOKE_ROOT>/limit-5`

Preferir autenticación Firefox existente:

`--auth-browser firefox --auth-profile <LOCAL_PROFILE>`

Si falla y el operador dispone de un archivo exportado:

`--cookies-file <LOCAL_COOKIE_FILE>`

No publiques los valores reales.

Ejecuta exactamente una vez cada comando:

xma download @Reuters --limit 1 ...
xma download @Reuters --limit 2 ...
xma download @Reuters --limit 5 ...

No ejecutes `inspect`.
No hagas retry automático.
No cambies de cuenta entre pruebas.

Para cada repositorio verifica:

- cantidad exacta de videos: 1, 2 y 5;
- cantidad exacta de sidecars: 1, 2 y 5;
- manifest presente;
- SQLite presente;
- cero `.part`;
- SHA-256 de cada archivo coincide con SQLite, sidecar y manifest;
- todos los archivos tienen tamaño mayor que cero;
- los archivos son reconocibles como contenido audiovisual;
- no hay cookies ni secretos dentro del repositorio.

Si un límite no obtiene la cantidad exacta:

- detente;
- no repitas el comando;
- reporta el bloqueo y la evidencia sanitizada.

## 15. Evidencia y privacidad

No subas a Git:

- videos;
- audios;
- SQLite del smoke;
- manifest local;
- sidecars locales;
- cookies;
- nombres reales de perfil;
- rutas personales.

El handoff solo puede publicar:

- conteos;
- extensiones;
- tamaños agregados;
- hashes de identidad sanitizados;
- resultado de validación;
- SHA/tree;
- CI;
- códigos de salida;
- estructura con placeholders.

Los SHA-256 de medios pueden conservarse en el paquete local para dot, pero
no es obligatorio publicarlos individualmente en el PR.

## 16. Handoff

Publica:

`docs/handoffs/XMA-CLI-001_HND-0004_B04-DOWNLOAD-SLICE_v0.1.0.md`

Debe contener:

- estado final;
- SHA y tree;
- commits;
- archivos modificados;
- arquitectura implementada;
- comandos CLI sanitizados;
- matriz 1/2/5;
- conteos de videos y sidecars;
- resultados de integridad;
- pruebas y cobertura;
- CI;
- limitaciones;
- deuda v2;
- rollback;
- confirmación de ausencia de secretos y medios en Git.

Deuda técnica v2 obligatoria:

- eliminar o endurecer `--cookies-file`;
- inicio de sesión guiado con Firefox;
- almacenamiento seguro del sistema;
- paginación durable;
- reanudación;
- rate limiting;
- operación para miles;
- retry/status/export/doctor;
- auditoría final independiente.

## 17. Estado de salida

Si implementación y smoke 1/2/5 pasan:

B04_VERTICAL_SLICE_COMPLETED / WAITING_CHAT_VALIDATION

Si código y pruebas pasan, pero smoke falla:

BLOCKED_PUBLIC_DOWNLOAD

Si existe riesgo de secreto:

FAILED_POTENTIAL_SECRET

Al finalizar:

- publica commits;
- abre o actualiza PR draft #4;
- espera CI verde;
- entrega el handoff;
- detente;
- no hagas merge;
- no inicies descarga masiva;
- no ejecutes dot.
