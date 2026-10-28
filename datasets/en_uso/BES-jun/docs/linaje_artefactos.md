# Linaje de artefactos derivados · BES-jun

No se borró ningún archivo. Los huérfanos quedan nombrados para no usarlos en el informe.

## Figuras vigentes

| Archivo | Productor |
|---|---|
| `reports/figuras/caudal_limites_por_hoja.png` | `analisis.graficos.guardar_figuras` |
| `reports/figuras/head_puntos_60hz.png` | `analisis.graficos.guardar_figuras` |
| `reports/figuras/survey_md_tvd_por_hoja.png` | `analisis.graficos.guardar_figuras` |
| `reports/figuras/inclinacion_survey_por_hoja.png` | `analisis.graficos.guardar_figuras` |
| `reports/figuras/interseccion_sistema_bomba.png` | `analisis.graficos.guardar_figuras` |
| `reports/figuras/impacto_ambiguedades_en_caudal.png` | `analisis.graficos.guardar_figuras` |
| `reports/figuras/elasticidad_q_estrella.png` | `informes.escribir_informe, vía analisis.graficos.figura_elasticidades` |

## Figuras sin productor vigente

- `reports/figuras/caudal_y_limites.png`: versión anterior. El informe no la referencia.
- `reports/figuras/head_tabulado.png`: versión anterior. El informe no la referencia.

## Datos procesados

`data_procesados/resultados_deterministicos.csv` lo escribe el cuaderno `04_calculos_deterministicos`. `curvas_bomba_60hz.csv` lo escribe `03_mapeo_y_preparacion_BES_jun`. El resto de CSV y Markdown de esa carpeta sale de los cuadernos de inventario, calidad y mapeo. El informe consolidado no lee cifras de esos CSV: las recalcula al generarse.
