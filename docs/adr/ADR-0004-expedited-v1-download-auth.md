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

## Recuperación pública PRM-0017

Leonel autorizó un diagnóstico sanitizado y una secuencia de recuperación acotada. El adaptador
distingue `PROVIDER_TIMEOUT`, `PROVIDER_CONNECTION`, `PROVIDER_HTTP_502`, `PROVIDER_HTTP_503`,
`PROVIDER_RATE_LIMIT`, `PROVIDER_RESTRICTED` y `PROVIDER_CONTRACT`, preservando los códigos de
salida y ocultando el detalle crudo.

Firefox obtuvo exactamente un video en Reuters límite 1. Reuters límite 2 terminó antes de descargar
con `PROVIDER_TIMEOUT`; no dejó residuos. La política fail-closed detuvo límite 5 y no autorizó
fallback, porque Firefox ya había funcionado en límite 1. El resultado es
`PARTIAL_PUBLIC_DOWNLOAD / BLOCKED`, no una validación de B04.

## Recovery acotado PRM-0018

`xma download` incorpora un watchdog Linux sobre la fase completa de discovery, 30 segundos por
defecto. PRM-0018 fijó inicialmente máximo 60 segundos. Leonel amplió expresamente durante la
ejecución una prueba adicional a 120 y después a 180 segundos; el rango implementado quedó 5–180
segundos y el timeout HTTP se subordinó al mismo límite total. Plataformas no Linux fallan cerradas.

La señal privada no puede ser absorbida por capturas ordinarias de `Exception`; handler y timer se
restauran siempre. Si gallery-dl devuelve un contrato vacío al alcanzar el deadline, se normaliza
como `PROVIDER_TIMEOUT`. Ningún timeout inicia persistencia o descarga.

Reuters límite 2 no produjo activos en Firefox 60 s ni en las ejecuciones COOKIE_FILE autorizadas.
La ejecución final de 180 s terminó código 8 / `PROVIDER_TIMEOUT` sin residuos. El límite 1 previo
no se repitió y límite 5 no se ejecutó. B04 permanece `BLOCKED_PUBLIC_DOWNLOAD`.

## Modelo incremental PRM-0019

`--limit` expresa ahora el total deseado en el repositorio. El padre verifica catálogo, archivos,
hashes y sidecars antes de red; un repositorio completo termina sin discovery. Un worker Linux hijo
ejecuta gallery-dl y lectura de autenticación, emite candidatos serializables por IPC y nunca envía
cookies al padre. La URL efímera existe solo en memoria. El padre descarga y persiste cada candidato
antes de solicitar el siguiente.

Cada comando permite uno o dos workers de máximo 30 s, 60 s acumulados. Al vencer, el padre termina,
espera, mata si fuese necesario y siempre hace join. El rango público vuelve a 5–60 s. El progreso
válido no se revierte y un manifest incompleto permite reanudación.

La prueba PRM-0019 partió de una copia del lote límite 1. Dos workers expiraron sin candidato nuevo;
se conservó exactamente un activo íntegro, límite 5 no se ejecutó y el estado quedó
`PARTIAL_PROGRESS_PRESERVED / BLOCKED`.

## Frontera IPC PRM-0020

La frontera incremental usa ahora `multiprocessing.Pipe(duplex=False)`: el hijo envía de forma
síncrona mensajes v1 de telemetría, candidato o terminal, y el padre conserva solo el extremo
receptor. Perfil y activo se reducen a DTOs explícitos con primitivas finitas; campos ajenos se
ignoran y una forma inválida termina sanitizadamente como `IPC_SERIALIZATION_FAILED`. EOF sin
terminal y muerte inesperada son `WORKER_FAILED`; timeout vivo y agotamiento limpio conservan
código 8. Ambos extremos se cierran y el proceso siempre termina con join.

Las pruebas offline no reprodujeron pérdida por feeder de Queue, de modo que esa explicación sigue
siendo una inferencia histórica, no causa confirmada. La única prueba pública PRM-0020 cargó auth e
inició el extractor en dos workers de 30 s, pero no emitió `PROFILE_SEEN` ni candidatos y terminó
`PROVIDER_TIMEOUT`. El total permaneció en uno; límite 5 no se ejecutó.

## Aceptación alternativa PRM-0021

GOV-AUTH-0026 autorizó una única ejecución BBCWorld límite 2 en un repositorio nuevo y límite 5
solo si se alcanzaban exactamente dos activos. Ambos workers emitieron `WORKER_STARTED`,
`AUTH_LOADED` y `EXTRACTOR_STARTED`, sin perfil, video o candidato, y el comando terminó código 8 /
`PROVIDER_TIMEOUT`. El manifest quedó incompleto con total cero; no se creó SQLite ni medio. Límite
5 no se ejecutó y el estado es `PROVIDER_BLOCKED`.

## Paridad y spawn PRM-0022

Una única prueba read-only `inspect @BBCWorld --limit 1` en el proceso principal terminó código 0
en 13 s, observó un perfil público y un activo, y no persistió archivos. Esto aisló la diferencia en
la frontera multiprocessing. El contexto incremental cambió exclusivamente de `fork` a `spawn`;
target, autenticación sin cookies, Pipe y argumentos son importables/serializables.

Con spawn, BBCWorld límite 2 completó `0 → 2` con integridad plena. La ejecución límite 5 avanzó
`2 → 4` y preservó cuatro activos íntegros antes de terminar código 5 / `WORKER_FAILED`. El cambio
observable respalda a fork como causa del bloqueo anterior sin candidatos; no demuestra que fork
cause el fallo posterior del quinto activo. Estado: `B04_LIMIT_2_VALIDATED / LIMIT_5_BLOCKED`.

## Target SINGLE_POST PRM-0023

Discovery distingue explícitamente `PROFILE` de `SINGLE_POST`. Una URL HTTPS permitida de estado se
normaliza a `https://x.com/<handle>/status/<post_id>` sin query/fragment. El DTO spawn contiene solo
modo, URL canónica, handle y post ID; el worker usa esa URL directamente sin `/timeline`. El padre
rechaza post o autor distintos antes de descargar.

La única aceptación no alcanzó la red: los archivos locales de captura ocuparon accidentalmente el
repositorio que debía estar vacío y el control de consistencia terminó código 9. No se creó SQLite,
manifest, sidecar o medio. No hubo retry conforme al mandato. Estado público: `REWORK_REQUIRED`.
