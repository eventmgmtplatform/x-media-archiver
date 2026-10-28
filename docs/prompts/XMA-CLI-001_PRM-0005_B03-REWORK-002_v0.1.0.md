# XMA-CLI-001-PRM-0005 — B03 Rework 002

**Versión:** 0.1.0

**Estado:** APPROVED FOR ONE EXECUTION

**Ejecutor:** Codex localhost

**Supervisión humana:** Leonel Galindo

**Repositorio:** `https://github.com/eventmgmtplatform/x-media-archiver.git`

**Rama:** `feature/xma-b03-discovery`

**Baseline funcional:** `0186129e06201b644a4d383d621740f291d1244d`

**Baseline de ejecución:** HEAD de PR #3 que contenga `AUD-0003 v0.1.1`, este prompt y `DOT-PRM-0005 v0.1.0`.

## 1. Autorización y objetivo

Leonel autorizó el 2026-10-28 una sola ejecución acotada de `B03-REWORK-002`. Corregir
exclusivamente `RW-01 / R-05` de `XMA-CLI-001_AUD-0003_B03-REWORK-001_v0.1.1`: metadatos
numéricos no finitos o fuera de la representación admitida por el contrato pueden provocar
`OverflowError` sin normalizar.

El resultado debe convertir esos casos en `DiscoveryContractError`, salida CLI 5, mensaje
sanitizado y ausencia de traceback. Este prompt no reabre R-01, R-02, R-03, R-04, R-06 o R-07,
salvo las actualizaciones mínimas de trazabilidad y las regresiones necesarias para demostrar que
no fueron degradados.

## 2. Precondiciones

1. Consultar GitHub y verificar que PR #3 está abierto, draft, sin merge y que su historia contiene
   la baseline funcional exacta.
2. Leer íntegros `AUD-0003 v0.1.1`, este prompt y `DOT-PRM-0005 v0.1.0` desde el HEAD remoto.
3. Verificar rama, upstream, HEAD, worktree limpio y CI de la baseline. No reescribir historia ni
   usar force-push.
4. Si el PR avanzó con cambios funcionales no gobernados, falta cualquier artefacto canónico o la
   evidencia no coincide, detenerse con estado `BLOCKED` sin modificar código.

## 3. Rework permitido y obligatorio

### 3.1 Frontera numérica del adaptador

- Revisar todas las conversiones numéricas del mapper de `gallery-dl`, como mínimo `num`, `width`,
  `height` y `duration`/`duration_ms`.
- Rechazar booleanos donde se espere un número.
- Rechazar `NaN`, infinito positivo e infinito negativo antes de convertir, redondear, restar o
  construir entidades de dominio.
- Exigir las invariantes existentes: índice de origen válido antes de convertirlo a índice base
  cero y dimensiones/duración no negativas.
- Definir una representación finita y acotada compatible con dominio y SQLite. Documentar el
  criterio técnico; no introducir límites de producto arbitrarios ni alterar el límite de discovery
  1–100.
- Conservar, cuando sea seguro, la compatibilidad con los valores finitos ya aceptados. No usar
  valores sustitutos, saturación silenciosa ni convertir un dato inválido a `None`.
- Normalizar `OverflowError` y errores equivalentes de esa frontera como
  `DiscoveryContractError` con texto constante y sanitizado. No capturar `BaseException` ni ocultar
  defectos de programación ajenos a la conversión gobernada.

### 3.2 CLI y seguridad de salida

- `inspect` y `sync` deben terminar con código 5 ante este cambio de contrato.
- No imprimir el valor numérico defectuoso, payload, URL firmada, respuesta cruda ni secreto.
- No mostrar traceback por defecto.
- No crear catálogo, medios o side effects cuando el fallo ocurre antes de persistencia.

### 3.3 Pruebas offline

- Añadir casos parametrizados del mapper para `NaN`, `+inf` y `-inf` en los campos pertinentes,
  incluyendo valores obtenibles por JSON como `1e400`.
- Cubrir al menos `num`, `width`, `height` y `duration`; verificar tipo de excepción y mensaje
  sanitizado sin reflejar un marcador sensible del fixture.
- Añadir una regresión CLI representativa que atraviese el adaptador/servicio mediante dobles
  offline y compruebe código 5, ausencia de traceback, ausencia del dato crudo y ausencia de
  catálogo.
- Conservar regresiones de valores finitos válidos, JSON estable, límites, cursor, variantes
  rotadas y persistencia metadata-only.
- Toda la suite automatizada debe permanecer sin red.

### 3.4 Trazabilidad

- Crear `HND-0003` addendum v0.1.2, o equivalente inequívoco, con baseline, archivos, decisiones
  de contrato, comandos, resultados, commit/tree final, CI, limitaciones y rollback.
- Actualizar únicamente la documentación necesaria para reflejar `B03-REWORK-002`,
  `WAITING_VALIDATION` y la permanencia del bloqueo público `AuthRequired`.
- No repetir Reuters/AP/BBCWorld ni ningún smoke contra X. La evidencia pública anterior se conserva
  sin reinterpretarla.

## 4. Restricciones

- No cookies, login, tokens, contraseñas, sesiones autenticadas ni secretos.
- No `yt-dlp`, FFmpeg, Twikit, `twscrape` ni otro extractor.
- No descargar videos, audio, thumbnails, sidecars ni respuestas reales.
- No crear `download`, `retry`, `status`, `export`, `doctor` ni funcionalidad B04/B05.
- No GUI, API, servidor, ORM, Redis, Docker, scheduler, migración de catálogos, tags o releases.
- No cambiar esquema SQLite, lockfile o código B02 salvo prueba de necesidad directa; la expectativa
  es cero cambios en ellos.
- No bases, medios, secretos, payloads o evidencias locales en Git.
- No pruebas CI con red, merge, aprobación del PR ni certificación del producto.

## 5. Validación

Ejecutar y registrar:

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

Cobertura total mínima: 90 %. Confirmar lockfile íntegro y sin cambios, wheel con los módulos
esperados y ausencia de archivos prohibidos. Publicar commits mínimos en la rama existente y
esperar CI verde sobre el HEAD final.

## 6. Entregables y parada

- Corrección mínima de `RW-01 / R-05`.
- Pruebas offline de mapper y CLI.
- Documentación mínima y `HND-0003 v0.1.2`.
- CI verde del HEAD final.

Detenerse tras publicar el handoff y obtener CI. No crear la auditoría posterior, no fusionar y no
autorizar B04. La entrega debe clasificarse únicamente como `WAITING_VALIDATION`, `BLOCKED` o
`FAILED`, con evidencia canónica.
