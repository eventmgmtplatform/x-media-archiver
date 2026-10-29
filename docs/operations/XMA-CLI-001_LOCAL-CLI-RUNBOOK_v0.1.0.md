# XMA-CLI-001 — Runbook local de la CLI v0.1.0

## Alcance y requisitos

Esta versión opera localmente y admite como máximo diez videos. Requiere Linux, Python 3.11 o
superior, `uv`, espacio suficiente y acceso de escritura al repositorio normalizado. Las
operaciones reales autenticadas requieren Firefox local ya autenticado; use solo el nombre de
perfil como `<LOCAL_PROFILE>`. No exporte cookies ni publique rutas, sesiones o URLs multimedia.

No se certifican cientos/miles de videos, scheduler, cursor remoto durable, automatización
desatendida, `yt-dlp`, FFmpeg, miniaturas ni `ficha.md`.

## Preparación y comprobación

```bash
git clone https://github.com/eventmgmtplatform/x-media-archiver.git
cd x-media-archiver
uv sync --locked --all-groups
uv run xma --help
uv run xma version
```

Use un repositorio distinto por perfil. No mezcle handles en la misma ruta.

## Operaciones acotadas

Descargar un total de 1, 2 o 5 videos de un perfil:

```bash
uv run xma download @HANDLE --limit 1 --repository ./repository-HANDLE \
  --auth-browser firefox --auth-profile <LOCAL_PROFILE>
uv run xma download @HANDLE --limit 2 --repository ./repository-HANDLE \
  --auth-browser firefox --auth-profile <LOCAL_PROFILE>
uv run xma download @HANDLE --limit 5 --repository ./repository-HANDLE \
  --auth-browser firefox --auth-profile <LOCAL_PROFILE>
```

Archivar durablemente hasta diez sobre el mismo repositorio:

```bash
uv run xma archive @HANDLE --limit 10 --batch-size 2 \
  --repository ./repository-HANDLE \
  --auth-browser firefox --auth-profile <LOCAL_PROFILE> \
  --request-interval 2 --discovery-timeout 30
```

Descargar exactamente una publicación:

```bash
uv run xma download "https://x.com/HANDLE/status/POST_ID" --limit 1 \
  --repository ./repository-single-post \
  --auth-browser firefox --auth-profile <LOCAL_PROFILE>
```

Discovery sin descarga: `inspect` observa metadatos; `sync` los cataloga. Consulte sus opciones con
`uv run xma inspect --help` y `uv run xma sync --help`. No confunda esos comandos con `download` o
`archive`.

## Status y reanudación

`status` es completamente offline:

```bash
uv run xma status --repository ./repository-HANDLE
uv run xma status --repository ./repository-HANDLE --json
```

`COMPLETED` confirma el total solicitado. `PAUSED` conserva progreso recuperable; revise
`last_error_code` antes de reanudar. `FAILED` indica inconsistencia o fallo no recuperable sin
diagnóstico. `PROVIDER_TIMEOUT` es un fallo transitorio del proveedor, no permiso para retries
descontrolados.

Ejecutar nuevamente con el mismo total no redescarga artifacts íntegros. Para elevar de cinco a
diez use una sola operación `archive`; no encadene descargas improvisadas. No borre
`catalog.sqlite3` si desea reanudar.

## Estructura real

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

No edite sidecars o manifests manualmente y no mueva videos fuera de esta estructura sin una
operación gobernada.

## Códigos de salida

| Código | Interpretación operativa |
|---:|---|
| 0 | operación completada |
| 2 | argumento o identidad inválidos |
| 3 | contenido restringido/autenticación requerida |
| 4 | rate limit |
| 5 | contrato o proveedor fallido |
| 6 | catálogo o persistencia local fallidos |
| 7 | target/run no encontrado |
| 8 | fallo transitorio o timeout del proveedor |
| 9 | descarga o conflicto de repositorio |

## Integridad, respaldo y limpieza segura

Detenga XMA antes de respaldar. Copie el directorio completo conservando permisos y estructura; no
respalde solo los videos. Verifique SQLite:

```bash
python - <<'PY'
import sqlite3
with sqlite3.connect("repository-HANDLE/catalog.sqlite3") as db:
    print(db.execute("PRAGMA integrity_check").fetchone()[0])
PY
```

El resultado esperado es `ok`. Compare tamaño y SHA-256 de cada video con `metadata.json` y el
catálogo. Si difieren, deténgase: no sobrescriba ni borre evidencia.

Solo con XMA detenido pueden eliminarse residuos seguros `*.part` y `*.tmp` de una operación
fallida, después de comprobar que no corresponden a un proceso activo. Nunca elimine
`catalog.sqlite3`, videos confirmados, sidecars o manifests para “reparar” un run.

## Seguridad

- Mantenga Firefox autenticado antes de una operación real.
- Nunca use el nombre real del perfil en documentación o tickets públicos.
- No copie, exporte, imprima ni persista cookies.
- No publique logs crudos, headers, tokens, query strings o URLs multimedia firmadas.
- `status` no accede a X.
- El máximo vigente es diez; no se certifica operación masiva.
