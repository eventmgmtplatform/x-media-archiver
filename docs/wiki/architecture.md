---
title: Arquitectura
---

[Inicio](index.html) · [Producto v1](product.html) · [Arquitectura](architecture.html) · [Releases](releases.html) · [Gobierno](governance.html) · [Roadmap v2](roadmap.html)

---

# Arquitectura

XMA es un monolito modular con fronteras hexagonales y dependencias dirigidas hacia el dominio.

```text
CLI (Typer/Rich)
      ↓
Servicios de aplicación
      ↓
Dominio y puertos
      ↓
Adaptadores: discovery · download · SQLite · filesystem
```

## Componentes

| Capa | Tecnología / responsabilidad |
|---|---|
| CLI | Python, Typer y Rich |
| Dominio | Entidades, identidades, estados y contratos tipados |
| Discovery | gallery-dl detrás de adaptadores acotados |
| Descarga | HTTP, staging `.part`, hash y movimiento atómico |
| Catálogo | SQLite v2, UoW y migraciones |
| Archivo durable | runs, checkpoints, rate limiting y `flock` |
| Empaquetado | Hatchling, uv y PyInstaller |
| Calidad | pytest, Ruff, mypy, cobertura ≥90 % |
| CI/CD | GitHub Actions, SBOM, auditoría y checksums |

## Principios

- local-first y metadata/evidencia sanitizada;
- fail-closed ante autenticación, catálogo o integridad inválidos;
- idempotencia y deduplicación por identidad estable;
- ninguna cookie, URL firmada o ruta personal en evidencia pública;
- cambios por rama, PR, CI, handoff y autorización humana.

Documentos de detalle:

- [Arquitectura](https://github.com/eventmgmtplatform/x-media-archiver/blob/main/docs/architecture/XMA-CLI-001_ARCHITECTURE_v0.1.0.md)
- [Esquema de catálogo](https://github.com/eventmgmtplatform/x-media-archiver/blob/main/docs/architecture/XMA-CLI-001_CATALOG-SCHEMA_v0.1.0.md)
- [ADR](https://github.com/eventmgmtplatform/x-media-archiver/tree/main/docs/adr)
