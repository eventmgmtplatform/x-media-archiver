# XMA-CLI-001-DOT-PRM-0007 — B03 Rework Audit 004

**Versión:** 0.1.0

**Estado:** INACTIVE UNTIL CODEX HANDOFF

**Ejecutor:** dot

**Supervisión humana:** Leonel Galindo

## 1. Objetivo

Auditar una sola ejecución autorizada de `XMA-CLI-001-PRM-0007 v0.1.0` sobre PR #3. Determinar si
RW-02 restaura la compatibilidad positiva de `ce3c067` sin reabrir la aceptación de negativos ni
degradar la normalización no finita, y si el único impedimento restante es `AuthRequired`.

## 2. Fuente de verdad

1. GitHub: PR, commits, trees, diff, comentarios y revisiones.
2. CI del HEAD final.
3. AUD-0003 v0.1.3, PRM-0007, HND-0003 v0.1.4 y documentación versionada.
4. Código y pruebas fijados por SHA. La conversación no sustituye evidencia canónica.

Fijar SHA y tree antes de auditar. Confirmar PR abierto/draft/sin merge y que CI corresponde al
mismo contenido. Si el HEAD cambia durante la auditoría, detenerse como `BLOCKED`.

## 3. Allowlist

- Validación semántica de duración negativa antes de conversión o redondeo.
- Restauración exacta del redondeo positivo de la baseline `ce3c067`.
- Regresiones offline de mapper, frontera CLI y persistencia temporal.
- Restauración de la regresión CLI para un valor no finito.
- HND-0003 v0.1.4 y documentación mínima.
- Ajustes mecánicos de formato/tipos derivados directamente.

## 4. Verificaciones

- Comparar `ce3c067542827f702caa4bfd89fc9bd9ac4905b1`, la baseline gobernada y el HEAD final;
  inventariar todos los commits y archivos.
- Reproducir offline los cinco negativos: `-0.0001`, `-0.0005`, `-5e-324`, `"-0.0001"` y
  `"-1e-400"`. Todos deben producir `DiscoveryContractError` constante antes de perder signo.
- Comparar mapper real de baseline y HEAD para floats/cadenas `0`, `0.0001`, `0.0005`, `0.0015`,
  `0.0025`, `0.0045`, `"0.0005"`, `"0.0025"`, `"1e-400"` y `"12.5"`. No debe existir deriva.
- Ejecutar fronteras `inspect` y `sync` mediante runner offline/proveedor/mapper/servicio para los
  negativos: código 5, sin traceback/dato crudo y sin directorio/SQLite.
- Verificar en catálogo temporal que float y cadena `0.0005` persisten `0 ms`, y `0.0025` persiste
  `2 ms`, igual que la baseline.
- Confirmar la regresión CLI restaurada para `width=json.loads("1e400")`: salida 5 sanitizada, sin
  traceback ni catálogo.
- Confirmar que no se degradaron no finitos, booleanos, rangos SQLite, JSON, límites, cursor,
  variantes rotadas, `metadata-only` ni R-01 a R-07.
- Confirmar suite offline, Ruff, mypy, pruebas, cobertura >= 90 %, build, lockfile y CI verde.
- Confirmar ausencia de archivos prohibidos, medios, bases, secretos y respuestas reales.

## 5. Desviaciones bloqueantes

Marcar `REWORK_REQUIRED` o `FAILED` ante aceptación de cualquier negativo, deriva positiva frente a
`ce3c067`, pérdida de la regresión no finita, sustitución silenciosa por cero/`None`, captura
amplia, cookies, autenticación, otro extractor, acceso a X, repetición del smoke, medios, comandos
B04/B05, infraestructura fuera de alcance, tests CI con red, cambios funcionales B02/esquema/
lockfile, merge, force-push, tag, release o B04.

## 6. Dictamen

Emitir exactamente uno:

- `BLOCKED`: RW-01/R-05/RW-02 cerrados y solo permanece el bloqueo público `AuthRequired`.
- `VALIDATED_WITH_OBSERVATIONS`: únicamente con un gate humano nuevo que redefina el criterio.
- `REWORK_REQUIRED`: persiste una carencia recuperable.
- `FAILED`: desviación material o incumplimiento irrecuperable.

Entregar el contenido completo de
`XMA-CLI-001_AUD-0003_B03-REWORK-004_v0.1.4.md` listo para versionarse, con matriz, evidencia,
riesgos, rollback y próxima acción. No modificar GitHub, aprobar el PR, fusionar ni autorizar B04.
