---
title: Roadmap v2
---

[Inicio](index.html) · [Producto v1](product.html) · [Arquitectura](architecture.html) · [Releases](releases.html) · [Gobierno](governance.html) · [Roadmap v2](roadmap.html)

---

# Roadmap v2 — archivo multimedia multiplataforma

## Visión

Evolucionar XMA hacia un archivador local-first capaz de incorporar, de manera incremental y
gobernada, contenido autorizado de distintas aplicaciones y plataformas.

## Orden propuesto

| Fase | Plataforma | Objetivo |
|---|---|---|
| V1 | X | Perfil, publicación individual y lotes acotados |
| V2.1 | Núcleo | Contrato común de plataforma y repositorio versionado |
| V2.2 | Telegram | Canales/chats autorizados, medios y checkpoints |
| V2.3 | WhatsApp | Exportaciones o interfaces oficiales autorizadas |
| V2.4 | Otras plataformas | Adaptadores priorizados por valor, legalidad y soporte |

## Trabajo técnico v2

v0.2.0 no ha comenzado. Telegram y WhatsApp permanecen como roadmap futuro y requieren prompts,
autorización y gates propios; este documento no los autoriza.

- separar `PlatformAdapter`, autenticación, discovery y descarga;
- introducir identidad `platform:account:post:media`;
- migrar sin romper repositorios v1;
- cursor remoto durable y paginación eficiente;
- configuración de políticas por plataforma;
- vault/keyring para secretos cuando sea necesario;
- scheduler opcional, colas y observabilidad;
- soporte de cientos/miles solo después de pruebas de capacidad;
- matriz de compatibilidad, términos de servicio y controles de privacidad.

## Criterios de incorporación

Cada plataforma requiere: fuente permitida, autenticación segura, límites/rate limiting, modelo de
identidad, pruebas offline, aceptación pública acotada, documentación, rollback y gate humano.

No se implementarán bypasses de autenticación, DRM o controles de acceso. Telegram y WhatsApp se
integrarán únicamente mediante contenido público, exportaciones del usuario o interfaces oficiales
para las que exista autorización.
