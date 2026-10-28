# XMA-CLI-001 — Gate Register

**Versión:** 0.1.0

**Fuente canónica:** GitHub, CI, handoffs y auditorías versionadas

| Fecha (America/Mexico_City) | Gate | Evidencia | Decisión / estado | Autorización |
|---|---|---|---|---|
| 2026-10-28 | Q0 | Arquitectura, ADR-0001 y plan B00–B07 | Baseline aprobada | Leonel |
| 2026-10-28 | Q1 | PR #1, HND-0001, CI y merge `2acb88c` | Cerrado | Leonel |
| 2026-10-28 | Q2 | PR #2, HND-0002, AUD-0002, CI #6 | `VALIDATED_WITH_OBSERVATIONS`; merge `b2bdca7` | Leonel |
| 2026-10-28 | Q3 / B03 | PR #3, AUD-0003 v0.1.1 y PRM-0005 | `WAITING_VALIDATION`; persiste `AuthRequired` externo | Leonel: B03-REWORK-002 autorizado |
| 2026-10-28 | Q3 / B03 | PR #3, AUD-0003 v0.1.2 y PRM-0006 | `WAITING_VALIDATION`; persiste `AuthRequired` externo | Leonel: B03-REWORK-003 autorizado |
| 2026-10-28 | Q3 / B03 | PR #3, AUD-0003 v0.1.3 y PRM-0007 | `WAITING_VALIDATION`; persiste `AuthRequired` externo | Leonel: B03-REWORK-004 autorizado una vez |
| 2026-10-28 | Q3 / B03 | PR #3, AUD-0003 v0.1.4 y PRM-0008 | `WAITING_VALIDATION`; persiste `AuthRequired` externo | Leonel: B03-REWORK-005 autorizado una vez |
| 2026-10-28 | Q3-Técnico / B03 | PR #3, HND-0003 v0.1.5, CI #26, AUD-0003 v0.1.5 y ADR-0002 | `VALIDATED_WITH_OBSERVATIONS`; implementación y controles técnicos aceptados | Leonel: división Q3 autorizada |
| 2026-10-28 | Q3-Público / B03 | Smoke anónimo Reuters → AP → BBCWorld y AUD-0003 v0.1.5 | `BLOCKED`; no se acreditaron dos activos públicos catalogados | Sin waiver; B04, merge y ampliación de acceso no autorizados |
| 2026-10-28 | Q3 documental / B03 | AUD-0004 v0.1.0 y DOC-01 | `WAITING_VALIDATION`; se precisa que el conteo aceptado debe ser exactamente 2 con `--limit 2` | Leonel autorizó rework documental y publicación de DOT-PRM-0010 |
| 2026-10-28 | Q3 documental / B03 | AUD-0004 v0.1.1, DOC-01 y CI #28 | `VALIDATED_WITH_OBSERVATIONS`; DOC-01 cerrado documentalmente | Leonel autorizó versionado y reconciliación; Q3-Público/B03 continúan `BLOCKED` |
| 2026-10-28 | Q3-Público / B03 Auth | ADR-0003, PRM-0009 y DOT-PRM-0011 | `AUTHORIZED_FOR_ONE_EXECUTION`; gate aún `BLOCKED` hasta evidencia y auditoría | Leonel autorizó sesión local Firefox y smoke `--limit 2`; identificadores locales no se publican; sin B04 ni merge |
| 2026-10-28 | Q3-Público / B03 Auth | HND-0003 v0.2.0 y aceptación Reuters → AP → BBCWorld | `WAITING_VALIDATION`; BBCWorld acreditó exactamente 2 activos distintos | PRM-0009 consumido una vez; DOT-PRM-0011 debe auditar; sin merge ni B04 |

## Registro de desviaciones, alertas y rework

| ID | Bloque | Evento | Clasificación | Resolución |
|---|---|---|---|---|
| GOV-OBS-0001 | B02 | El monitor conservador marcó el merge de PR #2 como desviación porque su propio contrato prohibía mutaciones. | Alerta de alcance del monitor; no defecto de código. | Leonel había autorizado el cierre y después restableció que cada fase futura requiere prompt y gate. No se extiende autorización implícita a B03–B07. |
| GOV-BLK-0002 | B03 | Reuters, AP y BBCWorld devolvieron `AuthRequired` en la prueba pública anónima. | Bloqueo externo; salida `3`, sin activos catalogados. | No introducir cookies, autenticación ni otro extractor. B04 no inicia. |
| GOV-RWK-0003 | B03 | AUD-0003 identificó R-01 a R-07: evidencia, PR/gobierno, JSON, errores, idempotencia, límite y cursor. | `REWORK_REQUIRED`. | Leonel autorizó PRM-0004/DOT-PRM-0004; Codex debe detenerse tras handoff y CI. |
| GOV-RWK-0004 | B03 | AUD-0003 v0.1.1 detectó `OverflowError` no normalizado ante metadatos numéricos no finitos. | `WAITING_VALIDATION` tras B03-REWORK-002. | PRM-0005 ejecutado una vez; DOT-PRM-0005 debe auditar el HEAD final. |
| GOV-RWK-0005 | B03 | AUD-0003 v0.1.2 demostró que duraciones negativas submilisegundo podían redondearse y persistirse como cero. | `WAITING_VALIDATION` tras B03-REWORK-003. | PRM-0006 ejecutado una vez; DOT-PRM-0006 debe auditar el nuevo HEAD. |
| GOV-RWK-0006 | B03 | AUD-0003 v0.1.3 detectó que `Decimal.from_float()` alteró los empates positivos históricos. | `WAITING_VALIDATION` tras B03-REWORK-004. | Leonel autorizó una ejecución de PRM-0007; DOT-PRM-0007 debe auditar el HEAD final. |
| GOV-RWK-0007 | B03 | AUD-0003 v0.1.4 detectó que `Decimal(value)` rechazaba exponentes extremos aceptados por la baseline. | `WAITING_VALIDATION` tras B03-REWORK-005. | Leonel autorizó una ejecución de PRM-0008; DOT-PRM-0008 debe auditar el HEAD final. |
| GOV-DEC-0008 | B03 / Q3 | AUD-0003 v0.1.5 cerró los reworks técnicos y mantuvo bloqueada la aceptación pública por `AuthRequired`. | Q3 se divide en Q3-Técnico y Q3-Público conforme a ADR-0002. | Leonel autorizó versionar la auditoría y la decisión; no autorizó merge, B04, cookies, autenticación ni otro extractor. |
| GOV-RWK-0009 | B03 / Q3 | AUD-0004 v0.1.0 detectó que «hasta dos» expresaba solo el máximo y no el mínimo de aceptación. | `CLOSED — VALIDATED_WITH_OBSERVATIONS`; DOC-01 fija conteo requerido exactamente 2 y `--limit 2` como máximo operativo. | AUD-0004 v0.1.1 valida el cierre; Q3-Público/B03 siguen `BLOCKED` y no se autorizan smoke, merge o B04. |
| GOV-DEC-0010 | B03 / Q3-Público | El modo anónimo terminó en `AuthRequired`; el humano confirmó una cuenta dedicada y visibilidad pública. | ADR-0003 autoriza una prueba local autenticada, sin descarga y con parámetros redactados. | Una ejecución PRM-0009 y auditoría DOT-PRM-0011; secretos/identificadores locales fuera de Git; B04/merge prohibidos. |
| GOV-EVD-0011 | B03 / Q3-Público | Reuters y AP terminaron con código 3; BBCWorld terminó con código 0 y exactamente 2 activos distintos. | `WAITING_VALIDATION`; evidencia sanitizada, solo `.sqlite3`, sin medios. | DOT-PRM-0011 debe auditar HND/CI; no autoriza transición, merge ni B04. |

Existe un rework B02 separado documentado por AUD-0002 v0.1.2, todavía sin integración ni CI sobre
su SHA final. B03 conserva `b2bdca7` como baseline; PRM-0004 exige conciliar esta trazabilidad sin
importar cambios B02 indiscriminadamente.

## Regla de transición

Ningún bloque posterior empieza por inferencia. Requiere prompt versionado, autorización humana,
rama aislada, handoff, auditoría y decisión del gate. Un merge nunca autoriza el bloque siguiente.

La validación de Q3-Técnico no satisface Q3-Público. Q3-Público debe acreditar exactamente dos
activos públicos de video distintos y catalogados en una prueba controlada con `--limit 2`.
El límite 2 es el máximo operativo y el mínimo de aceptación: cero o uno mantienen `BLOCKED`.
El criterio solo puede sustituirse mediante una nueva decisión humana versionada. Mientras
permanezca `BLOCKED`, no se autoriza merge, B04 ni certificación.

## Aislamiento de contexto — 2026-10-28

El recordatorio corporativo Netcool mostrado junto a la auditoría XMA es contexto ajeno a este
workstream. No modifica autorización, evidencia ni gates XMA. No se afirma resuelta ninguna
credencial ni se incorpora contenido reservado personal o corporativo como evidencia del proyecto.
El texto exacto de la reserva mencionada por Leonel no se recuperó; no se reconstruye por inferencia.

Rework B02 verificado en `feature/xma-b02-contracts`, publicación `4b8bdab`, AUD-0002 v0.1.2
(snapshot auditado `437dcf3`). No está integrado en main/B03; sigue pendiente de PR acotado y CI
sobre su entrega. Se conserva el cierre histórico Q2 sin convertirlo en certificación del rework.
