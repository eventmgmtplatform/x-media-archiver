# ADR-0001 — CLI local como monolito modular hexagonal

**Estado:** PROPOSED  
**Fecha:** 2026-10-28

## Contexto

El objetivo inmediato es descubrir y descargar de forma masiva contenido audiovisual de X desde una terminal. Una GUI, API web, Redis o microservicios incrementarían operación y superficie de fallo sin aportar valor al MVP.

## Decisión

Construir un paquete Python local con Typer/Rich, servicios de aplicación y puertos explícitos para `gallery-dl`, `yt-dlp`, SQLite y filesystem. Usar SQLite como catálogo y ledger de trabajos. Ejecutar FFmpeg como dependencia externa verificada por `doctor`.

## Consecuencias

- Instalación y ejecución simples.
- Tests aislados mediante puertos y fixtures.
- Motores sustituibles cuando cambie X.
- Un solo proceso limita escalamiento, aceptable para uso personal local.
- La licencia y distribución de dependencias deberán revisarse antes del primer release público.

## Alternativas descartadas

- MVC: no existe interfaz gráfica que justifique View/Controller.
- FastAPI: diferido hasta que exista necesidad real de acceso remoto.
- Clonar un downloader: acoplaría el producto a código pequeño y difícil de mantener.
- `twscrape` como base: se reserva como adaptador experimental por su dependencia de sesiones y GraphQL privado.
