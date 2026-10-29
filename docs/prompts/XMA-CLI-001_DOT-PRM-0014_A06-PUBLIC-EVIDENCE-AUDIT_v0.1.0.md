# XMA-CLI-001 — DOT-PRM-0014 A-06 Public Evidence Audit

**Versión:** 0.1.0
**Estado:** PREPARED / DO NOT RUN BEFORE HND-0003 v0.3.0
**Modo:** read-only
**Auditoría esperada:** AUD-0006 A-06-PUBLIC-EVIDENCE v0.1.0

## 1. Inicio permitido

Ejecutar una sola vez únicamente después de que:

- PRM-0012 haya sido liberado explícitamente por Leonel;
- Codex publique HND-0003 v0.3.0;
- CI esté verde sobre el mismo tree;
- Leonel adjunte a dot el paquete local exacto y sus hashes.

Si falta el catálogo/paquete, el hash no coincide o no puede abrirse con seguridad, dictaminar
BLOCKED / EVIDENCE_NOT_AVAILABLE. No repetir el smoke ni acceder a X, Firefox o cookies.

## 2. Verificación canónica

Confirmar en GitHub:

- PR #3 abierto, draft y sin merge;
- rama y HEAD/tree declarados;
- descendencia desde la baseline gobernada;
- AUD-0005 v0.1.2, PRM-0012, DOT-PRM-0014 y HND v0.3.0 presentes;
- CI verde sobre tree idéntico;
- diff limitado a documentación/handoff/evidencia sanitizada permitida, sin B04.

## 3. Auditoría del paquete local

Trabajar sobre una copia read-only del paquete adjunto. Verificar:

1. SHA-256 de catálogo y manifest contra HND.
2. PRAGMA integrity_check igual a ok.
3. esquema esperado y ausencia de tablas/columnas de cookies o secretos.
4. exactamente dos filas de activos de video aceptados y exactamente dos identidades
   post_id:media_index distintas.
5. target permitido, protected=false y marcador metadata-only.
6. hashes de identidad distintos y reproducibles desde el catálogo.
7. ausencia de URLs firmadas/query strings, cookies, headers, tokens, nombres/rutas locales,
   correo, teléfono, contraseña o 2FA.
8. lista de archivos sin medios, thumbnails, sidecars, cookies.sqlite o cookies.txt.
9. secuencia Reuters → AP → BBCWorld, --limit 2, sin retry y detención al primer resultado válido.
10. consistencia entre catálogo, manifest, HND, PR y CI.

No publicar valores sensibles ni rutas observadas. Si aparece un secreto, detener la reproducción,
no citarlo y emitir FAILED/BLOCKED sanitizado.

## 4. Matriz de decisión

- VALIDATED_WITH_OBSERVATIONS: integridad, hashes, conteos y dos activos públicos distintos se
  verifican; limitaciones quedan documentadas.
- REWORK_REQUIRED: evidencia recuperable pero inconsistente, incompleta o con defecto corregible.
- BLOCKED: 0/1 activos, paquete ausente, hash distinto, evidencia no verificable o precondición
  incumplida.
- FAILED: secreto expuesto, acción prohibida, manipulación o desviación material.

El dictamen técnico no autoriza merge ni B04. Solo Leonel puede decidir Q3-Público y B03.

## 5. Prohibiciones del auditor

No modificar GitHub, rama, PR, comentarios, estados, archivos ni paquetes originales. No ejecutar
xma contra X, no abrir Firefox/perfiles reales, no leer cookies, no descargar medios, no hacer
merge, tag, release ni iniciar B04/B05.

## 6. Entrega

Producir AUD-0006 A-06-PUBLIC-EVIDENCE v0.1.0 con identidad Git/tree/CI, matriz de evidencias,
consultas read-only, hashes, conteos, hallazgos, límites, riesgos y rollback. Entregarlo a Leonel
para decisión humana y eventual versionado; no publicarlo por cuenta propia.
