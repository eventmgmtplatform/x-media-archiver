# XMA-CLI-001 — AUD-0003 B03-REWORK-005

**Versión:** 0.1.5  
**Fecha:** 2026-10-28, 21:46–21:52 UTC  
**Auditor:** dot  
**Dictamen:** **BLOCKED**  
**Q3:** no aprobado; producto no certificado; B04 no autorizado.

## 1. Resumen ejecutivo

El [PR #3](https://github.com/eventmgmtplatform/x-media-archiver/pull/3) permanece abierto, draft y sin merge en el HEAD `beb2a7d9123b23f51f6f3a92571501cb25a025d6`, tree `f1b2207b0db65d92e7d7ba877a3444389b7b3010`. [CI #26](https://github.com/eventmgmtplatform/x-media-archiver/actions/runs/40774501390) pasó con 156 pruebas y 95.18 % de cobertura. El tree probado por el merge sintético de Actions es idéntico al tree del HEAD.

RW-03 queda cerrado en el alcance auditado: los seis negativos requeridos se rechazan; los tres casos extremos positivos/cero conservan 0 ms y se persisten correctamente; la matriz de compatibilidad anterior, width no finito y controles de signo, sintaxis y rangos pasan en las pruebas realizadas. No se encontró desviación de alcance ni degradación de los controles anteriores. Una prueba amplia de gramática y Unicode no encontró divergencias con el criterio gobernado; no constituye demostración matemática exhaustiva para todas las cadenas posibles.

El único gate funcional de aceptación que permanece abierto es la aceptación pública de dos activos. HND histórico declara restricciones anónimas en Reuters/AP/BBCWorld, coherentes con `AuthRequired`, pero no acredita esa aceptación. El smoke no se repitió; su causa interna exacta y filesystem original no fueron observados independientemente. **BLOCKED** es el dictamen del prompt, no una certificación ni permiso de avanzar a B04.

## 2. Fuentes y precondiciones

Leídos íntegramente: [DOT-PRM-0008](https://github.com/eventmgmtplatform/x-media-archiver/blob/beb2a7d9123b23f51f6f3a92571501cb25a025d6/docs/prompts/XMA-CLI-001_DOT-PRM-0008_B03-REWORK-AUDIT-005_v0.1.0.md), [PRM-0008](https://github.com/eventmgmtplatform/x-media-archiver/blob/beb2a7d9123b23f51f6f3a92571501cb25a025d6/docs/prompts/XMA-CLI-001_PRM-0008_B03-REWORK-005_v0.1.0.md), [AUD-0003 v0.1.4](https://github.com/eventmgmtplatform/x-media-archiver/blob/beb2a7d9123b23f51f6f3a92571501cb25a025d6/docs/audits/XMA-CLI-001_AUD-0003_B03-REWORK-004_v0.1.4.md) y [HND-0003 v0.1.5](https://github.com/eventmgmtplatform/x-media-archiver/blob/beb2a7d9123b23f51f6f3a92571501cb25a025d6/docs/handoffs/XMA-CLI-001_HND-0003_B03-20261028-001_v0.1.5.md). También se revisaron PR, historial, tree, diff, tests, documentación y logs.

| Control | Evidencia |
|---|---|
| PR | OPEN, draft, unmerged; HEAD `beb2a7d9123b23f51f6f3a92571501cb25a025d6`. |
| Tree | `f1b2207b0db65d92e7d7ba877a3444389b7b3010`; Git Data confirma identidad exacta. |
| Ascendencia | Baseline gobernada `faba3f4ab507730d8eeae8c5bf648f52541d8f9a`: ahead 2 / behind 0. Baselines funcional `6aae61f...` y compatibilidad `ce3c067...` son ancestros. |
| CI #26 | Run `40774501390`, attempt 1, completed/success; un job quality `123120116642`, 13 pasos exitosos; logs completos. |
| Tree CI | Checkout sintético `9d8d8b39caf9e4646b7ec7388a6859065d646016`, padres `b2bdca7...` y HEAD, con tree idéntico a `f1b2207...`. No se afirma checkout literal del HEAD. |
| Calidad CI | Locked sync, Ruff format/check, mypy, 156 tests, 95.18 % ≥ 90 %, sdist y wheel PASS. HND declara 94.87 % local, no remoto. |
| Discusión | 0 comentarios, 0 revisiones y 0 hilos; sin merge o auto-merge observado. |

## 3. Historia y alcance

[Comparación gobernada](https://github.com/eventmgmtplatform/x-media-archiver/compare/faba3f4ab507730d8eeae8c5bf648f52541d8f9a...beb2a7d9123b23f51f6f3a92571501cb25a025d6): dos commits lineales / nueve archivos.

1. `f48bcd42ce2dae42f7fbbcd6803d668b68b5cce9`, corrección funcional, tree `fc3e6836039ccf14df24d3efe93def59df3bb2ef`.
2. `beb2a7d9123b23f51f6f3a92571501cb25a025d6`, HND y documentación.

Archivos: `src/xma/adapters/discovery/gallery_dl.py`, `tests/adapters/test_gallery_dl_discovery.py`, `tests/application/test_discovery_service.py`, `tests/test_cli.py`, `README.md`, `CHANGELOG.md`, Gate Register, Implementation Plan y HND v0.1.5. Desde baseline funcional hay cinco commits / 12 archivos; desde `ce3c067`, 15 commits / 20 archivos.

Tree remoto completo: 72 blobs y 25 árboles, sin symlinks ni submódulos; blobs materializados y verificados contra SHA Git. Lockfile, workflow, esquema y B02 permanecen byte-idénticos a las baselines gobernada y de compatibilidad. El lockfile difiere de main por historia anterior de B03, no por este rework. No se observó cambio funcional B02 ni migración de catálogos.

**Autorización de ejecución:** PRM-0008 permanece marcado `PROPOSED — AWAITING HUMAN AUTHORIZATION`; HND y registro finales declaran que León aclaró su autorización para una ejecución. Esa declaración Git es posterior al commit funcional. La consulta de conversaciones disponibles recuperó autorización para publicar y un estado posterior que aún esperaba autorización de ejecución, pero no la aclaración posterior citada por HND. Por tanto el acto previo no fue corroborado independientemente por dot; esto no demuestra que faltara autorización. La autorización actual de auditoría no se usa para inferir retroactivamente la ejecución. Se recomienda conservar una referencia verificable a esa decisión en la trazabilidad del gobernante.

## 4. Matriz de conformidad

| Control | Resultado | Evidencia / límite |
|---|---|---|
| HEAD/tree/CI | PASS | SHA y tree suministrados coinciden; CI sintético prueba tree idéntico; 156/95.18 %. |
| Cinco negativos previos + `'-1e-1999999999999999998'` | PASS | `DiscoveryContractError` constante; no se pierde el signo del significando no cero. |
| Tres positivos/cero extremos | PASS | `'1e-1999999999999999998'`, `'0e1000000000000000000'`, `'-0e1000000000000000000'` producen 0 ms, igual a baseline; sync temporal persiste 0. |
| Inspect/sync | PASS en casos probados | Negativos: código 5, sin traceback, dato crudo, marcador, directorio o SQLite. Aceptados: éxito y persistencia de 0. Ver limitación de harness. |
| Matriz PRM-0007 | PASS | Diez casos de baseline y HEAD coinciden; empates float/cadena persisten 0/2 ms. |
| No finitos, booleanos, límites SQLite | PASS en muestras | 24 combinaciones de cuatro campos, width JSON `1e400` en ambas fronteras y límites representativos. |
| Gramática, signos, longitud | PASS en muestras | [Helper](https://github.com/eventmgmtplatform/x-media-archiver/blob/beb2a7d9123b23f51f6f3a92571501cb25a025d6/src/xma/adapters/discovery/gallery_dl.py#L261-L294) examina signo y significando hasta `e/E`; parseo final usa `float()`. 195,846 cadenas, incluyendo Unicode, sintaxis inválida y longitud hasta 1,000,004, sin discrepancias con el oráculo usado. No es prueba exhaustiva formal. |
| R-01–R-07 y seguridad | PASS en alcance observado | JSON, target/límite/cursor, metadata-only/variantes, B02 y evidencia histórica preservados. No se detectaron archivos prohibidos ni nuevas capturas amplias; escaneo de secretos no es exhaustivo. |
| Aceptación pública | BLOCKED | Dos activos no acreditados; se conserva `AuthRequired` histórico y no se repite el smoke. |

## 5. Reproducción sintética offline

| Entrada duración | Resultado mapper | Inspect / sync |
|---|---|---|
| `-0.0001`, `-0.0005`, `-5e-324`, `'-0.0001'`, `'-1e-400'`, `'-1e-1999999999999999998'` | Error de contrato constante | Código 5, salida sanitizada, sin directorio/catálogo. |
| `'1e-1999999999999999998'` | 0 ms, igual baseline | Éxito; sync temporal persiste 0. |
| `'0e1000000000000000000'` | 0 ms, igual baseline | Éxito; sync temporal persiste 0. |
| `'-0e1000000000000000000'` | 0 ms, igual baseline | Éxito; sync temporal persiste 0. |
| `0`, `0.0001`, `0.0005`, `0.0015`, `0.0025`, `0.0045`, `'0.0005'`, `'0.0025'`, `'1e-400'`, `'12.5'` | 0, 0, 0, 2, 2, 4, 0, 2, 0, 12500 ms | Coinciden con baseline; empates persistidos en catálogo temporal. |
| `width=json.loads('1e400')` | Error de contrato | Inspect y sync código 5 sanitizado, sin catálogo. |

Ampliación independiente: 195,846 cadenas, entre ellas 137,257 combinaciones ASCII cortas, 680 dígitos decimales Unicode, 1,232 otros caracteres numéricos, 29 espacios, sintaxis generada/mutada y cadenas de hasta 1,000,004 caracteres; cero discrepancias con el oráculo. 13,997 floats no negativos adicionales sin deriva. En total 247,724 llamadas al mapper y 168 a funciones de comando; un hook rechazó eventos de socket y no se intentó conexión.

**Límites de ejecución:** el entorno local carecía de Typer, Rich y gallery-dl. Se usaron shims de importación/salida/decoradores, con funciones de comando, proveedor, mapper, servicio y SQLite reales y runner sintético. Esto verifica la frontera de controladores, **no** un lanzamiento completo de Typer/CliRunner. CI ejecutó la suite real del repositorio. Los catálogos de prueba fueron temporales y se eliminaron; fuentes/fixtures fijados al SHA permanecieron sin cambios. Los resultados amplios no garantizan todas las combinaciones posibles.

## 6. Quality gates, desviaciones y riesgos

- **CI, lock y build: PASS según logs.** 156 pruebas y 95.18 %, Ruff, mypy y build. La instalación de dependencias puede usar red; el workflow no ejecuta smoke y los tests revisados usan dobles. La revisión estática de la suite completa no es medición de tráfico de todas sus pruebas.
- **R-01:** HND v0.1.1 conserva Reuters→AP→BBCWorld, horas, salida 3, stdout vacío, stderr sanitizado y SQLite inexistente declarado, con conteos N/A. No acredita dos activos ni la causa interna exacta de X. No hubo repetición de smoke durante esta auditoría.
- **R-02/R-03:** documentación mantiene `WAITING_VALIDATION`, Q3 no aprobado y B02 separado. HND v0.1.5 corrige el alcance de la afirmación previa sobre exponentes. La autorización de ejecución se declara pero su acto previo no pudo corroborarse independientemente; conservar trazabilidad verificable.
- **R-04/R-06/R-07:** JSON crudo, variantes metadata-only, idempotencia y controles target/límite/cursor preservados. Catálogos antiguos pueden entrar en conflicto; `cursor=None` no garantiza completitud.
- **Alcance y publicación:** sin medios, bases, respuestas reales, secretos, extractores adicionales ni componentes prohibidos detectados. Búsqueda por patrones no garantiza ausencia de todo secreto. Main permanece `b2bdca7`; tags y releases consultados vacíos; no se observó force-push. No se puede demostrar ausencia de historia borrada o acciones en la máquina original.
- **Riesgo residual:** la compatibilidad léxica se verificó extensamente, no formalmente para todas las entradas; no confundir cobertura ni CI con aceptación pública.

## 7. Rollback y contención

Mantener PR draft y detener certificación. Si el gobierno autoriza revertir solo REWORK-005, hacerlo mediante nuevos commits: primero documentación `beb2a7d`, después funcional `f48bcd4`, sin reescribir historia ni modificar catálogos o borrar evidencia. Contención integral B03: seleccionar `b2bdca7` en entorno aislado. No se ejecutó rollback.

## 8. Dictamen y próxima acción

**BLOCKED.** RW-01/R-05/RW-02/RW-03 pasan los controles y reproducciones auditados; la aceptación pública de dos activos permanece pendiente por la restricción anónima históricamente documentada. `VALIDATED_WITH_OBSERVATIONS` requeriría un gate humano nuevo y versionado que redefina el criterio público; no se encontró. No hay hallazgo recuperable de implementación que exija REWORK_REQUIRED ni desviación material que justifique FAILED.

**Próxima acción exacta:** entregar este informe al gobernante para su revisión y versionado autorizado. Mantener PR #3 draft y Q3 sin aprobar; el gobernante debe decidir un camino versionado para resolver o redefinir el gate público, sin cookies, autenticación ni ampliación implícita del alcance. No aprobar ni fusionar PR y no autorizar B04.

**Integridad:** consultas GitHub de solo lectura y pruebas sintéticas aisladas. No se modificaron GitHub, código, fixtures, ramas, PR, comentarios, revisiones ni estados; no hubo acceso a X, merge, tag ni release.
