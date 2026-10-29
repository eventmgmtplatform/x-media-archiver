# XMA-CLI-001 — HND-0004 B04 Download Slice

**Versión:** 0.8.1  
**Fecha:** 2026-10-29 (America/Mexico_City)  
**Estado:** `SINGLE_POST_NO_VIDEO`  
**Prompt:** `XMA-CLI-001-PRM-0024 B04-SINGLE-POST-PUBLIC-ACCEPTANCE-RETRY v0.1.0`

## Baseline y alcance

- Baseline/HEAD funcional: `c8bca0d92f84efb8e0c9cddccfdef258596334f6`.
- Tree baseline: `e71f5e31e15578d0859768b46fed8bcbe9ee9663`.
- Rama: `feature/xma-b04-download-slice`; PR #4 abierto, draft, mergeable y sin merge.
- CI baseline: run `40835619151`, `SUCCESS`, 302 pruebas, cobertura 90.57 %.
- HND precedente: v0.8.0, `REWORK_REQUIRED` por arnés local.
- No cambiaron `src/`, pruebas, dependencias, esquema, `uv.lock`, workflow, autenticación,
  timeouts, spawn/IPC, downloader o normalización.

## Precondiciones y arnés

Firefox estaba activo y `<LOCAL_PROFILE>` resolvió inequívocamente una sesión completa. La URL se
canonicalizó offline a host `x.com`, handle `tedmetal`, post ID `2115531877855732095`, sin query o
fragment. No se ejecutó inspect, gallery-dl directo, curl, wget ni consulta pública previa.

`<LOCAL_SINGLE_POST_REPO>` y `<LOCAL_SINGLE_POST_LOGS>` fueron directorios nuevos, distintos,
vacíos, no anidados y fuera de Git. stdout/stderr se escribieron exclusivamente en logs; no existía
archivo alguno dentro del repositorio al iniciar XMA.

## Ejecución pública única

- Target público: host `x.com`, handle `tedmetal`, post ID `2115531877855732095`.
- Código de salida: 8.
- Duración redondeada: 3 s.
- Telemetría: `WORKER_STARTED`, `AUTH_LOADED`, `EXTRACTOR_STARTED`.
- Terminal: `PROVIDER_EXHAUSTED`.
- No se observaron `PROFILE_SEEN`, `VIDEO_SEEN`, `DUPLICATE_SKIPPED` o `CANDIDATE_SENT`.
- Clasificación: `SINGLE_POST_NO_VIDEO`.

No hubo segunda solicitud, retry, fallback, otro perfil, post o cuenta.

## Conteos e integridad

- Manifest: `requested_total=1`, `existing_before=0`, `downloaded_this_run=0`, `total_after=0`,
  `complete=false`; target canónico sin query: PASS.
- Videos, sidecars, artifacts, jobs e identidades: 0.
- SQLite: ausente; `PRAGMA integrity_check`, hash y tamaño no aplican.
- Extensión local del repositorio: `.json` del manifest incompleto.
- `.part`/`.tmp`: 0.
- Cookies, URL firmada, headers, tokens, selector local o rutas personales en salida/evidencia:
  ausentes en la comprobación sanitizada.
- Repositorio, manifest y logs permanecen fuera de Git.

## Validaciones offline posteriores

| Comando | Resultado |
|---|---|
| `uv sync --locked --all-groups` | PASS |
| `uv run ruff format --check .` | PASS, 111 archivos |
| `uv run ruff check .` | PASS |
| `uv run mypy` | PASS, 38 archivos fuente |
| `uv run pytest` | PASS, 302 pruebas |
| cobertura local | PASS, 90.20 % |
| `uv build` | PASS, sdist y wheel |
| `git diff --check` | PASS |
| `uv.lock` byte-idéntico | PASS (`847ee02394976ad7a72b906e0e3bb994b2061307`) |
| archivos locales/prohibidos rastreados | cero nuevos |

## Riesgo y siguiente decisión

El camino público alcanzó el extractor de la URL exacta, pero no obtuvo un video compatible. Esta
evidencia no autoriza recorrer el perfil, elegir otro post ni modificar el proveedor. Cualquier
acción posterior requiere decisión humana explícita.

No hubo cambios funcionales, cookies exportadas, retry, perfil alternativo, otra descarga, dot,
merge, tag, release, B05 ni descarga masiva.
