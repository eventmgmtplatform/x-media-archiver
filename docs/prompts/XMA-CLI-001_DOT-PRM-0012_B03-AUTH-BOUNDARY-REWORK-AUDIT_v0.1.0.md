# XMA-CLI-001 — DOT-PRM-0012 B03 Auth Boundary Rework Audit

**Versión:** 0.1.0  
**Fecha:** 2026-10-28  
**Estado:** APPROVED AFTER HND-0003 v0.2.1 AND GREEN CI  
**Autoridad humana:** Leonel  
**Auditor:** dot  
**Origen:** AUD-0005 v0.1.0 y PRM-0010 v0.1.0  
**PR:** #3

## 1. Activación

Ejecutar una sola vez solo después de que Codex publique un SHA/tree estable, HND-0003 v0.2.1 y CI verde sobre el mismo tree. Si falta cualquiera, devolver `BLOCKED`.

## 2. Mandato

Auditar read-only A-01–A-06. GitHub/CI son evidencia canónica. Etiquetar el handoff y la evidencia local como declaraciones cuando dot no pueda reproducirlas sin acceder a datos sensibles.

No acceder a X, Firefox, perfiles reales, cookies, base de cookies, SQLite local ni filesystem original. No repetir smoke.

## 3. Controles

### Identidad
- confirmar SHA, tree, rama, base, diff, archivos y tree de CI;
- inspeccionar commits, PR, comentarios, revisiones, tags y releases;
- verificar alcance exclusivo B03/gobierno.

### A-01
- demostrar por código/pruebas offline que XMA no alcanza el fallback que copia `cookies.sqlite`;
- confirmar ausencia de copia, exportación, serialización y persistencia;
- confirmar minimización a dominios necesarios;
- marcar `REWORK_REQUIRED` si depende de que el fallback normalmente no ocurra.

### A-02
- inyectar excepciones y marcadores sintéticos;
- comprobar ausencia en stdout, stderr, logs, JSON, errores públicos y SQLite;
- comprobar que auth solicitada no degrada silenciosamente a anónimo.

### A-03
- probar `.`, `..`, separadores, absoluta, controles, espacios, vacío, longitud y escapes;
- revisar selección exacta y contenida sin enumerar perfiles reales.

### A-04
- verificar que `protected=True`, ausente, nulo o no booleano falle cerrado y no cree catálogo;
- solo `protected=False` permite continuar.

### A-05
- confirmar `<LOCAL_CACHE_PATH>` en el árbol actual;
- no reproducir la ruta histórica;
- confirmar ausencia de reescritura de historial;
- revisar consistencia de README, HND, Gate Register, plan y PR.

### A-06
Distinguir:
- `VERIFIED_DECLARATION`: HND registra integridad y dos identidades con evidencia existente, sin que dot inspeccione el original;
- `EVIDENCE_NOT_AVAILABLE`: el original no existe o no se vinculó;
- evidencia inventada o nueva ejecución no autorizada: `FAILED`.

No exigir publicar IDs, URLs, rutas, filenames, hashes, timestamps ni datos de sesión. La falta de evidencia mantiene Q3-Público bloqueado aunque A-01–A-05 pasen.

### Regresión
- anónimo predeterminado;
- Firefox único y opciones conjuntas;
- gallery-dl único/versionado, download off y caché en memoria;
- CI offline y cobertura >=90 %;
- sin medios, bases, cookies o evidencias rastreadas;
- sin B04/B05, merge, tag, release o certificación.

## 4. Resultado

Producir:

`docs/audits/XMA-CLI-001_AUD-0005_B03-AUTH-BOUNDARY-REWORK-001_v0.1.1.md`

Dictamen único:
- `VALIDATED_WITH_OBSERVATIONS`;
- `REWORK_REQUIRED`;
- `BLOCKED`;
- `FAILED`.

Separar resultado técnico A-01–A-05, trazabilidad A-06, Q3-Público, riesgos y evidencia reproducida frente a declaraciones.

Dot no modifica GitHub, no ejecuta rework, no aprueba Q3-Público y no autoriza merge o B04.
