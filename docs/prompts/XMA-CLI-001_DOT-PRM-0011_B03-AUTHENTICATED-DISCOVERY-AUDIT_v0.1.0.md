# XMA-CLI-001-DOT-PRM-0011 — Auditoría B03 Authenticated Discovery

**Versión:** 0.1.0  
**Estado:** APPROVED AFTER HND-0003 v0.2.0 AND GREEN CI  
**Ejecutor:** dot  
**Supervisión humana:** Leonel Galindo

## 1. Objetivo

Auditar una vez PRM-0009. Determinar si la autenticación local es mínima, no expone secretos,
conserva B03 y acredita exactamente dos activos públicos de video con `--limit 2`.

Dot no repite el smoke, no accede al navegador, no lee cookies y no modifica GitHub.

## 2. Snapshot

Fijar HEAD/tree posteriores a HND-0003 v0.2.0 y CI verde. Confirmar descendencia lineal desde
`946ebd11503e3b06f623e22b3aabe43c6e193a76` y comparar el diff. Si HEAD cambia, detenerse como `BLOCKED`.

## 3. Allowlist

- DTO/configuración de autenticación en infraestructura;
- adaptación mínima de `gallery-dl`;
- opciones de `inspect` y `sync` para Firefox/profile;
- fixtures y pruebas offline;
- HND, README, CHANGELOG, Gate Register, Plan y cuerpo del PR;
- una prueba local Reuters → AP → BBCWorld con `--limit 2`.

## 4. Verificaciones

1. Modo anónimo por defecto y parámetros explícitos obligatorios en conjunto.
2. Solo Firefox; sin rutas arbitrarias a cookies.
3. Ningún secreto o identificador local aparece en Git, CI, JSON, SQLite, errores o HND.
4. `gallery-dl` sigue sin descarga, con caché en memoria y sin configuración global.
5. CI y pruebas offline, cobertura mínima 90 %, lint, tipos y build verdes.
6. Evidencia pública con salida 0, límite 2 y exactamente dos activos distintos catalogados.
7. Cero medios, thumbnails, sidecars, staging o hashes.
8. Sin API X, otro extractor, B04/B05, GUI, servidor, ORM, Redis o Docker.
9. PR abierto/draft/sin merge; main, tags y releases sin ampliación.

## 5. Dictamen

- `VALIDATED_WITH_OBSERVATIONS`: controles pasan y se acreditan exactamente dos activos.
- `REWORK_REQUIRED`: defecto recuperable.
- `BLOCKED`: falta HND/CI/evidencia o no se obtienen exactamente dos activos.
- `FAILED`: secreto expuesto, descarga, otro extractor, merge o inicio B04.

## 6. Entrega

Entregar `XMA-CLI-001_AUD-0005_B03-AUTHENTICATED-DISCOVERY_v0.1.0.md` con snapshot, matriz,
evidencia, límites, riesgos y rollback. No modificar GitHub ni autorizar B04.
