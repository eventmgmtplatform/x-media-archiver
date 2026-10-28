# XMA-CLI-001 — B02 Rework Plan

**Versión:** 0.1.0

**Registrado:** 2026-10-28T08:33:52.385423Z

**Estado:** IN PROGRESS

## Autorización y límite

Leonel autorizó en la conversación supervisora un rework acotado de B02. Este registro es un
checkpoint contemporáneo del rework; no reconstruye ni atribuye un `START_AUTHORIZED` histórico a
la ejecución original.

Alcance exclusivo:

1. F-01: rechazar la ruta `.`.
2. F-02: permitir la actualización controlada de `DiscoveryRun`.
3. F-03: cerrar determinísticamente la conexión si falla `UnitOfWork.__enter__`.
4. F-04: validar la identidad compuesta de `DownloadJob`.
5. F-06: registrar el instante UTC real de aplicación de migraciones mediante un mecanismo
   testeable.
6. Reforzar la matriz de transiciones con expectativas independientes, sin cambiar la política.

O-05 permanece como observación y no se modifica. No se implementará B03, discovery, acceso a X,
cookies ni motores de descarga.

## Checkpoint contemporáneo

- Worktree: limpio antes de crear este documento.
- Rama: `feature/xma-b02-contracts`.
- HEAD inicial: `87bfb1a3802e7ff44521d6f4e8cdbcbd70420938`.
- Tree inicial: `34f9da352c222a912b936e2778f4e1e8251ae9f1`.
- `origin/main`: `b2bdca7961f00d54f2465a4f8d26b2003340c3b9` (squash de PR #2).
- `main` local: atrasado en `2acb88cb1644facc98f5e64253650a57df579e78`; no se moverá.
- Rama B03 observada: `origin/feature/xma-b03-discovery` en
  `aa6ac3360acb273011a8a5814da39d8ad4a01985`; no se tocará.
- Locks Git ajenos: ninguno observado.
- Procesos Git, pytest, Ruff, mypy o uv ajenos: ninguno observado.
- Diferencia de árbol entre `origin/main` y HEAD: solo la auditoría B02 v0.1.1.
- Ancestría: `merge-base(origin/main, HEAD)` es la baseline original `2acb88c`; el squash de PR #2
  puede inflar el diff triple-dot de un PR nuevo. No se hará rebase, merge ni force-push para
  ocultarlo.

## Plan de ejecución

1. Ejecutar los gates de baseline con dependencias bloqueadas ya instaladas.
2. Añadir primero regresiones independientes para los cinco defectos y la matriz normativa.
3. Aplicar cambios mínimos en dominio y adaptador SQLite.
4. Ejecutar pruebas focalizadas y luego todos los gates de cierre, cobertura total `>= 90 %` y
   validadores/transiciones al `100 %`.
5. Revisar diff, archivos rastreados, secretos, bases y artefactos prohibidos.
6. Publicar commits Conventional Commits y un handoff nuevo, sin sobrescribir evidencia previa.
7. Publicar la rama y abrir un draft PR contra `main` solo si la representación remota del diff es
   viable; en otro caso documentar el bloqueo exacto sin alterar historia.
8. Detenerse en `WAITING_VALIDATION`; no fusionar ni iniciar B03.

## Rollback previsto

Revertir, en orden inverso, los commits nuevos de documentación, pruebas y corrección. No eliminar
ni reescribir prompts, auditorías o handoffs publicados y no modificar `main`.
