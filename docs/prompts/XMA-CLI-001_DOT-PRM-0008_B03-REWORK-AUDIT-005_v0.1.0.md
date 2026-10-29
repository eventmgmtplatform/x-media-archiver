# XMA-CLI-001-DOT-PRM-0008 — B03 Rework Audit 005

**Versión:** 0.1.0

**Estado:** INACTIVE UNTIL CODEX HANDOFF

**Ejecutor:** dot

**Supervisión humana:** Leonel Galindo

## 1. Objetivo

Auditar una sola ejecución autorizada de `XMA-CLI-001-PRM-0008 v0.1.0` sobre PR #3. Determinar si
RW-03 elimina el límite de exponente introducido por `Decimal(value)` sin reabrir los negativos,
la matriz positiva, la sanitización o los límites SQLite, y si el único impedimento restante es
`AuthRequired`.

## 2. Fuente de verdad

1. GitHub: PR, commits, trees, diff, comentarios y revisiones.
2. CI del HEAD final.
3. AUD-0003 v0.1.4, PRM-0008, HND-0003 v0.1.5 y documentación versionada.
4. Código y pruebas fijados por SHA. La conversación no sustituye evidencia canónica.

Fijar SHA y tree antes de auditar. Confirmar PR abierto/draft/sin merge y que CI corresponde al
mismo contenido. Si el HEAD cambia durante la auditoría, detenerse como `BLOCKED`.

## 3. Criterio gobernado

- El dominio compatible de cadenas es el aceptado por `float()` en `ce3c067`, siempre que el
  resultado sea finito y el significando decimal sea semánticamente no negativo.
- El signo de cadenas debe validarse sin construir un `Decimal` del valor completo ni imponer un
  límite adicional de exponente.
- Un signo negativo con significando distinto de cero se rechaza aunque convierta a `-0.0`.
- Un cero con signo conserva el comportamiento histórico de cero.
- Tras la validación se conserva exactamente `float(value)`, multiplicación por 1000 y `round()`.

## 4. Allowlist

- Helper mínimo de análisis léxico/sintáctico para signo y significando de cadenas numéricas.
- Eliminación de imports decimales que queden sin uso.
- Regresiones offline de mapper, frontera CLI y persistencia temporal.
- HND-0003 v0.1.5 y documentación mínima.
- Ajustes mecánicos de formato/tipos derivados directamente.

## 5. Verificaciones

- Comparar `ce3c067542827f702caa4bfd89fc9bd9ac4905b1`,
  `6aae61f2d870249fad51a542f3d397ad2b0ecece`, la baseline gobernada y el HEAD final; inventariar
  todos los commits y archivos.
- Reproducir offline los cinco negativos de PRM-0007 y el nuevo negativo
  `"-1e-1999999999999999998"`; todos deben producir `DiscoveryContractError` constante antes de
  perder el signo.
- Reproducir `"1e-1999999999999999998"`, `"0e1000000000000000000"` y
  `"-0e1000000000000000000"`; mapper y fronteras deben coincidir con la baseline y producir
  `0 ms`.
- Verificar en catálogo temporal que los tres casos aceptados persisten `0 ms` y que el negativo
  no crea directorio ni SQLite.
- Comparar mapper real de baseline y HEAD para los diez casos de PRM-0007; no debe existir deriva.
- Confirmar la regresión CLI `width=json.loads("1e400")`, los empates float/cadena, no finitos,
  booleanos, rangos SQLite, JSON, límites, cursor, variantes rotadas, `metadata-only` y R-01 a R-07.
- Inspeccionar que el helper no acepte una gramática más amplia que `float()`, no confunda los
  dígitos del exponente con el significando y no imponga límites nuevos de longitud o exponente.
- Confirmar suite offline, Ruff, mypy, cobertura >= 90 %, build, lockfile y CI verde.
- Confirmar ausencia de archivos prohibidos, medios, bases, secretos y respuestas reales.

## 6. Desviaciones bloqueantes

Marcar `REWORK_REQUIRED` o `FAILED` ante aceptación de un negativo no cero, rechazo de cualquiera
de los nuevos positivos/ceros, deriva frente a `ce3c067`, pérdida de regresiones anteriores,
sustitución silenciosa, captura amplia, cookies, autenticación, otro extractor, acceso a X,
repetición del smoke, medios, comandos B04/B05, infraestructura fuera de alcance, tests CI con
red, cambios funcionales B02/esquema/lockfile, merge, force-push, tag, release o B04.

## 7. Dictamen

Emitir exactamente uno:

- `BLOCKED`: RW-01/R-05/RW-02/RW-03 cerrados y solo permanece el bloqueo público `AuthRequired`.
- `VALIDATED_WITH_OBSERVATIONS`: únicamente con un gate humano nuevo que redefina el criterio.
- `REWORK_REQUIRED`: persiste una carencia recuperable.
- `FAILED`: desviación material o incumplimiento irrecuperable.

Entregar el contenido completo de
`XMA-CLI-001_AUD-0003_B03-REWORK-005_v0.1.5.md` listo para versionarse, con matriz, evidencia,
riesgos, rollback y próxima acción. No modificar GitHub, aprobar el PR, fusionar ni autorizar B04.

