# 01 — Contexto y alcance

## Objetivo del sistema
HUC permite evaluar pozos con bomba electrosumergible a partir de expedientes (datasets) con motores determinísticos, visualizar estados/resultados y consultar un asistente lingüístico que **explica** esos resultados sin sustituir el cálculo físico.

## Actores
| Actor | Interacción |
|---|---|
| Operador/analista | Consola web (`:8000`), simulador (`:8001`), asistente |
| Desarrollador | Código en raíz + espejo `HUC-1.0.0/codigo/`, pruebas, Compose |
| Proceso automatizado | MQTT DATA→PROCESO→VIZ |

## Problemas que resuelve
- Unificar expedientes heterogéneos (BES-jun, RB-1521, RB-IA-2191) bajo contratos comunes de evaluación.
- Separar simulación de datos de hoja sin corromper originales.
- Ofrecer explicación en lenguaje natural anclada a magnitudes tipificadas.

## Funcionalidades implementadas (evidencia en código)
- Evaluación por pozo (`web/services/consola_operacional.py`, motores en `datasets/en_uso/*/src`).
- Publicación MQTT de escenarios/resultados (`proceso/`, `data/`).
- Consola y asistente Django (`web/apps/*`).
- Simulador con valores en uso temporales (`data/simuladores/valores_en_uso.py`).
- Inferencia Ollama opcional en el orquestador (`web/services/chat_orquestador.py`, `ollama_client.py`).

## Límites de responsabilidad
- **No** es un sistema de control en tiempo real del pozo.
- **No** autoriza maniobras (`recomendacion_operacional_autorizada` permanece en falso en evaluaciones actuales).
- **No** valida físicamente de forma independiente las fórmulas BES (estado `validacion_pendiente` en manifiesto).
- El laboratorio académico previo vive en `archive/esp-datascience-lab/` y no forma parte del runtime HUC.

## Fuera de alcance actual
Certificación industrial, multi-tenant cloud, entrenamiento de modelos físicos nuevos, reemplazo de motores por el LLM.
