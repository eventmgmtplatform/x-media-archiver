# ADR-0003 — Discovery autenticado mediante sesión local de navegador

**Estado:** ACCEPTED  
**Fecha:** 2026-10-28 (America/Mexico_City)  
**Decisor humano:** Leonel Galindo  
**Alcance:** B03/Q3-Público; no autoriza B04–B07, merge ni descarga.

## Contexto

Q3-Técnico está `VALIDATED_WITH_OBSERVATIONS`, pero el smoke anónimo contra Reuters, AP y
BBCWorld devolvió `AuthRequired`. Q3-Público continúa `BLOCKED` porque no se han catalogado
exactamente dos activos públicos de video distintos con `--limit 2`.

Leonel confirmó que dispone de una cuenta dedicada, una sesión local de Firefox y visibilidad de
las tres cuentas públicas. Los identificadores de cuenta y perfil, así como la postura de
credenciales, permanecen fuera de Git y se suministran únicamente en el entorno local.

## Decisión

Se autoriza una única extensión acotada de B03 para que `inspect` y `sync` puedan usar de forma
explícita una sesión existente de Firefox. La implementación conserva modo anónimo por defecto y
acepta autenticación solo cuando el operador suministra navegador y perfil mediante opciones CLI.

La app puede solicitar a `gallery-dl` leer cookies directamente del perfil local, pero no puede
copiar, exportar, serializar, imprimir, persistir ni registrar sus valores. No se autoriza
usuario/contraseña, archivos de credenciales dentro del repositorio, API X, otro extractor ni
evasión de controles.

## Contrato de la prueba pública

1. Ejecutar Reuters y usar AP y BBCWorld como fallback, siempre con `--limit 2`.
2. El gate pasa solo si una ejecución cataloga exactamente dos activos públicos de video
   distintos. Cero o uno no pasan.
3. La prueba solo cataloga metadatos; no descarga medios, miniaturas ni sidecars.
4. Repositorio temporal, SQLite y logs permanecen locales y fuera de Git.
5. La evidencia versionada contiene comandos redactados, códigos de salida, conteos y ausencia de
   medios; nunca contiene cookies, tokens, identificadores de autenticación o rutas sensibles.
6. CI continúa offline. El acceso real a X solo ocurre en la ejecución local autorizada.

## Consecuencias

- PR #3 permanece draft y sin merge.
- Q3-Público y B03 continúan `BLOCKED` hasta handoff, CI y auditoría.
- B04, descargas, otros extractores, tags, releases y certificación siguen sin autorización.
- PRM-0009 gobierna una ejecución de Codex; DOT-PRM-0011 gobierna la auditoría posterior.

## Rollback

Revertir la implementación mediante un nuevo commit autorizado y volver al modo anónimo. El
operador puede cerrar la sesión o invalidarla desde Firefox. No borrar auditorías ni reescribir
historia.
