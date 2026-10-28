# XMA-CLI-001 — AUD-0003 B03-REWORK-003

**Versión:** 0.1.3  
**Fecha:** 2026-10-28, 21:05–21:12 UTC  
**Auditor:** dot  
**Dictamen:** **REWORK_REQUIRED**  
**Q3:** no aprobado. Producto no certificado. B04 no autorizado.

## 1. Resumen ejecutivo

El PR #3 está abierto, draft y sin merge en el HEAD obligatorio `496e6ce4f1559c154a88dcd3985dbced1a7cf8af`, tree `d066237f0f3715882780af8feec4f51e5a014fc8`. CI canónico #20 / `40768500528` pasó: 130 pruebas y 94.80 % de cobertura; el tree del merge sintético probado coincide exactamente con el del HEAD.

Los cinco negativos exigidos se rechazaron como `DiscoveryContractError` en el mapper real y, en las fronteras inspect/sync reproducidas offline, terminaron con código 5, mensaje sanitizado y sin directorio ni catálogo. Sin embargo, **el cambio altera el resultado de duraciones positivas válidas respecto de la baseline funcional**, en contradicción con la conservación requerida por PRM-0006 y afirmada en HND/README. Por ejemplo, el float `0.0005` segundos pasa de 0 ms a 1 ms. Se confirmó a través del mapper y la persistencia aislada de sync. Es una carencia recuperable: **REWORK_REQUIRED**. No procede BLOCKED porque `AuthRequired` no es el único impedimento restante.

La aceptación pública de dos activos sigue sin acreditarse. Los resultados de Reuters/AP/BBCWorld son evidencia histórica sanitizada del ejecutor, no observación independiente actual. Esta auditoría no accedió a X ni repitió el smoke.

## 2. Fuentes y precondiciones

Lectura íntegra de [DOT-PRM-0006](https://github.com/eventmgmtplatform/x-media-archiver/blob/496e6ce4f1559c154a88dcd3985dbced1a7cf8af/docs/prompts/XMA-CLI-001_DOT-PRM-0006_B03-REWORK-AUDIT-003_v0.1.0.md), [PRM-0006](https://github.com/eventmgmtplatform/x-media-archiver/blob/496e6ce4f1559c154a88dcd3985dbced1a7cf8af/docs/prompts/XMA-CLI-001_PRM-0006_B03-REWORK-003_v0.1.0.md), [AUD-0003 v0.1.2](https://github.com/eventmgmtplatform/x-media-archiver/blob/496e6ce4f1559c154a88dcd3985dbced1a7cf8af/docs/audits/XMA-CLI-001_AUD-0003_B03-REWORK-002_v0.1.2.md) y [HND-0003 v0.1.3](https://github.com/eventmgmtplatform/x-media-archiver/blob/496e6ce4f1559c154a88dcd3985dbced1a7cf8af/docs/handoffs/XMA-CLI-001_HND-0003_B03-20261028-001_v0.1.3.md). Además se inspeccionaron GitHub, código, tests, documentación y logs.

| Control | Evidencia |
|---|---|
| [PR #3](https://github.com/eventmgmtplatform/x-media-archiver/pull/3) | OPEN, draft, sin merge ni auto-merge; HEAD obligatorio `496e6ce4f1559c154a88dcd3985dbced1a7cf8af`. |
| Tree | `d066237f0f3715882780af8feec4f51e5a014fc8`, confirmado por Git Data. |
| Baselines | Funcional `ce3c067542827f702caa4bfd89fc9bd9ac4905b1`; gobernada `1e952d5d8848fff1c5ac9e1c7e9124d3b637a25b`. Ambas son ancestros exactos; respectivamente ahead 5 y 2, behind 0. |
| [CI #20](https://github.com/eventmgmtplatform/x-media-archiver/actions/runs/40768500528) | Completed/success, un job `quality` / `123099033262`, 13 pasos exitosos. Locked sync, Ruff, mypy, 130 tests, 94.80 %, sdist y wheel. |
| Identidad del checkout | CI ejecutó merge sintético `be6ba02f266d0c06b4c8620218239a49de8ba625` con padres `b2bdca7...` y HEAD. Su tree es exactamente `d066237...`. No se afirma checkout literal del commit HEAD. |
| Discusión | 0 comentarios, 0 revisiones y 0 hilos; PR sin auto-merge. |

CI usó Python 3.12.16 y Ruff comprobó 56 archivos; HND informa localmente Python 3.12.14 y 55 archivos. Son entornos diferentes. GitHub no retuvo artefactos del run; el build se confirma por logs, no por inspección independiente del wheel remoto.

## 3. Commits y alcance

[Comparación funcional](https://github.com/eventmgmtplatform/x-media-archiver/compare/ce3c067542827f702caa4bfd89fc9bd9ac4905b1...496e6ce4f1559c154a88dcd3985dbced1a7cf8af): cinco commits y 11 archivos:

1. `3adf223ab55bf8c0090e5b91a385e90c66f1c224`, publicación AUD v0.1.2.
2. `ca23e12fe8a4020e6c5ae17fdb867b6d2a8ee158`, autorización PRM-0006.
3. `1e952d5d8848fff1c5ac9e1c7e9124d3b637a25b`, prompt DOT-PRM-0006 y baseline gobernada.
4. `978e02492f01da3d26b3e2a690b2a3e594b0ede7`, cambio funcional, tree `4cf31a37d3fd108fee194384f7feb42a70333f89`.
5. `496e6ce4f1559c154a88dcd3985dbced1a7cf8af`, publicación documental y handoff.

[Comparación gobernada](https://github.com/eventmgmtplatform/x-media-archiver/compare/1e952d5d8848fff1c5ac9e1c7e9124d3b637a25b...496e6ce4f1559c154a88dcd3985dbced1a7cf8af): dos commits y ocho archivos: `README.md`, `CHANGELOG.md`, Gate Register, Implementation Plan, HND v0.1.3, `src/xma/adapters/discovery/gallery_dl.py`, `tests/adapters/test_gallery_dl_discovery.py` y `tests/test_cli.py`.

Tree no truncado: 64 blobs y 25 árboles, sin symlinks ni submódulos; blobs recuperados verificados contra sus SHA Git. `uv.lock`, workflow, CLI productiva, servicio, catálogo/esquema y módulos B02 permanecen sin cambios desde baseline funcional. El lock difiere de main por B03 anterior, no por este rework.

## 4. Matriz de conformidad

| Control | Resultado | Evidencia / límite |
|---|---|---|
| Identidad, ascendencia, CI | PASS | SHA/tree obligatorios y árbol de CI coinciden; 130 pruebas y 94.80 %. |
| Cinco negativos requeridos | PASS | Mapper real rechaza todos con mensaje constante; ver sección 5. |
| Antes de perder signo | PASS para casos probados | [Mapper](https://github.com/eventmgmtplatform/x-media-archiver/blob/496e6ce4f1559c154a88dcd3985dbced1a7cf8af/src/xma/adapters/discovery/gallery_dl.py#L261-L278) convierte cadenas con Decimal y verifica negatividad antes de multiplicar/redondear. |
| Inspect y sync, error / no persistencia | PASS para casos probados | Los cinco negativos en ambas fronteras dieron código 5 sanitizado, sin stdout, traceback, marcador, directorio o SQLite. No se persistió cero por ellos. Ver limitación del harness. |
| Cero y positivos representativos | PASS parcial | `0`, `0.0001`, `0.0006`, `'1e-400'` y `'12.5'` aceptados conforme a política de HND; no implica conservación completa frente a baseline. |
| Positivos válidos y compatibilidad | **FAIL** | Floats `0.0005` y `0.0025` cambian respectivamente de 0→1 y 2→3 ms frente a `ce3c067`; mapper y sync reproducidos. [PRM-0006](https://github.com/eventmgmtplatform/x-media-archiver/blob/496e6ce4f1559c154a88dcd3985dbced1a7cf8af/docs/prompts/XMA-CLI-001_PRM-0006_B03-REWORK-003_v0.1.0.md#L25-L31) pide conservar comportamiento de positivos válidos; [HND](https://github.com/eventmgmtplatform/x-media-archiver/blob/496e6ce4f1559c154a88dcd3985dbced1a7cf8af/docs/handoffs/XMA-CLI-001_HND-0003_B03-20261028-001_v0.1.3.md#L42-L54) afirma conservación histórica. |
| No finitos, booleanos y rangos | PASS en casos probados | 24 combinaciones no finitas/booleanas de num, width, height y duration rechazadas; rangos representativos SQLite comprobados. |
| R-01 a R-04, R-06, R-07 | PASS por regresión estática y CI | Evidencia previa, separación B02, JSON, variantes metadata-only, límite y cursor preservados. R-05 queda abierto por compatibilidad positiva. |
| Suite offline y ausencia de elementos prohibidos | PASS con límites | Tests inspeccionados usan dobles; reproducciones bloquearon sockets. Revisión estática de suite no equivale a medición global de red. Sin archivos prohibidos ni secretos detectados en tree; búsqueda por patrones no es garantía absoluta. |

## 5. Reproducción sintética offline

| Entrada duración | Mapper HEAD | Fronteras inspect/sync |
|---|---|---|
| `-0.0001` | DiscoveryContractError constante | Código 5, sin directorio/SQLite. |
| `-0.0005` | DiscoveryContractError constante | Código 5, sin directorio/SQLite. |
| `-5e-324` | DiscoveryContractError constante | Código 5, sin directorio/SQLite. |
| `'-0.0001'` | DiscoveryContractError constante | Código 5, sin directorio/SQLite. |
| `'-1e-400'` | DiscoveryContractError constante | Código 5, sin directorio/SQLite. |
| `0`, `0.0001`, `0.0006`, `'1e-400'`, `'12.5'` | Aceptadas; submilisegundo positivo documentado como 0 ms cuando redondea a cero. | Casos válidos representativos aceptados. |

Los cinco errores usaron el texto `gallery-dl numeric metadata violates the B03 contract`, sin valor crudo ni marcador sintético. En total se ejecutaron 77 casos de mapper y 76 de funciones de comando; un hook bloqueó eventos de socket y no se intentó conexión. Se utilizaron fuentes y fixtures fijados al SHA y verificados con hashes Git, sin modificarlos.

**Limitación de ejecución:** para la reproducción local, `gallery_dl` se sustituyó solo para imports y se usó un shim de decoradores/anotaciones Typer con funciones de comando reales, proveedor real, mapper y servicio. Esto verifica la frontera de controladores, **no** un lanzamiento completo de Typer/CliRunner. CI sí ejecutó los tests reales del repositorio, incluida la regresión CLI con runner offline. Los catálogos positivos de prueba fueron temporales y aislados, no rastreados ni publicados.

### Hallazgo RW-02 — deriva en redondeo de positivos

Comparación independiente del mapper real y funciones inspect/sync entre baseline `ce3c067` y HEAD:

| Duración válida | Baseline | HEAD | Observación |
|---|---:|---:|---|
| float `0.0005` | 0 ms | 1 ms | Sync persiste el resultado diferente. |
| float `0.0025` | 2 ms | 3 ms | Sync persiste el resultado diferente. |
| cadena `'0.0005'` | 0 ms | 0 ms | Misma representación decimal, distinta del float nuevo. |
| cadena `'0.0025'` | 2 ms | 2 ms | Sin cambio observado. |

El algoritmo anterior redondeaba `float(value) * 1000`; el nuevo usa `Decimal.from_float` y multiplica el valor binario exacto antes de redondear. Aunque ambos utilicen redondeo al par más próximo, operan sobre cantidades intermedias diferentes. No se trata del defecto negativo anterior ni de una prueba de explotación real: es una regresión de compatibilidad reproducida con valores sintéticos válidos. HND y README deben dejar de afirmar conservación histórica hasta corregir o redefinir explícitamente el contrato mediante el gobierno correspondiente.

La prueba CLI previa de `width=json.loads('1e400')` fue reemplazada por casos de duración negativa; la reproducción independiente de esa frontera continúa pasando. Es una desviación recuperable frente a la preservación de regresiones exigida por PRM-0006, no un fallo observado de normalización; debe restaurarse esa prueba en el rework.

## 6. Trazabilidad, riesgos y quality gates

- **CI, lock, build:** PASS según logs remotos. `uv.lock` y workflow intactos frente a baseline funcional. La instalación de dependencias puede usar red; no se encontró smoke en el workflow ni extracción real en tests revisados.
- **R-01:** HND v0.1.1 conserva orden Reuters→AP→BBCWorld, comandos, tiempos, salida 3, ausencia de catálogo declarada y conteos N/A. No equivale a confirmar físicamente el entorno original ni la causa interna exacta de X.
- **R-02:** Q3 no aprobado, `WAITING_VALIDATION`, producto no certificado y B04 no autorizado. HND v0.1.3 corrige honestamente la afirmación histórica de v0.1.2 sobre negativos, pero su nueva afirmación de compatibilidad positiva es refutada por RW-02.
- **R-03:** rework B02 sigue separado y pendiente; no se certifica aquí. Persisten riesgos de catálogos antiguos y `cursor=None` sin garantía de completitud.
- **Estado remoto:** main en `b2bdca7961f00d54f2465a4f8d26b2003340c3b9`; refs tags y releases vacíos, sin B04 observado. Historia lineal y timeline sin force-push observado no prueban inexistencia de eventos o refs borrados.
- **Riesgo funcional:** el mismo dato semántico puede producir resultados diferentes según se entregue como float o como cadena en fronteras de medio milisegundo; puede cambiar metadatos persistidos.
- **Alcance:** sin medios, bases locales, respuestas reales, cookies, secretos, otros extractores o componentes prohibidos detectados en tree/diff. No se realizaron descargas ni smoke. Las declaraciones del filesystem original y el no acceso histórico de Codex no son observables físicamente desde esta auditoría.

## 7. Rework y rollback

Solicitar al gobernante preparar un rework acotado para Codex: conservar el rechazo de todo negativo antes de pérdida de signo y restablecer o definir explícitamente, mediante decisión versionada, el comportamiento de redondeo de positivos frente a la baseline. Añadir regresiones de mapper y frontera CLI/sync para floats y cadenas en `0.0005`, `0.0025` y otros empates, controles positivos no limítrofes y los cinco negativos; restaurar la prueba CLI no finita retirada. Contrastar los valores persistidos, actualizar HND/documentación y publicar CI y handoff para un nuevo HEAD. No se implementa una solución en esta auditoría.

Contención: mantener PR draft y detener certificación. Revertir solo REWORK-003, de ser autorizado, mediante commits nuevos: primero publicación documental y después `978e024`, sin reescribir historia, borrar evidencia ni modificar catálogos. Para contención integral B03, seleccionar `b2bdca7` en entorno aislado. No se ejecutó rollback.

## 8. Dictamen y próxima acción

**REWORK_REQUIRED.** Los negativos exigidos se corrigen, pero la conservación de positivos válidos y la exactitud de la documentación fallan. La condición de BLOCKED exige que solo reste el impedimento público, lo que no ocurre. No hay gate humano versionado para VALIDATED_WITH_OBSERVATIONS ni desviación material irrecuperable que exija FAILED.

**Próxima acción exacta:** Chat gobierna el rework mínimo de compatibilidad de redondeo y pruebas; Codex implementa y publica nueva evidencia; dot audita el nuevo SHA/tree y CI. La aceptación pública permanece bloqueada hasta evidencia suficiente o redefinición humana versionada. No aprobar ni fusionar PR #3; no iniciar B04.

**Integridad:** auditoría de solo lectura de GitHub con pruebas sintéticas aisladas. No se modificaron código, fixtures, ramas, PR, comentarios, revisiones ni estados; no hubo acceso a X, merge, tag ni release.

