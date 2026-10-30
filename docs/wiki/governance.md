---
title: Gobierno
---

[Inicio](index.html) · [Producto v1](product.html) · [Archivo completo B06](b06-complete-profile-archive.html) · [Arquitectura](architecture.html) · [Releases](releases.html) · [Gobierno](governance.html) · [Roadmap v2](roadmap.html)

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
| Certificaciones | [CERT-0001 B06](https://github.com/eventmgmtplatform/x-media-archiver/blob/main/docs/certifications/XMA-CLI-001_CERT-0001_B06-COMPLETE-PROFILE-ARCHIVE_v0.1.0.md) |

## Regla por release

1. Actualizar código, pruebas y documentación gobernada.
2. Actualizar wiki: producto, versión y roadmap.
3. Validar CI, seguridad, licencias y artefactos.
4. Integrar mediante squash autorizado.
5. Crear tag anotado y GitHub Release draft.
6. Publicar solo después de revisión humana.

La publicación de Pages no autoriza por sí misma merge, tag o release del producto.
PRM-0056 `CLI-EXECUTION-REPORTING` está integrado y validado; PRM-0063 prepara el release candidate
v0.2.0 sin autorizar merge, tag, Release o PyPI.
