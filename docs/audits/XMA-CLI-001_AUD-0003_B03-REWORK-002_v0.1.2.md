# XMA-CLI-001 — AUD-0003 B03-REWORK-002

**Versión:** 0.1.2  
**Fecha:** 2026-10-28, 20:45–20:49 UTC  
**Auditor:** dot  
**Dictamen:** **REWORK_REQUIRED**  
**Q3:** no aprobado. Producto no certificado. B04 no autorizado.

## 1. Resumen ejecutivo

El PR #3 permaneció abierto, draft y sin merge en el HEAD `ce3c067542827f702caa4bfd89fc9bd9ac4905b1`, descendiente de la baseline gobernada `adf045ab1447a364da37df4483cc2af2d6c430c2`. CI #16 terminó verde con 112 pruebas y cobertura 94.97 %. Actions probó un merge sintético cuyo tree coincide exactamente con el del HEAD.

El rework corrige el `OverflowError` original y rechaza los casos no finitos y booleanos probados. **RW-01/R-05 permanece abierto:** una duración negativa de magnitud inferior o igual a medio milisegundo puede redondearse a cero antes de comprobar la negatividad y persistirse como válida. Se reprodujo offline con el mapper real y con los controladores de inspect/sync. Esto contradice PRM-0005 y HND v0.1.2. Es una carencia recuperable, por lo que el único dictamen aplicable es **REWORK_REQUIRED**, no BLOCKED.

La aceptación pública de dos activos sigue sin acreditarse. La restricción anónima es evidencia histórica sanitizada declarada por el ejecutor; no se accedió a X ni se repitió el smoke.

## 2. Fuentes y precondiciones

Se leyeron íntegros [DOT-PRM-0005](https://github.com/eventmgmtplatform/x-media-archiver/blob/adf045ab1447a364da37df4483cc2af2d6c430c2/docs/prompts/XMA-CLI-001_DOT-PRM-0005_B03-REWORK-AUDIT-002_v0.1.0.md), [PRM-0005](https://github.com/eventmgmtplatform/x-media-archiver/blob/ce3c067542827f702caa4bfd89fc9bd9ac4905b1/docs/prompts/XMA-CLI-001_PRM-0005_B03-REWORK-002_v0.1.0.md), [AUD-0003 v0.1.1](https://github.com/eventmgmtplatform/x-media-archiver/blob/ce3c067542827f702caa4bfd89fc9bd9ac4905b1/docs/audits/XMA-CLI-001_AUD-0003_B03-REWORK-001_v0.1.1.md) y [HND-0003 v0.1.2](https://github.com/eventmgmtplatform/x-media-archiver/blob/ce3c067542827f702caa4bfd89fc9bd9ac4905b1/docs/handoffs/XMA-CLI-001_HND-0003_B03-20261028-001_v0.1.2.md). Se revisaron PR, comentarios, revisiones, historia, tree, diff, código, pruebas, documentación y logs.

| Control | Resultado |
|---|---|
| [PR #3](https://github.com/eventmgmtplatform/x-media-archiver/pull/3) | OPEN, draft, sin merge ni auto-merge; reconsultado 20:48 UTC en el mismo HEAD. |
| HEAD / tree | `ce3c067542827f702caa4bfd89fc9bd9ac4905b1` / `df461f3386a4a9417b50b2b430f1624ff1bed56d`. |
| Ascendencia | Merge-base con `adf045ab1447a364da37df4483cc2af2d6c430c2` es esa baseline; ahead 2, behind 0. |
| CI final | [#16 / 40765654644](https://github.com/eventmgmtplatform/x-media-archiver/actions/runs/40765654644), completed/success, asociado al HEAD. Un job `quality` con 13 pasos exitosos. |
| Checkout CI | Merge sintético `696789f933d48e052e6972bef81b9d197b88a1b1`, padres `b2bdca7...` y HEAD exacto; su tree es `df461f...`, idéntico al auditado. No se afirma checkout literal del commit HEAD. |
| CI evidencia | Log completo: `uv sync --locked`, Ruff format/check, mypy, 112 pruebas, 94.97 % ≥ 90 %, sdist y wheel. HND declara 94.65 % local, distinta de CI remoto. |
| Discusión | 0 comentarios, 0 revisiones y 0 hilos. |

## 3. Inventario de commits y archivos

[Comparación gobernada completa](https://github.com/eventmgmtplatform/x-media-archiver/compare/adf045ab1447a364da37df4483cc2af2d6c430c2...ce3c067542827f702caa4bfd89fc9bd9ac4905b1):

1. `615e6d330572aba9c8253a55a17758a89e672b8c`, `fix: normalize discovery numeric metadata`, tree `1f3a27dd869350c6f4a8ce74719158f72d359ce3`.
2. `ce3c067542827f702caa4bfd89fc9bd9ac4905b1`, `docs: record B03 rework 002 handoff`.

Los nueve archivos modificados son: `CHANGELOG.md`; `README.md`; `docs/governance/XMA-CLI-001_GATE-REGISTER_v0.1.0.md`; `docs/handoffs/XMA-CLI-001_HND-0003_B03-20261028-001_v0.1.2.md`; `docs/planning/XMA-CLI-001_IMPLEMENTATION_PLAN_v0.1.0.md`; `src/xma/adapters/discovery/gallery_dl.py`; `src/xma/cli.py`; `tests/adapters/test_gallery_dl_discovery.py`; `tests/test_cli.py`.

Desde baseline funcional `0186129...` hay cinco commits y 12 archivos, incluyendo tres commits documentales de gobierno. El tree completo, no truncado, contiene 60 blobs y 25 árboles, sin symlinks ni submódulos; se reprodujeron los hashes y el tree raíz. `uv.lock`, workflow y módulos/fixtures B02 son idénticos a la baseline funcional. No hay migración ni borrado de catálogos en el diff.

## 4. Matriz RW-01 / R-05

| Criterio | Resultado | Evidencia |
|---|---|---|
| `num`, `width`, `height`, `duration` | PASS parcial | Mapper real usa validadores por campo; `duration` se convierte a `duration_ms`. Invariante de duración negativa falla abajo. |
| Booleanos | PASS | `True` y `False` rechazados en cuatro campos en pruebas independientes. |
| NaN, +inf, -inf, JSON `1e400` | PASS | Cuatro valores por campo, normalizados a `DiscoveryContractError` constante; sin OverflowError en los casos probados. |
| Validación antes de int/resta | PASS en casos probados | Índice de origen validado 1..2^63 antes de restar; dimensiones enteras 0..2^63−1. Se rechazaron fracciones y rangos inválidos probados. |
| Duración no negativa antes de redondear | **FAIL** | [Código líneas 260–275](https://github.com/eventmgmtplatform/x-media-archiver/blob/ce3c067542827f702caa4bfd89fc9bd9ac4905b1/src/xma/adapters/discovery/gallery_dl.py#L260-L275) comprueba `result < 0` después de `round`. `-0.0001`, `-0.0005` y cadena `'-0.0001'` producen `duration_ms=0`. Se constató persistencia de 0 en SQLite aislado. |
| SQLite/rangos y finitud | PASS parcial | Límites de entero SQLite ejercidos para índice y dimensiones; valores desbordados/no finitos rechazados. El defecto negativo implica que no se satisface globalmente el contrato. |
| Sin saturación o sustitución silenciosa | **FAIL** | La duración negativa probada se transforma en cero válido; contradice la prohibición expresa de PRM-0005. |
| Error sanitizado y CLI 5 | PASS parcial | Casos de `width=1e400`, `duration=inf`, `num=True`, `height=-1` dieron salida 5, mensaje constante, sin payload, marcador o traceback en la integración aislada. El caso negativo pequeño no dispara error y devuelve éxito. |
| Sin SQLite ante error | PASS en casos probados | Para los cuatro casos inválidos de la fila anterior no se creó repositorio/catálogo. Para duración negativa pequeña, erróneamente aceptada, sync sí creó un catálogo aislado y guardó cero. |
| Captura delimitada | PASS con observación | Nuevas conversiones capturan errores específicos; no se introdujo captura amplia nueva. El runner de gallery-dl contiene un `except Exception` preexistente para clasificar fallos externos, fuera de la nueva frontera numérica; no se presenta como código añadido por este rework. |

## 5. Fixtures y reproducciones sintéticas offline

Se inspeccionaron [tests del adaptador](https://github.com/eventmgmtplatform/x-media-archiver/blob/ce3c067542827f702caa4bfd89fc9bd9ac4905b1/tests/adapters/test_gallery_dl_discovery.py) y [tests CLI](https://github.com/eventmgmtplatform/x-media-archiver/blob/ce3c067542827f702caa4bfd89fc9bd9ac4905b1/tests/test_cli.py). Los primeros ejercen el mapper real; la regresión CLI atraviesa proveedor y servicio con runner offline, no solo un doble que arroja la excepción final. La prueba negativa de duración existente usa `-0.001` y no cubre negativos que redondean a cero.

| Grupo | Reproducción independiente | Resultado |
|---|---|---|
| No finitos y booleanos | 24 combinaciones: cuatro campos × NaN, +inf, −inf, `json.loads('1e400')`, `True`, `False` | Todos rechazados con `DiscoveryContractError` constante. |
| Índice de origen | Cero, negativos, fracciones y límites de entero SQLite | Inválidos rechazados; límites válidos probados aceptados. |
| Dimensiones | Negativos, fracciones, límites y desbordes | Inválidos probados rechazados; límites válidos aceptados. |
| Duración negativa | `-0.001` | Rechazada correctamente. |
| Duración negativa pequeña | `-0.0001`, `-0.0005`, `-5e-324`, `'-0.0001'`, `'-1e-400'` | **Falla:** aceptadas y convertidas a cero en el mapper. Las cadenas con exponente muy pequeño muestran además pérdida de signo por conversión a float. |
| Valores válidos | Valores finitos representativos, cadenas numéricas admitidas y límites enteros | Casos probados aceptados; no implica demostración de todos los posibles valores finitos. |
| Frontera de comandos | 16 casos mediante funciones de comando reales, proveedor real y servicio, runner sintético | Cuatro tipos inválidos representativos: código 5 y sin catálogo. Negativos pequeños: retorno normal y `sync` persiste cero en SQLite temporal. |

Las 64 pruebas de mapper y 16 de controladores se ejecutaron sin X, con un hook que rechaza eventos de socket; no se intentó red. El módulo `gallery_dl` fue sustituido solo para resolver imports. En la prueba de controladores se usó un shim de decoradores/anotaciones Typer y componentes Click/Rich disponibles: **no fue un lanzamiento de la CLI real ni CliRunner**, por ausencia de Typer en ese entorno. CI ejecutó la suite real completa. Los archivos del snapshot se verificaron sin cambios tras las pruebas; catálogos de prueba se crearon únicamente en un directorio temporal aislado, no en Git.

## 6. Regresión de R-01–R-07

| Control | Resultado | Observación |
|---|---|---|
| R-01 | PASS documental | HND v0.1.1 conserva comandos, orden, tiempos, salida y limitaciones del smoke; no se repitió. La inexistencia de SQLite original permanece como declaración del ejecutor. |
| R-02 | PASS documental con salvedad | README, CHANGELOG, registro, plan y PR mantienen WAITING_VALIDATION, producto no certificado y bloqueo público separado. La afirmación de HND de que se rechazan todos los negativos es incorrecta en el caso reproducido y debe corregirse junto con R-05. |
| R-03 | PASS | Rework B02 separado y no integrado; sin cambios funcionales B02 en este diff. No se certifica B02. |
| R-04 | PASS por regresión | Emisión JSON y pruebas previas preservadas; CI verde. |
| R-05 | **FAIL** | Duraciones negativas pequeñas se aceptan como cero; ver secciones 4–5. |
| R-06 | PASS por regresión | Política metadata-only y regresiones de variantes rotadas preservadas; riesgo de conflicto con catálogos antiguos permanece documentado. |
| R-07 | PASS por regresión | Validación target/límite y limitación `cursor=None` preservadas. |

## 7. Quality gates, alcance y riesgos

- **CI y lockfile: PASS.** 112 pruebas, 94.97 % remoto; lint, formato, mypy y build correctos; lockfile sin cambios. Instalación de dependencias usa red, pero el workflow no ejecuta smoke y los tests revisados usan fixtures/dobles. La revisión de la suite completa es estática; la prohibición de sockets fue medida solo en las reproducciones independientes indicadas.
- **Alcance: PASS con límites de observación.** Se inspeccionaron tree y diff: sin medios, bases, respuestas reales, evidencias locales, extractores adicionales, nuevas funciones B04/B05, cambios de esquema o B02 observados. No se detectaron secretos por patrones; ello no prueba ausencia de toda posible codificación. El catálogo temporal de la reproducción no fue rastreado ni publicado.
- **Estado remoto: PASS observado.** Main `b2bdca7961f00d54f2465a4f8d26b2003340c3b9`; tags y releases vacíos; sin merge ni B04 observado. Historia lineal y timeline sin evento de force-push; no puede descartarse exhaustivamente historia borrada. La no repetición del smoke y limpieza del entorno original son declaraciones del ejecutor, no observación directa de dot.
- **Riesgos abiertos:** defecto de validación y documentación HND sobre negativos; aceptación pública de dos activos; conflictos posibles con catálogos antiguos; rework B02 separado; `cursor=None` no garantiza completitud. La evidencia histórica no demuestra por sí sola la causa interna exacta del servicio remoto.

## 8. Rework y rollback

Solicitar a Codex, mediante el gobierno y autorización correspondientes, rechazar duraciones negativas **antes** de cualquier conversión o redondeo que pueda ocultar signo, incluidos valores numéricos y cadenas con subdesbordamiento; conservar rango SQLite y comportamiento válido. Añadir regresiones offline del mapper y de la frontera CLI para `-0.0001`, `-0.0005`, cadena negativa pequeña y exponente negativo extremo, verificando `DiscoveryContractError`, código 5, salida sanitizada y ausencia de catálogo; incluir controles de cero y positivos válidos. Actualizar el handoff, ejecutar gates y CI en el nuevo HEAD, y solicitar nueva auditoría. No se ordena aquí una implementación directa.

Contención: conservar PR draft y detener certificación. Para revertir solo REWORK-002, usar commits de reversión autorizados, primero documentación y después `615e6d3`, sin reescribir historia ni borrar catálogos o evidencia. Contención integral B03: seleccionar `b2bdca7` en entorno aislado. No se ejecutó rollback.

## 9. Dictamen y próxima acción

**REWORK_REQUIRED.** Aunque el defecto original de no finitos se normaliza y CI es verde, RW-01/R-05 no está cerrado por aceptación y persistencia de duración negativa como cero. No se cumple la condición para BLOCKED de que solo reste la aceptación pública. No existe gate humano versionado que permita VALIDATED_WITH_OBSERVATIONS y no se encontró una desviación material irrecuperable que justifique FAILED.

**Próxima acción exacta:** Chat debe gobernar un rework mínimo de la validación de duración y su trazabilidad para Codex; una vez publicado el nuevo SHA, handoff y CI verde, dot debe auditar esa entrega. El bloqueo público continúa separado. No aprobar ni fusionar PR #3 y no autorizar B04.

**Integridad:** auditoría de solo lectura de GitHub y pruebas sintéticas aisladas. No se modificaron GitHub, fixtures, código, ramas, PR, comentarios, revisiones ni estados. No se accedió a X, no se hizo merge, tag ni release.
