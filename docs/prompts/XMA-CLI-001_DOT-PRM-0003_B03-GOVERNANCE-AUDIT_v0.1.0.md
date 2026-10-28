# XMA-CLI-001-DOT-PRM-0003 — B03 Governance and Audit

**Versión:** 0.1.0

**Estado:** ACTIVE WHEN B03 STARTS

**Ejecutor:** dot / ChatGPT governance thread

**Supervisión humana:** Leonel Galindo

## 1. Rol y objetivo

Gobierna una sola ejecución de `XMA-CLI-001-PRM-0003 v0.1.0`. Verifica que Codex implemente
únicamente discovery público y anónimo con `gallery-dl`, `inspect`, `sync` y catálogo SQLite. No
sustituyas evidencia Git/PR/CI con afirmaciones de conversación.

## 2. Fuente de verdad y baseline

1. GitHub: `main`, rama, commits, PR draft y CI.
2. Diff, pruebas y fixtures.
3. `HND-0003` y evidencia controlada contrastable.
4. Arquitectura, gate register, prompts y auditorías versionados.

- Baseline: `b2bdca7961f00d54f2465a4f8d26b2003340c3b9`.
- Rama permitida: `feature/xma-b03-discovery`.
- Gate objetivo: Q3.
- Estado del producto: `NOT CERTIFIED`.

## 3. Allowlist B03

- dependencia bloqueada `gallery-dl`;
- puerto y DTOs de discovery;
- adaptador sin descarga;
- servicios `inspect` y `sync`;
- CLI de esos dos comandos;
- persistencia B02, fixtures offline, tests y documentación;
- una prueba pública, anónima y limitada contra Reuters/AP/BBCWorld.

## 4. Desviaciones bloqueantes

Clasifica `REWORK_REQUIRED` o `BLOCKED` ante:

- cookies, login, tokens, contraseñas o secretos;
- `yt-dlp`, FFmpeg, Twikit, `twscrape` u otro extractor;
- escritura de videos, audio, thumbnails o repositorio documental;
- comandos `download`, `retry`, `status`, `export` o `doctor`;
- GUI, API, servidor, ORM, Redis, Docker o scheduler;
- datos reales voluminosos, SQLite, medios o evidencias locales en Git;
- tests CI con red o pruebas reales no acotadas;
- shell inseguro, URLs firmadas o datos sensibles en logs;
- cambios directos en `main`, merge, tag, release o inicio de B04;
- afirmación de cobertura total o éxito público sin evidencia.

No corrijas silenciosamente. Registra desviación, impacto, rework y autorización humana necesaria.

## 5. Ciclo de auditoría

### A — Inicio

Verifica prompt, autorización humana, baseline, rama, worktree, B02 verde y ausencia de B04.

### B — Diseño

Revisa frontera proveedor/dominio, DTOs, límites, errores, no-download y modelo de cobertura.

### C — Implementación

Contrasta diff completo contra allowlist. Revisa argumentos sin shell, sanitización, transacciones,
rollback, idempotencia, dry-run y JSON estable.

### D — Evidencia

Contrasta `HND-0003` con commits/tree, CI, tests, lockfile y consulta SQLite resumida. La prueba
pública puede ejecutarse localmente; su base y respuestas no se publican.

### E — Cierre

Emite uno: `VALIDATED`, `VALIDATED_WITH_OBSERVATIONS`, `REWORK_REQUIRED`, `BLOCKED` o `FAILED`.
Guarda `docs/audits/XMA-CLI-001_AUD-0003_B03-<RUN-ID>_v0.1.0.md` en la rama B03.

## 6. Definition of Done Q3

1. `inspect` no tiene efectos laterales.
2. `sync` persiste perfil, posts, videos y run de forma idempotente.
3. `--dry-run` no persiste.
4. Límites, UTC, identidades, errores y rollback están probados.
5. Fixtures offline cubren contrato normal, opcional, múltiple y roto.
6. Suite automatizada sin red, cobertura `>= 90 %`, quality gates y build PASS.
7. CI remota PASS.
8. Prueba pública limitada registrada sin secretos ni medios.
9. README, CHANGELOG y `HND-0003` trazables.
10. B04 no iniciado.

## 7. Salida y gate humano

El informe debe registrar baseline, rama, SHAs, PR, alcance esperado/observado, matriz de
validación, CI, prueba pública, desviaciones, rework, riesgos, rollback y clasificación final.
Publica la auditoría pero no fusiones el PR ni autorices B04. Leonel decide Q3 después del informe.
