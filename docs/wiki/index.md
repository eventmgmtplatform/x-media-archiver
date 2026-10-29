---
title: X Media Archiver
---

[Inicio](index.html) · [Producto v1](product.html) · [Arquitectura](architecture.html) · [Releases](releases.html) · [Gobierno](governance.html) · [Roadmap v2](roadmap.html)

---

# X Media Archiver

**XMA** es una CLI local-first para descubrir, catalogar, descargar y reanudar archivos de video
públicos en un repositorio normalizado, verificable y deduplicado.

> Estado actual: **v0.1.0 Release Candidate**. Linux x86_64, máximo operativo de diez videos.
> El merge, tag y GitHub Release siguen sujetos al gate humano de liberación.

## Capacidades actuales

| Capacidad | v0.1.0 |
|---|---|
| Perfil de X | Inspección, catálogo y descarga |
| Publicación individual de X | Descarga por URL exacta |
| Lotes | 1, 2 y 5 videos |
| Archivo durable | Hasta 10 videos |
| Reanudación | Checkpoints, deduplicación y rate limiting |
| Evidencia | SQLite, sidecars JSON, manifests, tamaños y SHA-256 |
| Estado offline | `xma status` |
| Entrega | Bundle Linux, wheel y sdist |

## Navegación

- [Qué contiene la v1](product.html)
- [Cómo está construido](architecture.html)
- [Control de releases](releases.html)
- [Gobierno y documentos canónicos](governance.html)
- [Roadmap v2: X → Telegram → WhatsApp](roadmap.html)

## Fuente canónica

La wiki resume el producto. En caso de diferencia, prevalecen el código, los ADR, los gates, el
changelog y los handoffs del repositorio. Consulte el [README canónico](https://github.com/eventmgmtplatform/x-media-archiver/blob/main/README.md).
