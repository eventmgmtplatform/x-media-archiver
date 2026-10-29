# XMA-CLI-001-DOT-PRM-0006 — B03 Rework Audit 003

**Versión:** 0.1.0

**Estado:** ACTIVE AFTER CODEX HANDOFF

**Ejecutor:** dot

**Supervisión humana:** Leonel Galindo

## 1. Objetivo

Auditar una sola ejecución de `XMA-CLI-001-PRM-0006 v0.1.0` sobre PR #3. Determinar si la
duración negativa pequeña se rechaza antes de perder su signo, si RW-01/R-05 queda cerrado sin
degradaciones y si el único impedimento restante es `AuthRequired`.

## 2. Fuente de verdad

1. GitHub: PR, commits, trees, diff, comentarios y revisiones.
2. CI del HEAD final.
3. AUD-0003 v0.1.2, PRM-0006, HND-0003 v0.1.3 y documentación versionada.
4. Código y pruebas. La conversación no sustituye evidencia canónica.

Fijar SHA y tree antes de auditar. Confirmar PR abierto/draft/sin merge y que CI corresponde al
mismo contenido. Si el HEAD cambia durante la auditoría, detenerse como `BLOCKED`.

## 3. Allowlist

- Validación de duración negativa antes de conversión o redondeo.
- Manejo exacto o equivalente de cadenas cuyo signo puede perderse por subdesbordamiento.
- Regresiones offline de mapper y frontera CLI.
- HND-0003 v0.1.3 y documentación mínima.
- Ajustes mecánicos de formato/tipos derivados directamente.

## 4. Verificaciones

- Comparar baseline `ce3c067542827f702caa4bfd89fc9bd9ac4905b1`, baseline gobernada y HEAD
  final; inventariar todos los commits y archivos.
- Reproducir offline con mapper real: `-0.0001`, `-0.0005`, `-5e-324`, `"-0.0001"` y
  `"-1e-400"`. Todos deben producir `DiscoveryContractError` constante.
- Confirmar que el rechazo ocurre antes de una conversión que oculte el signo.
- Verificar cero, positivos submilisegundo y positivos válidos según la política documentada.
- Ejecutar una frontera CLI realista mediante runner offline/proveedor/mapper/servicio para
  `inspect` y `sync`: código 5, sin traceback/dato crudo y sin directorio/SQLite.
- Confirmar que ninguna duración negativa se persiste como cero.
- Verificar que no se degradaron no finitos, booleanos, rangos SQLite, JSON, límites, cursor,
  variantes rotadas, metadata-only ni los controles R-01 a R-07.
- Confirmar suite offline, Ruff, mypy, pruebas, cobertura >= 90 %, build, lockfile y CI verde.
- Confirmar ausencia de archivos prohibidos, medios, bases, secretos y respuestas reales.

## 5. Desviaciones bloqueantes

Marcar `REWORK_REQUIRED` o `FAILED` ante aceptación de cualquier duración negativa, sustitución
silenciosa por cero/`None`, captura amplia, cookies, autenticación, otro extractor, acceso a X,
repetición del smoke, medios, comandos B04/B05, infraestructura fuera de alcance, tests CI con red,
cambios funcionales B02/esquema/lockfile, merge, force-push, tag, release o B04.

## 6. Dictamen

Emitir exactamente uno:

- `BLOCKED`: RW-01/R-05 cerrado y solo permanece el bloqueo público `AuthRequired`.
- `VALIDATED_WITH_OBSERVATIONS`: únicamente con un gate humano nuevo que redefina el criterio.
- `REWORK_REQUIRED`: persiste una carencia recuperable.
- `FAILED`: desviación material o incumplimiento irrecuperable.

Entregar el contenido completo de
`XMA-CLI-001_AUD-0003_B03-REWORK-003_v0.1.3.md` listo para versionarse, con matriz, evidencia,
riesgos, rollback y próxima acción. No modificar GitHub, aprobar el PR, fusionar ni autorizar B04.
