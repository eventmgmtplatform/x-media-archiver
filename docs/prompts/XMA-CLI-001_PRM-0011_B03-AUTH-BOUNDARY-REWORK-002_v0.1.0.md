# XMA-CLI-001 — PRM-0011 B03 Auth Boundary Rework 002

**Versión:** 0.1.0  
**Fecha:** 2026-10-28  
**Estado:** APPROVED FOR ONE EXECUTION  
**Autoridad humana:** Leonel  
**Ejecutor:** Codex  
**Origen:** AUD-0005 v0.1.1, dictamen REWORK_REQUIRED  
**Baseline funcional auditada:** `dc11051c08612254175ebbe36d9fa3789274e99f`  
**Tree auditado:** `e4155e3a2b2e2d8fb8abc47a18ff5145a2ac99c8`  
**Rama obligatoria:** `feature/xma-b03-discovery`  
**PR:** #3

## 1. Objetivo

Ejecutar una sola iteración acotada de `B03-AUTH-BOUNDARY-REWORK-002` para corregir F-01 y F-02 de AUD-0005 v0.1.1 y reconciliar O-01, sin repetir el smoke, sin acceder a X, sin ampliar B03 y sin iniciar B04.

Este mandato no intenta cerrar A-06. La evidencia original permanece `EVIDENCE_NOT_AVAILABLE`; Q3-Público y la transición general B03 continuarán `BLOCKED` aun cuando el rework técnico sea correcto.

## 2. Precondición y secuencia

1. Confirmar que la rama parte exactamente del commit de gobernanza que publique AUD-0005 v0.1.1, PRM-0011 y DOT-PRM-0013 sobre la baseline indicada.
2. Leer íntegramente ADR-0003, HND-0003 v0.2.1, AUD-0005 v0.1.1 y este prompt.
3. Ejecutar este prompt una sola vez. Si HEAD cambió antes de iniciar o el árbol no contiene los tres documentos gobernados, detenerse con `BLOCKED`.
4. Implementar únicamente R-01, R-02 y R-03.
5. Ejecutar pruebas exclusivamente offline y la suite completa.
6. Publicar HND-0003 v0.2.2 con SHA, tree y evidencia sanitizada.
7. Esperar CI verde sobre el mismo tree y detenerse en `WAITING_VALIDATION`.
8. No ejecutar DOT-PRM-0013; corresponde a dot después del handoff y CI.

## 3. Alcance obligatorio

### R-01 — Sesión autenticada fail-closed

Cuando el usuario solicita autenticación Firefox, la sesión cargada debe contener las cookies `auth_token` y `ct0`, ambas como valores no vacíos. La comprobación pertenece únicamente a infraestructura y no cambia contratos de dominio ni DTO de salida.

Si falta cualquiera, su valor es vacío o la sesión es insuficiente:

- devolver el error XMA constante y sanitizado ya gobernado;
- no crear ni ejecutar el job de gallery-dl;
- no continuar como guest o anónimo;
- no crear catálogo ni persistir resultados;
- no imprimir, serializar, registrar o exponer nombres adicionales, valores, rutas o excepciones originales.

El modo anónimo explícito o predeterminado debe conservar su comportamiento vigente. No se debe intentar validar una sesión mediante red ni determinar expiración de credenciales reales.

Agregar pruebas sintéticas offline que cubran al menos: diccionario vacío; solo `ct0`; solo `auth_token`; ambos con uno vacío; ambos sintéticos no vacíos; error del lector; modo anónimo. La sesión sintética suficiente solo demuestra la frontera local y no autoriza X.

### R-02 — Resolución de symlink circular sanitizada

Normalizar específicamente el error de resolución producido por un enlace simbólico circular al mismo contrato público sanitizado de discovery.

La captura debe ser estrecha y estar ubicada alrededor de la operación de resolución correspondiente; no introducir un `except Exception` general ni ocultar defectos ajenos.

Agregar pruebas offline con filesystem sintético que demuestren:

- rechazo del bucle de symlink;
- ausencia del marcador de ruta sintético en stdout, stderr, logs y error público;
- `inspect` y `sync` terminan con el código de salida gobernado;
- gallery-dl no se crea o ejecuta;
- `sync` no inicia UoW ni crea/persiste catálogo;
- los controles existentes de contención, traversal y selección exacta no se degradan.

### R-03 — Reconciliación documental

Actualizar exclusivamente la documentación necesaria para distinguir:

- `IMPLEMENTED / WAITING_VALIDATION`: entrega de Codex;
- validación independiente pendiente: R-01 y R-02;
- `EVIDENCE_NOT_AVAILABLE`: A-06;
- `BLOCKED`: Q3-Público y transición general B03.

README, Gate Register, Implementation Plan, HND y cuerpo del PR no deben afirmar que A-01–A-06 están validados o cerrados. No reescribir historial ni reconstruir evidencia.

## 4. Pruebas y controles obligatorios

Todas las pruebas serán offline. Sustituir filesystem, SQLite de cookies, navegador, red y gallery-dl cuando corresponda. No usar perfiles, cookies ni datos reales.

Además de R-01 y R-02, demostrar regresión de:

1. modo anónimo predeterminado;
2. `--auth-browser` y `--auth-profile` obligatorios en conjunto;
3. Firefox como único navegador;
4. selector simple, exacto y contenido;
5. `protected is False` como único estado permitido;
6. download deshabilitado y caché en memoria;
7. ausencia de copia, exportación, serialización y persistencia de cookies;
8. regresión completa B02/B03.

Ejecutar:

- `uv sync --locked --all-groups`;
- Ruff format/check;
- mypy;
- pytest con cobertura mínima de 90 %;
- build de sdist y wheel;
- `git diff --check`;
- comprobación de `uv.lock` byte-idéntico, salvo autorización humana posterior expresa.

CI no puede ejecutar pruebas que accedan a X, navegador o perfiles/cookies reales. La descarga normal de dependencias del job no se interpreta como una prueba funcional con red.

## 5. Entregables

- Cambio mínimo de código para R-01 y R-02.
- Pruebas offline específicas y de regresión.
- Reconciliación documental R-03.
- `docs/handoffs/XMA-CLI-001_HND-0003_B03-20261028-001_v0.2.2.md`.
- Gate Register e Implementation Plan en `REWORK_COMPLETED / WAITING_VALIDATION`, con Q3-Público/B03 aún `BLOCKED`.
- PR #3 reconciliado con SHA, tree, CI, pruebas, cobertura y limitaciones.
- Ninguna evidencia local, SQLite, cookie DB, medio o log sensible rastreado.

## 6. Prohibiciones

No smoke, X, perfiles/cookies reales, cookies.txt, exportación de cookies, username/password, tokens, correo, teléfono, 2FA, API X, yt-dlp, FFmpeg, Twikit, twscrape u otro extractor.

No descarga, thumbnails, sidecars, staging, hashes de medios, comandos B04/B05, GUI, API propia, servidor, ORM, Redis, Docker o scheduler.

No reconstruir A-06, no inventar resultados, no merge, tag, release, certificación, cambio directo en main ni reescritura de historial.

## 7. Salida

- `WAITING_VALIDATION`: nuevo SHA/tree, HND-0003 v0.2.2 y CI verde.
- `BLOCKED`: precondición incumplida o solución compatible no disponible.
- `FAILED`: exposición real, desviación material o control obligatorio incumplido.

Codex no decide Q3-Público, no cierra B03, no autoriza merge/B04 y no ejecuta la auditoría independiente.

