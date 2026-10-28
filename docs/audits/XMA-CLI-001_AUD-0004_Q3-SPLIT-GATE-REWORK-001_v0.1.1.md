# XMA-CLI-001 — AUD-0004 Q3 Split Gate Rework 001

**Versión:** 0.1.1  
**Fecha:** 2026-10-28, 22:27–22:29 UTC  
**Auditor:** dot  
**Mandato:** XMA-CLI-001-DOT-PRM-0010 v0.1.0  
**Dictamen documental:** **VALIDATED_WITH_OBSERVATIONS**  
**Alcance:** DOC-01 exclusivamente; sin reauditoría funcional ni smoke.

## 1. Resumen ejecutivo

DOC-01 está corregido en el snapshot auditado. ADR-0002, Gate Register, Implementation Plan y el cuerpo del PR establecen que Q3-Público exige **exactamente dos activos públicos de video distintos y catalogados**; `--limit 2` es el máximo operativo y cero o uno no pasan el gate.

La separación de estados se preserva: **Q3-Técnico `VALIDATED_WITH_OBSERVATIONS`**, **Q3-Público `BLOCKED`** y **transición general B03 `BLOCKED`**. No se encontró waiver actual ni autorización de smoke, merge, B04 o ampliación de acceso. El dictamen de este informe valida la corrección **documental**, no la aceptación pública ni el producto.

## 2. Identidad y fuentes

- [DOT-PRM-0010 v0.1.0](https://github.com/eventmgmtplatform/x-media-archiver/blob/1033b17b49377055f7065dfb8100a4c6c543c762/docs/prompts/XMA-CLI-001_DOT-PRM-0010_Q3-SPLIT-GATE-REAUDIT_v0.1.0.md), leído íntegramente.
- [PR #3](https://github.com/eventmgmtplatform/x-media-archiver/pull/3), [ADR-0002](https://github.com/eventmgmtplatform/x-media-archiver/blob/1033b17b49377055f7065dfb8100a4c6c543c762/docs/adr/ADR-0002-q3-split-technical-public-gate.md), [Gate Register](https://github.com/eventmgmtplatform/x-media-archiver/blob/1033b17b49377055f7065dfb8100a4c6c543c762/docs/governance/XMA-CLI-001_GATE-REGISTER_v0.1.0.md), [Implementation Plan](https://github.com/eventmgmtplatform/x-media-archiver/blob/1033b17b49377055f7065dfb8100a4c6c543c762/docs/planning/XMA-CLI-001_IMPLEMENTATION_PLAN_v0.1.0.md), AUD-0004 v0.1.0 y AUD-0003 v0.1.5.
- HEAD `1033b17b49377055f7065dfb8100a4c6c543c762`; tree `d78777795e202a9c5865f3f1ac5b924e52a26767`. PR abierto, draft, sin merge y main `b2bdca7961f00d54f2465a4f8d26b2003340c3b9`.
- Baseline documental `4e61c3de6f88251d586faea7077fbf5da90c6b33`, tree `d79b0fe5fb4924fcb05ac0276279bcb02c814eb1`; es padre único del HEAD.
- Snapshot técnico histórico `beb2a7d9123b23f51f6f3a92571501cb25a025d6`, tree `f1b2207b0db65d92e7d7ba877a3444389b7b3010`, con CI #26. CI #27 corresponde al baseline documental anterior.
- [CI #28 / 40779552268](https://github.com/eventmgmtplatform/x-media-archiver/actions/runs/40779552268): completed/success, un job quality y 13 pasos exitosos; locked sync, Ruff, mypy, **156 pruebas, 95.18 %**, sdist y wheel. Checkout merge sintético `2c9e033ee34b03650fb94e5783f2af8590b3146d`, tree idéntico al HEAD; no fue checkout literal del HEAD. CI #28 acredita el tree documental, no aceptación pública y no sustituye CI #26.

## 3. Matriz DOC-01

| Control | Resultado | Evidencia |
|---|---|---|
| HEAD/tree estables | PASS | Identidad exacta, parent y CI verificados; reconsulta final sin cambios. |
| AUD-0004 v0.1.0 íntegro | PASS | Archivo publicado coincide byte por byte con la entrega de dot: 10,001 bytes; SHA-256 `112ae4732ebc8898b305b15feaef30b8976958024a45706132020cb61fdbdc17`; blob Git `48e91cb88db4915286156ed420c0a7d065764316`. Conserva `REWORK_REQUIRED` histórico. |
| Máximo operativo | PASS | ADR, registro, plan y PR distinguen `--limit 2` como máximo de la prueba. |
| Umbral público | PASS | ADR, Gate Register y PR requieren exactamente dos activos públicos de video distintos catalogados; plan lo especifica en su siguiente paso autorizado. |
| Cero o uno | PASS | Los documentos indican expresamente que 0 o 1 no satisfacen Q3-Público. |
| Estados | PASS | Q3-Técnico `VALIDATED_WITH_OBSERVATIONS`; Q3-Público y transición general B03 `BLOCKED`. |
| Sin waiver o ampliación | PASS | No existe waiver actual ni autorización para smoke, merge, B04, cookies, autenticación, otro extractor, descarga, tag, release o certificación. La posibilidad de una decisión humana futura explícita y versionada no es un waiver presente. |
| Allowlist | PASS | Un commit documental y cinco archivos permitidos; sin cambios a código, tests/fixtures, lockfile, workflow ni HND. |
| Estado GitHub | PASS observado | PR abierto/draft/sin merge; main sin cambios; 0 comentarios, revisiones e hilos; refs tags y releases vacíos. Consultas no demuestran ausencia de eventos borrados. |

## 4. Diff e integridad

[Comparación exacta](https://github.com/eventmgmtplatform/x-media-archiver/compare/4e61c3de6f88251d586faea7077fbf5da90c6b33...1033b17b49377055f7065dfb8100a4c6c543c762): un commit lineal con cinco archivos permitidos:

1. `docs/audits/XMA-CLI-001_AUD-0004_Q3-SPLIT-GATE_20261028-001_v0.1.0.md`.
2. `docs/adr/ADR-0002-q3-split-technical-public-gate.md`.
3. `docs/governance/XMA-CLI-001_GATE-REGISTER_v0.1.0.md`.
4. `docs/planning/XMA-CLI-001_IMPLEMENTATION_PLAN_v0.1.0.md`.
5. `docs/prompts/XMA-CLI-001_DOT-PRM-0010_Q3-SPLIT-GATE-REAUDIT_v0.1.0.md`.

Árboles recursivos no truncados: 75 blobs en baseline y 77 en HEAD; 72 blobs comunes sin cambio. No hay cambios de fuente, pruebas, fixtures, workflow, lockfile o handoff, ni incorporación observada de medios, bases, secretos, cookies, otro extractor o componentes B04/B05. La revisión de secretos y de historia tiene límites y no demuestra ausencia de todo dato o evento oculto.

## 5. Observaciones y riesgos

1. **Aceptación pública pendiente:** el smoke histórico no acreditó dos activos y Q3-Público sigue `BLOCKED`. Esta auditoría no repitió la prueba ni observó directamente el entorno original. El resultado técnico no certifica el comportamiento público.
2. **CI separadas:** CI #26 es evidencia del tree técnico, CI #27 del baseline documental y CI #28 del tree documental de esta corrección. Ninguna sustituye la aceptación pública.
3. **Trazabilidad histórica:** AUD-0003 v0.1.5 conserva la observación de que la autorización previa de ejecución se declaró en HND, pero dot no corroboró independientemente el acto humano anterior. No se reconstruye ni infiere con esta auditoría.
4. **Rework B02 y riesgos históricos:** permanecen separados; no se certifican aquí. `cursor=None` no promete completitud y los catálogos anteriores pueden requerir una decisión separada.

## 6. Rollback

Si se requiere revertir DOC-01, hacerlo solo mediante un nuevo commit autorizado para esta corrección documental; no reescribir historia, borrar auditorías ni modificar catálogos. No se ejecutó rollback.

## 7. Dictamen y próxima acción

**VALIDATED_WITH_OBSERVATIONS.** DOC-01 queda cerrado documentalmente: el mínimo y máximo exigidos son inequívocos, los estados y restricciones permanecen y el diff está dentro de la allowlist. Esta validación no cambia el estado público ni la transición: ambos siguen **BLOCKED**.

**Próxima acción exacta:** entregar este informe al gobernante para revisión y versionado autorizado. Mantener PR #3 draft y Q3-Público/B03 bloqueados hasta que el criterio de dos activos se cumpla con un plan específicamente autorizado o una decisión humana posterior, explícita y versionada lo cambie. No aprobar ni fusionar el PR y no iniciar B04.

**Integridad:** auditoría documental de solo lectura. No se modificaron GitHub, código, ramas, PR, comentarios, revisiones ni estados; no se realizó smoke ni acceso a X, merge, tag o release.
