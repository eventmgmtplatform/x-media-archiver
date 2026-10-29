# XMA-CLI-001 — AUD-0005: B03 Auth Boundary Rework 001

**Versión:** 0.1.1  
**Fecha:** 2026-10-29 UTC  
**Auditor:** dot  
**Mandato:** XMA-CLI-001-DOT-PRM-0012 v0.1.0  
**Dictamen:** **REWORK_REQUIRED**  
**Naturaleza:** auditoría independiente, una ejecución, solo lectura; informe preparado para revisión humana y eventual versionado.

## 1. Resumen ejecutivo

Las precondiciones de identidad y CI se cumplieron. La revisión de la frontera autenticada encontró dos fallas recuperables en A-02: una sesión sintética sin credencial de sesión, pero con una cookie no vacía, alcanza el flujo guest; y un bucle de symlink sintético produce una excepción no sanitizada que escapa del lector, adaptador y funciones de comando. No se comprobó que alguno de estos sucesos ocurriera en el smoke histórico ni que se expusiera información real.

A-01, A-04 y A-05 satisfacen los controles examinados con las limitaciones indicadas; A-03 rechaza los escapes comprobados, pero falla como control integral por la excepción no sanitizada en el caso de bucle de enlace. A-06 es **NOT_VERIFIABLE / EVIDENCE_NOT_AVAILABLE**. El catálogo original no fue vinculado de manera inequívoca; no es posible comprobar independientemente su integridad ni sus dos identidades. Q3-Público y la transición general B03 continúan **BLOCKED**. El resultado de esta auditoría del rework no modifica el estado histórico Q3-Técnico ni sustituye una decisión humana sobre gates.

## 2. Identidad y precondiciones

- Repositorio [eventmgmtplatform/x-media-archiver](https://github.com/eventmgmtplatform/x-media-archiver), [PR #3](https://github.com/eventmgmtplatform/x-media-archiver/pull/3), rama `feature/xma-b03-discovery`.
- HEAD auditado: `dc11051c08612254175ebbe36d9fa3789274e99f`.
- Tree auditado: `e4155e3a2b2e2d8fb8abc47a18ff5145a2ac99c8`. La API Git Data vincula el HEAD con ese tree. Al cierre de la inspección el PR permanecía en el mismo HEAD, abierto, draft y sin merge.
- Base del PR: `main`, `b2bdca7961f00d54f2465a4f8d26b2003340c3b9`. Baseline de este rework: `d94dbcca88286056c07bb1f097c4576f899b9881`; dos commits descendientes: `e6a1017871b0e8e06ed75d68eeb8cb68313dd299` y el HEAD. La ancestría es verificable; un snapshot por sí solo no demuestra ausencia histórica universal de force-push.
- HND-0003 v0.2.1 presente en el tree, blob `4ada77bfa267e228b6e872e9bc71aa3c4ece66a0`; contenido íntegro revisado. [Handoff](https://github.com/eventmgmtplatform/x-media-archiver/blob/dc11051c08612254175ebbe36d9fa3789274e99f/docs/handoffs/XMA-CLI-001_HND-0003_B03-20261028-001_v0.2.1.md).
- [CI #33, run 40795268397](https://github.com/eventmgmtplatform/x-media-archiver/actions/runs/40795268397): SUCCESS, intento 1, **204 pruebas y cobertura 94.71 %** según log; job `quality` 123190105409 y pasos de calidad exitosos. El checkout usa el merge sintético `3ac968163b5312677e9dd7b4cc695137e17ee2ca`, cuyo tree es idéntico al tree auditado; no constituye un merge del PR. La cobertura y pruebas CI son evidencia remota, no resultados locales de dot.
- [Prompt canónico](https://github.com/eventmgmtplatform/x-media-archiver/blob/dc11051c08612254175ebbe36d9fa3789274e99f/docs/prompts/XMA-CLI-001_DOT-PRM-0012_B03-AUTH-BOUNDARY-REWORK-AUDIT_v0.1.0.md) leído íntegramente.

## 3. Matriz de controles

| Control | Resultado | Evidencia y límites |
|---|---|---|
| A-01 | PASS | Lector propio usa SQLite URI `mode=ro&immutable=1`, `query_only` y allowlist exacta de hosts; entrega un diccionario a gallery-dl, no el selector de navegador que activa su fallback de copia. Prueba sintética con conexión simulada y revisión de rama upstream. No se abrió ningún perfil ni DB real; no es una prueba de todos los sistemas operativos. |
| A-02 | FAIL | Excepciones esperadas probadas se sanitizan, pero un `RuntimeError` por symlink circular escapa y contiene el marcador de ruta sintética. Además, un diccionario no vacío sin `auth_token` pasa el lector y el flujo upstream puede seleccionar guest. Ver hallazgos F-01/F-02. |
| A-03 | FAIL | Selector rechaza 17 entradas inválidas y se observaron selección exacta y contención en casos sintéticos, incluidos traversal y symlink hacia fuera. Sin embargo un symlink circular no termina con error sanitizado, por lo que el control integral no queda cerrado. No se demuestra que un enlace circular permita escape de contención. |
| A-04 | PASS | `protected is not False` rechaza true, null, ausencia y valores ambiguos antes de persistencia. Matriz sintética de 99 casos en funciones reales de mapper, servicio y CLI con dependencias sustituidas; los rechazados no alcanzaron UoW, CLI devolvió 5. Solo false avanzó. |
| A-05 | PASS | Árbol actual contiene `<LOCAL_CACHE_PATH>` en el handoff histórico corregido. Escaneo acotado de 88 blobs de texto no encontró firmas comunes de rutas personales o secretos. No se reescribió historia en esta auditoría. La detección por patrones no prueba ausencia universal. |
| A-06 | NOT_VERIFIABLE | HND declara **EVIDENCE_NOT_AVAILABLE**: no se vinculó el SQLite original de forma inequívoca. Integridad, conteo y dos identidades no fueron comprobados por dot. La declaración anterior sobre BBCWorld es histórica, no una evidencia verificada de aceptación. |

Fuentes de controles: [lector Firefox](https://github.com/eventmgmtplatform/x-media-archiver/blob/dc11051c08612254175ebbe36d9fa3789274e99f/src/xma/adapters/discovery/firefox_auth.py#L14-L110), [runner](https://github.com/eventmgmtplatform/x-media-archiver/blob/dc11051c08612254175ebbe36d9fa3789274e99f/src/xma/adapters/discovery/gallery_dl.py#L75-L104), [mapper](https://github.com/eventmgmtplatform/x-media-archiver/blob/dc11051c08612254175ebbe36d9fa3789274e99f/src/xma/adapters/discovery/gallery_dl.py#L162-L164), [servicio](https://github.com/eventmgmtplatform/x-media-archiver/blob/dc11051c08612254175ebbe36d9fa3789274e99f/src/xma/application/discovery.py#L57-L67).

## 4. Hallazgos y rework requerido

### F-01 — degradación silenciosa a guest con sesión incompleta

El lector comprueba que el diccionario sea no vacío, pero no que exista la cookie necesaria para autenticación. Con un inventario y filas exclusivamente sintéticos que contienen solo `ct0`, el lector real devolvió el diccionario, el runner real lo entregó al job simulado y las funciones exactas de login y llamada de gallery-dl 1.32.18 seleccionaron el camino guest antes de cualquier acceso de red. Esto contradice la garantía de A-02 de que una autenticación solicitada no degrade silenciosamente.

**Límite:** se ejecutaron cuerpos de funciones upstream y XMA con dependencias y job sustituidos; no se realizó petición X ni se comprobó que un perfil real o el smoke previo presentara esta condición. La validez o expiración de una sesión real no se ha determinado.

**Acción requerida para Codex, bajo nuevo gobierno:** definir y hacer cumplir una condición fail-closed para sesión incompleta, sin exponer credenciales, y probar de forma offline tanto el caso guest-only como fallas y sesión sintética suficiente a través de lector, adaptador y comandos. No introducir cookies reales en pruebas.

### F-02 — excepción de resolución no sanitizada

Un perfil e inventario sintéticos cuyo path apunta a un enlace simbólico circular provoca `RuntimeError` en `Path.resolve`; el lector captura errores seleccionados pero no ese tipo. La excepción conserva un marcador sintético de ruta y atraviesa el adaptador y las funciones reales `inspect` y `sync` en pruebas aisladas. La prueba no ejecutó el parser/renderizado real de Typer, por lo que no se afirma haber observado un traceback CLI completo ni una fuga real. El riesgo de propagación contradice la sanitización constante exigida.

**Acción requerida:** cubrir el error concreto de resolución con el mismo contrato público sanitizado, sin captura amplia injustificada; incluir pruebas offline de bucle de symlink en ambas fronteras de comando y comprobar stdout, stderr, logs y ausencia de persistencia. Mantener rechazo y contención de los demás casos.

### O-01 — redacción documental

README y Gate Register describen A-01–A-06 como cerrados o implementados, aunque también mantienen explícitamente A-06 indisponible y Q3-Público bloqueado. Aclarar la diferencia entre entrega del rework y verificación del control evidencial; no promover el gate. No se exige reescritura del historial.

## 5. Pruebas independientes y alcance

- Reproducción offline del lector y selector: 17 selectores inválidos, tres valores límite aceptados; inventarios y enlaces simbólicos sintéticos; resolución contenida; conexión SQLite simulada y allowlist de dominios; inyección de errores y marcadores ficticios. Se reprodujeron F-01 y F-02 sin abrir bases de cookies ni perfiles reales.
- A-04: 99 combinaciones sintéticas, 5 casos de selección y 3 spies del runner. No son 107 pruebas pytest. Las funciones de producción fueron ejecutadas con stubs de gallery-dl, Typer y Rich; el parser real y la suite pytest completa no se ejecutaron localmente por falta de dependencias disponibles offline. No se realizaron instalaciones por red.
- Runner: modo anónimo por defecto; Firefox y perfil se requieren conjuntamente; Firefox único; descarga y downloader deshabilitados, caché en memoria, cookies-update desactivado. El spy confirma que una excepción reconocida del lector impide crear el job; F-01 muestra que un diccionario insuficiente no es detectado como fallo.
- CI contiene sync de dependencias, Ruff, mypy, pytest y build. No se observa smoke ni llamada a X en el workflow de pruebas. La instalación de dependencias usa red: CI no es un entorno completamente aislado de red; la afirmación revisada es que las pruebas no acceden a X, no que toda la ejecución carezca de red.
- Se revisaron [diff gobernado](https://github.com/eventmgmtplatform/x-media-archiver/compare/d94dbcca88286056c07bb1f097c4576f899b9881...dc11051c08612254175ebbe36d9fa3789274e99f), commits, workflow, HND, README, Gate Register y plan. El rework comprende 13 archivos; lockfile, workflow, esquema SQLite y funcionalidad B02 no cambiaron en ese diff. El PR completo muestra 60 archivos y 35 commits.
- Árbol recursivo no truncado: 113 entradas, 88 blobs. No se detectaron archivos multimedia, bases, exportaciones de cookies, sidecars o staging por nombres/extensiones, ni dependencias ejecutables prohibidas en el alcance revisado. No se observaron implementación B04/B05, tags ni releases. Estas comprobaciones no prueban lo sucedido fuera de los datos inspeccionados.
- No se accedió a X, Firefox, perfiles reales, cookies, sesión, SQLite original ni filesystem original; no se ejecutó smoke y no se reconstruyó evidencia. Declaraciones del HND sobre actividades históricas no se convierten en comprobaciones independientes.

## 6. Riesgos residuales y rollback

1. Una sesión no vacía pero incompleta puede operar como guest sin que el usuario lo sepa. La prueba no acredita uso indebido real.
2. Una ruta de inventario con bucle puede producir una excepción sin sanitizar; no se observó filtración real. Datos sensibles no deben incorporarse a ejemplos, logs, tickets ni pruebas de corrección.
3. La aceptación pública previa no es verificable: no usar el resultado declarado como autorización de Q3-Público o cierre de B03.
4. Los escaneos por patrones y la ejecución con stubs no demuestran ausencia absoluta de secretos o todos los comportamientos de plataforma.

**Rollback operativo propuesto, sujeto a gobierno humano:** mantener deshabilitado el uso autenticado de la entrega pendiente y el PR en draft; si se requiere reversión, evaluar un revert explícito y trazable de los commits del rework en la rama autorizada, preservando historia y evidencia, con evaluación de dependencias y CI por Codex. No borrar catálogos ni reescribir historia. Este informe no ejecuta ni autoriza rollback.

## 7. Dictamen y siguiente acción

**REWORK_REQUIRED** por F-01 y F-02, recuperables sin atribuir exposición o ejecución real. El CI verde no cubre estas fronteras sintéticas. A-06 permanece **EVIDENCE_NOT_AVAILABLE** y Q3-Público/B03 **BLOCKED**, independientemente de la resolución técnica.

**Siguiente acción exacta:** León y Chat revisan este informe y gobiernan un rework acotado para Codex sobre F-01/F-02 y la aclaración O-01, con pruebas exclusivamente sintéticas offline y nueva evidencia de CI; una nueva auditoría requiere su propio mandato. Cualquier decisión posterior sobre Q3-Público, cierre B03, merge o B04 corresponde a León. No se aprueba ni fusiona el PR, ni se autoriza B04, tag, release, certificación o nuevo smoke mediante este informe.
