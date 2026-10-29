# XMA-CLI-001 — AUD-0006 A-06-PUBLIC-EVIDENCE v0.1.0

**Fecha:** 2026-10-28 (America/Mexico_City)  
**Auditor:** dot  
**Tipo:** auditoría independiente read-only  
**Resultado:** `BLOCKED / EVIDENCE_NOT_AVAILABLE`

## Alcance solicitado

Auditar el paquete local producido por PRM-0012 para A-06, contrastándolo contra:

- repositorio `eventmgmtplatform/x-media-archiver`;
- PR #3, rama `feature/xma-b03-discovery`;
- HEAD funcional `7adb2f670ef20deff8b70aec0fad0037762ebb8b`;
- tree funcional `128c7cf7b8466848516e3b4223be4b40c73397d5`;
- HND-0003 v0.3.0;
- CI #38 / run `40819317628`;
- catálogo esperado SHA-256 `61f0d43c72a4b2967c109c11c82ddc1811a7a7781a9d81468546eb7fd10523d7`;
- manifest esperado SHA-256 `f4d2e1e8749cbcb45c25847f68392f08cfc7573564874786c3c277e91e5ae1b9`.

## Precondición

La solicitud de auditoría exigía recibir directamente:

1. exactamente un archivo `.sqlite3`;
2. exactamente un manifest sanitizado `.json`.

Los adjuntos no estaban disponibles en la conversación de dot que recibió DOT-PRM-0014. La auditoría se detuvo antes de inspeccionar GitHub o ejecutar comprobaciones sobre el paquete.

## Matriz

| Control | Resultado | Evidencia |
|---|---|---|
| Catálogo SQLite recibido | BLOCKED | No recibido en la conversación auditora |
| Manifest JSON recibido | BLOCKED | No recibido en la conversación auditora |
| SHA-256 del catálogo | NOT_EXECUTED | Archivo ausente |
| SHA-256 del manifest | NOT_EXECUTED | Archivo ausente |
| `PRAGMA integrity_check` | NOT_EXECUTED | Archivo ausente |
| Esquema y conteos | NOT_EXECUTED | Archivo ausente |
| Identidades distintas | NOT_EXECUTED | Archivo ausente |
| Política metadata-only | NOT_EXECUTED | Archivo ausente |
| Privacidad y secretos | NOT_EXECUTED | Archivo ausente |
| HEAD, tree y CI | NOT_EXECUTED | La precondición ordenaba detenerse antes |
| Acceso a X, Firefox o cookies | PASS | No realizado |
| Mutaciones GitHub | PASS | No realizadas |

## Hallazgo

La declaración del handoff y los hashes esperados no sustituyen la inspección del paquete exacto. Aceptar A-06 sin los adjuntos impediría comprobar procedencia, integridad, conteos y ausencia de datos sensibles.

## Riesgo

Promover Q3-Público basándose únicamente en evidencia declarada produciría un cierre no reproducible y rompería la separación entre ejecución y validación independiente.

## Dictamen

`BLOCKED / EVIDENCE_NOT_AVAILABLE`.

Este resultado no invalida la ejecución PRM-0012 ni afirma que el paquete sea incorrecto. Registra únicamente que la evidencia no llegó a la frontera auditora.

A-06, Q3-Público y la transición general B03 continúan `BLOCKED`. No se autoriza merge, B04, B05, tag, release o certificación.

## Acción requerida

Entregar directamente a dot exactamente el catálogo y manifest cuyos hashes coincidan con los valores esperados. La nueva auditoría debe usar un mandato versionado independiente, no repetir el smoke y no acceder a X, Firefox o cookies.

## Rollback

No aplica. La auditoría fue read-only y no modificó documentación, GitHub ni evidencia local.
