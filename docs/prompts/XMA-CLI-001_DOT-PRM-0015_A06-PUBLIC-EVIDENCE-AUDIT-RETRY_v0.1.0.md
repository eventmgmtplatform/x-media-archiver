# XMA-CLI-001 — DOT-PRM-0015 A06-PUBLIC-EVIDENCE-AUDIT-RETRY v0.1.0

**Estado:** APPROVED FOR ONE READ-ONLY EXECUTION  
**Decisor humano:** Leonel Galindo  
**Fecha:** 2026-10-28 (America/Mexico_City)  
**Salida esperada:** AUD-0006 A-06-PUBLIC-EVIDENCE v0.1.1

## Objetivo

Reauditar A-06 después del bloqueo documental AUD-0006 v0.1.0. Verificar el paquete exacto adjunto sin repetir el smoke, sin acceder a X, Firefox o cookies y sin modificar GitHub.

## Fuente canónica

- Repositorio: `eventmgmtplatform/x-media-archiver`
- PR: #3
- Rama: `feature/xma-b03-discovery`
- HEAD funcional: `7adb2f670ef20deff8b70aec0fad0037762ebb8b`
- Tree funcional: `128c7cf7b8466848516e3b4223be4b40c73397d5`
- Baseline de ejecución: `f434944b5531291249718afb502618d14d81e21b`
- Tree baseline: `e7b2698429fa3e6855350b37c914bf5cc6187a1d`
- Handoff: HND-0003 v0.3.0
- CI: #38 / run `40819317628`, SUCCESS, 214 pruebas, 94.74 %
- Auditoría previa: AUD-0006 v0.1.0, `BLOCKED / EVIDENCE_NOT_AVAILABLE`

## Adjuntos obligatorios

La conversación auditora debe contener exactamente:

1. un catálogo `.sqlite3`;
2. un manifest sanitizado `.json`.

Hashes esperados:

- catálogo: `61f0d43c72a4b2967c109c11c82ddc1811a7a7781a9d81468546eb7fd10523d7`;
- manifest: `f4d2e1e8749cbcb45c25847f68392f08cfc7573564874786c3c277e91e5ae1b9`.

Si falta un archivo, existe más de un candidato inequívoco, un hash no coincide o el paquete no puede inspeccionarse con seguridad, detenerse con `BLOCKED / EVIDENCE_NOT_AVAILABLE`.

## Controles

### 1. Integridad

- Calcular SHA-256 de ambos adjuntos.
- Abrir una copia de trabajo únicamente en modo lectura.
- Ejecutar `PRAGMA integrity_check`.
- Confirmar esquema de aplicación versión 1.
- No modificar los archivos originales.
- No publicar el paquete en GitHub, CI o comentarios.

### 2. Evidencia funcional A-06

Confirmar desde SQLite y manifest:

- target Reuters;
- código de salida declarado 0;
- exactamente dos activos;
- exactamente dos identidades `post_id:media_index` distintas;
- ambos de tipo `VIDEO`;
- `protected=false`;
- metadata-only;
- sin medios, thumbnails, sidecars, staging ni hashes de medios;
- paquete limitado a `.sqlite3` y `.json`;
- secuencia detenida después de Reuters;
- AP y BBCWorld no ejecutados;
- sin retry ni `inspect` adicional.

Contrastar los hashes sanitizados de identidades entre catálogo, manifest y HND-0003 v0.3.0 sin reproducir identificadores completos innecesarios.

### 3. Privacidad

Verificar que el esquema, los valores y el manifest no contengan:

- valores de cookies;
- valores de `auth_token` o `ct0`;
- contraseñas, tokens o headers;
- correo, teléfono, 2FA o códigos de recuperación;
- URLs firmadas o query strings sensibles;
- nombre concreto de perfil Firefox;
- rutas personales o usuario local;
- `cookies.txt`;
- contenido multimedia.

Ante un secreto potencial: no reproducirlo, emitir `POTENTIAL_SECRET` y detenerse.

### 4. GitHub y CI

Verificar read-only:

- PR #3 abierto, draft y sin merge;
- HEAD/tree funcionales coincidentes;
- HND-0003 v0.3.0 presente;
- diff A-06 limitado a README, Gate Register, Implementation Plan y HND;
- CI #38 verde sobre el tree correspondiente;
- SQLite, manifest y paquete no rastreados;
- sin cambio funcional de código, esquema, dependencias o `uv.lock`;
- sin tag, release, certificación ni inicio de B04/B05.

Los commits posteriores exclusivamente de gobernanza no alteran el snapshot funcional; deben identificarse por separado.

## Dictamen

Producir AUD-0006 v0.1.1 con matriz, evidencia, limitaciones, riesgos residuales y rollback. Dictamen único:

- `VALIDATED_WITH_OBSERVATIONS`;
- `REWORK_REQUIRED`;
- `BLOCKED`;
- `FAILED`.

`VALIDATED_WITH_OBSERVATIONS` solo es admisible si los hashes coinciden, la integridad es `ok`, existen exactamente dos activos distintos, toda la evidencia es metadata-only y no aparecen secretos ni desviaciones.

La auditoría no aprueba por sí sola A-06, Q3-Público, B03, merge o B04. Solo Leonel decide esas transiciones.

## Restricciones

- Read-only.
- No repetir el smoke.
- No acceder a X, Firefox, perfiles o cookies.
- No modificar GitHub, ramas, PR, comentarios, revisiones, estados ni adjuntos.
- No hacer merge.
- No autorizar B04/B05.
- No subir SQLite o manifest a GitHub/CI.
