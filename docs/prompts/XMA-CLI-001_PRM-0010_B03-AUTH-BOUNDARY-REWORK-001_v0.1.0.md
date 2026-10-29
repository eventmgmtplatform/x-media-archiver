# XMA-CLI-001 — PRM-0010 B03 Auth Boundary Rework 001

**Versión:** 0.1.0  
**Fecha:** 2026-10-28  
**Estado:** APPROVED FOR ONE EXECUTION  
**Autoridad humana:** Leonel  
**Ejecutor:** Codex  
**Origen:** AUD-0005 v0.1.0, dictamen REWORK_REQUIRED  
**Baseline funcional auditada:** `29741c20978a9a3b097c790fc352d73b1007c193`  
**Tree auditado:** `42d470898aebd78654a3ff1153e340904ce68372`  
**Rama obligatoria:** `feature/xma-b03-discovery`  
**PR:** #3

## 1. Objetivo

Ejecutar una sola iteración acotada de `B03-AUTH-BOUNDARY-REWORK-001` para cerrar A-01 a A-06 de AUD-0005 sin repetir el smoke público, sin ampliar el acceso y sin iniciar B04.

La evidencia de BBCWorld con dos activos continúa siendo una declaración versionada del ejecutor. Este prompt no la convierte en evidencia independiente ni autoriza Q3-Público.

## 2. Secuencia

1. Confirmar que la rama parte exactamente de la baseline gobernada que contiene este prompt.
2. Leer íntegramente ADR-0003, PRM-0009, DOT-PRM-0011, HND-0003 v0.2.0, AUD-0005 v0.1.0 y este prompt.
3. Si HEAD cambió antes de iniciar, detenerse y reportar `BLOCKED`.
4. Implementar únicamente A-01–A-06.
5. Ejecutar pruebas offline y la suite completa.
6. Publicar HND-0003 v0.2.1 con SHA, tree y resultados sanitizados.
7. Esperar CI verde y detenerse en `WAITING_VALIDATION`.
8. No ejecutar DOT-PRM-0012; corresponde a dot después del handoff y CI.

## 3. Alcance obligatorio

### A-01 — Prohibir copias de la base de cookies

La lectura de la sesión Firefox debe permanecer dentro de infraestructura y ser solo lectura. El flujo alcanzable de XMA no puede invocar el fallback de la dependencia que copia `cookies.sqlite` a un directorio temporal.

Se permite adaptar o encapsular el límite de infraestructura de gallery-dl. No se permite otro extractor, exportar cookies, escribir una copia, serializarlas, imprimirlas, persistirlas ni incluirlas en dominio, DTO de salida, SQLite, JSON, logs o excepciones.

Los valores utilizados en memoria deben limitarse a los dominios necesarios para X y descartarse al terminar el proceso.

### A-02 — Sanitizar warnings y errores

Ninguna excepción de la dependencia puede emitir valores de cookies, selector de perfil, rutas locales o texto arbitrario del lector.

Toda falla de sesión debe convertirse en un error XMA constante y sanitizado, terminar con el código gobernado, impedir continuación silenciosa sin la autenticación solicitada y no producir traceback en la CLI ordinaria.

Agregar pruebas offline con marcadores sintéticos. Ningún marcador puede aparecer en stdout, stderr, logs, JSON ni SQLite.

### A-03 — Selector de perfil contenido

`--auth-profile` representa un nombre, nunca una ruta. Aceptar solo un componente simple de máximo 128 caracteres y patrón equivalente a `[A-Za-z0-9][A-Za-z0-9._-]*`.

Rechazar `.`, `..`, rutas absolutas, `/`, `\\`, espacios, caracteres de control, vacío, resoluciones fuera de las raíces Firefox autorizadas y enlaces o resoluciones que rompan la contención.

La selección debe corresponder a una entrada exacta del inventario local de perfiles Firefox. No hacer búsqueda recursiva fuera de esa entrada. Las pruebas usarán filesystem sintético.

### A-04 — Solo perfiles públicos

Aplicar política fail-closed:
- `protected is False`: candidato permitido;
- `protected is True`: error de contrato sanitizado, sin catálogo;
- ausente, nulo o no booleano: error de contrato sanitizado, sin catálogo.

Agregar pruebas offline del mapper y de `sync` que demuestren ausencia de repositorio y SQLite ante estados no públicos.

### A-05 — Saneamiento documental

En el árbol actual, reemplazar la ruta personal heredada identificada por AUD-0005 por `<LOCAL_CACHE_PATH>`. No reproducir su valor en commit, diff, PR, handoff, logs o mensajes.

No reescribir historial Git. Documentar que el saneamiento es hacia adelante y que cualquier reescritura histórica exige otra autorización humana.

Corregir la contradicción del README entre el bloqueo anónimo histórico y la autenticación Firefox controlada vigente.

### A-06 — Evidencia SQLite existente

No repetir Reuters, AP o BBCWorld y no acceder nuevamente a X.

Si el catálogo temporal original todavía existe, realizar solo lectura local y registrar exclusivamente:
- `PRAGMA integrity_check = ok`;
- cantidad total de activos de video;
- cantidad de identidades distintas;
- confirmación de exactamente dos filas/identidades distintas;
- extensión `.sqlite3`;
- ausencia de archivos multimedia.

No publicar IDs, URLs, filenames, rutas, hashes, timestamps, contenido, cookies ni selector real. Los comandos deben usar marcadores redactados.

Si el catálogo original no existe o no puede vincularse inequívocamente con la ejecución autorizada, registrar `EVIDENCE_NOT_AVAILABLE`. No reconstruirlo, no inventar resultados y no repetir el smoke. Q3-Público permanecerá bloqueado.

## 4. Pruebas obligatorias

Todas las pruebas serán offline y sustituirán filesystem, SQLite de cookies, navegador, red y gallery-dl cuando corresponda.

Cubrir:
1. fallback de copia inalcanzable;
2. ningún archivo temporal o persistente de cookies;
3. excepciones totalmente sanitizadas;
4. sin degradación anónima silenciosa;
5. rechazo de `.`, `..`, rutas y escapes;
6. resolución contenida en el perfil exacto;
7. perfil protegido o indeterminado no se cataloga;
8. anónimo predeterminado;
9. opciones auth obligatorias en conjunto;
10. download deshabilitado y caché gallery-dl en memoria;
11. regresión completa B02/B03.

Ejecutar locked sync, Ruff format/check, mypy, pytest con cobertura mínima de 90 %, build sdist/wheel y `git diff --check`. CI no puede ejecutar red, navegador ni X.

## 5. Entregables

- Código y pruebas mínimos.
- Documentación y trazabilidad A-01–A-06.
- `docs/handoffs/XMA-CLI-001_HND-0003_B03-20261028-001_v0.2.1.md`.
- Gate Register e Implementation Plan como `REWORK_COMPLETED / WAITING_VALIDATION`.
- PR #3 actualizado con estado, SHA/tree, CI y limitaciones.
- Ninguna evidencia local, SQLite, cookie DB, medio o log sensible rastreado.

## 6. Prohibiciones

No smoke, X, cookies.txt, exportación de cookies, username/password, tokens, correo, teléfono, 2FA, API X, yt-dlp, FFmpeg, Twikit, twscrape u otro extractor.

No descarga, thumbnails, sidecars, staging, hashes, comandos B04/B05, GUI, API propia, servidor, ORM, Redis, Docker o scheduler.

No merge, tag, release, certificación, main directo ni reescritura de historial.

## 7. Salida

- `WAITING_VALIDATION`: nuevo SHA/tree, HND-0003 v0.2.1 y CI verde.
- `BLOCKED`: precondición o solución compatible con ADR-0003 no disponible.
- `FAILED`: exposición real, desviación material o control obligatorio incumplido.

Codex no decide Q3-Público, no autoriza B04 y no ejecuta la auditoría independiente.
