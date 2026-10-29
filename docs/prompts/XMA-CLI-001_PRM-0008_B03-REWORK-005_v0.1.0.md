# XMA-CLI-001-PRM-0008 — B03 Rework 005

**Versión:** 0.1.0

**Estado:** PROPOSED — AWAITING HUMAN AUTHORIZATION

**Ejecutor:** Codex localhost

**Supervisión humana:** Leonel Galindo

**Repositorio:** `https://github.com/eventmgmtplatform/x-media-archiver.git`

**Rama:** `feature/xma-b03-discovery`

**Baseline funcional auditada:** `6aae61f2d870249fad51a542f3d397ad2b0ecece`

**Tree auditado:** `8644dba6aa31d979c730613bb87c355e3586ec3a`

**Baseline de compatibilidad:** `ce3c067542827f702caa4bfd89fc9bd9ac4905b1`

**Baseline de ejecución:** HEAD de PR #3 que contenga `AUD-0003 v0.1.4`, este prompt y
`DOT-PRM-0008 v0.1.0`.

## 1. Gate y objetivo

Este documento no autoriza por sí solo la ejecución. Leonel debe autorizar expresamente una única
ejecución acotada de `B03-REWORK-005`.

Corregir exclusivamente RW-03 de
`XMA-CLI-001_AUD-0003_B03-REWORK-004_v0.1.4`: B03-REWORK-004 conserva la matriz explícita de
PRM-0007, pero usa `Decimal(value)` para validar el signo de cadenas y por ello introduce un límite
de exponente que no existía en la baseline `ce3c067`.

El resultado debe conservar simultáneamente:

- el dominio histórico de cadenas numéricas aceptadas por `float()` cuando representan un valor
  finito y semánticamente no negativo;
- el rechazo previo al redondeo de cadenas negativas que `float()` subdesborda a `-0.0`;
- la matriz positiva, los cinco negativos, los no finitos, booleanos y límites SQLite ya cerrados;
- la salida sanitizada y la ausencia de directorio o SQLite ante error.

## 2. Criterio de representación versionado

1. La compatibilidad de B03 se define contra la conversión de `ce3c067`: una cadena que
   `float(value)` acepta, cuyo resultado es finito y cuyo significando decimal es semánticamente
   no negativo, debe continuar hasta `seconds * 1000` y `round()` sin imponer límites adicionales
   de `Decimal` sobre el exponente.
2. La validación del signo de una cadena debe ser sintáctica o léxica y no debe construir un
   `Decimal` del valor completo. Debe inspeccionar el signo y el significando, sin evaluar ni
   acotar la magnitud del exponente.
3. Un signo `-` con significando decimal distinto de cero es negativo aunque `float()` produzca
   `-0.0`; debe rechazarse. Un cero con signo, incluido `-0e...`, representa cero y conserva la
   compatibilidad histórica.
4. Después de validar sintaxis, finitud y signo, la conversión sigue exactamente:
   `seconds = float(value)`, `milliseconds = seconds * 1000`, `round(milliseconds)`.
5. No ampliar la gramática más allá de lo que acepta `float()` ni aceptar NaN, infinitos,
   booleanos o valores fuera del entero SQLite firmado de 64 bits.

## 3. Precondiciones

1. Consultar GitHub y fijar PR #3 abierto, draft y sin merge, con HEAD descendiente exacto de
   `6aae61f2d870249fad51a542f3d397ad2b0ecece`.
2. Leer íntegros AUD-0003 v0.1.4, este prompt, DOT-PRM-0008 y HND-0003 v0.1.4 desde el HEAD
   remoto.
3. Verificar autorización humana inequívoca, rama/upstream, worktree limpio y CI #24 verde.
   Solo fast-forward; sin force-push ni reescritura.
4. Si el PR avanzó con cambios funcionales no gobernados, falta autorización o la evidencia no
   coincide, detenerse como `BLOCKED`.

## 4. Rework obligatorio

### 4.1 Implementación mínima

- Reemplazar exclusivamente la dependencia de `Decimal(value)` usada para determinar el signo de
  cadenas en `_duration_ms` por un helper pequeño, tipado y probado que analice la representación
  aceptada por `float()` sin evaluar la magnitud del exponente.
- Mantener la conversión histórica y el mensaje constante
  `gallery-dl numeric metadata violates the B03 contract`.
- Eliminar imports de `Decimal` o excepciones decimales que queden sin uso.
- No introducir un límite de longitud, dígitos o exponente, saturación, sustitución por cero/`None`,
  truncamiento silencioso ni captura de `Exception` o `BaseException`.
- No modificar proveedor, comandos, catálogo, esquema ni contratos fuera de lo estrictamente
  necesario para RW-03.

### 4.2 Regresiones offline

Mantener toda la matriz de PRM-0007 y añadir como mínimo:

| Entrada | Resultado esperado |
|---|---:|
| `"1e-1999999999999999998"` | `0 ms` |
| `"0e1000000000000000000"` | `0 ms` |
| `"-1e-1999999999999999998"` | error de contrato |
| `"-0e1000000000000000000"` | `0 ms` |

- Probar mapper real, `inspect` y `sync` offline para esos cuatro casos.
- Para los tres positivos/cero aceptados, `inspect` debe terminar con éxito y `sync` debe persistir
  `0 ms` en un catálogo temporal.
- Para el negativo no cero, ambos comandos deben devolver código 5, mensaje sanitizado, sin
  traceback, dato crudo, directorio ni SQLite.
- Mantener los cinco negativos anteriores, los diez positivos explícitos, persistencia de empates
  float/cadena, `width=json.loads("1e400")`, NaN, infinitos, booleanos, rangos SQLite, JSON,
  límites, cursor, variantes rotadas y `metadata-only`.
- Toda la suite debe permanecer sin red.

### 4.3 Trazabilidad

- Crear HND-0003 addendum v0.1.5 con baseline, archivos, criterio versionado, matriz, comandos,
  resultados, commit/tree final, CI, limitaciones y rollback.
- Corregir mediante el addendum las afirmaciones generales de compatibilidad de HND v0.1.4; no
  reescribir documentos publicados.
- Actualizar solo README, CHANGELOG, Gate Register, Implementation Plan y cuerpo del PR cuando sea
  necesario para reflejar `B03-REWORK-005 / WAITING_VALIDATION`.
- No repetir el smoke de Reuters, AP o BBCWorld.

## 5. Restricciones

- No cookies, autenticación, secretos, sesiones o respuestas reales.
- No otro extractor, descargas, medios, thumbnails, sidecars, staging o hashes de medios.
- No comandos B04/B05, GUI, API, servidor, ORM, Redis, Docker o scheduler.
- No modificar esquema SQLite, lockfile, workflow, B02 o catálogos existentes.
- No bases, medios o evidencias locales rastreadas.
- No merge, tag, release, aprobación del PR, auditoría propia ni inicio de B04.

## 6. Validación

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

## 7. Entregables y parada

- Corrección mínima de RW-03 sin reabrir las regresiones anteriores.
- Regresiones offline de mapper, CLI y persistencia temporal.
- Documentación mínima y HND-0003 v0.1.5.
- CI verde del HEAD final.

Detenerse después del handoff y CI. Entregar únicamente `WAITING_VALIDATION`, `BLOCKED` o
`FAILED`. No crear la auditoría posterior ni autorizar B04.

