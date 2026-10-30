---
title: Archivo completo B06
---

[Inicio](index.html) · [Producto v1](product.html) · [Archivo completo B06](b06-complete-profile-archive.html) · [Arquitectura](architecture.html) · [Releases](releases.html) · [Gobierno](governance.html) · [Roadmap v2](roadmap.html)

---

# B06 — archivo completo de perfil

B06 está `VALIDATED_WITH_OBSERVATIONS` e incluido en el release candidate v0.2.0. Una ejecución pública única sobre
una cuenta observada produjo 22 videos provider-best y terminó mediante agotamiento tipado del
proveedor. El release candidate aún no está etiquetado ni publicado.

## Operación

```bash
uv run xma archive @HANDLE --all --max-items 30 --batch-size 5 \
  --repository ./repository-HANDLE --quality best \
  --auth-browser firefox --auth-profile PROFILE_NAME

uv run xma archive @HANDLE --all --resume --max-items 50 \
  --repository ./repository-HANDLE --quality best \
  --auth-browser firefox --auth-profile PROFILE_NAME

uv run xma status --repository ./repository-HANDLE --json
```

- `PROVIDER_EXHAUSTED`: cuenta observada completa, run `COMPLETED`, no resumible.
- `SAFETY_CAP_REACHED`: pausa íntegra y resumible; no significa cuenta completa.
- Timeout, error transitorio, worker, catálogo o descarga nunca se interpretan como agotamiento.
- Repetir `archive --all` sobre el mismo repositorio íntegro después de `PROVIDER_EXHAUSTED` es un
  no-op terminal: conserva run, checkpoint, timestamps, catálogo, manifest y artifacts sin cargar
  autenticación, iniciar discovery ni descargar. Una actualización futura requiere un modo
  explícito distinto.
- `status` es offline y no cambia timestamps ni estado.

## Durabilidad y seguridad

`RESCAN_DEDUP_V2` reconstruye identidades verificadas desde SQLite y filesystem. Cada página se
confirma después de persistir artifacts, sidecars, tamaños y SHA-256. Los checkpoints no adelantan
al catálogo, los artifacts íntegros no se sobrescriben y el lock impide dos writers simultáneos.

La autenticación lee una sesión Firefox local mediante una frontera contenida y read-only. Cookies,
perfil, rutas personales, headers, tokens y URLs firmadas no se publican ni persisten en evidencia.

## Evidencia y límites

La aceptación observó 22 videos, sidecars, artifacts, jobs e identidades; SQLite íntegro, manifest
`complete=true / exhausted=true`, provider-best y cero residuos. CERT-0001 conserva la trazabilidad
sin publicar target, perfil, rutas o medios. Una aceptación pública posterior repitió exactamente
una vez `archive --all` y confirmó 22→22, el mismo terminal y checkpoint 5/5, fingerprints
byte-idénticos y ausencia observable de worker, autenticación, discovery, candidatos o descarga.

Observaciones:

- certifica una cuenta pública observada, no todas las cuentas de X;
- `RESCAN_DEDUP_V2` puede ser ineficiente a gran escala;
- no certifica miles de descargas, scheduler ni operación masiva/desatendida;
- CLI execution reporting schema 1 está integrado y validado;
- Telegram y WhatsApp permanecen en el roadmap futuro.
