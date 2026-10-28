# XMA-CLI-001-DOT-PRM-0004 — B03 Rework Audit

**Versión:** 0.1.0

**Estado:** ACTIVE AFTER CODEX HANDOFF

**Ejecutor:** dot

**Supervisión humana:** Leonel Galindo

## 1. Objetivo

Auditar una sola ejecución de `XMA-CLI-001-PRM-0004 v0.1.0` sobre PR #3. Determinar si R-01 a
R-07 quedaron cerrados sin ampliar B03 y si el único impedimento restante es `AuthRequired`.

## 2. Fuente de verdad

1. GitHub: commits, trees, PR, diff, comentarios y revisiones.
2. CI sobre el HEAD final.
3. AUD-0003 v0.1.0, PRM-0004, handoff/addendum del rework y documentación versionada.
4. Código, fixtures y pruebas. La conversación no sustituye evidencia canónica.

## 3. Allowlist

- Correcciones de JSON, errores, idempotencia, límite y cursor de B03.
- Evidencia sanitizada y documentación del smoke anónimo.
- Conciliación documental del rework B02, sin integración indiscriminada.
- `gallery-dl` como único extractor, en modo sin descarga.
- `inspect`, `sync`, catálogo SQLite B02, fixtures y tests offline.

## 4. Desviaciones bloqueantes

Marcar `REWORK_REQUIRED` o `FAILED` ante cookies, autenticación, secretos, otro extractor, medios,
thumbnails, sidecars, staging, hashes de medios nuevos, comandos B04/B05, GUI, API, servidor, ORM,
Redis, Docker, tests CI con red, evidencias locales rastreadas, cambio directo en `main`, merge,
tag, release, force-push o inicio de B04.

## 5. Verificaciones R-01 a R-07

### R-01

- Comandos, timestamps, orden y fallback trazables.
- Conteos o N/A justificado por fallo previo a persistencia.
- Ausencia de medios y evidencia sanitizada; no aceptar datos inventados.
- Rollback integral y métricas honestas.

### R-02

- README, CHANGELOG, Gate Register, plan y cuerpo del PR coherentes con el estado final.
- Si el cuerpo del PR no pudo actualizarse, verificar que la limitación y el texto propuesto estén
  versionados y no se declare resuelto.

### R-03

- AUD-0002 v0.1.2 y su rework aparecen conciliados sin afirmar integración inexistente.
- Cualquier código B02 incorporado tiene justificación directa, diff mínimo y pruebas B03.

### R-04

- JSON no pasa por Rich ni otra presentación con markup/wrapping.
- `json.loads` pasa para markup, Unicode y cadenas largas.

### R-05

- Not-found, restricted, rate limit, contrato y transient están normalizados.
- Errores esperables de catálogo/filesystem no muestran traceback por defecto.
- Códigos de salida y pruebas coinciden con README.

### R-06

- Variantes efímeras están sanitizadas o actualizadas por política explícita.
- Dos sync con variante rotada no crean duplicado ni conflicto.
- No se imprimen URLs firmadas.

### R-07

- La aplicación rechaza o limita defensivamente resultados que exceden el límite.
- Existe prueba de proveedor defectuoso y documentación de `cursor=None`.

## 6. Quality gates

- Suite automatizada completamente offline.
- Ruff, mypy, pruebas, cobertura >= 90 %, build y lockfile PASS.
- CI final verde sobre el contenido auditado.
- Sin archivos prohibidos, secretos ni medios en el tree.

## 7. Dictamen

Emitir exactamente uno:

- `BLOCKED`: R-01 a R-07 cerrados y únicamente permanece `AuthRequired` externo.
- `VALIDATED_WITH_OBSERVATIONS`: solo si se cumple el criterio público o un gate humano lo redefine
  mediante un prompt versionado; no inferir esa autorización.
- `REWORK_REQUIRED`: existe una carencia recuperable.
- `FAILED`: desviación material o incumplimiento irrecuperable.

Entregar el contenido completo de `XMA-CLI-001_AUD-0003_B03-REWORK-001_v0.1.1.md` listo para
versionarse. No modificar GitHub, no aprobar el PR, no fusionar y no autorizar B04.
