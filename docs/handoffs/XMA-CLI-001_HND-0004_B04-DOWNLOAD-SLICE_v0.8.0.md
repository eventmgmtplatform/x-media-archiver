# XMA-CLI-001 — HND-0004 B04 Download Slice

**Versión:** 0.8.0  
**Fecha:** 2026-10-29 (America/Mexico_City)  
**Estado:** `REWORK_REQUIRED`  
**Prompt:** `XMA-CLI-001-PRM-0023 B04-SINGLE-POST-DOWNLOAD v0.1.0`

## Baseline y entrega funcional

- Baseline: `512cd49e5bd8d567cc793353694145b246a104c4`.
- Tree baseline: `30048f9ec758a71d92ed00dd3f7a8d81199fa740`.
- Rama: `feature/xma-b04-download-slice`; PR #4 abierto y draft.
- Commit funcional: `3cc29cd6d4391fdeb468674bab894d316fd8d437`.
- CI funcional: run `40835440646`, `SUCCESS`, antes de la aceptación.
- El commit documental que contiene este handoff recibe CI final sobre su mismo tree.

## Diseño SINGLE_POST

`DiscoveryTarget` distingue `PROFILE` y `SINGLE_POST`. Se admiten exclusivamente URLs HTTPS de
estado en x.com/twitter.com con handle y post ID numérico; se eliminan query y fragment y se genera
una URL x.com canónica. Hosts, esquemas, rutas extra y post IDs inválidos fallan cerrados.

El DTO spawn contiene únicamente modo, URL canónica, handle y post ID. Para `SINGLE_POST`, el worker
construye DataJob con la URL exacta y nunca añade `/timeline`. El padre valida que post y autor
coincidan antes de descargar. Perfil, spawn, semántica acumulada, catálogo, manifest y downloader
existentes se conservan. Manifest y salida usan la URL canónica, nunca la query original.

Archivos funcionales: dominio discovery/export, worker incremental, aplicación download y pruebas
de dominio, adaptador y servicio. Sin cambios de esquema, dependencias, workflow o `uv.lock`.

## Pruebas y CI

| Comando | Resultado |
|---|---|
| `uv sync --locked --all-groups` | PASS |
| `uv run ruff format --check .` | PASS, 110 archivos |
| `uv run ruff check .` | PASS |
| `uv run mypy` | PASS, 38 archivos fuente |
| `uv run pytest` | PASS, 302 pruebas |
| cobertura local | PASS, 90.20 % |
| `uv build` | PASS, sdist y wheel |
| `git diff --check` | PASS |
| `uv.lock` byte-idéntico | PASS (`847ee02394976ad7a72b906e0e3bb994b2061307`) |
| archivos prohibidos rastreados | cero nuevos |

La suite cubre canonicalización, query/fragment, hosts/rutas inválidos, PROFILE sin regresión, URL
directa sin timeline, post/autor fail-closed, DTO spawn, ausencia de query en manifest/sidecar e
idempotencia offline.

## Aceptación pública única

Target sanitizado: host `x.com`, handle `tedmetal`, post ID `2115531877855732095`.

El comando autorizado se ejecutó una sola vez con límite 1, un intento y timeout externo de 45 s.
Terminó inmediatamente con código 9: los archivos de captura stdout/stderr se crearon por error
dentro de `<LOCAL_SINGLE_POST_ROOT>`, por lo que el repositorio ya no estaba vacío. El control local
de consistencia respondió `catalog and filesystem do not agree` antes de discovery.

- Acceso a X: no iniciado.
- Videos, sidecars, artifacts, jobs e identidades: 0.
- SQLite y manifest: ausentes; integrity/hash no aplican.
- `.part`/`.tmp`: 0.
- Cookies, URL multimedia firmada y query de compartición persistidas: 0.
- Retry: no ejecutado.

La implementación no recibió una aceptación pública válida. La autorización quedó consumida por el
único comando y no se improvisó una repetición.

## Riesgo y rollback

Riesgo pendiente: el camino SINGLE_POST sigue sin evidencia pública válida aunque las pruebas y CI
sean verdes. Rollback: revertir el commit funcional y el documental; no reescribir historia ni
borrar evidencia local. Una nueva aceptación requiere mandato humano explícito con captura fuera
del repositorio objetivo.

No hubo cookies exportadas, perfil alternativo, recorrido de cuenta, descarga de otro post, dot,
merge, tag, release, B05 ni descarga masiva.
