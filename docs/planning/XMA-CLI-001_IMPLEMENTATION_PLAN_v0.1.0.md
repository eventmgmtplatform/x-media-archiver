# XMA-CLI-001 — Plan de implementación

**Versión:** 0.1.0  
**Estado:** ACTIVE / Q2 CLOSED / B03 GOVERNED / B04 VALIDATED_WITH_OBSERVATIONS / B05 REWORK_REQUIRED
**Método:** Engineering OS + Scrum/Accelerate proporcional al riesgo

## Objetivo de entrega

Producir `xma` v0.1.0 capaz de inspeccionar un perfil público, catalogar videos disponibles y descargarlos con documentación normalizada, reanudación e idempotencia.

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


## Reauditoría A-06

AUD-0006 v0.1.0 registró `BLOCKED / EVIDENCE_NOT_AVAILABLE` porque el catálogo y manifest no
estaban adjuntos en la conversación de dot. No se inspeccionó GitHub, no se repitió el smoke y no
se invalidó la ejecución PRM-0012.

Leonel autorizó DOT-PRM-0015 para una única ejecución read-only que produzca AUD-0006 v0.1.1.
La ejecución solo puede comenzar cuando dot reciba directamente exactamente un `.sqlite3` y un
`.json` cuyos hashes coincidan con HND-0003 v0.3.0. Hasta el dictamen y decisión humana,
A-06, Q3-Público y B03 continúan `BLOCKED`; merge y B05 siguen sin autorización. La única
autorización B04 vigente es el corte vertical acotado por GOV-DEC-0020 y ADR-0004.
