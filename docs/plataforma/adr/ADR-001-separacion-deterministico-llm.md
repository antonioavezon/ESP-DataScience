# ADR-001 — Separación motor determinístico / LLM

- **Estado:** Aceptada (implementada)
- **Contexto:** Riesgo de que un LLM invente física de pozo.
- **Decisión:** Orquestador elige operaciones de un catálogo; motores calculan; LLM solo redacta sobre hechos.
- **Consecuencias:** Mayor complejidad de intención; mayor fidelidad factual; naturalidad variable.
