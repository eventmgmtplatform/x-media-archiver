# XMA-CLI-001 — Git, branching y release governance

**Versión:** 0.1.0  
**Estado:** ACCEPTED

## Modelo de ramas

Trunk-based development protegido:

- `main`: baseline integrable; nunca recibe push directo.
- `feature/xma-bNN-<slug>`: un bloque aprobado.
- `fix/xma-<issue>-<slug>`: corrección acotada.
- `release/vX.Y.Z`: solo estabilización cuando el release lo requiera.

No se mantendrá una rama `develop`: para un equipo pequeño introduce promoción adicional sin valor demostrado.

## Flujo

Issue/actividad → prompt aprobado → branch → commits pequeños → pruebas → handoff → PR → validación → aprobación humana → merge squash → tag/release.

## Commits y PR

Conventional Commits: `feat`, `fix`, `docs`, `test`, `refactor`, `build`, `ci`, `chore`. Todo PR referencia bloque, requisito, prompt, pruebas, evidencia, riesgos y rollback. El autor de código no declara por sí solo el gate certificado.

## Protecciones mínimas

- PR obligatorio para `main`.
- CI requerida: format, lint, typecheck, unit tests, dependency/secret scan.
- Rama actualizada antes de merge.
- Historial lineal y squash merge.
- Tags `vMAJOR.MINOR.PATCH` únicamente desde `main` validada.

## Versionado y changelog

SemVer desde `0.1.0`. `CHANGELOG.md` usa Keep a Changelog con `Unreleased`, Added, Changed, Fixed, Security y Known Limitations. Un release registra tag, commit, fecha, artefactos, checksum, validaciones, limitaciones y rollback.

## Licencias

Antes de distribución se verificará la composición efectiva. `gallery-dl` es GPL-2.0-only; se prioriza invocación como proceso externo y separación por adaptador. `yt-dlp`, binarios y dependencias pueden tener licencias distintas según el método de empaquetado. Ningún release público se aprueba sin revisión registrada.

## Recuperación

- Revertir el commit squash del PR fallido.
- Conservar esquema SQLite migrable hacia adelante y backup antes de migraciones destructivas.
- No reescribir tags publicados.
- Publicar patch release cuando un artefacto ya distribuido requiera corrección.
