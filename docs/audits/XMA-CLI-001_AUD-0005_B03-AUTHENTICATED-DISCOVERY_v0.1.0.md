# XMA-CLI-001 — AUD-0005 B03 Authenticated Discovery

**Versión:** 0.1.0  
**Fecha:** 2026-10-28, 23:21–23:29 UTC  
**Auditor:** dot  
**Mandato:** XMA-CLI-001-DOT-PRM-0011 v0.1.0  
**Dictamen:** **REWORK_REQUIRED**  
**Q3-Público, cierre B03, merge y B04:** sujetos a decisión posterior de León; no aprobados por esta auditoría.

## 1. Resumen ejecutivo

El [PR #3](https://github.com/eventmgmtplatform/x-media-archiver/pull/3) se examinó en el HEAD `29741c20978a9a3b097c790fc352d73b1007c193`, tree `42d470898aebd78654a3ff1153e340904ce68372`, abierto, draft y sin merge. [CI #31](https://github.com/eventmgmtplatform/x-media-archiver/actions/runs/40786290849) pasó con 171 pruebas y 95.25 % de cobertura sobre un tree idéntico al HEAD.

El handoff declara que Reuters y AP terminaron con salida 3 y cero activos y que BBCWorld terminó con salida 0 y dos activos distintos en SQLite temporal. Esta auditoría comprobó que la declaración está versionada y coincide con el cuerpo del PR, pero **no observó el smoke, el catálogo ni el filesystem original**. No se repitió la prueba ni se accedió al navegador o a cookies.

Existen carencias recuperables en el límite de autenticación: la versión fijada de `gallery-dl` contempla copiar temporalmente la base de cookies si falla su apertura inicial; una excepción del cargador puede llegar sin sanitizar a un warning; y el selector permite componentes de directorio especiales. Además, la evidencia documental no registra comprobación explícita de integridad/readback de SQLite, el README conserva texto anterior contradictorio y se identificó una ruta de usuario personal heredada en documentación histórica. **No se encontró evidencia de valores reales de cookies expuestos ni se demostró que las rutas condicionales ocurrieran en el smoke.** Corresponde `REWORK_REQUIRED`, no `FAILED` por una exposición o descarga no demostrada.

## 2. Identidad, fuentes y límites

Se leyeron íntegramente [DOT-PRM-0011](https://github.com/eventmgmtplatform/x-media-archiver/blob/29741c20978a9a3b097c790fc352d73b1007c193/docs/prompts/XMA-CLI-001_DOT-PRM-0011_B03-AUTHENTICATED-DISCOVERY-AUDIT_v0.1.0.md), [PRM-0009](https://github.com/eventmgmtplatform/x-media-archiver/blob/29741c20978a9a3b097c790fc352d73b1007c193/docs/prompts/XMA-CLI-001_PRM-0009_B03-AUTHENTICATED-DISCOVERY_v0.1.0.md), [ADR-0003](https://github.com/eventmgmtplatform/x-media-archiver/blob/0d840e9362a1daf15d4150bd0763853ed3dcbfc4/docs/adr/ADR-0003-firefox-session-authenticated-public-discovery.md) y [HND-0003 v0.2.0](https://github.com/eventmgmtplatform/x-media-archiver/blob/29741c20978a9a3b097c790fc352d73b1007c193/docs/handoffs/XMA-CLI-001_HND-0003_B03-20261028-001_v0.2.0.md), además de PR, documentación, diff, tree, tests y logs.

| Control | Resultado |
|---|---|
| HEAD / tree | `29741c20978a9a3b097c790fc352d73b1007c193` / `42d470898aebd78654a3ff1153e340904ce68372`, coincidencia exacta. |
| Rama / PR | `feature/xma-b03-discovery`, abierto, draft, sin merge; main `b2bdca7961f00d54f2465a4f8d26b2003340c3b9`. |
| Baseline | `946ebd11503e3b06f623e22b3aabe43c6e193a76`, tree `378529fd4f533391b4f09e246676f48f32224f5c`; tres commits lineales, ahead 3 / behind 0. |
| CI #31 | Run `40786290849`, éxito; un job `quality`, 13 pasos exitosos; locked sync, Ruff, mypy, 171 tests, 95.25 % ≥90 %, sdist y wheel. |
| Tree CI | Checkout sintético `6e7e0af98f7dc656008407d0712ae7a2bff90fce`, padres main y HEAD; tree idéntico al HEAD. No fue checkout literal del commit HEAD. |
| Ejecución real | HND y PR son declaraciones sanitizadas; dot no inspeccionó máquina original, sesión, SQLite o wheel local. CI acredita checks del tree, no aceptación real ni ausencia física de archivos en el directorio temporal. |

## 3. Alcance e inventario

[Comparación baseline–HEAD](https://github.com/eventmgmtplatform/x-media-archiver/compare/946ebd11503e3b06f623e22b3aabe43c6e193a76...29741c20978a9a3b097c790fc352d73b1007c193):

1. `0d840e9362a1daf15d4150bd0763853ed3dcbfc4`, ADR/prompt de acceso controlado.
2. `87e9698b44237300a2cd058304ec030bf2cdf256`, implementación de autenticación Firefox.
3. `29741c20978a9a3b097c790fc352d73b1007c193`, handoff/documentación.

Trece archivos: README, CHANGELOG, ADR-0003, Gate Register, Implementation Plan, PRM-0009, DOT-PRM-0011, HND v0.2.0, adaptador y export de discovery, CLI, tests de adaptador y CLI. El tree íntegro no truncado contiene 82 blobs; 69 son idénticos a baseline, nueve modificados y cuatro añadidos. Workflow, lockfile y adaptador/esquema SQLite no cambiaron. No se identificaron nuevas implementaciones B04/B05, extractores adicionales o archivos de medios, bases/cookies en Git. La inspección por patrones no demuestra ausencia universal de secretos.

## 4. Matriz de controles

| Control | Resultado | Evidencia / limitación |
|---|---|---|
| SHA, tree, CI | PASS | Identidad exacta y tree de CI confirmado; 171 pruebas, 95.25 %. |
| Anónimo predeterminado | PASS por código/pruebas | Sin opciones, se construye proveedor anónimo; las opciones se exigen juntas y combinaciones incompletas terminan con código 2. |
| Firefox y perfil | **FAIL parcial** | Solo `firefox` pasa validación nominal; DTO rechaza separadores de ruta, pero acepta `.` y `..`. En el resolver de la dependencia, `..` puede salir de la raíz prevista y activar búsqueda recursiva. Ver hallazgo A-03. |
| No copiar/exportar/serializar cookies | **FAIL de diseño condicional** | `cookies-update=False` deshabilita actualización/exportación habitual y cache de gallery-dl es `:memory:`, pero la dependencia tiene fallback que copia la base a un directorio temporal si falla apertura SQLite inicial. No se observó que se activara en el smoke. A-01. |
| Sin identificadores en warnings | **FAIL de diseño condicional** | La dependencia registra sin sanitizar una excepción del cargador y la consume antes de la clasificación externa de XMA; una prueba sintética hizo aparecer un marcador en el warning. No se demostró exposición real. A-02. |
| gallery-dl, sin descarga y cache | PASS parcial | Configuración inspeccionada establece descarga deshabilitada y cache `:memory:`; único extractor. No confundir esa caché con el fallback temporal del lector de cookies. |
| Tests offline / CI | PASS con límites | CI ejecuta tests con dobles/fixtures, no smoke. La instalación de dependencias puede usar red; la revisión de suite no equivale a medición completa de tráfico. No se ejecutó smoke ni navegador. |
| Aceptación de dos activos | **EVIDENCIA DECLARADA, NO VERIFICADA INDEPENDIENTEMENTE** | HND/PR coinciden en BBCWorld salida 0, dos distintos; no se aporta resultado de readback/integridad SQLite y dot no accedió al catálogo real. Ver sección 6. |
| Datos sensibles y rutas | **FAIL documental heredado** | Se identificó una ruta personal de cache en un handoff B02 ya presente en baseline; no es cookie ni secreto de autenticación y no se reproduce. A-05. No se hallaron selectores reales de autenticación ni valores de cookies por patrones. |
| Merge/tag/release/B04 | PASS observado | PR draft y sin merge; refs tags y releases vacíos, sin B04/B05 observado. Esto no prueba eventos o refs borrados. |

## 5. Hallazgos y evidencia

### A-01 — Copia temporal condicional de la base de cookies

En `gallery-dl` **1.32.18** (tag oficial resuelto a commit `175d21fd8f7e52963911c02916d0634461cddb24`), [DatabaseConnection](https://github.com/mikf/gallery-dl/blob/175d21fd8f7e52963911c02916d0634461cddb24/gallery_dl/cookies.py#L927-L964) intenta conexión SQLite read-only/immutable y, si esa apertura lanza excepción, crea un directorio temporal y copia el archivo de base antes de abrir la copia. Se cierra y limpia normalmente en `__exit__`; la copia sigue existiendo temporalmente en disco y no está cubierta por la caché `:memory:`. El [adaptador](https://github.com/eventmgmtplatform/x-media-archiver/blob/29741c20978a9a3b097c790fc352d73b1007c193/src/xma/adapters/discovery/gallery_dl.py#L91-L119) entrega el selector del navegador a esa dependencia. ADR-0003 prohíbe copiar, exportar, serializar o persistir valores de cookies.

Una prueba sintética aislada con llamadas de filesystem/conexión sustituidas confirmó el camino de fallback; no se abrió ni copió una base real. **No hay evidencia de que el fallback se activara durante el smoke ni de exposición real.** Se requiere una solución o decisión humana versionada que satisfaga explícitamente el contrato antes de certificar el control.

### A-02 — Warning de biblioteca fuera del límite de sanitización

[El cargador de cookies de gallery-dl](https://github.com/mikf/gallery-dl/blob/175d21fd8f7e52963911c02916d0634461cddb24/gallery_dl/extractor/common.py#L691-L709) captura una excepción, la incluye en un warning y continúa con cookies vacías. Esto puede ocurrir antes de que el [adaptador de XMA clasifique excepciones externas](https://github.com/eventmgmtplatform/x-media-archiver/blob/29741c20978a9a3b097c790fc352d73b1007c193/src/xma/adapters/discovery/gallery_dl.py#L122-L137). Una excepción sintética con marcador de identificador apareció en el logger bajo dobles; no se usaron ni expusieron credenciales reales. El warning puede contener información contextual que debe sanitizarse; una continuación sin cookies también impide inferir que cualquier éxito observado usó necesariamente la sesión prevista. No se ha probado que un warning concreto real apareciera en CI o smoke.

### A-03 — Validación insuficiente del selector de perfil

[BrowserAuthentication](https://github.com/eventmgmtplatform/x-media-archiver/blob/29741c20978a9a3b097c790fc352d73b1007c193/src/xma/adapters/discovery/gallery_dl.py#L37-L53) rechaza separadores y espacios, pero acepta `.` y `..`. El resolver de la dependencia combina el selector con su raíz y puede buscar recursivamente; una prueba con filesystem simulado mostró que `..` puede remontar la raíz prevista. Ello no prueba que el perfil real ni rutas del usuario se hayan accedido indebidamente. El contrato requiere un nombre local, no rutas arbitrarias; se requiere validar componentes especiales y probar contención sin consultar perfiles reales.

**Minimización adicional:** el selector de navegador pasa dominio `None`; la consulta de Firefox de la dependencia no limita las cookies cargadas al dominio objetivo. Una prueba con base simulada confirma la consulta sin filtro. Esto no demuestra que se hayan transmitido cookies de otros dominios. Es un riesgo de minimización a evaluar junto con A-01 y A-02.

### A-04 — Perfil protegido no diferenciado

El mapper lee identidad y nombre del perfil pero no evalúa la bandera de protección. Una prueba sintética con `protected=True` produjo un lote con activos y salida pública sin esa bandera; upstream expone ese campo. Esto demuestra falta de rechazo en el mapper, no que X haya devuelto contenido protegido ni que la sesión real tuviera ese acceso. ADR-0003 limita el trabajo a descubrimiento de activos públicos; confirmar y aplicar una política explícita para perfiles protegidos/desconocidos sin ampliar alcance.

### A-05 — Ruta personal heredada y afirmación demasiado amplia

Se detectó una ruta de caché bajo un directorio personal identificable en `docs/handoffs/XMA-CLI-001_HND-0002_B02-20261028-001_v0.1.0.md:94`. Su valor se omite deliberadamente. Es anterior al rework, presente en la baseline e integrada por B02; **no es evidencia de un secreto ni de un perfil de autenticación expuesto**. La afirmación de HND v0.2.0 de ausencia absoluta de identificadores locales en el tree debe precisarse. El tratamiento del archivo histórico requiere decisión gobernada apropiada; no se borró ni reescribió historia.

### A-06 — Trazabilidad de aceptación y documentación

HND/PR registran conteos, pero no el método ni resultado de una comprobación de integridad/readback SQLite, requerida por PRM-0009. El conteo público de la aplicación deriva del lote descubierto, no es por sí solo una consulta independiente de las filas persistidas. ADR-0003 pide comandos redactados; HND no registra una invocación completa ejecutada y redactada. El README mantiene además texto histórico sin calificar sobre ausencia de autenticación/bloqueo, inconsistente con la sección nueva. Recuperar o registrar evidencia sanitizada disponible desde la ejecución local, sin repetir smoke y sin publicar identificadores, cookies, rutas o URLs; corregir la documentación.

## 6. Aceptación pública declarada por el ejecutor

| Target | Salida declarada | Activos / distintos | Archivos declarados |
|---|---:|---:|---|
| Reuters | 3 | 0 / 0 | 0 |
| AP | 3 | 0 / 0 | 0 |
| BBCWorld | 0 | 2 / 2 | 1, extensión `.sqlite3` |

HND declara límite 2, secuencia única, parada al obtener dos y ausencia de medios, thumbnails, sidecars, staging y hashes de medios. Son **atestaciones versionadas**, no observaciones independientes de dot. La conservación del catálogo y logs locales fuera de Git es deliberada: no se exige revelar datos de autenticación ni repetir el smoke. Falta un resultado sanitizado de integridad/consulta de filas y la invocación ejecutada redactada, si se conservaron; no inventar evidencia.

## 7. Riesgos y acciones de rework

1. Corregir A-01–A-03 de forma acotada, con pruebas offline que ejerciten el comportamiento real de la dependencia y sus excepciones, sin leer perfiles ni cookies reales y sin crear nuevas credenciales. No sustituir con otra tecnología o ampliar acceso por inferencia.
2. Tratar A-04 mediante regla explícita y pruebas sintéticas de perfil protegido, preservando el mandato de activos públicos.
3. Gobernar A-05 sin publicar nuevamente la ruta ni reescribir historia por iniciativa del auditor; evaluar impacto y corrección documental de afirmaciones.
4. Completar A-06 con evidencia sanitizada disponible, comprobación explícita de integridad y conteo de dos filas distintas, y comandos redactados; si la evidencia original no existe, declararlo y pedir una decisión específica. No repetir el smoke sin autorización y prompt nuevos.
5. Reejecutar pruebas offline y CI sobre el nuevo SHA; publicar handoff y solicitar nueva auditoría. Q3-Público, B03, merge y B04 requieren decisión posterior de León.

## 8. Rollback

La contención propuesta por HND es mantener el PR draft y, si se autoriza, revertir mediante commits nuevos primero la documentación de entrega y después `87e9698`, regresando al modo anónimo; preservar catálogos y auditorías. El operador puede cerrar o invalidar su sesión local por separado. No se ejecutó rollback ni se cambió sesión alguna.

## 9. Dictamen y próxima acción

**REWORK_REQUIRED.** Los controles de CI y la declaración de dos activos no compensan las carencias recuperables de protección y trazabilidad enumeradas. `FAILED` requeriría evidencia de exposición real de secreto, descarga o desviación material consumada; no se encontró. `BLOCKED` por falta de evidencia sería una alternativa si no se pudiera recuperar evidencia, pero las fallas de implementación confirmadas determinan aquí `REWORK_REQUIRED`. No se valida Q3-Público ni se autoriza B04.

**Próxima acción exacta:** Chat debe revisar este informe, gobernar un rework y la forma de evidenciar la aceptación sin revelar datos sensibles; Codex puede implementar solo tras el prompt y autorización pertinentes. Dot reauditará el nuevo SHA/tree y CI. No publicar este informe en GitHub sin decisión del gobernante.

**Integridad de auditoría:** consultas read-only de GitHub y pruebas sintéticas con operaciones sensibles sustituidas. No se accedió a X, navegador ni cookies, no se repitió smoke y no se modificaron GitHub, código, ramas, PR, comentarios, revisiones o estados. Ninguna sesión se alteró.