# XMA-CLI-001 — AUD-0005 B03 Auth Boundary Rework 002

**Versión:** 0.1.2  
**Fecha:** 2026-10-29 UTC  
**Auditor:** dot  
**Mandato:** XMA-CLI-001-DOT-PRM-0013 v0.1.0  
**Dictamen único:** **VALIDATED_WITH_OBSERVATIONS**  
**Alcance del dictamen:** rework técnico R-01–R-03, no aceptación pública ni cierre de B03.  
**Destino previsto:** `docs/audits/XMA-CLI-001_AUD-0005_B03-AUTH-BOUNDARY-REWORK-002_v0.1.2.md`; preparado para revisión y eventual versionado humano, sin publicación por dot.

## 1. Resumen ejecutivo

Las precondiciones de identidad, descendencia, handoff y CI se cumplieron. Las reproducciones sintéticas offline y la revisión documental no encontraron fallos en R-01, R-02 o R-03 dentro de sus límites. CI #35 fue verde con 214 pruebas y cobertura 94.74 % sobre un tree idéntico al auditado.

El dictamen valida con observaciones el **rework técnico** examinado. No valida la vigencia de ninguna sesión real, ni demuestra la aceptación pública histórica. A-06 sigue **EVIDENCE_NOT_AVAILABLE**: no se inspeccionó ni reconstruyó el catálogo original. **Q3-Público y la transición general B03 permanecen BLOCKED**, aunque los controles técnicos pasen. La decisión posterior de gates corresponde a León; no se autoriza smoke, merge, B04, tag, release ni certificación.

## 2. Identidad y precondiciones

- Repositorio: [eventmgmtplatform/x-media-archiver](https://github.com/eventmgmtplatform/x-media-archiver), [PR #3](https://github.com/eventmgmtplatform/x-media-archiver/pull/3), rama `feature/xma-b03-discovery`.
- HEAD: `4c28b8e3e233b794e1dacf0abb2597e28d2c01d0`. Tree: `0c211a97c0920a167cd4bff4fa40cc18abdd3bc9`. GitHub vincula ese commit y ese tree; al cierre de la revisión el PR seguía en el HEAD fijado, abierto, draft y sin merge.
- Base del PR: `main`, `b2bdca7961f00d54f2465a4f8d26b2003340c3b9`. Baseline gobernada `b5c790ebb6131598f1fe114a98fd2ffe169d898f`, tree `375bbc635517aefed920d2d40a0fbc177141f486`. [Comparación](https://github.com/eventmgmtplatform/x-media-archiver/compare/b5c790ebb6131598f1fe114a98fd2ffe169d898f...4c28b8e3e233b794e1dacf0abb2597e28d2c01d0): dos commits delante, ninguno detrás, merge-base baseline. Cadena: baseline → `1acebcf4edb16700c8f5a7963e3e0cfdd9d440a7` (tree `5e908f2c6f6efc1f0618dcd980da548f92bcac84`) → HEAD. La ancestría no demuestra por sí sola la ausencia histórica universal de force-push.
- La baseline contiene AUD-0005 v0.1.1, PRM-0011 y DOT-PRM-0013, conservados como blobs idénticos en HEAD. [DOT-PRM-0013](https://github.com/eventmgmtplatform/x-media-archiver/blob/4c28b8e3e233b794e1dacf0abb2597e28d2c01d0/docs/prompts/XMA-CLI-001_DOT-PRM-0013_B03-AUTH-BOUNDARY-REWORK-002-AUDIT_v0.1.0.md) leído íntegro.
- [HND-0003 v0.2.2](https://github.com/eventmgmtplatform/x-media-archiver/blob/4c28b8e3e233b794e1dacf0abb2597e28d2c01d0/docs/handoffs/XMA-CLI-001_HND-0003_B03-20261028-001_v0.2.2.md), blob `01caf4870a69126c8ef87eda0e7f42ab682e356d`, presente en HEAD y leído íntegro.
- [CI #35 / run 40798491697](https://github.com/eventmgmtplatform/x-media-archiver/actions/runs/40798491697): **SUCCESS**, job `quality` 123200626461 y pasos exitosos. Logs: **214 passed**, cobertura **94.74 %**, Ruff, mypy y build aprobados. El checkout fue el merge sintético `e669890997ecc34e65c8b894bd80a4a0cb241f90`, cuyo tree Git es exactamente `0c211a97c0920a167cd4bff4fa40cc18abdd3bc9`. Esto no es un merge del PR. Las 214 pruebas y cobertura son evidencia CI, no un resultado de pytest local de dot.

## 3. Matriz R-01–R-03

| Control | Estado | Evidencia independiente y límites |
|---|---|---|
| R-01 sesión fail-closed | PASS | 62 combinaciones con lector SQLite y filesystem sintéticos: entradas incompletas y error rechazan con mensaje constante, código CLI 3, sin job/UoW/catálogo ni continuación guest. Los dos valores no vacíos pasan la frontera local con job falso; no se prueba sesión real. Funciones reales XMA, dependencias externas sustituidas. |
| R-02 symlink circular | PASS | 30 comprobaciones de 5 ubicaciones de bucle por lector, adaptador y funciones inspect/sync con variantes JSON; error XMA sanitizado, código 3 y ningún job, conexión SQL, UoW o catálogo. Contención y selectores inválidos probados. Cuerpos reales cargados por AST, con stubs; no se ejecutó parser real Typer. |
| R-03 documentación | PASS | README, Gate Register, Implementation Plan, HND y cuerpo PR leídos; estados de entrega pendiente de validación, A-06 no disponible y Q3-Público/B03 bloqueados son consistentes. No se observó autorización de merge/B04 o certificación. |

## 4. Reproducciones independientes

### R-01

Se probaron: diccionario vacío; solo `ct0`; solo `auth_token`; cada valor vacío con el otro presente; ambos vacíos; ambos valores sintéticos no vacíos; error del lector por tabla sintética ausente; y modo anónimo. Se ejercitaron lector y funciones reales de servicio `inspect`, `sync --dry-run`, `sync` y funciones CLI equivalentes; el anónimo no llama al lector.

En cada caso incompleto o de error se observó el mensaje público constante `authenticated Firefox session is unavailable`, sin marcadores sintéticos en las salidas/logs/JSON/catálogos inspeccionados. Los spies no registraron creación o ejecución de job, UoW ni catálogo y no hubo fallback guest/anónimo. Los archivos de entrada sintéticos conservaron bytes y nombres. El caso completo y el anónimo usaron únicamente job falso; los catálogos creados para casos válidos eran sintéticos. Estos resultados no determinan la vigencia de una sesión real.

La frontera depende del contrato del lector: el adaptador no revalida un diccionario inválido artificialmente inyectado por un doble, pero el lector real examinado rechaza las entradas incompletas antes de devolverlas.

### R-02

Se generaron bucles de enlace exclusivamente sintéticos en raíz, inventario, perfil, base y par mutuo. En lector/adaptador/inspect/sync y salidas JSON examinadas el resultado fue error controlado sin `RuntimeError`, traceback ni marcador en la salida pública; no se creó job, conexión SQL, UoW o catálogo. Se probaron además siete rechazos de contención/selección, una selección exacta válida y 16 selectores inválidos. Se verificó captura estrecha de `RuntimeError` alrededor de `Path.resolve` y ausencia de nuevo `except Exception` general en el lector. No se ejecutó el renderizado real de Typer/Rich.

Fuentes: [lector](https://github.com/eventmgmtplatform/x-media-archiver/blob/4c28b8e3e233b794e1dacf0abb2597e28d2c01d0/src/xma/adapters/discovery/firefox_auth.py), [runner](https://github.com/eventmgmtplatform/x-media-archiver/blob/4c28b8e3e233b794e1dacf0abb2597e28d2c01d0/src/xma/adapters/discovery/gallery_dl.py), [tests lector](https://github.com/eventmgmtplatform/x-media-archiver/blob/4c28b8e3e233b794e1dacf0abb2597e28d2c01d0/tests/adapters/test_firefox_auth.py), [tests CLI](https://github.com/eventmgmtplatform/x-media-archiver/blob/4c28b8e3e233b794e1dacf0abb2597e28d2c01d0/tests/test_cli.py).

### R-03

[README](https://github.com/eventmgmtplatform/x-media-archiver/blob/4c28b8e3e233b794e1dacf0abb2597e28d2c01d0/README.md), [Gate Register](https://github.com/eventmgmtplatform/x-media-archiver/blob/4c28b8e3e233b794e1dacf0abb2597e28d2c01d0/docs/governance/XMA-CLI-001_GATE-REGISTER_v0.1.0.md), [Implementation Plan](https://github.com/eventmgmtplatform/x-media-archiver/blob/4c28b8e3e233b794e1dacf0abb2597e28d2c01d0/docs/planning/XMA-CLI-001_IMPLEMENTATION_PLAN_v0.1.0.md), HND y cuerpo del PR distinguen implementación entregada y `WAITING_VALIDATION` de la evidencia pública no disponible. Las menciones históricas a dos activos no constituyen comprobación independiente.

## 5. Regresión y alcance

- 99 combinaciones sintéticas de política pública: únicamente `protected is False` avanza; `true`, ausente, null, números, cadenas y contenedores se rechazan antes de UoW. Cinco casos de selección: anónimo por defecto, pareja Firefox/perfil válida y rechazo de opciones parciales u otro navegador. Tres spies de runner verifican selección y configuración. Son comprobaciones del harness, no 107 pruebas pytest.
- Se observó `gallery-dl` 1.32.18 como extractor fijado, descarga y downloader deshabilitados, caché en memoria y actualización de cookies deshabilitada. Lector de Firefox propio usa SQLite read-only/immutable y entrega a la dependencia datos en memoria, evitando el fallback upstream de copia de la base. No se observó exportación o persistencia de cookies en el flujo revisado; esto no certifica ejecución en todo entorno.
- El workflow y pruebas inspeccionados no ejecutan smoke ni acceso funcional observado a X, navegador o perfiles reales. La instalación de dependencias CI puede usar red: no se afirma aislamiento total de red. El mínimo de cobertura configurado es 90 %; CI reportó 94.74 %.
- Diff baseline→HEAD: ocho archivos, lector Firefox, tres pruebas, README, Gate Register, Implementation Plan y HND. `uv.lock`, workflow, dominio, catálogo y esquema conservan blobs idénticos. Sin implementación B04/B05 añadida en el diff.
- Árbol recursivo sin truncar: no se identificaron bases locales, cookies, medios, thumbnails, sidecars ni staging rastreados por nombre. Diff inspeccionado sin rutas personales o secretos reales visibles; valores de prueba son sintéticos. No se realizó un escaneo exhaustivo de secretos de todos los blobs ni del historial.
- Comentarios de conversación, revisiones y comentarios inline consultados: vacíos; no se observaron hilos inline. Refs de tags y releases: vacíos. PR abierto/draft/sin merge. Estas verificaciones corresponden al corte observado, no prueban actividades externas a GitHub.

## 6. Evidencia, declaraciones y limitaciones

**Comprobado por dot:** identidad Git/tree y relación del tree probado por CI; logs y resultado CI; contenido de documentos y diff; casos sintéticos aquí descritos, ejecutados offline; estado del PR y refs consultadas. Los 30 blobs de código/tests/configuración materializados para la reproducción se cotejaron con el tree.

**Declarado, no verificado independientemente:** resultados históricos Reuters/AP/BBCWorld y presunta catalogación de dos activos. La auditoría no inspeccionó SQLite original ni ejecutó smoke, y HND v0.2.2 mantiene **EVIDENCE_NOT_AVAILABLE**. No se puede afirmar integridad, conteo ni dos identidades verificadas.

**Límites técnicos:** gallery-dl, Typer y Rich se sustituyeron por stubs en los harness locales; no se ejecutó el parser/renderer real ni la suite pytest completa local. R-02 usó cuerpos reales cargados por AST. El verde y la cobertura son evidencia de CI, no una reproducción local completa. Casos sintéticos no prueban el estado de una cuenta, sesión o plataforma real. No se accedió a X, Firefox, perfiles, cookies o SQLite originales ni se reconstruyó evidencia.

## 7. Riesgos residuales y rollback

1. A-06 indisponible impide la aceptación pública independientemente del rework técnico. Conservar el bloqueo hasta una decisión y evidencia gobernadas por León.
2. Funciones con stubs y cobertura CI no demuestran todos los entornos, cambios upstream o validez remota de credenciales. No inferir exposición real ni ausencia universal de secretos.
3. Si se descubre una regresión, mantener el PR draft y suspender uso autenticado pendiente de evaluación. Un revert trazable de los commits del rework puede ser considerado por el equipo y ejecutado por Codex bajo nueva autorización, preservando historial y evidencia; no borrar catálogos ni reescribir historia. Esta auditoría no ejecuta ni autoriza rollback.

## 8. Dictamen y próxima acción

**VALIDATED_WITH_OBSERVATIONS** exclusivamente para R-01–R-03 y la regresión examinada, por los límites de entorno y evidencia descritos. **Q3-Público: BLOCKED. Transición general B03: BLOCKED. A-06: EVIDENCE_NOT_AVAILABLE.** No se autoriza smoke, merge, B04/B05, tag, release ni certificación.

**Próxima acción:** León y Chat revisan y deciden si versionar este informe y cómo gobernar, mediante un mandato humano separado, la resolución de A-06 y de los gates. No tratar la declaración histórica como evidencia comprobada ni realizar una nueva prueba por el solo hecho de esta validación.
