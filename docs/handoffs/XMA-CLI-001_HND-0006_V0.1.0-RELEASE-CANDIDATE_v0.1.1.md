# XMA-CLI-001 — HND-0006 v0.1.1 RC compliance and operability

**Fecha:** 2026-10-29

**Estado:** `V0.1.0_RC_READY / WAITING_CHAT_VALIDATION`

**Autoridad:** `XMA-CLI-001-PRM-0033 V0.1.0 RC COMPLIANCE AND OPERABILITY REWORK`

## Baseline y alcance

- Rama: `release/v0.1.0`; PR #6 abierto y draft.
- Baseline: `af3dccc5d2cf743aeb920a08892ac0055848770e`; tree
  `420f26de4dea2d89af8bde5564ae32869232f76c`.
- `uv.lock` de baseline: SHA-256
  `740808fbc25aef0dd6996c8fc6744ae80c17970fd020a18dc5b3a4f6d4cadf16`.
- El SHA/tree del último commit y los enlaces de CI se reconcilian en el cuerpo del PR después de la
  última escritura Git, evitando un ciclo de commits autorreferencial.

El rework se limitó a licencia, empaquetado, documentación operativa, trazabilidad y controles de
distribución. No cambió `src/`, tests funcionales, esquema SQLite, dependencias de producción,
`uv.lock`, workflows de comportamiento, autenticación o descarga.

## Licencia y corresponding source

`LICENSE` contiene el texto canónico completo GPL-2.0-only y la metadata conserva el identificador
SPDX `GPL-2.0-only`. La validación compara byte a byte la licencia del wheel y sdist contra la copia
raíz, y comprueba título/fin del texto dentro del bundle.

El build obtiene `gallery_dl-1.32.18.tar.gz` desde el asset oficial de PyPI y exige SHA-256
`1c5562af3799a0bec96be0f64d95a416aee688fd09fe3893ca3a6c87bbe65bcd`. El archivo se distribuye,
figura en manifest/checksums y no se rastrea en Git. THIRD_PARTY_NOTICES y release notes describen
esa entrega de corresponding source.

## Bundle autocontenido

El tar Linux x86_64 incluye binario, `QUICKSTART.md`, `README.md`, `LICENSE`,
`THIRD_PARTY_NOTICES.md` y los runbooks BAU/locales en `docs/operations/`. QUICKSTART cubre:

- instalación y versión 0.1.0;
- Firefox y selector de nombre contenido;
- download de 1, 2 y 5, SINGLE_POST, archive hasta 10;
- status, reanudación, layout/nombres, límites y errores principales.

La documentación de source usa el tag `v0.1.0`, no la rama temporal, y el wheel se denomina
`x_media_archiver-0.1.0-py3-none-any.whl`.

## Manifest y checksums

`RELEASE-MANIFEST.json` se genera como `xma-release-manifest-v1` e incluye versión, source SHA/tree,
hash de `uv.lock`, Python/plataforma de build, layout/formato del bundle y nombre/tamaño/SHA-256 de
cada payload. El manifest no se lista a sí mismo. `SHA256SUMS` incluye el manifest y todos los assets
distribuidos salvo el propio archivo de checksums, evitando autorreferencia.

La validación recalcula inventario, tamaños y hashes; exige que `source_sha` coincida con
`GITHUB_SHA`; valida el source gallery-dl; extrae el bundle sin Python/uv; y comprueba documentos y
licencia. Portabilidad se ejecuta en Ubuntu 22.04 y 24.04.

## Validación y seguridad

La matriz obligatoria comprende suite completa con cobertura mínima 90 %, Ruff format/lint, mypy,
build/metadata, pip-audit, inventario de licencias, wheel aislado, bundle sin Python/uv, checksums,
corresponding source y portabilidad 22.04/24.04. Los resultados finales y URLs de runs quedan en el
cuerpo del PR #6, sobre el mismo HEAD definitivo.

`uv.lock` debe permanecer byte-idéntico. El escaneo impide rastrear cookies, secretos, medios,
SQLite, logs o repositorios locales. Los artifacts generados permanecen fuera de Git.

## Riesgo y rollback

Riesgos conservados: Linux x86_64, máximo diez, disponibilidad externa del proveedor y
`RESCAN_DEDUP_V1` ineficiente a escala. Rollback: revertir el commit documental/empaquetado de
PRM-0033 o cerrar PR #6; nunca reescribir historia o tags.

No hubo acceso a X, Firefox/cookies, nuevas descargas, merge, tag, GitHub Release ni PyPI. PR #6
permanece draft y requiere validación humana.
