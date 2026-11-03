# ADR-004 — GitHub Actions como gate de calidad

## Estado
Aceptado (2026-11-03)

## Contexto
HUC consolidó código y SDD en GitHub, pero carecía de pipelines remotos. Las pruebas existían y pasaban en local; el riesgo era integrar a `main` sin evidencia reproducible fuera de la estación del desarrollador.

## Decisión
1. Introducir workflows `ci.yml`, `security.yml` y `especializadas.yml`.
2. Ejecutar solo suites categoría A (y seguridad básica) en runners `ubuntu-latest` con Python 3.14.
3. Mantener Ollama/MQTT E2E/holdouts fuera del gate automático.
4. Centralizar comandos en `scripts/ci/` y `requirements-ci.txt`.
5. No modificar lógica física ni datasets para adaptar el proyecto al CI.

## Consecuencias
- PRs obtienen señal automática de regresión en módulos núcleo.
- Requiere Python 3.14 en Actions (disponible vía `actions/setup-python`).
- La obligatoriedad de bloqueo de merge depende de configuración administrativa de protección de `main`.
- `pip-audit` puede fallar el job ante CVE nuevas: tratar como hallazgo, no silenciar.
