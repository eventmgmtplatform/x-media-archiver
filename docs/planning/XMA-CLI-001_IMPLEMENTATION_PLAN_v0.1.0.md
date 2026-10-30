# XMA-CLI-001 — Plan de implementación

**Versión:** 0.1.0  
**Estado:** V0.1.1 RELEASED / POSTRELEASE RECONCILIATION
**Método:** Engineering OS + Scrum/Accelerate proporcional al riesgo

## Objetivo de entrega

Producir y mantener `xma` v0.1.1 para inspeccionar perfiles públicos, catalogar videos y descargarlos con documentación normalizada, reanudación, idempotencia y límites gobernados de hasta diez.

## Roles y fuente de verdad

- Leonel: Product Owner y human gate; autoriza transiciones y releases.
- ChatGPT/dot: Solution Architect, Scrum Master y DevOps Accelerate; gobierna alcance, arquitectura, DoD, prompts y validación.
- Codex: Engineering execution; modifica código, prueba y produce handoff.
- Git: verdad de código, cambios y releases.
- CI: verdad de verificaciones automatizadas.
- Biblioteca: verdad canónica de prompts, planes y PKC.

## Backlog por gates

| Bloque | Resultado | Actividades | Gate/DoD |
|---|---|---|---|
| B00 | Baseline de diseño | arquitectura, ADR, plan, gobierno | Q0 aprobado |
| B01 | Foundation | repositorio, `pyproject`, layout, CLI `--help`, lint/test/CI | Q1: build y tests PASS |
| B02 | Contratos | entidades, schemas, puertos, migración SQLite inicial | Q2: contract tests PASS |
| B03 | Discovery | adapter gallery-dl, inspect/sync, fixtures, cobertura | Q3-Técnico: implementación auditada; Q3-Público: exactamente 2 activos públicos distintos catalogados con `--limit 2` antes de B04; 0 o 1 no pasan |
| B04 | Download | yt-dlp, FFmpeg, staging, hash, sidecars | Q4: descarga reproducible PASS |
| B05 | Operación CLI | selección, progreso, retry, status, export, doctor | Q5 funcional PASS |
| B06 | Hardening | errores, seguridad, secret scan, rollback, docs | Q5 seguridad PASS |
| B07 | Release | package, changelog, SBOM/provenance cuando aplique | Q6 y `v0.1.0` aprobada |

Cada bloque contiene de 3 a 6 validaciones, se ejecuta en una rama aislada y termina con handoff. No se inicia el siguiente bloque por iniciativa de Codex.

## Métricas Accelerate adaptadas

- Lead time: autorización de bloque a handoff validable.
- Deployment/release frequency: releases certificadas, no número de commits.
- Change failure rate: bloques reabiertos o revertidos / bloques cerrados.
- Mean time to recovery: detección de regresión a restauración de baseline verde.
- Flow efficiency: tiempo activo / tiempo total del bloque.
- Desviación: actividades fuera del alcance aprobado / actividades ejecutadas; objetivo `0`.

No se fijan estimaciones de calendario sin medir B01 y B02. Se usarán tamaños `S/M/L`, dependencias y evidencia de ciclo real.

## Definition of Done común

1. Alcance aprobado y sin cambios laterales.
2. Branch y commits identificados.
3. Tests requeridos PASS; resultados negativos documentados.
4. No secretos, binarios descargados ni repositorio audiovisual en Git.
5. Evidencia y handoff Markdown trazables.
6. README, CHANGELOG y decisiones actualizados.
7. Rollback o reversión definida.
8. ChatGPT valida; Leonel autoriza transición.

## Siguiente paso gobernado

B06 implements the `0.2.0.dev0` complete-profile archive contract offline with explicit ALL mode,
`RESCAN_DEDUP_V2`, schema v3, safety pauses, resume, and typed provider exhaustion. PRM-0046 hardened
the boundary so ALL status names provider exhaustion as its goal, safety caps are checked against
verified state before discovery or mutation, and unexpected failures cross the CLI only as a
sanitized typed error. HND-0015 v0.1.1 records the synthetic evidence. The current state is
`B06_OFFLINE_HARDENED / PUBLIC_ACCEPTANCE_PENDING`. Public 20→50 acceptance and full-account
operation require a separate human decision; Telegram and WhatsApp remain future roadmap items.

AUD-0005 v0.1.2 cierra R-01–R-03 como `VALIDATED_WITH_OBSERVATIONS` dentro del alcance técnico
auditado. CI #35 pasó con 214 pruebas y 94.74 % de cobertura sobre el mismo tree. Este cierre no
acredita la aceptación pública histórica.

A-06 dispone ahora de un paquete local verificable y queda `WAITING_VALIDATION`; no se declara
aprobado. PRM-0012 se consumió una vez: Reuters produjo exactamente dos activos distintos con
`--limit 2` y la secuencia se detuvo antes de AP y BBCWorld. HND-0003 v0.3.0 enlaza el catálogo
y manifest por hash. Q3-Público y la transición general B03 siguen `BLOCKED`.

El catálogo y manifest permanecen temporalmente fuera de Git para entrega local a Leonel.
DOT-PRM-0014 puede activarse únicamente después de HND v0.3.0, CI verde y recepción del paquete
exacto. Si falta o no coincide su hash, A-06 vuelve a quedar bloqueado.

Siguen prohibidos merge, B05, descarga masiva, otros extractores, API X, cookies exportadas,
tags, releases y certificación. El rework B02 permanece separado y no integrado.

## Corte vertical B04 autorizado

GOV-DEC-0020 y ADR-0004 autorizan exclusivamente `xma download` con límite 1–5, tres pruebas
independientes 1/2/5 y máximo acumulado de ocho archivos. La implementación usa los contratos
SQLite existentes, gallery-dl para discovery y un adaptador HTTPS tipado para staging, hash y
movimiento atómico. No cambia el esquema ni `uv.lock`.

Después de pruebas offline verdes, Codex ejecuta Reuters 1/2/5, publica HND-0004, espera CI del PR
draft apilado y se detiene. No se autoriza merge, descarga masiva, B05, tag, release o
certificación.

La ejecución pública consumida se detuvo en el primer comando: Reuters límite 1 terminó con código
8 y cero archivos creados. No hubo retry y los límites 2/5 no se ejecutaron. La implementación
offline permanece entregada, pero el gate público queda `BLOCKED_PUBLIC_DOWNLOAD` hasta una nueva
decisión humana.

PRM-0017 incorporó diagnóstico sanitizado y consumió una recuperación pública: Reuters límite 1
pasó con Firefox; límite 2 terminó `PROVIDER_TIMEOUT` antes de descargar y sin residuos. La política
detuvo límite 5 y no habilitó fallback. Q4 continúa bloqueado y no autoriza B05.

PRM-0018 añadió un watchdog Linux con deadline total, 30 s por defecto y rango ampliado por decisión
humana a 5–180 s. El límite 2 no produjo activos con Firefox ni COOKIE_FILE; la ejecución final de
180 s terminó `PROVIDER_TIMEOUT` sin residuos. Límite 1 no se repitió y límite 5 no se ejecutó. El
total exitoso gobernado permanece en uno y Q4 continúa bloqueado.

PRM-0019 sustituyó la garantía SIGALRM principal por un worker Linux terminable y cambió download a
semántica acumulada. El padre persiste cada candidato inmediatamente y permite hasta dos peticiones
de 30 s. La ejecución límite 2 conservó el activo inicial pero no encontró otro; límite 5 no se
ejecutó. Q4 permanece bloqueado y la paginación durable/operación masiva siguen reservadas a B05.

PRM-0020 reemplazó Queue por Pipe síncrono, DTOs primitivos y terminales/telemetría explícitos. CI y
las regresiones offline quedaron verdes, pero la única aceptación límite 2 no superó
`EXTRACTOR_STARTED` antes de dos timeouts. El repositorio conserva exactamente un activo íntegro;
Q4 continúa `PARTIAL_PROGRESS_PRESERVED / PROVIDER_BLOCKED` y límite 5 no se habilitó.

GOV-AUTH-0026/PRM-0021 ejecutó BBCWorld límite 2 una sola vez desde cero. Los dos workers alcanzaron
el extractor sin candidato y el total permaneció cero; no se creó SQLite ni medio y límite 5 quedó
inhabilitado. Q4 continúa `PROVIDER_BLOCKED`; no hubo cambio funcional.

PRM-0022 verificó que discovery principal sí producía un activo y migró el worker de fork a spawn.
BBCWorld límite 2 pasó con dos activos; límite 5 preservó cuatro y terminó `WORKER_FAILED`. Q4 queda
`B04_LIMIT_2_VALIDATED / LIMIT_5_BLOCKED`; no se habilitan B05 ni nuevas ejecuciones.

PRM-0023 implementó el target `SINGLE_POST` con URL canónica y validación fail-closed. Pruebas y CI
funcionales pasaron, pero la única aceptación se bloqueó localmente antes de red porque la captura
ocupó el repositorio vacío. Estado `REWORK_REQUIRED`; no se repitió ni se habilita B05.

PRM-0024 repitió una sola vez con repositorio/logs separados y sin cambios funcionales. El post
exacto agotó discovery sin video ni candidato; total cero, manifest incompleto y cero residuos.
Estado `SINGLE_POST_NO_VIDEO`; no se autoriza otra ejecución ni B05.

PRM-0025 alineó el adaptador principal con el modo SINGLE_POST explícito. Inspect encontró el
video exacto y habilitó una única descarga, que completó `0 → 1` con catálogo, sidecar, manifest,
hashes e integridad coherentes. Estado `SINGLE_POST_DOWNLOAD_VALIDATED /
WAITING_CHAT_VALIDATION`; descarga masiva, merge y B05 permanecen fuera de alcance.

PRM-0026 reprodujo un falso `WORKER_FAILED` cuando EOF/terminal llegaba después del último
candidato válido. El rework mínimo conserva fail-closed antes de completar `remaining`. La única
reanudación BBCWorld completó `4 → 5`, preservó los cuatro hashes iniciales y añadió exactamente un
artifact/job. Estado `B04_LIMIT_5_VALIDATED / WAITING_CHAT_VALIDATION`; el gate humano sigue
pendiente y no se autoriza descarga masiva, merge o B05.

Leonel cerró B04 como `VALIDATED_WITH_OBSERVATIONS`. B05 puede comenzar exclusivamente en la rama
apilada `feature/xma-b05-durable-archive`, con paginación `RESCAN_DEDUP_V1`, checkpoints, rate
limiting, reanudación y status; la primera aceptación queda limitada a diez videos.

PRM-0027 implementó el corte durable y obtuvo 332 pruebas verdes con 90.44 % de cobertura. La
migración preservó cinco assets B04 e integridad, pero la aceptación única terminó código 9 antes
de discovery: el run inició conteo cero, calculó una página absoluta de dos y chocó con los cinco
existentes. El run quedó `RUNNING` en página cero. Estado `REWORK_REQUIRED`; no hay retry autorizado.

PRM-0028 corrigió la reconciliación verificada, targets absolutos y transiciones terminales. La
única reanudación completó `5 → 7 → 9 → 10` y conservó integridad, hashes y cero residuos. El
resultado reportó `existing_before=5`, pero `status` leyó el cero histórico porque el UPSERT no
actualizó ese campo. B05 sigue `REWORK_REQUIRED`; la ejecución pública fue consumida sin retry.

PRM-0029 corrigió únicamente el UPSERT y reparó offline el run completado. `status` confirma ahora
`existing_before=5`, total 10, página 3 y checkpoint 10; integridad y hashes permanecen válidos.
Estado `B05_LIMIT_10_VALIDATED / WAITING_CHAT_VALIDATION`. Esta versión queda limitada a diez;
cientos/miles, cursor remoto, scheduler y optimización de escala permanecen en backlog posterior.

PRM-0030 cierra B05 como `VALIDATED_WITH_OBSERVATIONS` y publica un runbook reproducible para
download 1/2/5, archive 10, SINGLE_POST y status offline. Wheel y sdist se construyeron offline.
La instalación aislada exigida no pudo completarse porque Python 3.12 y `gallery-dl` no estaban
disponibles en la caché local; no se habilitó red. El máximo de producto permanece en diez.

PRM-0031 corrigió la clonación para seleccionar explícitamente la rama apilada y consumió una sola
instalación aislada autorizada. CPython 3.12.13, las dependencias Linux de producción exportadas
desde `uv.lock`, el wheel local, todos los comandos help/version y `status` sintético offline
pasaron. Estado `B05_LOCAL_OPERABILITY_READY / WAITING_CHAT_VALIDATION`; máximo diez, sin release.

PRM-0032 crea `release/v0.1.0` desde main, consolida mediante squash el snapshot validado B05 y
reconcilia manualmente las defensas B02 compatibles con B03–B05. Prepara versión/licencia,
bundle Linux, SBOM, checksums, documentación y workflows; el PR hacia main permanece draft. No se
autoriza merge, tag, GitHub Release ni PyPI.

PRM-0033 completa el cumplimiento del candidato sin cambiar funcionalidad: sustituye el resumen de
licencia por GPL-2.0-only completo, incorpora como asset el source oficial verificado de gallery-dl
1.32.18, vuelve autocontenido el bundle y liga source SHA/tree, `uv.lock` y artifacts mediante
`RELEASE-MANIFEST.json` y `SHA256SUMS`. PR #6 permanece draft y en validación humana.


## Reauditoría A-06

AUD-0006 v0.1.0 registró `BLOCKED / EVIDENCE_NOT_AVAILABLE` porque el catálogo y manifest no
estaban adjuntos en la conversación de dot. No se inspeccionó GitHub, no se repitió el smoke y no
se invalidó la ejecución PRM-0012.

Leonel autorizó DOT-PRM-0015 para una única ejecución read-only que produzca AUD-0006 v0.1.1.
La ejecución solo puede comenzar cuando dot reciba directamente exactamente un `.sqlite3` y un
`.json` cuyos hashes coincidan con HND-0003 v0.3.0. Hasta el dictamen y decisión humana,
A-06, Q3-Público y B03 continúan `BLOCKED`; merge y B05 siguen sin autorización. La única
autorización B04 vigente es el corte vertical acotado por GOV-DEC-0020 y ADR-0004.

## Roadmap posterior a v1 — plataforma multimedia extensible

Después de liberar y estabilizar v0.1.0, el producto evolucionará gradualmente hacia un archivador
multiplataforma local-first. El orden gobernado es: núcleo común de adaptadores, Telegram,
WhatsApp y posteriormente otras plataformas priorizadas.

La v2 debe separar contratos de identidad, autenticación, discovery, descarga y checkpoints por
plataforma; preservar compatibilidad con repositorios v1; y añadir cursor remoto durable,
observabilidad y controles de capacidad antes de autorizar cientos o miles de activos. Cada
integración requiere revisión de términos, privacidad, autenticación, rate limiting, pruebas offline,
aceptación pública acotada, rollback y gate humano. No se implementarán bypasses de controles de
acceso o DRM.

La fuente ejecutiva de seguimiento será `docs/wiki/roadmap.md`, reconciliada con este plan,
CHANGELOG, ADR, Gate Register y notas de cada release.

## Estado de Product Wiki y GitHub Pages

La wiki de producto quedó integrada en `release/v0.1.0` mediante PR #7 y documenta producto,
arquitectura, releases, gobierno y roadmap X → Telegram → WhatsApp → otras plataformas. Los
documentos operativos y de gobierno del repositorio continúan siendo la fuente canónica.

El workflow `.github/workflows/pages.yml` ya construye `docs/wiki` y queda preparado para
republicar automáticamente cuando cambie `docs/wiki/**` o el propio workflow en `main`,
`release/v0.1.0` o la rama documental autorizada.

Estado: `WIKI_INTEGRATED / PAGES_ACTIVATION_PENDING`. La activación administrativa
**Settings → Pages → GitHub Actions**, la ejecución del workflow Pages y la verificación de
`https://eventmgmtplatform.github.io/x-media-archiver/` quedan pendientes hasta disponer de una
sesión GitHub autorizada. La URL no se declara publicada ni verificada.

Este pendiente no modifica funcionalidad, dependencias, esquema, `uv.lock` ni artifacts del
candidato. Tampoco autoriza merge a `main`, tag, GitHub Release o publicación PyPI.

## Cierre de v0.1.0

PRM-0034 fue autorizado por Leonel y PR #6 se integró mediante squash en `main`. El primer intento
del workflow de publicación falló antes de crear jobs por sintaxis de evaluación y quedó registrado
como GOV-RWK-0041. PR #8 corrigió únicamente esa frontera.

El commit `c997cce488b4486ffd8dc079cd25819bec402b77` quedó fijado por el tag anotado e inmutable
`v0.1.0`. GitHub Release 428337129 fue publicada el 2026-10-29 con diez assets, incluyendo bundle
Linux, wheel, sdist, manifest, SBOM, requisitos, licencia, avisos, source de gallery-dl y checksums.
El workflow descargó de nuevo los assets, verificó `SHA256SUMS`, extrajo el bundle y ejecutó
help/version sin Python o uv.

Estado final: `V0.1.0_RELEASED / POSTRELEASE_VERIFIED`. GitHub Pages y su despliegue permanecen
pendientes; PyPI no fue autorizado ni publicado. La siguiente evolución funcional pertenece al
backlog v2 y requiere nuevo gate humano.

## Hotfix v0.1.1

PRM-0032 con Addendum 001 autoriza una rama desde main para recuperar jobs `FAILED_FINAL` sin
artifact/residuo, convertir límites absolutos inferiores en no-op, añadir `--add`, acotar scan y
persistir la política `provider-best`. Download acepta 1–10 y archive conserva su máximo 10; ningún
flujo permite más de diez, operación masiva o scheduler. La promoción requiere suite/CI verdes y la
única aceptación 0→1→2→5 seguida por un no-op absoluto, sin retry manual.

La implementación completó 391 pruebas con cobertura 90.63%, CI verde y la secuencia pública única
0→1→2→5. El `--limit 1` posterior fue un no-op offline que conservó cinco artifacts. Estado:
`V0.1.1_HOTFIX_VALIDATED / WAITING_CHAT_RELEASE_DECISION`; publicación sigue sin autorización.

PRM-0034 autoriza únicamente la preparación del release candidate: reconciliación documental,
validación local/distributiva, rama `release/v0.1.1` fast-forward y CI quality/RC sobre el mismo
commit. No autoriza cambios runtime, X, merge, tag, GitHub Release, PyPI, v0.1.2 o v0.2.0.

PRM-0038/0038B autoriza v0.1.2 media recovery con clasificación sanitizada, una renovación acotada,
`download --add 1..20`, total máximo 20 y archive máximo 20. `download --limit` permanece 1..10.

PRM-0035 integró PR #10 mediante squash en el commit firmado
`9490dbdfd43517a08c68745147d3a6d34d23af25`, conservando el tree RC
`f5a154687d984d0e50596a8daf17b7a4bd565dda`. El tag anotado `v0.1.1` apunta a ese commit y
el workflow 40961716484 creó un Release draft con diez assets verificados.

PRM-0036 publicó exclusivamente ese draft. GitHub Release 428434769 quedó público el 2026-10-29;
`SHA256SUMS`, bundle autónomo 0.1.1, wheel, sdist, manifest, SBOM, licencia, requisitos y source
de gallery-dl fueron verificados públicamente. PyPI permanece sin publicar.

Estado de producto: `V0.1.1_RELEASED / POSTRELEASE_VERIFIED`. PRM-0037 limita el cierre a
documentación y ramas obsoletas. GitHub Pages permanece pendiente de activación administrativa y
no afecta la disponibilidad del Release.

## Release v0.1.2 y cierre postrelease

PRM-0038 a PRM-0040 entregaron clasificación MEDIA_* sanitizada, renovación acotada, continuación
tras candidatos fallidos, deadline de discovery activo, `download --add 1..20`, total máximo 20 y
`archive --limit 20`. La aceptación pública única completó 0→5→10→20 con integridad, provider-best,
hashes previos estables y cero residuos. No ocurrió DownloadError en la prueba pública; esa frontera
se valida exclusivamente con fixtures offline deterministas.

Leonel declaró el alcance `VALIDATED_WITH_OBSERVATIONS`. v0.1.2 fue integrada en main mediante PR
#12, etiquetada con el tag anotado `v0.1.2` y publicada como GitHub Release 428531308 el 2026-10-30.
Los diez assets, checksums, bundle standalone, wheel, sdist, SBOM, licencia, corresponding source y
portabilidad Ubuntu 22.04/24.04 quedaron verificados. PyPI no fue publicado.

PRM-0044 limita el cierre a reconciliación documental, CI, squash y limpieza de las ramas temporales
v0.1.2. GitHub Pages/Actions continúa pendiente de habilitación; Telegram y WhatsApp permanecen en
el roadmap futuro; soporte masivo, scheduler y cursor remoto eficiente siguen diferidos. v0.2.0 no
ha comenzado y no se infiere por este cierre.
