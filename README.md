# HUC

Plataforma local de evaluación de pozos con bomba electrosumergible (ESP/BES).

## Arranque

Ver `inicio.md` y el paquete contenedorizado en `HUC-1.0.0/`.

```bash
cd HUC-1.0.0
./iniciar.sh gpu
```

- Visualización: puerto `8000`
- Simulador/Data: puerto `8001`

## Módulos

| Módulo | Rol |
|---|---|
| `data/` | Simulador y publicación de escenarios |
| `proceso/` | Motor determinístico vía MQTT |
| `web/` | Consola Django y asistente |
| `modelos_ia/` | Capa lingüística (Ollama) |
| `datasets/en_uso/` | Expedientes BES-jun, RB-1521, RB-IA-2191 |

## Principio del asistente

El motor determinístico calcula. El modelo lingüístico comprende, consulta e interpreta resultados ya calculados. La web presenta.

## Laboratorio previo

El contenido histórico del repositorio `ESP-DataScience` (laboratorio de ciencia de datos) quedó archivado en `archive/esp-datascience-lab/` tras la consolidación de HUC en `main`.
