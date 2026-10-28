# ADR-0002 — Separación de Q3-Técnico y Q3-Público

**Estado:** ACCEPTED  
**Fecha:** 2026-10-28 (America/Mexico_City)  
**Decisor humano:** Leonel Galindo  
**Alcance:** B03 Discovery; no modifica B04–B07.

## Contexto

PRM-0003 exige dos clases de evidencia para cerrar B03:

1. implementación, contratos, persistencia, CLI, pruebas offline y CI;
2. una prueba pública anónima que catalogue hasta dos activos de video de Reuters, AP o BBCWorld.

AUD-0003 v0.1.5 determinó `BLOCKED`: los reworks técnicos pasan, CI #26 está verde con 156
pruebas y 95.18 % de cobertura, pero el smoke histórico terminó en `AuthRequired` para las tres
cuentas y no acreditó dos activos catalogados. Repetir rework de código no resolvería por sí solo
esa restricción externa.

## Decisión

Q3 se separa en dos subgates acumulativos:

- **Q3-Técnico:** valida la implementación B03, sus contratos, pruebas offline, seguridad de
  alcance y CI. Queda `VALIDATED_WITH_OBSERVATIONS` sobre el snapshot auditado
  `beb2a7d9123b23f51f6f3a92571501cb25a025d6`, tree
  `f1b2207b0db65d92e7d7ba877a3444389b7b3010`, conforme a AUD-0003 v0.1.5.
- **Q3-Público:** valida el comportamiento real anónimo y debe acreditar hasta dos activos de
  video catalogados, sin medios descargados. Permanece `BLOCKED` por `AuthRequired`.

Ambos subgates pertenecen a Q3. La validación técnica no sustituye la aceptación pública y no
certifica el producto. Q3-Público es condición previa de cualquier transición a B04, salvo que una
decisión humana posterior, explícita y versionada cambie el requisito o autorice una estrategia de
acceso distinta.

## Restricciones preservadas

Esta decisión no autoriza:

- merge de PR #3;
- B04 ni comandos o componentes B04/B05;
- cookies, login, tokens, sesiones autenticadas o secretos;
- otro extractor, API o mecanismo alternativo de acceso;
- repetición del smoke sin prompt y autorización específicos;
- descarga de medios, tags, releases o certificación.

PR #3 permanece draft. B04 y el objetivo de descarga continúan bloqueados.

## Consecuencias

Positivas:

- se evita reabrir código técnicamente conforme para compensar un bloqueo externo;
- se conserva evidencia diferenciada entre calidad interna y aceptación real;
- el siguiente problema se trata como decisión de producto/acceso, no como defecto inexistente.

Costos y riesgos:

- B03 no está funcionalmente aceptado de extremo a extremo;
- el proyecto no puede avanzar a descarga mientras Q3-Público permanezca bloqueado;
- resolver el acceso podría requerir una nueva ADR, análisis de seguridad y autorización humana.

## Evidencia

- PR #3, HEAD técnico auditado `beb2a7d`, tree `f1b2207`.
- HND-0003 v0.1.5.
- AUD-0003 v0.1.5, dictamen `BLOCKED`.
- CI #26 / run `40774501390`: 156 pruebas, 95.18 %.
- Smoke histórico Reuters → AP → BBCWorld: `AuthRequired`, sin activos catalogados.

## Reversión

Revertir únicamente los documentos de esta decisión mediante un nuevo commit autorizado. No
reescribir historia, borrar auditorías, modificar catálogos ni reinterpretar AUD-0003 v0.1.5.
