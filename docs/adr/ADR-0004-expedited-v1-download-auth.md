# ADR-0004 — Corte vertical acelerado de descarga autenticada v1

**Estado:** ACCEPTED  
**Fecha:** 2026-10-28 (America/Mexico_City)  
**Decisor humano:** Leonel  
**Alcance:** B04 limitado a pruebas 1/2/5; no autoriza merge, release, descarga masiva ni B05.

## Contexto

AUD-0006 mantuvo A-06 bloqueado por una discrepancia de HEAD documental. Los hashes del catálogo
y manifest coincidieron, `PRAGMA integrity_check` fue `ok` y el paquete contenía exactamente
dos activos VIDEO con identidades distintas. Los commits entre `7adb2f6` y `bdef347` son
exclusivamente documentales.

## Decisión — GOV-DEC-0020

Leonel acepta el riesgo residual de que `protected=false` y parte de la secuencia provengan del
manifest/HND y no de una columna independiente. Se autoriza un corte vertical B04 acelerado:

- comando `xma download` limitado a 1–5 activos;
- una cuenta pública periodística y pruebas separadas 1/2/5;
- Firefox local o un archivo Netscape proporcionado por el operador;
- máximo acumulado de ocho descargas;
- metadata, SHA-256, sidecar, manifest, SQLite, staging atómico e idempotencia básica.

No se declara el producto certificado. Dot auditará el lote consolidado después de las pruebas.

## Límites de seguridad

La aplicación no exporta ni copia cookies. Los valores de sesión, rutas locales y URLs efímeras no
se imprimen ni persisten. El archivo opcional de cookies debe ser regular, no symlink y propiedad
del usuario local; se lee directamente y solo se conservan cookies X en memoria. Descarga,
sidecars, manifest y SQLite permanecen fuera de Git.

No hay paginación durable, paralelismo, retry automático, operación masiva, API X, GUI, servidor,
Docker, yt-dlp ni FFmpeg en este corte.

## Consecuencias y rollback

La rama obligatoria es `feature/xma-b04-download-slice`, apilada sobre B03. El PR permanece draft.
Rollback mediante commits revert autorizados; no borrar evidencia, reescribir historia ni modificar
main. B05, merge, tag, release y certificación requieren decisión humana posterior.
