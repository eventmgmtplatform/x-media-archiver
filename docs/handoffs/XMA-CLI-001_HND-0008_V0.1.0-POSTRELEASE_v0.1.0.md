# XMA-CLI-001 — HND-0008 v0.1.0 postrelease

**Fecha:** 2026-10-29  
**Estado:** `V0.1.0_RELEASED / POSTRELEASE_VERIFIED`  
**Commit liberado:** `c997cce488b4486ffd8dc079cd25819bec402b77`  
**Tag:** `v0.1.0` (annotated; objeto `1d06a9330a63b1a25bca675811239615490eb51c`)  
**GitHub Release:** https://github.com/eventmgmtplatform/x-media-archiver/releases/tag/v0.1.0

## Integración

PR #6 consolidó B02–B05, cumplimiento, wiki y gobierno mediante squash. El intento inicial de
publicación falló antes de crear jobs por una expresión YAML y no produjo tag o Release. GOV-RWK-0041
quedó corregido por PR #8 sin cambios funcionales.

El tag anotado apunta exactamente al commit de main `c997cce488b4486ffd8dc079cd25819bec402b77`.
No se reescribió historia ni tag.

## Validación

- CI main #93 / run 40945247308: SUCCESS.
- Publish v0.1.0 / run 40945247091: SUCCESS.
- Build y validación de candidato: PASS.
- Tag anotado y ascendencia main: PASS.
- GitHub Release pública, no draft y no prerelease: PASS.
- Descarga postrelease de assets: PASS.
- `SHA256SUMS`: PASS.
- Extracción del bundle Linux x86_64: PASS.
- `xma --help` y `xma version --short = 0.1.0` sin Python/uv: PASS.

## Assets publicados

1. `gallery_dl-1.32.18.tar.gz`
2. `LICENSE`
3. `RELEASE-MANIFEST.json`
4. `requirements-linux-x86_64.txt`
5. `sbom.cdx.json`
6. `SHA256SUMS`
7. `THIRD_PARTY_NOTICES.md`
8. `xma-v0.1.0-linux-x86_64.tar.gz`
9. `x_media_archiver-0.1.0-py3-none-any.whl`
10. `x_media_archiver-0.1.0.tar.gz`

## Pendientes

- Activar GitHub Pages mediante GitHub Actions y verificar la URL de la wiki.
- PyPI requiere autorización separada y no fue publicado.
- El máximo operativo permanece en diez videos.
- Telegram, WhatsApp, operación masiva y demás plataformas permanecen en roadmap v2.

## Rollback

El tag publicado no se reescribe. Ante un defecto, documentar impacto, retirar o marcar assets si
corresponde, revertir en main mediante PR y preparar una versión patch.
