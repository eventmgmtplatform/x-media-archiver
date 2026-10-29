# XMA-CLI-001 — HND-0007 Product Wiki v0.1.0

**Fecha:** 2026-10-29  
**Estado:** `WIKI_READY / WAITING_CHAT_VALIDATION`  
**Base:** `3a5c0fe4b3579995b70784023a77756a6073d005`  
**Rama:** `docs/xma-product-wiki-v0.1.0`

## Alcance

Se agregó una wiki pequeña de producto para GitHub Pages: resumen, v1, arquitectura, releases,
gobierno y roadmap v2. La documentación enlaza a los archivos canónicos del repositorio y no
sustituye ADR, gates, changelog, handoffs o runbooks.

El roadmap registra la evolución gobernada X → Telegram → WhatsApp → otras plataformas. No
implementa adaptadores nuevos ni amplía el máximo operativo v1.

## Publicación

El workflow Pages construye `docs/wiki` con Jekyll y publica desde la rama documental para
validación; después de integrar la documentación, `main` será la fuente estable.

## Restricciones

Sin cambios funcionales, dependencias, esquema, uv.lock, acceso a X, descargas, merge, tag,
GitHub Release o PyPI. La wiki no autoriza la liberación v0.1.0.
