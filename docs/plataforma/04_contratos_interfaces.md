# 04 — Contratos e interfaces

## HTTP — Visualización (`web`, puerto 8000)
| Ruta | Uso |
|---|---|
| `/` | Inicio consola |
| `/asistente/`, `/asistente/enviar/` | Chat |
| `/api/consola/pozos/`, `.../resultado/` | API consola |
| `/datasets/` | Listado/selección de expedientes |

## HTTP — Data (`data`, puerto 8001)
| Ruta | Uso |
|---|---|
| `/api/sesion/`, `/api/acceder/`, `/api/cerrar-sesion/` | Sesión simulador |
| `/api/pozos/<id>/base|aplicar|restaurar|fase|automatica/` | Controles y secuencias |

## MQTT (`proceso/contratos/mensajes.py`)
| Topic | Dirección | Contenido |
|---|---|---|
| `huc/v1/data/{pozo}/escenario` | DATA→PROC | Controles/escenario |
| `huc/v1/proceso/{pozo}/resultado` | PROC→VIZ | Resultados tipificados |
| `huc/v1/proceso/{pozo}/estado` | PROC→VIZ | Estado evaluación |
| `huc/v1/servicios/proceso/estado` | PROC | Latido servicio |

## Contrato de resultados determinísticos
Cada magnitud relevante expone al menos: `valor`, `valor_visible`, `unidad`, `nombre` (inspección de motores BES/RB).  
Capa asistente normaliza unidades de caudal (`web/services/unidades_caudal.py`).

## Contrato lingüístico JSON v1
`web/services/chat_contrato.py`: `schema_version=1.0`, `answer.blocks` tipados (paragraph, table, definition, notice, …).  
El LLM no redefine tablas numéricas; fusiona campos lingüísticos validados.

## Variables de entorno documentadas (no secretos)
Ver `HUC-1.0.0/.env.example`: `OLLAMA_MODEL`, `OLLAMA_BASE_URL`, `HUC_MQTT_*`, `DJANGO_ALLOWED_HOSTS`, `HUC_IA_URL`.  
**No versionar** `HUC-1.0.0/.env` ni `.env` reales.
