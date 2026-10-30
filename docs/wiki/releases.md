---
title: Releases
---

[Inicio](index.html) · [Producto v1](product.html) · [Arquitectura](architecture.html) · [Releases](releases.html) · [Gobierno](governance.html) · [Roadmap v2](roadmap.html)

---

# Releases

## Matriz de control

| Versión | Estado | Plataforma | Alcance |
|---|---|---|---|
| 0.1.2 | Released | Linux x86_64 | Media recovery, deadline activo, add/archive hasta 20 y provider-best |
| 0.1.1 | Released | Linux x86_64 | Recovery, modo aditivo, límites 1–10 y provider-best |
| 0.1.0 | Released | Linux x86_64 | X, URL individual, lotes 1/2/5 y archive 10 |
| 0.2.x | Planeada | Linux | Estabilización operativa y deuda v1 |
| 2.0.0 | Roadmap | Por definir | Núcleo multiplataforma y nuevos adaptadores |

## v0.1.2

Publicado el 2026-10-30. [Descargar GitHub Release](https://github.com/eventmgmtplatform/x-media-archiver/releases/tag/v0.1.2).

Incluye clasificación sanitizada de fallos multimedia, renovación acotada, continuación del
escaneo tras candidatos fallidos, deadline activo, `download --limit 1..10`, `--add 1..20`, total
máximo veinte, `archive --limit 20` y provider-best. La aceptación pública completó 0→5→10→20.
El escenario DownloadError no ocurrió públicamente; su continuidad se validó offline.

Evidencia y control:

- [CHANGELOG](https://github.com/eventmgmtplatform/x-media-archiver/blob/main/CHANGELOG.md)
- [Release notes v0.1.2](https://github.com/eventmgmtplatform/x-media-archiver/blob/main/docs/release/XMA-CLI-001_RELEASE-NOTES_v0.1.2.md)
- [HND-0014 postrelease](https://github.com/eventmgmtplatform/x-media-archiver/blob/main/docs/handoffs/XMA-CLI-001_HND-0014_V0.1.2-POSTRELEASE_v0.1.0.md)

## v0.1.1

Publicado el 2026-10-29. [Descargar GitHub Release](https://github.com/eventmgmtplatform/x-media-archiver/releases/tag/v0.1.1).

Corrige la recuperación de trabajos fallidos sin artifacts, agrega `--add 1..10`, convierte
límites absolutos inferiores en no-op offline, acota el escaneo y documenta la selección
`provider-best`. Conserva el máximo global de diez y no certifica operación masiva.

Evidencia y control:

- [CHANGELOG](https://github.com/eventmgmtplatform/x-media-archiver/blob/main/CHANGELOG.md)
- [Release notes v0.1.1](https://github.com/eventmgmtplatform/x-media-archiver/blob/main/docs/release/XMA-CLI-001_RELEASE-NOTES_v0.1.1.md)
- [HND-0011 postrelease](https://github.com/eventmgmtplatform/x-media-archiver/blob/main/docs/handoffs/XMA-CLI-001_HND-0011_V0.1.1-POSTRELEASE_v0.1.0.md)

## v0.1.0

Publicado el 2026-10-29. [Descargar GitHub Release](https://github.com/eventmgmtplatform/x-media-archiver/releases/tag/v0.1.0).

Incluye discovery, catálogo, descarga, reanudación, estado offline, SQLite v2, hashes, sidecars,
manifests y bundle standalone.

Evidencia y control:

- [CHANGELOG](https://github.com/eventmgmtplatform/x-media-archiver/blob/main/CHANGELOG.md)
- [Release notes v0.1.0](https://github.com/eventmgmtplatform/x-media-archiver/blob/main/docs/release/XMA-CLI-001_RELEASE-NOTES_v0.1.0.md)
- [HND-0008 postrelease](https://github.com/eventmgmtplatform/x-media-archiver/blob/main/docs/handoffs/XMA-CLI-001_HND-0008_V0.1.0-POSTRELEASE_v0.1.0.md)
- [Checklist de release](https://github.com/eventmgmtplatform/x-media-archiver/blob/main/docs/release/XMA-CLI-001_RELEASE-CHECKLIST_v1.0.0.md)

Cada nueva release debe actualizar esta matriz, el changelog, las notas, la página de producto y el
roadmap antes del tag.
