# XMA-CLI-001 — Gate Register

**Versión:** 0.1.0

**Fuente canónica:** GitHub, CI, handoffs y auditorías versionadas

| Fecha (America/Mexico_City) | Gate | Evidencia | Decisión / estado | Autorización |
|---|---|---|---|---|
| 2026-10-28 | Q0 | Arquitectura, ADR-0001 y plan B00–B07 | Baseline aprobada | Leonel |
| 2026-10-28 | Q1 | PR #1, HND-0001, CI y merge `2acb88c` | Cerrado | Leonel |
| 2026-10-28 | Q2 | PR #2, HND-0002, AUD-0002, CI #6 | `VALIDATED_WITH_OBSERVATIONS`; merge `b2bdca7` | Leonel |
| 2026-10-28 | Q3 / B03 | PR #3, AUD-0003 v0.1.1 y PRM-0005 | `WAITING_VALIDATION`; persiste `AuthRequired` externo | Leonel: B03-REWORK-002 autorizado |

## Registro de desviaciones, alertas y rework

| ID | Bloque | Evento | Clasificación | Resolución |
|---|---|---|---|---|
| GOV-OBS-0001 | B02 | El monitor conservador marcó el merge de PR #2 como desviación porque su propio contrato prohibía mutaciones. | Alerta de alcance del monitor; no defecto de código. | Leonel había autorizado el cierre y después restableció que cada fase futura requiere prompt y gate. No se extiende autorización implícita a B03–B07. |
| GOV-BLK-0002 | B03 | Reuters, AP y BBCWorld devolvieron `AuthRequired` en la prueba pública anónima. | Bloqueo externo; salida `3`, sin activos catalogados. | No introducir cookies, autenticación ni otro extractor. B04 no inicia. |
| GOV-RWK-0003 | B03 | AUD-0003 identificó R-01 a R-07: evidencia, PR/gobierno, JSON, errores, idempotencia, límite y cursor. | `REWORK_REQUIRED`. | Leonel autorizó PRM-0004/DOT-PRM-0004; Codex debe detenerse tras handoff y CI. |
| GOV-RWK-0004 | B03 | AUD-0003 v0.1.1 detectó `OverflowError` no normalizado ante metadatos numéricos no finitos. | `WAITING_VALIDATION` tras B03-REWORK-002. | PRM-0005 ejecutado una vez; DOT-PRM-0005 debe auditar el HEAD final. |

Existe un rework B02 separado documentado por AUD-0002 v0.1.2, todavía sin integración ni CI sobre
su SHA final. B03 conserva `b2bdca7` como baseline; PRM-0004 exige conciliar esta trazabilidad sin
importar cambios B02 indiscriminadamente.

## Regla de transición

Ningún bloque posterior empieza por inferencia. Requiere prompt versionado, autorización humana,
rama aislada, handoff, auditoría y decisión del gate. Un merge nunca autoriza el bloque siguiente.

## Aislamiento de contexto — 2026-10-28

El recordatorio corporativo Netcool mostrado junto a la auditoría XMA es contexto ajeno a este
workstream. No modifica autorización, evidencia ni gates XMA. No se afirma resuelta ninguna
credencial ni se incorpora contenido reservado personal o corporativo como evidencia del proyecto.
El texto exacto de la reserva mencionada por Leonel no se recuperó; no se reconstruye por inferencia.

Rework B02 verificado en `feature/xma-b02-contracts`, publicación `4b8bdab`, AUD-0002 v0.1.2
(snapshot auditado `437dcf3`). No está integrado en main/B03; sigue pendiente de PR acotado y CI
sobre su entrega. Se conserva el cierre histórico Q2 sin convertirlo en certificación del rework.
