# XMA-CLI-001 — Gate Register

**Versión:** 0.1.0

**Fuente canónica:** GitHub, CI, handoffs y auditorías versionadas

| Fecha (America/Mexico_City) | Gate | Evidencia | Decisión / estado | Autorización |
|---|---|---|---|---|
| 2026-10-28 | Q0 | Arquitectura, ADR-0001 y plan B00–B07 | Baseline aprobada | Leonel |
| 2026-10-28 | Q1 | PR #1, HND-0001, CI y merge `2acb88c` | Cerrado | Leonel |
| 2026-10-28 | Q2 | PR #2, HND-0002, AUD-0002, CI #6 | `VALIDATED_WITH_OBSERVATIONS`; merge `b2bdca7` | Leonel |
| 2026-10-28 | Q3 / B03 | PR #3, CI #10 y HND-0003 | `BLOCKED`; Reuters, AP y BBCWorld requieren autenticación anónima no disponible | Leonel: decisión requerida |

## Registro de desviaciones, alertas y rework

| ID | Bloque | Evento | Clasificación | Resolución |
|---|---|---|---|---|
| GOV-OBS-0001 | B02 | El monitor conservador marcó el merge de PR #2 como desviación porque su propio contrato prohibía mutaciones. | Alerta de alcance del monitor; no defecto de código. | Leonel había autorizado el cierre y después restableció que cada fase futura requiere prompt y gate. No se extiende autorización implícita a B03–B07. |
| GOV-BLK-0002 | B03 | Reuters, AP y BBCWorld devolvieron `AuthRequired` en la prueba pública anónima. | Bloqueo externo; salida `3`, sin activos catalogados. | No introducir cookies, autenticación ni otro extractor. Se requiere decisión humana; B04 no inicia. |

No existe rework funcional abierto de B02. Las observaciones técnicas de `AUD-0002` se conservan
para la matriz de hardening B06.

## Regla de transición

Ningún bloque posterior empieza por inferencia. Requiere prompt versionado, autorización humana,
rama aislada, handoff, auditoría y decisión del gate. Un merge nunca autoriza el bloque siguiente.
