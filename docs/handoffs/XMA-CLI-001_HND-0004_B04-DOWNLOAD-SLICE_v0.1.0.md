# XMA-CLI-001 — HND-0004 B04 Download Slice

**Versión:** 0.1.0  
**Fecha:** 2026-10-28 (America/Mexico_City)  
**Estado:** `BLOCKED_PUBLIC_DOWNLOAD`  
**Prompt:** `XMA-CLI-001-PRM-0016 B04-DOWNLOAD-VERTICAL-SLICE v0.1.0`

## Baseline y publicación

- Baseline B03: `bdef347ab83edba8ca63b9f13c8afa524178967e`.
- Tree baseline: `d57f9155e696a90f529641a2349fb694dcaa3d23`.
- Rama: `feature/xma-b04-download-slice`.
- PR draft apilado: #4, base `feature/xma-b03-discovery`.
- Commit de implementación: `059f902d543e260cf1ee66faa7c0abb5ea03da3c`.
- Tree de implementación: `8fc0a3c7c80b6879cc8978e29fc5235db553a4ad`.
- Publicación inicial del handoff: `430a707881aefadb183331616de7bbb7a196e2a5`.
- Tree de esa publicación: `dc76c124c1676a11d45b66945d862e0fe4671ee2`.
- CI #43 / run `40823455324`: `SUCCESS` sobre esa publicación; 236 pruebas y cobertura 93.24 %.
- La reconciliación que registra este resultado de CI es exclusivamente documental y se verifica en
  el siguiente run del mismo PR draft.

## Alcance entregado

Se añadió el comando acotado `xma download`, límites 1–5, autenticación Firefox o archivo Netscape
caller-owned mutuamente excluyentes, puerto tipado de descarga, streaming a `.part`, SHA-256,
movimiento atómico, sidecar, manifest y persistencia con los contratos SQLite existentes. La
idempotencia verifica catálogo, tamaño, hash y sidecar; cualquier divergencia falla cerrada.

No cambiaron el esquema SQLite, workflow, dependencias ni `uv.lock`. No se inició B05.

## Validación offline

| Comando | Resultado |
|---|---|
| `uv sync --locked --all-groups` | PASS |
| `uv run ruff format --check .` | PASS, 99 archivos |
| `uv run ruff check .` | PASS |
| `uv run mypy` | PASS, 34 archivos fuente |
| `uv run pytest` | PASS, 236 pruebas |
| cobertura | PASS, 92.80 % |
| `uv build` | PASS, sdist y wheel |
| `git diff --check` | PASS |
| `uv.lock` byte-idéntico a baseline | PASS |
| revisión de archivos rastreados prohibidos | PASS |

Las pruebas cubren límites 1/2/5, staging, hash y tamaño, sidecars, manifest, transiciones,
idempotencia, conflicto fail-closed, limpieza de fallo, frontera HTTP y autenticación alternativa.
Toda la suite automatizada permaneció offline.

## Smoke público único

Se usó Reuters, un único perfil Firefox local representado como `<LOCAL_PROFILE>` y repositorios
independientes bajo `<LOCAL_SMOKE_ROOT>`. No se inspeccionaron ni publicaron cookies, rutas o datos
de sesión.

| Orden | Target | Límite | Código | Videos | Sidecars | SQLite | `.part` | Resultado |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | Reuters | 1 | 8 | 0 | 0 | 0 | 0 | fallo transitorio sanitizado del proveedor |
| 2 | Reuters | 2 | no ejecutado | 0 | 0 | 0 | 0 | detenido por contrato |
| 3 | Reuters | 5 | no ejecutado | 0 | 0 | 0 | 0 | detenido por contrato |

El primer límite no obtuvo exactamente un activo. Conforme a PRM-0016, la secuencia se detuvo sin
retry; no se ejecutaron los límites 2 y 5. No hubo descargas, sidecars, manifests, SQLite ni staging
residual. El perfil real y las rutas locales no se versionan.

## Archivos de implementación

- Dominio: `src/xma/domain/download.py`, errores y puerto de descarga.
- Aplicación: `src/xma/application/download.py`.
- Infraestructura: `src/xma/adapters/download/`, frontera de autenticación y CLI.
- Pruebas: mapper/servicio, adaptadores HTTP/auth y CLI.
- Documentación: README, CHANGELOG, ADR-0004, Gate Register, plan, PRM-0016 y este handoff.

## Riesgos, limitaciones y rollback

El gate público 1/2/5 no está acreditado; el fallo transitorio no autoriza retry ni inferir que la
descarga funcionaría en X. El corte no implementa paginación durable, concurrencia, retry, progreso
ni operación masiva. La autenticación sigue siendo local y read-only.

Rollback: cerrar el PR draft y borrar la rama B04; la rama B03 y su tree no fueron modificados. Los
repositorios temporales locales no contienen activos y pueden retirarse después de la auditoría.

## Decisión requerida

Se requiere decisión humana para cualquier nueva ejecución pública o rework. Este handoff no
autoriza merge, tag, release, certificación, retry, B05 ni auditoría ejecutada por Codex.

Estado final: **`BLOCKED_PUBLIC_DOWNLOAD`**.
