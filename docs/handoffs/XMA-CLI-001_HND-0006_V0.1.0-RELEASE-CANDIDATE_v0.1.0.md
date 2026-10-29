# XMA-CLI-001 — HND-0006 v0.1.0 Release Candidate

**Fecha:** 2026-10-29  
**Estado:** `V0.1.0_RC_READY / WAITING_CHAT_VALIDATION`  
**Autoridad:** `XMA-CLI-001-PRM-0032 V0.1.0-RELEASE-CANDIDATE-PREPARATION`

## Baselines y estrategia

- main: `b2bdca7961f00d54f2465a4f8d26b2003340c3b9`.
- snapshot validado B05: `927c683af83c6e1343501842e9c0d59dc82e4e6b`, tree
  `957acd87021e4be8a445dc8fc3b3d5a42355029f`, CI 40906599341 SUCCESS.
- rework B02: baseline `89605d1c475ad23b42184d24f7afb89d3e8159e1`, head
  `4b8bdab3f8e5cbc06cf2fe987206f75f9c040d22`.
- Rama temporal: `release/v0.1.0`, creada exactamente desde main.

El snapshot B05 fue importado como un único commit squash, sin merges de historia ni mutaciones de
las ramas B03–B05. El rework B02 se portó manualmente: identidad compuesta estricta, rechazo de ruta
`.`, timestamps reales/injectables de migración, progreso controlado de discovery runs y cierre de
la conexión si falla el enter de UoW. Se conservaron SQLite v2 y todas las capacidades B03–B05.

Matriz: PR #3, #4 y #5 permanecen abiertos; el nuevo PR draft `release/v0.1.0 → main` los sustituirá
solo después de una integración humana futura.

## Versión, licencia y composición

- Versión CLI/metadata/artifacts: `0.1.0`.
- Licencia declarada: `GPL-2.0-only`; autor: eventmgmtplatform; URLs de proyecto incluidas.
- `THIRD_PARTY_NOTICES.md` y SBOM CycloneDX registran la composición.
- gallery-dl 1.32.18, GPL-2.0-only, source oficial PyPI
  `gallery_dl-1.32.18.tar.gz`, SHA-256
  `1c5562af3799a0bec96be0f64d95a416aee688fd09fe3893ca3a6c87bbe65bcd`.

No se emite conclusión legal; se registra la composición y el mecanismo para obtener/verificar
corresponding source.

## Candidate artifacts locales

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `xma-v0.1.0-linux-x86_64.tar.gz` | 22,946,458 | `faa626b5d2f71766334078b5f61b1ce81c1ca7d4dd2d024ca0739e3424a84718` |
| `x_media_archiver-0.1.0-py3-none-any.whl` | 47,949 | `2496d256374dc446dc74e2cc537c7b8436cd7b3137c3caeeb37410b152e6076d` |
| `x_media_archiver-0.1.0.tar.gz` | 294,321 | `5e1b14878e81e266273e9e2cc9c622153539b9b7f284442ae18abbf1b8211239` |
| `requirements-linux-x86_64.txt` | 14,683 | `a7f6ab131b9a77367680e097dd5c1bac9080ace32cbcc35b5152ea597fa6ff64` |
| `sbom.cdx.json` | 49,884 | `660424d197c769c639d4793633daf08239cc39274108ea8a5548e3ae0e29d765` |
| `SHA256SUMS` | 564 | `b62b720bf010aea052308f687a090d903b88a1a661f2b4662e7fe3060973fbef` |

Estos artifacts no están rastreados ni publicados. Wheel y sdist fueron reproducibles
byte-for-byte en builds consecutivos. Requirements/SBOM se hicieron reproducibles eliminando el
header dependiente de ruta y usando modo CycloneDX reproducible. El bundle PyInstaller mostró una
diferencia binaria entre builds; cada candidato se fija mediante SHA256SUMS, se extrae y valida. La
limitación queda documentada como riesgo de reproducibilidad upstream.

## Validación

- Python de build: CPython 3.12.13; wheel instalado aisladamente con 13 dependencias de producción
  exactas de `uv.lock`.
- Entry point, version y ayudas de inspect/sync/download/archive/status: PASS.
- Status humano/JSON contra SQLite sintético: PASS, offline.
- Bundle extraído y ejecutado sin Python/uv en PATH: PASS.
- Portabilidad: Ubuntu 22.04 PASS; Ubuntu 24.04 PASS.
- B02: 42 pruebas específicas PASS; suite total: 356 PASS, cobertura local 90.39 %.
- Ruff format/lint, mypy, build, metadata, diff: PASS.
- pip-audit producción: cero vulnerabilidades conocidas; inventario de licencias generado.
- Secret/forbidden tracked-file scan: PASS; no media, SQLite, cookies, logs o artifacts rastreados.
- CI final: [40928956435](https://github.com/eventmgmtplatform/x-media-archiver/actions/runs/40928956435),
  `SUCCESS`, 356 pruebas, 90.76 %, build/auditoría verdes.
- Release candidate/portabilidad:
  [40928956602](https://github.com/eventmgmtplatform/x-media-archiver/actions/runs/40928956602),
  `SUCCESS`, artifacts subidos y bundle validado en Ubuntu 22.04/24.04.

## GitHub, riesgos y rollback

Se configuró squash-only, merge/rebase merge deshabilitados, delete-branch-on-merge y protección de
main con PR/check `quality` estricto, historial lineal, conversaciones resueltas, admins incluidos,
sin force-push ni eliminación. No se exigió una aprobación externa imposible para un mantenedor.

Riesgos: disponibilidad del proveedor, máximo diez, `RESCAN_DEDUP_V1` ineficiente a escala,
portabilidad limitada a Linux x86_64 y bundle no byte-reproducible. Rollback antes de integración:
cerrar el PR y eliminar la rama temporal de forma gobernada. Después de integración, revertir el
squash en main y preparar patch; nunca reescribir tags.

No hubo acceso a X, Firefox/cookies, descargas públicas, modificación de repositorios de usuario,
merge, cierre de PR #3–#5, tag, GitHub Release o publicación PyPI.
