# XMA-CLI-001-DOT-PRM-0005 — B03 Rework Audit 002

**Versión:** 0.1.0

**Estado:** ACTIVE AFTER CODEX HANDOFF

**Ejecutor:** dot

**Supervisión humana:** Leonel Galindo

## 1. Objetivo

Auditar una sola ejecución de `XMA-CLI-001-PRM-0005 v0.1.0` sobre PR #3. Determinar si
`RW-01 / R-05` quedó cerrado sin ampliar B03, sin degradar los seis controles ya aprobados y si el
único impedimento restante es el `AuthRequired` de la aceptación pública.

## 2. Fuente de verdad y precondición

1. GitHub: commits, trees, PR, diff, comentarios y revisiones.
2. CI sobre el HEAD final entregado por Codex.
3. `AUD-0003 v0.1.1`, `PRM-0005`, handoff/addendum v0.1.2 y documentación versionada.
4. Código, fixtures y pruebas. La conversación y el filesystem original del ejecutor no sustituyen
   evidencia canónica.

Antes de auditar, fijar SHA y tree del HEAD, confirmar PR abierto/draft/sin merge y demostrar que CI
corresponde al mismo contenido. Si el HEAD se mueve durante la auditoría, detenerse como `BLOCKED`
y no mezclar snapshots.

## 3. Allowlist

- Validación y normalización de `num`, `width`, `height`, `duration`/`duration_ms` en la frontera
  `gallery-dl`.
- Conversión a `DiscoveryContractError`, código CLI 5 y salida sanitizada.
- Pruebas offline de mapper/CLI y regresiones estrictamente relacionadas.
- `HND-0003 v0.1.2` y documentación mínima de estado.
- Ajustes mecánicos de formato/tipos requeridos por esos cambios.

Todo archivo modificado fuera de esta lista requiere justificación directa y mínima.

## 4. Desviaciones bloqueantes

Marcar `REWORK_REQUIRED` o `FAILED` ante cookies, autenticación, secretos, otro extractor, acceso
live a X, repetición del smoke, medios, thumbnails, sidecars, staging, hashes nuevos de medios,
comandos B04/B05, GUI, API, servidor, ORM, Redis, Docker, tests CI con red, migración o borrado de
catálogos, cambios funcionales B02, evidencias locales rastreadas, cambio directo en `main`,
force-push, merge, tag, release o inicio de B04.

## 5. Verificaciones obligatorias

### 5.1 Identidad y diff

- Comparar baseline funcional `0186129e06201b644a4d383d621740f291d1244d`, baseline gobernada y
  HEAD final.
- Inventariar todos los commits y archivos. Confirmar diff mínimo y ausencia de cambios a
  `uv.lock`, workflow, esquema SQLite y B02, salvo justificación gobernada explícita.

### 5.2 Cierre RW-01 / R-05

- Confirmar validación previa a conversión de valores no finitos y fuera de la representación
  admitida.
- Verificar `num`, `width`, `height` y `duration`; booleanos no deben aceptarse como números.
- Confirmar invariantes de índice, no negatividad y representación compatible con persistencia.
- No aceptar saturación, sustitución por cero/`None` ni truncamiento nuevo silencioso.
- `NaN`, `+inf`, `-inf` y un caso como JSON `1e400` deben terminar como
  `DiscoveryContractError`, nunca como `OverflowError` sin normalizar.
- CLI debe devolver 5, sin traceback, payload, valor crudo ni marcador sensible; no debe crear
  catálogo ante el fallo.
- Revisar que la captura sea deliberada y no incluya `BaseException` o un `Exception` amplio que
  oculte defectos ajenos.

### 5.3 Pruebas independientes y regresiones

- Inspeccionar y, cuando el entorno lo permita, reproducir con datos sintéticos offline el caso
  original y sus variantes. No acceder a X.
- Verificar que las pruebas ejercen el mapper real y una frontera CLI representativa, no solo un
  doble que arroja directamente la excepción final.
- Confirmar que valores finitos válidos siguen funcionando y que R-01, R-02, R-03, R-04, R-06 y
  R-07 no fueron degradados por el nuevo diff.
- Confirmar que el smoke no fue repetido y que `AuthRequired` continúa separado del defecto interno.

### 5.4 Quality gates

- Suite automatizada completamente offline.
- Ruff, mypy, pruebas, cobertura >= 90 %, build y lockfile PASS.
- CI final verde sobre el tree auditado.
- Sin archivos prohibidos, secretos, medios, bases ni respuestas reales en el tree.
- Handoff con comandos, resultados, commit/tree, CI, limitaciones y rollback honestos.

## 6. Dictamen

Emitir exactamente uno:

- `BLOCKED`: `RW-01 / R-05` cerrado, controles previos no degradados y solo permanece el bloqueo
  público externo `AuthRequired`.
- `VALIDATED_WITH_OBSERVATIONS`: únicamente si existe un nuevo gate humano versionado que redefine
  el criterio público; este prompt no lo concede.
- `REWORK_REQUIRED`: persiste una carencia recuperable.
- `FAILED`: desviación material o incumplimiento irrecuperable.

Entregar el contenido completo de
`XMA-CLI-001_AUD-0003_B03-REWORK-002_v0.1.2.md` listo para versionarse, con matriz de controles,
evidencia, riesgos, rollback y próxima acción. No modificar GitHub, aprobar el PR, fusionar ni
autorizar B04.
