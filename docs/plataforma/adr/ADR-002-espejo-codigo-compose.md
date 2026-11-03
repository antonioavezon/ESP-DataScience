# ADR-002 — Espejo `HUC-1.0.0/codigo`

- **Estado:** Aceptada
- **Contexto:** Compose necesita contexto de build autocontenido.
- **Decisión:** Mantener `codigo/` sincronizado desde la raíz vía `instalar.sh`/rsync.
- **Consecuencias:** Duplicidad controlada; riesgo de desfase si se olvida sincronizar.
