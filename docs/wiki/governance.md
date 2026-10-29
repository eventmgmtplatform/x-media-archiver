---
title: Gobierno
---

[Inicio](index.html) · [Producto v1](product.html) · [Arquitectura](architecture.html) · [Releases](releases.html) · [Gobierno](governance.html) · [Roadmap v2](roadmap.html)

---

# Gobierno y fuente documental

La wiki es el índice ejecutivo; no sustituye los documentos gobernados.

| Tema | Documento canónico |
|---|---|
| Plan | [Implementation Plan](https://github.com/eventmgmtplatform/x-media-archiver/blob/main/docs/planning/XMA-CLI-001_IMPLEMENTATION_PLAN_v0.1.0.md) |
| Gates | [Gate Register](https://github.com/eventmgmtplatform/x-media-archiver/blob/main/docs/governance/XMA-CLI-001_GATE-REGISTER_v0.1.0.md) |
| Git y releases | [Git Release Governance](https://github.com/eventmgmtplatform/x-media-archiver/blob/main/docs/governance/XMA-CLI-001_GIT_RELEASE_GOVERNANCE_v0.1.0.md) |
| Releases | [Release Management](https://github.com/eventmgmtplatform/x-media-archiver/blob/main/docs/release/XMA-CLI-001_RELEASE-MANAGEMENT_v1.0.0.md) |
| Operación | [BAU](https://github.com/eventmgmtplatform/x-media-archiver/blob/main/docs/operations/XMA-CLI-001_BAU-OPERATIONS_v1.0.0.md) |
| Requisitos | [System Requirements](https://github.com/eventmgmtplatform/x-media-archiver/blob/main/docs/requirements/XMA-CLI-001_SYSTEM-REQUIREMENTS_v1.0.0.md) |
| Decisiones | [ADR](https://github.com/eventmgmtplatform/x-media-archiver/tree/main/docs/adr) |
| Evidencia | [Handoffs](https://github.com/eventmgmtplatform/x-media-archiver/tree/main/docs/handoffs) |
| Auditorías | [Audits](https://github.com/eventmgmtplatform/x-media-archiver/tree/main/docs/audits) |

## Regla por release

1. Actualizar código, pruebas y documentación gobernada.
2. Actualizar wiki: producto, versión y roadmap.
3. Validar CI, seguridad, licencias y artefactos.
4. Integrar mediante squash autorizado.
5. Crear tag anotado y GitHub Release draft.
6. Publicar solo después de revisión humana.

La publicación de Pages no autoriza por sí misma merge, tag o release del producto.
