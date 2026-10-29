# XMA-CLI-001 — AUD-0003 B03-REWORK-001

**Versión:** 0.1.1  
**Fecha:** 2026-10-28, auditoría independiente 19:53–19:57 UTC  
**Auditor:** dot  
**Dictamen:** **REWORK_REQUIRED**  
**Gate Q3:** no aprobado; producto no certificado. B04 no autorizado.

## 1. Resumen ejecutivo

La precondición de identidad se cumplió: el PR #3 estaba abierto, draft y sin fusionar, con HEAD `0186129e06201b644a4d383d621740f291d1244d`. CI #13 corresponde a ese HEAD y terminó verde: 77 pruebas, cobertura 94.68 %. Actions probó un commit sintético de merge cuyo tree es idéntico al tree del HEAD. Se inspeccionó el prompt canónico íntegro, la baseline, el tree, el diff, los jobs y logs, código, pruebas, documentación y handoff.

R-01, R-02, R-03, R-04, R-06 y R-07 pasan en el alcance auditado. **R-05 falla:** metadatos numéricos no finitos del proveedor pueden provocar `OverflowError` fuera de la normalización de errores y de la captura de CLI. Es una carencia recuperable en el tratamiento de contrato, por lo que no corresponde clasificar el resultado como BLOCKED solo por el obstáculo público. No se observó una desviación material de alcance que sustente FAILED.

El handoff informa restricciones anónimas en Reuters, AP y BBCWorld y no acredita la aceptación pública de dos activos. Esa información es evidencia declarada y sanitizada del ejecutor, no una repetición ni observación independiente de dot. La aceptación pública sigue bloqueada. No se realizó una nueva prueba en X.

## 2. Fuentes y delimitación

- [PR #3](https://github.com/eventmgmtplatform/x-media-archiver/pull/3); [comparación completa](https://github.com/eventmgmtplatform/x-media-archiver/compare/b2bdca7961f00d54f2465a4f8d26b2003340c3b9...0186129e06201b644a4d383d621740f291d1244d); [diff de rework](https://github.com/eventmgmtplatform/x-media-archiver/compare/7755853c378b3dc5ec25a52adc6c33f29f8bc8d7...0186129e06201b644a4d383d621740f291d1244d).
- [DOT-PRM-0004 v0.1.0](https://github.com/eventmgmtplatform/x-media-archiver/blob/0186129e06201b644a4d383d621740f291d1244d/docs/prompts/XMA-CLI-001_DOT-PRM-0004_B03-REWORK-AUDIT_v0.1.0.md); [PRM-0004 v0.1.0](https://github.com/eventmgmtplatform/x-media-archiver/blob/0186129e06201b644a4d383d621740f291d1244d/docs/prompts/XMA-CLI-001_PRM-0004_B03-REWORK-001_v0.1.0.md); [AUD-0003 v0.1.0](https://github.com/eventmgmtplatform/x-media-archiver/blob/0186129e06201b644a4d383d621740f291d1244d/docs/audits/XMA-CLI-001_AUD-0003_B03-20261028-001_v0.1.0.md); [HND-0003 v0.1.1](https://github.com/eventmgmtplatform/x-media-archiver/blob/0186129e06201b644a4d383d621740f291d1244d/docs/handoffs/XMA-CLI-001_HND-0003_B03-20261028-001_v0.1.1.md).
- [CI #13, run 40750630452](https://github.com/eventmgmtplatform/x-media-archiver/actions/runs/40750630452); [CI baseline #12](https://github.com/eventmgmtplatform/x-media-archiver/actions/runs/40724041690).
- Inspección de las 56 entradas blob y 25 árboles del tree remoto no truncado; hashes de blobs reproducidos y tree reconstruido `086c1b245be14b9ed925fbe4cc62bee2b726b7bc`. Sin submódulos ni enlaces simbólicos. Se inspeccionaron los 27 archivos del diff del PR y los 12 del rework.
- La evaluación de secretos es una revisión de contenido y patrones, no una garantía contra toda codificación posible. La revisión de ausencia de red en tests es estática, no una medición de tráfico. No se inspeccionó el filesystem original del ejecutor.

## 3. Identidad Git, PR y CI

| Control | Evidencia y resultado |
|---|---|
| PR y rama | #3, `feature/xma-b03-discovery`, abierto, draft, sin merge ni auto-merge. HEAD exacto `0186129e06201b644a4d383d621740f291d1244d`. |
| Baseline de rework | `7755853c378b3dc5ec25a52adc6c33f29f8bc8d7`, padre único de `0186129`; CI #12 verde. Rework ahead 1 / behind 0. |
| Baseline B03 | `main` `b2bdca7961f00d54f2465a4f8d26b2003340c3b9`; seis commits lineales, ahead 6 / behind 0. |
| Tree probado | CI asocia HEAD `0186129...`; checkout sintético `fc46c1f2402082095746a87972141143f4f634b8`. Ambos tienen tree `086c1b245be14b9ed925fbe4cc62bee2b726b7bc`. |
| CI #13 | Una ejecución, un job `quality`, 13 pasos exitosos. Locked sync, Ruff format/check, mypy, pytest y build de sdist/wheel. 77 pruebas, cobertura 94.68 % ≥ 90 %. |
| Conversación y revisión | 0 comentarios, 0 revisiones enviadas, 0 hilos de revisión. Timeline consultado sin evento de force-push; ello no prueba exhaustivamente la historia de pushes. |
| Publicación | Refs de tags y releases vacíos en la consulta. No se observó B04 iniciado. Sin cambio directo en main observado. La ausencia histórica de refs borradas no puede probarse con esta consulta. |

## 4. Matriz R-01–R-07

| ID | Resultado | Evidencia y observaciones |
|---|---|---|
| R-01 | **PASS** | [HND líneas 12–54 y 74–107](https://github.com/eventmgmtplatform/x-media-archiver/blob/0186129e06201b644a4d383d621740f291d1244d/docs/handoffs/XMA-CLI-001_HND-0003_B03-20261028-001_v0.1.1.md#L12-L107): comandos, orden Reuters → AP → BBCWorld, horas UTC, fallback, salida 3, stdout vacío y stderr sanitizado; N/A por fallo previo a persistencia; comprobación declarada de SQLite inexistente y directorios sin archivos. Incluye inventario, métricas y rollback integral. El [servicio](https://github.com/eventmgmtplatform/x-media-archiver/blob/0186129e06201b644a4d383d621740f291d1244d/src/xma/application/discovery.py#L56-L67) descubre antes de abrir UoW. **Límite:** resultados locales declarados, no reproducidos por dot; no se retuvo respuesta cruda. No se cumplen dos activos públicos. |
| R-02 | **PASS** | README, CHANGELOG, Gate Register, Implementation Plan y cuerpo actual del PR reflejan rework, `WAITING_VALIDATION`, `REWORK_REQUIRED`, bloqueo público y producto no certificado. El cuerpo identifica HEAD, tree, handoff y CI #13. La referencia histórica a CI #11 no se presenta como CI final del rework. |
| R-03 | **PASS** | [AUD-0002 v0.1.2](https://github.com/eventmgmtplatform/x-media-archiver/blob/4b8bdab3f8e5cbc06cf2fe987206f75f9c040d22/docs/audits/XMA-CLI-001_AUD-0002_B02-20261028-001_v0.1.2.md) existe en rama B02 `4b8bdab...`, clasificado BLOCKED. HND y registro reconocen que fixes y riesgos B02 no están integrados en `main` ni B03. Los módulos y esquema B02 permanecen idénticos a `b2bdca7`; no se certifica B02 mediante esta auditoría. |
| R-04 | **PASS** | [CLI](https://github.com/eventmgmtplatform/x-media-archiver/blob/0186129e06201b644a4d383d621740f291d1244d/src/xma/cli.py#L147-L155) utiliza `typer.echo` y `json.dumps` con `ensure_ascii=False`, orden estable, sin render Rich. Tests de inspect y sync dry-run validan `json.loads`, Unicode, markup y cadenas largas; suite CI verde. |
| R-05 | **FAIL** | Taxonomía y captura de persistencia mejoraron y sus pruebas pasan, pero [mapper](https://github.com/eventmgmtplatform/x-media-archiver/blob/0186129e06201b644a4d383d621740f291d1244d/src/xma/adapters/discovery/gallery_dl.py#L164-L200) solo normaliza `KeyError`, `TypeError` y `ValueError`. Un `width` o `duration` no finito como el producido por `json.loads('1e400')` causa `OverflowError` en [conversiones](https://github.com/eventmgmtplatform/x-media-archiver/blob/0186129e06201b644a4d383d621740f291d1244d/src/xma/adapters/discovery/gallery_dl.py#L230-L243), no `DiscoveryContractError`. La [CLI](https://github.com/eventmgmtplatform/x-media-archiver/blob/0186129e06201b644a4d383d621740f291d1244d/src/xma/cli.py#L80-L85) no captura ese error como fallo esperado; puede mostrar traceback. Reproducido en prueba aislada del mapper, sin X. No se afirma que haya ocurrido en producción ni que exponga secretos en este caso. |
| R-06 | **PASS** | Política explícita metadata-only: identidad `post_id:media_index`; persistencia reemplaza variantes por `('metadata-only',)` y salida pública no imprime URLs firmadas. Prueba offline independiente con dos variantes firmadas rotadas: un perfil, un post, un activo, dos runs; sin bytes de firma persistidos. Catálogos antiguos no se migran automáticamente y pueden devolver conflicto/salida 6; limitación documentada. |
| R-07 | **PASS** | [Servicio líneas 42–55](https://github.com/eventmgmtplatform/x-media-archiver/blob/0186129e06201b644a4d383d621740f291d1244d/src/xma/application/discovery.py#L42-L55) valida target devuelto, requested_limit y conteo; tests de proveedor defectuoso y `cursor=None`. No se promete paginación ni completitud. Se observó como riesgo adicional que el handle del perfil observado puede diferir del target; no se clasifica como falla R-07 porque el contrato previo admite cambios de handle y este control exige coherencia del target de lote, no igualdad literal del handle. |

## 5. Hallazgo recuperable y rework requerido

**RW-01 / R-05 — normalización de metadatos no finitos.** Severidad: moderada, recuperable. El payload sintético con número JSON `1e400` se convierte a infinito en Python; `int` de width o `round` de duration produce `OverflowError`. El mapper no lo convierte en `DiscoveryContractError`; inspect/sync no lo normalizan en CLI. Las pruebas verdes no cubren ese caso. No se ejecutó la CLI completa localmente por ausencia de dependencias del entorno; la propagación al límite de CLI se concluye del código inspeccionado, no de un traceback capturado.

Acción para Codex, sujeto al gobierno de Chat y a un prompt autorizado: validar finitud y rango de campos numéricos del proveedor y normalizar fallos como error de contrato sanitizado; añadir pruebas offline del mapper y de CLI para width/duration no finitos, verificando código documentado y ausencia de traceback y datos crudos. Reejecutar gates y CI sobre el nuevo HEAD, publicar handoff trazable y solicitar nueva auditoría. Evitar captura indiscriminada de `BaseException`. No modificar el SHA auditado ni afirmar cierre antes de verificar la nueva entrega.

## 6. Quality gates y desviaciones

| Gate | Resultado | Sustento / límite |
|---|---|---|
| Identidad PR/CI | PASS | HEAD exacto y tree del merge de Actions idéntico al HEAD. |
| CI, lint, tipos, pruebas, build | PASS | CI #13, 77/77, 94.68 %, Ruff, mypy y build; 94.89 % es la cifra local declarada en HND, no la remota. |
| Lockfile | PASS | `uv sync --locked` en CI; `uv.lock` sin cambios desde baseline de rework. |
| Offline automatizado | PASS con observación | Fixtures y dobles; no se encontró llamada de extracción real en tests ni smoke en workflow. La instalación de dependencias sí usa red; no hay medición de tráfico de tests ni bloqueo de egress. |
| Límites de B03 y tree | PASS con límites | `gallery-dl` único extractor, configuración anónima, sin descarga y caché en memoria; sin medios, bases locales, evidencias locales o secretos detectados en tree; revisión de patrones no es prueba absoluta. |
| Contrato y errores | **FAIL** | RW-01 / R-05; ver sección 5. |
| Aceptación pública | **BLOCKED** | HND declara restricción anónima en tres cuentas, sin dos activos aceptados. Evidencia no reproducida de forma independiente. |
| B02 | Observación abierta | Rework separado y no integrado; riesgos documentados no se certifican en B03. |
| Merge/tag/release/B04 | PASS en estado observado | Sin merge, tags, releases ni inicio B04 observados; consulta no prueba ausencia de eventos históricos borrados. |

## 7. Riesgos y observaciones

1. El fallo R-05 puede convertir un cambio de contrato del proveedor en excepción no normalizada; pruebas verdes no eliminan el riesgo.
2. La aceptación pública de dos activos sigue pendiente. La restricción observada es coherente con `AuthRequired`, pero el handoff no conserva la excepción cruda; no se atribuye certeza independiente sobre causa interna de X.
3. Catálogos creados por versiones anteriores pueden contener variantes incompatibles con la política nueva; la salida 6 está documentada, sin migración automática. Preservar catálogos y planificar una decisión separada antes de intervenirlos.
4. Riesgos B02 de cierre excepcional, timestamp de migración e invariantes terminales siguen en su línea de trabajo, sin integración ni certificación implícita.
5. `cursor=None` significa que no hay paginación real ni garantía de completitud. El posible desajuste entre handle observado y target requiere análisis de identidad si el gobierno lo prioriza; no se incorpora como requisito nuevo del rework actual.
6. El smoke, la limpieza del worktree original y la inexistencia de SQLite local son declaraciones sanitizadas del ejecutor, no observaciones físicas de dot.

## 8. Rollback y contención

Mantener PR #3 draft y detener uso/certificación de B03 ante la brecha. Para contención integral, seleccionar la baseline `b2bdca7` en un entorno aislado, preservar catálogos y evidencia; no borrar datos ni reescribir historia. Una reversión publicada requiere decisión y commits trazables. Revertir solo el commit de rework no equivale a retirar B03 completo y no debe degradar el lockfile. Ninguna reversión fue ejecutada por esta auditoría.

## 9. Dictamen y próxima acción

**REWORK_REQUIRED.** Aunque la evidencia documental y seis controles pasan y CI es verde, R-05 conserva una falla recuperable demostrada. El criterio del prompt para BLOCKED exige R-01–R-07 cerrados y que el único impedimento sea `AuthRequired`; esa condición no se cumple. No procede `VALIDATED_WITH_OBSERVATIONS`, tampoco hay evidencia de desviación material irrecuperable que obligue a `FAILED`.

**Próxima acción exacta:** el gobernante debe preparar un prompt de rework acotado para que Codex cierre RW-01/R-05, añada regresiones offline y publique handoff y CI para un nuevo SHA; después dot deberá verificar de nuevo ese SHA y los gates. La aceptación pública permanecerá bloqueada hasta evidencia válida o una redefinición humana versionada del gate. No aprobar ni fusionar PR #3 y no iniciar B04.

**Integridad de la auditoría:** lectura y pruebas aisladas únicamente. No se modificaron GitHub, código, ramas, PR, comentarios, revisiones ni estados; no se hizo merge, tag ni release.
