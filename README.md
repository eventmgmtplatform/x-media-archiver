# X Media Archiver CLI

CLI local para descubrir el contenido audiovisual público de un perfil de X, catalogarlo y descargarlo en un repositorio normalizado con metadatos y evidencia de integridad.

## Estado

- Workstream: `XMA-CLI-001`
- Madurez: `DESIGN`
- Baseline de arquitectura: `v0.1.0`
- Implementación: `B02 VALIDATED / B03 DISCOVERY — START AUTHORIZED`
- Certificación de producto: `NOT CERTIFIED`

## Objetivo del MVP

1. Recibir un `@usuario`, URL de perfil o URL de publicación.
2. Descubrir publicaciones con video, GIF animado, broadcast o Space soportado.
3. Presentar un resumen y permitir descarga masiva desde la terminal.
4. Descargar mediante `yt-dlp` y `ffmpeg`.
5. Crear una carpeta normalizada por publicación con video, `metadata.json`, `ficha.md`, miniatura y URL original.
6. Registrar catálogo, progreso, errores y deduplicación en SQLite.
7. Reanudar ejecuciones y sincronizar solamente contenido nuevo.

## Documentación

- [Arquitectura](docs/architecture/XMA-CLI-001_ARCHITECTURE_v0.1.0.md)
- [ADR-0001](docs/adr/ADR-0001-cli-modular-monolith.md)
- [Plan de actividades](docs/planning/XMA-CLI-001_IMPLEMENTATION_PLAN_v0.1.0.md)
- [Gobierno Git y releases](docs/governance/XMA-CLI-001_GIT_RELEASE_GOVERNANCE_v0.1.0.md)
- [Prompt inicial de Codex](docs/prompts/XMA-CLI-001_PRM-0001_FOUNDATION-BOOTSTRAP_v0.1.0.md)
- [Catálogo SQLite v1](docs/architecture/XMA-CLI-001_CATALOG-SCHEMA_v0.1.0.md)
- [Gate register](docs/governance/XMA-CLI-001_GATE-REGISTER_v0.1.0.md)
- [Prompt B03 para Codex](docs/prompts/XMA-CLI-001_PRM-0003_B03-DISCOVERY_v0.1.0.md)
- [Prompt B03 para dot](docs/prompts/XMA-CLI-001_DOT-PRM-0003_B03-GOVERNANCE-AUDIT_v0.1.0.md)

## Principio de operación

`Leonel autoriza → ChatGPT diseña y gobierna → Codex ejecuta → Codex entrega handoff Markdown → ChatGPT valida → Leonel autoriza la transición`.

Codex no encadena fases ni publica releases sin un gate explícito.

## Desarrollo local

```bash
uv sync --all-groups
uv run xma --help
uv run xma version
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest
uv build
```

### Núcleo B02

`xma.domain` contiene entidades inmutables, validadores, estados y puertos sin dependencias de
CLI o persistencia. `xma.adapters.catalog` implementa el catálogo SQLite mediante una migración
monotónica, claves foráneas activas y límites transaccionales explícitos.

Los comandos de discovery y descarga se incorporarán en bloques posteriores; no forman parte de
B02.
