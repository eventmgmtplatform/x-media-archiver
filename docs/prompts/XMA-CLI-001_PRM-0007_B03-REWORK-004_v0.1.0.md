# XMA-CLI-001-PRM-0007 — B03 Rework 004

**Versión:** 0.1.0

**Estado:** PROPOSED — AWAITING HUMAN AUTHORIZATION

**Ejecutor:** Codex localhost

**Supervisión humana:** Leonel Galindo

**Repositorio:** `https://github.com/eventmgmtplatform/x-media-archiver.git`

**Rama:** `feature/xma-b03-discovery`

**Baseline funcional auditada:** `496e6ce4f1559c154a88dcd3985dbced1a7cf8af`

**Baseline de referencia para compatibilidad:** `ce3c067542827f702caa4bfd89fc9bd9ac4905b1`

**Baseline de ejecución:** HEAD de PR #3 que contenga `AUD-0003 v0.1.3`, este prompt y
`DOT-PRM-0007 v0.1.0`.

## 1. Gate y objetivo

Este documento no autoriza por sí solo la ejecución. Leonel debe autorizar expresamente una única
ejecución acotada de `B03-REWORK-004`.

Corregir exclusivamente RW-02 de
`XMA-CLI-001_AUD-0003_B03-REWORK-003_v0.1.3`: B03-REWORK-003 rechaza correctamente las
duraciones negativas pequeñas, pero cambió el redondeo de floats positivos válidos en empates de
medio milisegundo. Por ejemplo, `0.0005` pasó de `0 ms` a `1 ms` y `0.0025` de `2 ms` a `3 ms`.

El resultado debe conservar simultáneamente:

- rechazo semántico de todo negativo antes de una conversión que pueda ocultar el signo;
- resultados de redondeo positivos de la baseline `ce3c067`;
- normalización sanitizada de no finitos, booleanos y rangos inválidos;
- ausencia de persistencia o directorio ante errores de contrato.

## 2. Precondiciones

1. Consultar GitHub y fijar PR #3 abierto, draft y sin merge, con HEAD descendiente exacto de
   `496e6ce4f1559c154a88dcd3985dbced1a7cf8af`.
2. Leer íntegros AUD-0003 v0.1.3, este prompt, DOT-PRM-0007 y HND-0003 v0.1.3 desde el HEAD
   remoto.
3. Verificar autorización humana versionada o inequívoca, rama/upstream, worktree limpio y CI #20
   verde. Solo fast-forward; sin force-push ni reescritura.
4. Si el PR avanzó con cambios funcionales no gobernados, falta autorización o la evidencia no
   coincide, detenerse como `BLOCKED`.

## 3. Rework obligatorio

### 3.1 Compatibilidad de conversión

- Separar la validación semántica de signo/finitud de la conversión histórica a milisegundos.
- Para cadenas, validar primero con `Decimal` o representación exacta equivalente. Rechazar una
  cadena semánticamente negativa antes de `float(value)`, incluidos `"-0.0001"` y `"-1e-400"`.
- Para floats, validar finitud y negatividad antes de multiplicar o redondear; `-5e-324` debe
  rechazarse.
- Después de validar que el valor es finito y no negativo, conservar exactamente la conversión de
  la baseline: `seconds = float(value)`, `milliseconds = seconds * 1000`, `round(milliseconds)`.
  No usar `Decimal.from_float()` como operando del redondeo positivo.
- Mantener el rango SQLite, el rechazo de booleanos y el mensaje constante
  `gallery-dl numeric metadata violates the B03 contract`.
- No introducir límites de producto, saturación, sustitución por cero/`None`, truncamiento
  silencioso ni captura amplia de `Exception` o `BaseException`.

### 3.2 Matriz de regresión offline

- Mantener los cinco negativos mínimos: `-0.0001`, `-0.0005`, `-5e-324`, `"-0.0001"` y
  `"-1e-400"`. Todos deben producir `DiscoveryContractError` constante.
- Fijar compatibilidad de mapper para floats y cadenas con estos resultados de baseline:

| Entrada | Resultado esperado |
|---|---:|
| `0` | `0 ms` |
| `0.0001` | `0 ms` |
| `0.0005` | `0 ms` |
| `0.0015` | `2 ms` |
| `0.0025` | `2 ms` |
| `0.0045` | `4 ms` |
| `"0.0005"` | `0 ms` |
| `"0.0025"` | `2 ms` |
| `"1e-400"` | `0 ms` |
| `"12.5"` | `12500 ms` |

- Atravesar runner offline, proveedor, mapper, servicio y comandos `inspect`/`sync` para negativos;
  verificar código 5, mensaje sanitizado, ausencia de traceback/dato crudo y ausencia de
  directorio/SQLite.
- Verificar mediante `sync` temporal que floats `0.0005` y `0.0025`, y sus cadenas equivalentes,
  persisten respectivamente `0 ms` y `2 ms`.
- Restaurar como prueba adicional la regresión CLI no finita reemplazada en B03-REWORK-003:
  `width=json.loads("1e400")` debe producir salida 5 sanitizada y no crear catálogo. No retirar las
  pruebas negativas para restaurarla.
- Mantener las regresiones de NaN, infinitos, booleanos, rangos SQLite, JSON, límites, cursor,
  variantes rotadas, `metadata-only` y R-01 a R-07. Toda la suite debe ejecutarse sin red.

### 3.3 Trazabilidad

- Crear HND-0003 addendum v0.1.4 con baseline, archivos, decisión de compatibilidad, matriz,
  comandos, resultados, commit/tree final, CI, limitaciones y rollback.
- Corregir mediante el addendum las afirmaciones de HND v0.1.3 y README sobre conservación
  histórica; no reescribir documentos publicados.
- Actualizar solo README, CHANGELOG, Gate Register, Implementation Plan y cuerpo del PR cuando sea
  necesario para reflejar `B03-REWORK-004 / WAITING_VALIDATION`.
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

- Corrección mínima de compatibilidad positiva sin reabrir negativos.
- Regresiones offline de mapper, CLI y persistencia temporal.
- Restauración de la regresión CLI no finita.
- Documentación mínima y HND-0003 v0.1.4.
- CI verde del HEAD final.

Detenerse después del handoff y CI. Entregar únicamente `WAITING_VALIDATION`, `BLOCKED` o
`FAILED`. No crear la auditoría posterior ni autorizar B04.
