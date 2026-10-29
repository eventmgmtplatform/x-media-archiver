# XMA-CLI-001-PRM-0006 — B03 Rework 003

**Versión:** 0.1.0

**Estado:** APPROVED FOR ONE EXECUTION

**Ejecutor:** Codex localhost

**Supervisión humana:** Leonel Galindo

**Repositorio:** `https://github.com/eventmgmtplatform/x-media-archiver.git`

**Rama:** `feature/xma-b03-discovery`

**Baseline funcional:** `ce3c067542827f702caa4bfd89fc9bd9ac4905b1`

**Baseline de ejecución:** HEAD de PR #3 que contenga `AUD-0003 v0.1.2`, este prompt y
`DOT-PRM-0006 v0.1.0`.

## 1. Autorización y objetivo

Leonel autorizó resolver los fixtures y cerrar el hallazgo recuperable de R-05. Esta es una sola
ejecución acotada de `B03-REWORK-003`.

Corregir exclusivamente el defecto documentado en
`XMA-CLI-001_AUD-0003_B03-REWORK-002_v0.1.2`: una duración negativa suficientemente pequeña
puede perder el signo durante la conversión o redondearse a cero y aceptarse como válida.

El resultado debe rechazar toda duración semánticamente negativa antes de una conversión que
oculte su signo. Debe conservar el comportamiento de cero y duraciones positivas válidas. Este
prompt no reabre otros controles salvo las regresiones y la trazabilidad mínimas necesarias.

## 2. Precondiciones

1. Consultar GitHub y verificar PR #3 abierto, draft, sin merge y HEAD descendiente exacto de la
   baseline funcional.
2. Leer íntegros AUD-0003 v0.1.2, este prompt y DOT-PRM-0006 desde el HEAD remoto.
3. Verificar rama, upstream, worktree limpio y CI #16 verde. Solo fast-forward; sin force-push ni
   reescritura de historia.
4. Si el PR avanzó con cambios funcionales no gobernados o falta evidencia canónica, detenerse como
   `BLOCKED`.

## 3. Rework obligatorio

### 3.1 Validación de duración

- Validar el valor de duración en segundos antes de multiplicar o redondear.
- Rechazar todo valor semánticamente menor que cero, aunque su magnitud sea inferior a medio
  milisegundo o se subdesborde al convertirlo a `float`.
- Para cadenas numéricas, conservar el signo y magnitud durante la validación mediante una
  representación decimal exacta o una solución equivalente; no depender exclusivamente de
  `float(value)` cuando pueda convertir una cadena negativa no nula en `-0.0`.
- Cubrir como mínimo `-0.0001`, `-0.0005`, `-5e-324`, `"-0.0001"` y `"-1e-400"`.
- Mantener el rechazo de booleanos, NaN, infinitos, valores fuera del rango SQLite y demás casos de
  PRM-0005.
- Mantener cero y duraciones positivas válidas. Documentar explícitamente el resultado de
  duraciones positivas menores a medio milisegundo; no introducir un límite de producto nuevo.
- Conservar el mensaje constante y sanitizado
  `gallery-dl numeric metadata violates the B03 contract`.
- No usar saturación, sustitución por cero/`None`, truncamiento silencioso ni captura amplia de
  `Exception` o `BaseException`.

### 3.2 Pruebas offline

- Añadir regresiones del mapper real para los cinco negativos mínimos indicados.
- Añadir controles para cero, una duración positiva submilisegundo, una cadena positiva extrema
  dentro de la representación aceptada y los valores positivos existentes.
- Añadir o extender regresiones de `inspect` y `sync` que atraviesen runner offline, proveedor,
  mapper y servicio; verificar código 5, mensaje sanitizado, ausencia de traceback/dato crudo y
  ausencia de directorio o SQLite.
- Verificar explícitamente que `sync` no persiste cero para una duración negativa.
- Mantener toda la suite sin red y preservar las regresiones anteriores de R-01 a R-07.

### 3.3 Trazabilidad

- Crear HND-0003 addendum v0.1.3 con baseline, archivos, decisión numérica, comandos, resultados,
  commit/tree final, CI, limitaciones y rollback.
- Corregir HND v0.1.2 mediante el nuevo addendum: su afirmación de rechazo de todos los negativos no
  es válida para el snapshot histórico.
- Actualizar solo la documentación necesaria y el cuerpo de PR al estado
  `B03-REWORK-003 / WAITING_VALIDATION`.
- No repetir el smoke de Reuters, AP o BBCWorld.

## 4. Restricciones

- No cookies, autenticación, secretos, sesiones o respuestas reales.
- No otro extractor, descargas, medios, thumbnails, sidecars, staging o hashes de medios.
- No comandos B04/B05, GUI, API, servidor, ORM, Redis, Docker o scheduler.
- No modificar esquema SQLite, lockfile, workflow, B02 o catálogos existentes.
- No bases, medios o evidencias locales rastreadas.
- No merge, tag, release, aprobación del PR, auditoría propia ni inicio de B04.

## 5. Validación

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

Cobertura total mínima: 90 %. Confirmar lockfile byte-idéntico, wheel íntegro y ausencia de archivos
prohibidos. Publicar commits mínimos y esperar CI verde sobre el HEAD final.

## 6. Entregables y parada

- Corrección mínima de validación de duración.
- Regresiones offline de mapper y CLI.
- Documentación mínima y HND-0003 v0.1.3.
- CI verde del HEAD final.

Detenerse después del handoff y CI. Entregar únicamente `WAITING_VALIDATION`, `BLOCKED` o
`FAILED`. No crear la auditoría posterior ni autorizar B04.
