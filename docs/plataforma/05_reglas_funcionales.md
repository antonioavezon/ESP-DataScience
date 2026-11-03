# 05 — Reglas funcionales e invariantes

## Responsabilidades
| Módulo | Debe | No debe |
|---|---|---|
| Motores dataset | Calcular magnitudes y estados según fórmulas del expediente | Explicar en lenguaje natural |
| Orquestador chat | Enrutar intención → operación autorizada | Ejecutar código/fórmulas inventadas por el LLM |
| LLM | Explicar hechos recibidos | Inventar PIP/THD/caudales o autorizar maniobras |
| Simulador Data | Publicar escenarios temporales | Sobrescribir Excel/datasets originales |
| Visualización | Presentar contrato/HTML | Recalcular física |

## Invariantes (requisito vs implementación)
| ID | Requisito declarado | Estado en código | Evidencia |
|---|---|---|---|
| INV-1 | Determinístico independiente del LLM | Cumple | `chat_herramientas` / motores |
| INV-2 | LLM no sustituye cálculo | Cumple (diseño + pruebas) | omitir_llm, validación cifras, tests ensamble |
| INV-3 | Contratos verificables | Cumple parcialmente | MQTT topics + JSON v1; schemas BES en integracion/ |
| INV-4 | Simulación no persiste como real | Cumple | `valores_en_uso` en memoria |
| INV-5 | Retorno a dataset | Cumple | endpoint restaurar/base |
| INV-6 | Contexto pozo/dataset en UI | Cumple con residuales de anáfora | selectores + intención |
| INV-7 | JSON Django consistente | Cumple | `chat_contrato.validar` |
| INV-8 | Separación DATA/PROC/VIZ/IA | Cumple en Compose | `compose.yaml` |

## Brechas conocidas
- Identidades hoja↔código BES provisionales (`integracion/pozos.json`).
- BES sin reglas RC aprobadas operacionalmente.
- Anáforas numéricas sin prefijo `QF-` piden aclaración (falla segura).
