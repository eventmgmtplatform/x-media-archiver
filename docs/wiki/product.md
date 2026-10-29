---
title: Producto v1
---

[Inicio](index.html) · [Producto v1](product.html) · [Arquitectura](architecture.html) · [Releases](releases.html) · [Gobierno](governance.html) · [Roadmap v2](roadmap.html)

---

# Producto v1

## Qué hace

XMA acepta un perfil, handle o URL de publicación de X y crea un repositorio local normalizado.
Los comandos principales son:

| Comando | Función |
|---|---|
| `inspect` | Descubre metadatos sin persistir |
| `sync` | Cataloga metadatos en SQLite |
| `download` | Descarga un total o incremento configurable de 1 a 10 activos |
| `archive` | Archiva y reanuda hasta 10 activos |
| `status` | Consulta offline el estado e integridad |

## Repositorio generado

```text
repository-HANDLE/
├── catalog.sqlite3
├── manifests/
│   └── latest.json
└── profiles/
    └── HANDLE/
        └── posts/
            └── POST_ID/
                └── MEDIA_INDEX/
                    ├── metadata.json
                    └── video.EXT
```

La identidad estable es `POST_ID:MEDIA_INDEX`. Un activo íntegro no se sobrescribe durante una
reanudación.

## Incluido

- autenticación local Firefox de solo lectura;
- modo anónimo cuando el proveedor lo permite;
- descarga atómica mediante archivos `.part`;
- validación de tamaño y SHA-256;
- SQLite v2 y migraciones monotónicas;
- sidecars y manifests sanitizados;
- checkpoints, bloqueo `flock`, cooldown y reanudación;
- URL individual (`SINGLE_POST`);
- bundle Linux x86_64 sin requerir Python o uv.

## Límites conocidos

- máximo de diez videos por operación certificada;
- Linux x86_64; Ubuntu 22.04 y 24.04 validados;
- sin scheduler, daemon, GUI o API;
- sin cursor remoto eficiente para miles;
- disponibilidad y cambios de X fuera del control del producto.

Consulte [requisitos](https://github.com/eventmgmtplatform/x-media-archiver/blob/main/docs/requirements/XMA-CLI-001_SYSTEM-REQUIREMENTS_v1.0.0.md)
y el [runbook](https://github.com/eventmgmtplatform/x-media-archiver/blob/main/docs/operations/XMA-CLI-001_LOCAL-CLI-RUNBOOK_v0.1.0.md).
