# XMA-CLI-001 — DOT-PRM-0013 B03 Auth Boundary Rework 002 Audit

**Versión:** 0.1.0  
**Fecha:** 2026-10-28  
**Estado:** APPROVED AFTER HND-0003 v0.2.2 AND GREEN CI  
**Autoridad humana:** Leonel  
**Auditor:** dot  
**Origen:** AUD-0005 v0.1.1 y PRM-0011 v0.1.0  
**PR:** #3

## 1. Activación

Ejecutar una sola vez únicamente después de que Codex publique un SHA/tree estable, HND-0003 v0.2.2 y CI verde sobre el mismo tree. Si falta cualquiera, devolver `BLOCKED` sin completar la auditoría.

## 2. Mandato

Auditar en modo read-only R-01, R-02 y R-03, junto con la regresión obligatoria. GitHub y CI son evidencia canónica. Distinguir evidencia reproducida por dot de declaraciones del handoff.

No acceder a X, Firefox, perfiles o cookies reales, base de cookies, SQLite original ni filesystem original. No repetir smoke, no reconstruir A-06 y no modificar GitHub.

## 3. Identidad y alcance

Antes de ejecutar reproducciones:

- confirmar SHA, tree, rama, base, HND y tree probado por CI;
- confirmar que el rework desciende del commit de gobernanza que contiene AUD-0005 v0.1.1, PRM-0011 y DOT-PRM-0013;
- revisar commits, diff, archivos, PR, comentarios, revisiones, tags y releases;
- confirmar alcance exclusivo B03/rework/gobierno;
- detenerse con `BLOCKED` si HEAD cambia durante la auditoría.

## 4. Controles independientes

### R-01 — Fail-closed de sesión

Con fixtures exclusivamente sintéticos y offline, probar al menos:

- diccionario vacío;
- solo `ct0`;
- solo `auth_token`;
- cualquiera presente pero vacío;
- ambos valores sintéticos no vacíos;
- error del lector;
- modo anónimo.

Para todos los casos incompletos confirmar:

- error público constante y sanitizado;
- ausencia de valores y marcadores en stdout, stderr, logs, JSON y SQLite;
- no creación/ejecución del job gallery-dl;
- ausencia de continuación guest/anónima cuando se solicitó auth;
- ausencia de UoW, catálogo y persistencia.

El caso sintético suficiente solo valida la frontera local; no debe realizar red ni afirmar validez de una sesión real.

### R-02 — Symlink circular

Crear únicamente un filesystem sintético. Comprobar que el bucle de symlink:

- termina mediante el contrato XMA sanitizado;
- no propaga `RuntimeError`, traceback ni marcador de ruta;
- cubre lector, adaptador, `inspect` y `sync`;
- no crea job, UoW o catálogo;
- conserva rechazo de traversal, escapes y selección fuera de contención.

Revisar que la captura sea estrecha y no sea un `except Exception` general.

### R-03 — Documentación

Confirmar consistencia entre README, Gate Register, Implementation Plan, HND v0.2.2 y cuerpo del PR:

- R-01/R-02 entregados y pendientes de esta validación hasta el dictamen;
- A-06 `EVIDENCE_NOT_AVAILABLE`;
- Q3-Público y B03 `BLOCKED`;
- ningún texto afirma cierre, certificación, merge o autorización B04.

### Regresión

Confirmar:

- anónimo predeterminado;
- opciones auth obligatorias en conjunto y Firefox único;
- gallery-dl único/versionado, download off y caché en memoria;
- política pública fail-closed;
- sin copia/exportación/serialización/persistencia de cookies;
- pruebas CI sin acceso funcional a X, navegador o perfiles reales;
- cobertura CI >= 90 %;
- sin medios, bases, cookies ni evidencias locales rastreadas;
- sin B04/B05, merge, tag, release o certificación.

La instalación de dependencias por CI no constituye por sí sola una desviación de pruebas funcionales offline.

## 5. A-06 y gates

A-06 permanece fuera del rework técnico y debe registrarse como `EVIDENCE_NOT_AVAILABLE`, salvo nueva evidencia gobernada por un mandato humano posterior. No aceptar declaraciones históricas como comprobación independiente.

Incluso si R-01–R-03 pasan, Q3-Público y la transición general B03 permanecen `BLOCKED`. Dot no puede resolver ese gate ni autorizar un smoke.

## 6. Resultado

Producir:

`docs/audits/XMA-CLI-001_AUD-0005_B03-AUTH-BOUNDARY-REWORK-002_v0.1.2.md`

El informe debe incluir identidad, matriz R-01–R-03, pruebas independientes, regresión, limitaciones, riesgos, rollback y separación entre estado técnico y Q3-Público.

Dictamen único:

- `VALIDATED_WITH_OBSERVATIONS`;
- `REWORK_REQUIRED`;
- `BLOCKED`;
- `FAILED`.

Dot no modifica código, documentación, ramas, PR, comentarios, revisiones o estados; no aprueba Q3-Público y no autoriza merge, B04, tag, release, certificación o smoke.

