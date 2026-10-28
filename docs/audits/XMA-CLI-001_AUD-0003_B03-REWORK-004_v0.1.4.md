# XMA-CLI-001 — AUD-0003 B03-REWORK-004

**Versión:** 0.1.4  
**Fecha:** 2026-10-28, 21:27–21:33 UTC  
**Auditor:** dot  
**Dictamen:** **REWORK_REQUIRED**  
**Gate Q3:** no aprobado; producto no certificado; B04 no autorizado.

## 1. Resumen ejecutivo

El [PR #3](https://github.com/eventmgmtplatform/x-media-archiver/pull/3) está abierto, draft y sin merge. El HEAD auditado es `6aae61f2d870249fad51a542f3d397ad2b0ecece`, tree `8644dba6aa31d979c730613bb87c355e3586ec3a`. [CI #24](https://github.com/eventmgmtplatform/x-media-archiver/actions/runs/40771889052) pasó con 141 pruebas y cobertura remota 94.84 %; el tree del merge sintético probado coincide con el del HEAD.

La matriz explícita de PRM-0007 pasa: los cinco negativos se rechazan, los diez positivos requeridos coinciden con la baseline `ce3c067`, la persistencia temporal es correcta y la regresión CLI de `width=1e400` está restaurada. **No obstante, la compatibilidad positiva exacta no es universal:** una cadena numérica positiva finita con exponente extremadamente pequeño aceptada por la baseline es rechazada por el nuevo paso `Decimal(value)`. El mismo problema afecta una representación de cero. La condición no es un fallo de los diez ejemplos exigidos ni un fallo observado en datos reales; es un contraejemplo sintético al requisito general de compatibilidad exacta y de no introducir límites nuevos. Por ello el dictamen es **REWORK_REQUIRED**.

La aceptación pública de dos activos sigue sin acreditarse. El smoke histórico de Reuters/AP/BBCWorld es evidencia sanitizada declarada por el ejecutor; dot no accedió a X ni lo repitió. No se autoriza merge ni B04.

## 2. Fuentes y precondiciones

Se leyeron íntegros [DOT-PRM-0007](https://github.com/eventmgmtplatform/x-media-archiver/blob/6aae61f2d870249fad51a542f3d397ad2b0ecece/docs/prompts/XMA-CLI-001_DOT-PRM-0007_B03-REWORK-AUDIT-004_v0.1.0.md), [PRM-0007](https://github.com/eventmgmtplatform/x-media-archiver/blob/6aae61f2d870249fad51a542f3d397ad2b0ecece/docs/prompts/XMA-CLI-001_PRM-0007_B03-REWORK-004_v0.1.0.md), [AUD-0003 v0.1.3](https://github.com/eventmgmtplatform/x-media-archiver/blob/6aae61f2d870249fad51a542f3d397ad2b0ecece/docs/audits/XMA-CLI-001_AUD-0003_B03-REWORK-003_v0.1.3.md) y [HND-0003 v0.1.4](https://github.com/eventmgmtplatform/x-media-archiver/blob/6aae61f2d870249fad51a542f3d397ad2b0ecece/docs/handoffs/XMA-CLI-001_HND-0003_B03-20261028-001_v0.1.4.md). Se contrastaron código, pruebas, PR, commits, tree, diff, documentación y logs.

| Control | Resultado |
|---|---|
| PR | OPEN, draft, sin merge ni auto-merge; HEAD `6aae61f2d870249fad51a542f3d397ad2b0ecece`. |
| Tree | `8644dba6aa31d979c730613bb87c355e3586ec3a`, confirmado por Git Data. |
| Ascendencia | Desde baseline gobernada `3ce527dc1c4ae345c1474b40a2d23b305b3c96c3`, ahead 2 / behind 0; compatibilidad `ce3c067542827f702caa4bfd89fc9bd9ac4905b1` es ancestro. |
| CI | Run #24 `40771889052`, completed/success; único job `quality` / `123110950845`, 13 pasos exitosos, logs completos inspeccionados. |
| Tree de CI | Actions hizo checkout del merge sintético `c28587b573a96b1066791f0d885628d26781f96f`, padres `b2bdca7...` y el HEAD auditado; tree igual a `8644dba...`. No se afirma checkout literal del HEAD. |
| CI calidad | `uv sync --locked --all-groups`; Ruff format/check, mypy, 141 tests / 94.84 % ≥ 90 %, sdist y wheel PASS. No hay artefactos retenidos; el build se acredita mediante logs, no inspección independiente del wheel remoto. |
| PR discusión | 0 comentarios, 0 revisiones y 0 hilos; no se observó force-push en timeline. |

HND informa 141 pruebas y 94.51 % en Python 3.14.4 local; CI usó Python 3.12.16 y cobertura 94.84 %. Son resultados de entornos distintos, no cifras intercambiables.

## 3. Historia, inventario y autorización

[Comparación gobernada](https://github.com/eventmgmtplatform/x-media-archiver/compare/3ce527dc1c4ae345c1474b40a2d23b305b3c96c3...6aae61f2d870249fad51a542f3d397ad2b0ecece):

1. `8da212a0211d4f9238d2e38c96d5a3a6ad492c74`, corrección funcional; tree `35d9ac67d3974603775f13c86e803a1950f2ac71`.
2. `6aae61f2d870249fad51a542f3d397ad2b0ecece`, handoff y documentación.

Nueve archivos: `src/xma/adapters/discovery/gallery_dl.py`, `tests/adapters/test_gallery_dl_discovery.py`, `tests/application/test_discovery_service.py`, `tests/test_cli.py`, `README.md`, `CHANGELOG.md`, Gate Register, Implementation Plan y HND v0.1.4. La comparación con `ce3c067` comprende 10 commits / 16 archivos; con `496e6ce`, 5 commits / 12 archivos. Historia PR observada: 21 commits lineales. Tree recursivo no truncado: 68 blobs y 25 árboles, sin symlinks ni submódulos.

`uv.lock`, workflow, esquema y código B02 son idénticos a las baselines gobernada y de compatibilidad; el lock sí difiere de main por cambios anteriores de B03. No se importó rework B02 ni se modificaron catálogos existentes en el diff.

**Trazabilidad de autorización:** PRM-0007 permanece rotulado `PROPOSED — AWAITING HUMAN AUTHORIZATION`; el HND y Gate Register finales afirman que León autorizó una ejecución. Esa afirmación Git se publicó después del commit funcional. Como contexto independiente, tras recibir el estado que solicitaba autorización, León escribió [«Adelante, la salida de codex, dot o los dos según aplique»](https://chatgpt.com/c/6ae19fba-4bd0-83e8-8fa1-792cb4386a2a?messageId=bbb216d3-4c95-4822-a439-49d48cecc23b) antes del commit funcional; el gobernante preparó después el prompt Codex. La afirmación de HND es retrospectiva y Git por sí solo no muestra el acto humano anterior. La autorización actual de auditoría no se usa para inferir retroactivamente otra acción. No se concluye que la ejecución fuese no autorizada.

## 4. Matriz de conformidad

| Control | Resultado | Evidencia / observación |
|---|---|---|
| Identidad PR/tree/CI | PASS | HEAD y tree entregados coinciden; CI sintético tiene el mismo tree; 141 tests, 94.84 %. |
| Cinco negativos | PASS | Mapper real rechaza `-0.0001`, `-0.0005`, `-5e-324`, `'-0.0001'`, `'-1e-400'` con `DiscoveryContractError` constante antes de pérdida de signo. |
| Inspect y sync | PASS para los casos exigidos | Código 5, salida sanitizada, sin traceback/dato crudo, sin directorio ni SQLite. |
| Diez valores explícitos de compatibilidad | PASS | Mapper baseline y HEAD coinciden: 0, 0, 0, 2, 2, 4, 0, 2, 0 y 12500 ms en el orden del prompt. |
| Persistencia de empates | PASS | Floats/cadenas `0.0005` guardan 0 ms y `0.0025` guardan 2 ms en SQLite temporal; también `0.0006` y cadena guardan 1 ms. |
| CLI no finito | PASS | Regresión restaurada `width=json.loads('1e400')`, inspect/sync código 5, sanitizado, sin catálogo. |
| No finitos, booleanos, SQLite | PASS en muestras | 24 combinaciones de cuatro campos con NaN, ±inf, `1e400`, True/False rechazadas; rangos representativos verificados. |
| Compatibilidad positiva exacta / cero | **FAIL** | Cadena positiva `'1e-1999999999999999998'`: baseline 0 ms; HEAD `DiscoveryContractError`/CLI 5. Cadena `'0e1000000000000000000'`: baseline 0 ms; HEAD error. Ver sección 5. |
| R-01–R-04, R-06–R-07 | PASS por inspección y CI | Smoke histórico preservado, B02 separado, JSON sin Rich, metadata-only/variantes rotadas y defensa target/límite/cursor preservadas. R-05/RW-02 permanece abierto por compatibilidad general. |
| Capturas y alcance | PASS con límites | No se añadió captura amplia a la frontera numérica; runner externo conserva `except Exception` preexistente. Sin medios, bases, secretos o archivos prohibidos detectados en tree/diff, sujeto a límites de búsqueda. |

## 5. Reproducción offline

### Casos obligatorios

Los cinco negativos anteriores se probaron en el mapper real y por funciones de comando inspect/sync con proveedor, mapper y servicio reales, runner sintético y SQLite temporal. Todos devolvieron `DiscoveryContractError` y mensaje constante `gallery-dl numeric metadata violates the B03 contract`; inspect/sync finalizaron con código 5, sin payload, marcador sintético, traceback, directorio ni SQLite.

| Entrada | Baseline `ce3c067` | HEAD | Resultado |
|---|---:|---:|---|
| `0` | 0 | 0 | PASS |
| `0.0001` | 0 | 0 | PASS |
| `0.0005` | 0 | 0 | PASS |
| `0.0015` | 2 | 2 | PASS |
| `0.0025` | 2 | 2 | PASS |
| `0.0045` | 4 | 4 | PASS |
| `'0.0005'` | 0 | 0 | PASS |
| `'0.0025'` | 2 | 2 | PASS |
| `'1e-400'` | 0 | 0 | PASS |
| `'12.5'` | 12500 | 12500 | PASS |

Las cifras son milisegundos. Los cuatro empates float/cadena se probaron además con persistencia temporal real. Un barrido de 2,000 floats positivos no mostró deriva. El caso de width no finito pasó en ambas fronteras. Esos resultados no demuestran compatibilidad universal.

### Hallazgo RW-03 — exponente decimal extremo

| Entrada sintética | Baseline real | HEAD real |
|---|---|---|
| `'1e-1999999999999999998'` | Mapper retorna 0 ms; inspect/sync retornan éxito y sync persiste 0. | `DiscoveryContractError` constante; inspect/sync código 5 y sin catálogo. |
| `'0e1000000000000000000'` | Mapper retorna 0 ms. | `DiscoveryContractError`. |

Son cadenas numéricas válidas, semánticamente no negativas; Python `float(value)` de la baseline las convierte a cero. En HEAD, [el paso previo `Decimal(value)`](https://github.com/eventmgmtplatform/x-media-archiver/blob/6aae61f2d870249fad51a542f3d397ad2b0ecece/src/xma/adapters/discovery/gallery_dl.py#L261-L280) falla por límites de exponente de la implementación decimal antes de llegar a la conversión histórica y el error se normaliza. La cadena adyacente `'1e-1999999999999999997'` sí construye Decimal finito en el entorno de prueba. **No se afirma que X entregue estos valores ni que exista explotación real.** El resultado es un límite nuevo y una divergencia reproducible del dominio aceptado frente a `ce3c067`; DOT-PRM-0007 exige compatibilidad exacta, no solo los ejemplos de la tabla. Por tanto RW-02 no se cierra íntegramente.

La reproducción comprendió 4,103 llamadas al mapper y 164 a funciones de comando, con fuentes/fixtures fijados al SHA y hashes Git comprobados. Un hook rechazó eventos de socket; no se intentó red. `gallery_dl` se sustituyó solo para imports y se usó shims de imports/salida/decoradores para Typer y Rich con funciones de comando, proveedor, servicio y SQLite reales. **No fue un lanzamiento completo de Typer/CliRunner**; CI sí ejecutó la suite real del repositorio. Los catálogos de prueba fueron temporales, no rastreados, y se limpiaron.

## 6. Quality gates, riesgos y desviaciones

- **CI y lock:** PASS según logs; 141 pruebas, 94.84 %, Ruff, mypy y build. Test suite revisada usa fixtures y dobles; workflow no ejecuta smoke. La instalación de dependencias puede usar red y la revisión estática no demuestra por sí sola aislamiento de red de la suite completa.
- **R-01:** HND v0.1.1 preserva orden Reuters→AP→BBCWorld, tiempos, salida 3, stdout vacío, stderr sanitizado, SQLite inexistente declarado y conteos N/A. No se inspeccionó físicamente el entorno original ni se acredita causa interna exacta de X.
- **R-02/R-03:** Q3 no aprobado, `WAITING_VALIDATION`, producto no certificado, B02 separado; HND v0.1.4 corrige la afirmación histórica de v0.1.3 para los empates ordinarios. La afirmación de compatibilidad exacta requiere matiz por RW-03.
- **R-04/R-06/R-07:** JSON crudo, metadata-only, variantes rotadas y controles de límite/target/cursor preservados por inspección y CI. Catálogos antiguos pueden seguir en conflicto; `cursor=None` no promete completitud.
- **Seguridad/alcance:** sin medios, bases, respuestas reales, extractores adicionales, infraestructura ni archivos prohibidos detectados. La búsqueda de secretos no prueba ausencia de toda codificación posible. Main permanece `b2bdca7`; tags y releases consultados están vacíos. Historia lineal/timeline sin force-push observado no demuestra inexistencia de refs o eventos borrados.
- **Riesgo RW-03:** el impacto reproducido se limita a representaciones de exponente extraordinario; debe decidirse si el contrato exige la compatibilidad completa o si el gobierno lo redefine explícitamente. No degradar la protección de negativos al resolverlo.

## 7. Rework y rollback

El gobernante debe acotar una corrección o una decisión versionada sobre el rango de representación aceptado. Si se conserva la compatibilidad exacta exigida, Codex debe aceptar los ejemplos positivos/cero anteriores sin perder la validación previa del signo para cadenas negativas extremas, agregar regresiones offline de mapper y fronteras inspect/sync, preservar los cinco negativos y la matriz actual, actualizar el handoff y publicar CI verde sobre un nuevo SHA. No se implementa una solución en esta auditoría.

Contención: mantener PR draft y detener certificación. Para revertir solo REWORK-004, usar commits nuevos autorizados, primero documentación `6aae61f` y luego funcional `8da212a`, sin reescritura, modificación de catálogos ni borrado de evidencia. Para contención integral B03, seleccionar `b2bdca7` en un entorno aislado. No se ejecutó rollback.

## 8. Dictamen y próxima acción

**REWORK_REQUIRED.** El conjunto explícito de ejemplos y CI pasan, pero RW-03 demuestra que no se conserva toda la compatibilidad positiva/cero previamente aceptada. No se satisface el criterio de BLOCKED de que únicamente reste `AuthRequired`; no hay gate humano versionado que permita `VALIDATED_WITH_OBSERVATIONS`, ni desviación material irrecuperable para `FAILED`.

**Próxima acción exacta:** Chat debe gobernar RW-03 y su criterio de representación; Codex ejecuta únicamente el rework autorizado y publica handoff/CI, después dot audita el nuevo SHA y tree. La aceptación pública continúa separada y pendiente. No aprobar ni fusionar PR #3 y no iniciar B04.

**Integridad:** solo lecturas GitHub y pruebas sintéticas aisladas. No se modificaron GitHub, código, fixtures, ramas, PR, comentarios, revisiones ni estados; no hubo acceso a X, merge, tag ni release.
