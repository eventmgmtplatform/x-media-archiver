---
title: X Media Archiver
---

[Inicio](index.html) · [Producto v1](product.html) · [Archivo completo B06](b06-complete-profile-archive.html) · [Arquitectura](architecture.html) · [Releases](releases.html) · [Gobierno](governance.html) · [Roadmap v2](roadmap.html)

---

# X Media Archiver

**XMA** es una CLI local-first para descubrir, catalogar, descargar y reanudar archivos de video
públicos en un repositorio normalizado, verificable y deduplicado.

> Estado actual: **v0.2.0 release candidate**; no publicado. v0.1.2 continúa como release pública.

## Capacidades actuales

| Capacidad | v0.2.0 RC |
|---|---|
| Perfil de X | Inspección, catálogo y descarga |
| Publicación individual de X | Descarga por URL exacta |
| Lotes | Totales de 1 a 10 o incrementos de 1 a 20, máximo total 20 |
| Archivo durable | BOUNDED hasta 20; ALL con safety cap explícito |
| Reanudación | Checkpoints, deduplicación y rate limiting |
| Evidencia | SQLite, sidecars JSON, manifests, tamaños y SHA-256 |
| Estado offline | `xma status` |
| Reporting | Humano y JSON schema 1; progreso por invocación |
| Entrega | Bundle Linux, wheel y sdist |

## Navegación

- [Qué contiene la v1](product.html)
- [Archivo completo B06 validado con observaciones](b06-complete-profile-archive.html)
- [Cómo está construido](architecture.html)
- [Control de releases](releases.html)
- [Gobierno y documentos canónicos](governance.html)
- [Roadmap v2: X → Telegram → WhatsApp](roadmap.html)

## Fuente canónica

La wiki resume el producto. En caso de diferencia, prevalecen el código, los ADR, los gates, el
changelog y los handoffs del repositorio. Consulte el [README canónico](https://github.com/eventmgmtplatform/x-media-archiver/blob/main/README.md).
