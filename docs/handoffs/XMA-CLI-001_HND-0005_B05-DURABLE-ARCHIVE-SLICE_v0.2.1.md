# XMA-CLI-001 — HND-0005 B05 Durable Archive Slice v0.2.1

**Fecha:** 2026-10-29  
**Estado:** `B05_LOCAL_OPERABILITY_READY / WAITING_CHAT_VALIDATION`  
**Gate B05:** `VALIDATED_WITH_OBSERVATIONS`  
**Autoridad:** `XMA-CLI-001-PRM-0031 B05-ISOLATED-INSTALL-ACCEPTANCE v0.1.0`

## Baseline y alcance

- Baseline: `7f3880504b3a13724ca46255e08dd577eb5d03b3`, tree
  `09bd70c2b924c0a1ea29750b1cf280167ae4573c`.
- CI baseline: [40905036104](https://github.com/eventmgmtplatform/x-media-archiver/actions/runs/40905036104),
  `SUCCESS`, 341 pruebas, cobertura 90.71 %.
- PR #5 permaneció abierto, draft, sin merge y apilado sobre B04.
- La revisión documental final es el commit que contiene este handoff; su SHA, tree y CI quedan
  registrados en el cuerpo y checks del PR #5, sin introducir una autorreferencia Git imposible.

Solo cambiaron README, runbook, CHANGELOG, ADR-0005, Gate Register, Implementation Plan y este
handoff. El runbook clona explícitamente `feature/xma-b05-durable-archive`, verifica branch/HEAD y
distingue source de wheel local. El README conserva el historial, pero marca como superados los
estados incompatibles con B04/B05 vigentes.

## Paquetes construidos

| Artifact | Tamaño | SHA-256 |
|---|---:|---|
| `x_media_archiver-0.1.0.dev0-py3-none-any.whl` | 52,001 bytes | `f2d14c5c9cca1750e23300b449aaa593c14e9379461fe7b2c56933facd81eaa7` |
| `x_media_archiver-0.1.0.dev0.tar.gz` | 270,254 bytes | `5edf30a538e6f553e6c56363639df29d27d63efc85d4badef699fa67769b0504` |

Versión `0.1.0.dev0`; entry point `xma = xma.cli:app`. `dist/` permaneció ignorado y no se publicó.

## Instalación aislada única

- CPython administrado por uv: `3.12.13`.
- Dependencias Linux de producción cotejadas con `uv.lock`: annotated-doc 0.0.5, certifi
  2026.10.23, charset-normalizer 3.5.2, gallery-dl 1.32.18, idna 3.20,
  markdown-it-py 4.2.0, mdurl 0.1.2, pygments 2.21.0, requests 2.34.2, rich 14.3.4,
  shellingham 1.5.4, typer 0.27.3 y urllib3 2.8.0.
- El wheel se instaló localmente con `--no-deps`; XMA no se obtuvo de red.
- `xma --help`, `version` y las ayudas de `inspect`, `sync`, `download`, `archive` y `status`:
  código 0, sin traceback. Download conserva 1–5; archive, 1–10; status no exige autenticación.
- `status` humano y JSON pasaron contra un repositorio sintético: `COMPLETED`, cinco iniciales,
  total diez, página tres, remaining cero y `complete=true`, completamente offline.
- El entorno, Python, export y repositorio sintético temporales fueron eliminados después de
  capturar evidencia sanitizada.

## Validación

| Comando | Resultado |
|---|---|
| `uv sync --locked --all-groups` | PASS |
| `uv run ruff format --check .` | PASS, 128 archivos |
| `uv run ruff check .` | PASS |
| `uv run mypy` | PASS, 44 archivos fuente |
| `uv run pytest` | PASS, 341 pruebas, cobertura 90.33 % |
| `uv build` | PASS, wheel y sdist |
| `git diff --check` | PASS |

`uv.lock` conservó SHA-256
`7a7e7215a354abefde9351de1691a651ea6c37fcc7f9326125642068433c0788`. No se modificaron código,
pruebas, esquema, dependencias o workflows. No se rastrearon artifacts, SQLite, manifests privados,
logs, cookies o medios. La CI final verde corresponde al tree documental publicado en PR #5.

## Límites y rollback

B05 sigue limitado a diez videos y `VALIDATED_WITH_OBSERVATIONS`. El producto no está certificado,
el wheel no es release y la rama no está integrada. Cientos/miles, cursor remoto, scheduler,
automatización desatendida y optimización de escala permanecen fuera de alcance.

No hubo acceso a X, Firefox, cookies, perfiles, descargas, dot, merge, tag o release. Rollback:
revertir el commit documental PRM-0031; no afecta código funcional ni repositorios de usuario.
