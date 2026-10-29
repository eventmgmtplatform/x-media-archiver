# XMA-CLI-001 — PRM-0012 A-06 Public Evidence Recovery

**Versión:** 0.1.0
**Estado:** APPROVED FOR ONE EXECUTION / NOT_STARTED
**Autoridad de preparación:** Leonel, 2026-10-28 America/Mexico_City
**Ejecución:** liberada una vez por Leonel el 2026-10-28 (America/Mexico_City)
**Repositorio:** eventmgmtplatform/x-media-archiver
**PR:** #3, feature/xma-b03-discovery

## 1. Objetivo único

Recuperar evidencia verificable de A-06 mediante una sola prueba pública controlada de discovery
y catalogación metadata-only. El criterio de aceptación es exactamente dos activos públicos de
video distintos catalogados con --limit 2. Cero o uno no pasan.

Este mandato no autoriza merge, B04/B05, descarga de medios, certificación, tag o release.

## 2. Precondiciones obligatorias

Antes de ejecutar, Codex debe:

1. Confirmar en Gate Register GOV-AUTH-0016 y la baseline de gobernanza que libera PRM-0012 una sola vez.
2. Confirmar PR #3 abierto y draft, rama feature/xma-b03-discovery.
3. Registrar el SHA y tree de gobernanza que contengan AUD-0005 v0.1.2, este prompt y DOT-PRM-0014.
4. Confirmar CI verde sobre ese tree y worktree limpio.
5. Confirmar Firefox como único navegador y un perfil local ya autenticado, sin publicar su nombre
   real, ruta, cuenta local o identificadores personales.
6. Usar una carpeta temporal explícita fuera del repositorio Git.

Si alguna precondición falla, detenerse en BLOCKED sin acceder a X.

## 3. Ejecución permitida

Una sola secuencia, en este orden:

1. Reuters
2. AP
3. BBCWorld

Para cada objetivo se permite exactamente un comando xma sync autenticado con --limit 2, repositorio
temporal y los parámetros --auth-browser firefox --auth-profile <LOCAL_PROFILE>. El valor real de
perfil se usa solo localmente y nunca aparece en Git, CI, HND, logs publicados o salidas copiadas.

Detener la secuencia inmediatamente cuando un objetivo produzca exactamente dos activos públicos
de video distintos catalogados. Si un objetivo produce cero o uno, registrar el resultado
sanitizado y continuar al siguiente. No reintentar. No ejecutar inspect adicional. No cambiar de
cuenta, navegador, extractor o configuración.

## 4. Evidencia local obligatoria

Conservar temporalmente, fuera de Git y sin borrar hasta concluir la auditoría:

- el catálogo SQLite generado;
- un manifest JSON sanitizado;
- el SHA-256 del catálogo y del manifest;
- salida sanitizada de PRAGMA integrity_check;
- versión de esquema;
- conteo total y conteo DISTINCT de la identidad post_id:media_index;
- para cada activo aceptado: hash SHA-256 de su identidad canónica, tipo de medio, target público
  y confirmación protected=false/metadata-only;
- lista de extensiones del repositorio temporal;
- códigos de salida por target y UTC de inicio/fin;
- SHA/tree ejecutados y versión de xma/gallery-dl.

El manifest no debe contener cookies, valores auth_token/ct0, headers, tokens, URL firmada, query
string, nombre o ruta real del perfil, correo, teléfono, contraseña, 2FA, ruta personal, medios,
miniaturas o sidecars. Las identidades públicas se publican solo como hashes distintos.

El catálogo y el paquete no se committean, no se suben a CI y no se incorporan al PR. Leonel debe
recibirlos por el mecanismo local autorizado para adjuntarlos después a dot. El HND publica solo
los hashes, conteos y resultados sanitizados necesarios para enlazar el paquete.

## 5. Validaciones posteriores

Ejecutar sin repetir el acceso público:

- uv sync --locked --all-groups
- ruff format --check .
- ruff check .
- mypy
- pytest
- uv build
- git diff --check
- verificación de que uv.lock no cambió;
- verificación de que Git no rastrea SQLite, manifest local, cookies, medios ni evidencias privadas.

## 6. Handoff

Publicar HND-0003 v0.3.0 con:

- SHA y tree exactos;
- matriz A-06 con 0/1/2 activos por target y códigos de salida;
- hashes del paquete local y catálogo;
- resultado de integridad y conteos, sin secretos;
- CI sobre el mismo tree;
- confirmación de una sola ejecución, sin retries;
- confirmación de ausencia de medios y datos sensibles;
- estado WAITING_VALIDATION.

No declarar A-06, Q3-Público o B03 como aprobados. Si no se obtienen exactamente dos activos, usar
BLOCKED y conservar la evidencia del resultado.

## 7. Prohibiciones

Prohibidos cookies.txt, exportar/copiar/serializar cookies Firefox, username/password, .env secreto,
.netrc, keyring nuevo, rutas arbitrarias a cookies, navegador distinto de Firefox, API X, yt-dlp,
FFmpeg, Twikit, twscrape u otro extractor; download/retry/status/export/doctor; GUI, API propia,
servidor, ORM, Redis, Docker, scheduler; medios, thumbnails, sidecars, staging o hashes de medios;
cambios funcionales de código, esquema o dependencias; merge, B04/B05, tag, release o certificación.

Ante un secreto potencial, detenerse, no publicarlo y reportar BLOCKED de forma sanitizada.

## 8. Secuencia de control

1. Leonel libera explícitamente PRM-0012.
2. Codex lo ejecuta una sola vez y publica HND-0003 v0.3.0.
3. Codex espera CI verde y entrega el paquete local a Leonel; se detiene.
4. Leonel adjunta el paquete exacto a dot.
5. Dot ejecuta DOT-PRM-0014 read-only.
6. Solo Leonel decide A-06, Q3-Público, B03, merge o B04.
