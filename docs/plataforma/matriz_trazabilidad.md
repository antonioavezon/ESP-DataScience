# Matriz de trazabilidad

| Requisito | Componente | Evidencia código | Contrato | Prueba |
|---|---|---|---|---|
| INV-1 Motor independiente | datasets motors + herramientas | `chat_herramientas.py` | resultados tipificados | BES/RB pytest; WEB |
| INV-2 LLM no calcula | orquestador + contrato | `chat_orquestador.py`, `chat_contrato.py` | JSON v1 | `test_ensamble_dedupe`, `test_chat_orquestador` |
| INV-4 Simulación temporal | Data | `valores_en_uso.py` | API base/aplicar/restaurar | `data/tests/test_valores_en_uso.py` |
| INV-5 Retorno a hoja | Data views | `views.restaurar` | HTTP | tests data + manual |
| Unidades caudal | motores RB + unidades_caudal | `unidades_caudal.py` | etiquetas BOPD/BWPD | `test_unidades_caudal` |
| MQTT escenarios/resultados | proceso contratos | `mensajes.py` | topics huc/v1 | `proceso/tests`; E2E histórico |
| Despliegue Compose | HUC-1.0.0 | `compose.yaml` | env example | `compose config` |
| Docs SDD | docs/plataforma | este árbol | — | revisión humana Fase 2 |

Leyenda de cumplimiento: ver §05. Elementos marcados como brecha no bloquean documentación pero condicionan specs futuras.
