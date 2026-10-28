# XMA-CLI-001-PRM-0009 — B03 Authenticated Discovery

**Versión:** 0.1.0  
**Estado:** APPROVED FOR ONE EXECUTION  
**Ejecutor:** Codex localhost  
**Supervisión humana:** Leonel Galindo  
**Repositorio:** `https://github.com/eventmgmtplatform/x-media-archiver.git`  
**Rama:** `feature/xma-b03-discovery`  
**Baseline gobernada:** `946ebd11503e3b06f623e22b3aabe43c6e193a76`  
**Tree:** `378529fd4f533391b4f09e246676f48f32224f5c`

## 1. Objetivo

Implementar una capacidad mínima y genérica para que B03 use, cuando el operador lo solicite,
cookies leídas directamente de una sesión local de Firefox. Mantener anónimo el modo por defecto.
Los valores concretos de cuenta y perfil se suministran localmente y nunca se documentan en Git.

## 2. Precondiciones

1. Fijar PR #3 abierto, draft, sin merge y descendiente exacto de la baseline.
2. Leer ADR-0003, este prompt, DOT-PRM-0011, Gate Register, Plan y HND-0003 v0.1.5.
3. Confirmar worktree limpio, upstream correcto y CI #29 verde.
4. Pedir al operador los parámetros locales sin imprimir cookies ni inspeccionar su contenido.
5. Si el HEAD avanzó con cambios funcionales no gobernados, detenerse como `BLOCKED`.

## 3. Implementación permitida

- Añadir un DTO/configuración tipada de autenticación en infraestructura, no en dominio.
- Añadir a `inspect` y `sync` opciones `--auth-browser` y `--auth-profile`.
- Exigir ambas juntas; rechazar combinaciones incompletas con salida 2 sanitizada.
- Permitir únicamente Firefox en esta ejecución; no aceptar rutas arbitrarias a cookies.
- Configurar `gallery-dl` para leer la sesión directamente del perfil indicado.
- Conservar `config.clear()`, caché en memoria, descarga deshabilitada, límite, filtros de video,
  política `metadata-only` y clasificación de errores.
- No cargar configuración global, no usar username/password y no exportar cookies.

El nombre del perfil puede existir en argumentos locales, pero no debe aparecer en JSON, SQLite,
errores públicos, HND, cuerpo del PR ni logs CI. Ningún valor de cookie puede entrar al dominio.

## 4. Pruebas offline

Agregar pruebas sin navegador ni red para modo anónimo, configuración válida, combinaciones
incompletas, navegador no permitido, propagación al adaptador, errores sanitizados y ausencia de
datos de autenticación en JSON/SQLite. Cubrir `inspect`, `sync --dry-run` y `sync` con runners
sintéticos. Mantener todas las regresiones históricas y cobertura total mínima de 90 %.

## 5. Smoke público controlado

Solo después de validaciones locales verdes, ejecutar localmente Reuters → AP → BBCWorld,
deteniéndose en el primer perfil que produzca exactamente dos activos:

```bash
uv run xma sync @Reuters --limit 2 --repository <TEMP_REPOSITORY> \
  --auth-browser <LOCAL_BROWSER> --auth-profile <LOCAL_PROFILE>
```

El operador sustituye los placeholders localmente. No versionarlos. Usar repositorio temporal
fuera del árbol Git. Si Reuters no acredita dos activos, repetir con AP y BBCWorld. No ampliar
límite, paginar, reintentar en bucle ni consultar otras cuentas.

Éxito exige salida 0, límite solicitado 2, exactamente dos activos distintos catalogados, SQLite
consistente y cero medios, thumbnails o sidecars. Documentar solo target, código de salida,
conteos y extensiones. Redactar argumentos de autenticación, rutas, post IDs y URLs firmadas.

## 6. Handoff

- Crear HND-0003 addendum v0.2.0 con baseline, archivos, pruebas, CI, evidencia sanitizada,
  riesgos, rollback y estado `WAITING_VALIDATION`, `BLOCKED` o `FAILED`.
- Actualizar README, CHANGELOG, Gate Register, Plan y cuerpo del PR solo cuando sea necesario.
- Publicar commits mínimos fast-forward y esperar CI verde.

## 7. Prohibiciones

- No cookies, passwords, tokens, correo, teléfono, 2FA, códigos de recuperación o identificadores
  locales en Git, logs CI, HND o cuerpo del PR.
- No `cookies.txt`, `.env` con secretos, `.netrc`, keyring nuevo ni archivo secreto en la app.
- No API X, yt-dlp, FFmpeg, Twikit, twscrape u otro extractor.
- No descarga, thumbnails, sidecars, staging, hashes de medios o comandos B04/B05.
- No GUI, servidor, ORM, Redis, Docker, CI con red, cambios a main, merge, tag o release.

## 8. Validación y parada

```bash
uv sync --locked --all-groups
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest
uv build
git diff --check
git status --short
```

Detenerse después de HND-0003 v0.2.0 y CI. No ejecutar la auditoría ni declarar Q3 validado.
