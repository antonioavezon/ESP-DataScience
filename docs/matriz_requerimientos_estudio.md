# Matriz de requerimientos de esta iteración

El encargo pide saber qué se puede calcular, qué comportamiento tiene fundamento y qué reglas podrían salir del estudio. Cada fila separa cálculo, estimación y pronóstico.

| Pedido | Dato en BES-jun | Cálculo posible ahora | Evidencia | Regla posible |
|---|---|---|---|---|
| Identificar pozos | Hoja, rótulo Cluster y rótulo Pozo, con códigos distintos | Cinco hojas separadas. La llave única no está declarada en el libro | `datasets/en_uso/BES-jun/data_procesados/calidad.md` | No |
| Calcular gravedad del crudo | API = 12 °API en las cinco hojas | Cálculo directo F-01 | Cache 0.9860627177700348 y prueba | No |
| Calcular gradiente | API, temperatura, BS&W, densidad de agua | Cálculo directo de las celdas B98, B100 y B102 | La prueba reproduce el balance que usa ese gradiente | No, hasta aclarar la unidad de BS&W |
| Obtener PIP sin sensor | No están `k_f`, `η_em` ni `P_loss` del documento E1 | No calculable con E1 §4.7 | `docs/decision_modelo_base.md` | No |
| Corregir la presión de sensor a la profundidad de intake | Presión de sensor, TVD intake, TVD sensor, gradiente | Cálculo directo de la celda «PIP en (ft)», con el signo de la hoja | Coincide con el cache en las 5 hojas | No. El signo frente a F-12 queda pendiente |
| Estimar caudal futuro | No hay serie de fechas de operación | No es pronóstico | Cuatro fechas son `=TODAY()` | No |
| Ver si el caudal cae en los límites escritos | Caudal y tres celdas de límite, en BFPD | Comparación directa, no un modelo | QF-084 por encima de 10000 BFPD | RC-BES-01 a RC-BES-03, pendientes |
| Curva Q-H de fabricante | Tabla de 6 puntos por referencia, a 60 Hz | Se pueden graficar los puntos escritos | `datasets/en_uso/BES-jun/reports/figuras/head_tabulado.png` | No, hasta saber si la tabla es de catálogo |
| Validar contra el artículo SensorLess | El artículo no trae estos pozos | No aplica | A1 queda como contexto | No |
| Explicar con un GLM | Fuera de esta etapa | No se instala | Regla 7 del encargo y fase 7 del plan | No |
| Estadística del survey | Bloque Measured de cada hoja | Descriptiva por hoja: n, mínimo, máximo, media, mediana, desviación y percentiles | `datasets/en_uso/BES-jun/data_procesados/estadisticas_survey.csv` | No |
| Informe y PDF | Este expediente | Cálculo directo documentado, sin predicción validada | `datasets/en_uso/BES-jun/pdf/informes/informe_analisis_BES-jun.pdf` | No |

## Comportamiento que sí tiene fundamento en los documentos

- Subir la frecuencia escala el caudal con N, la altura con N² y la potencia con N³. Lo escriben E1 §4.2 y las celdas de afinidad de BES-jun. No se usó para predecir otro día.
- La hoja llama THD a descarga TVD + fricción + THP en ft − PIP en ft. El PDF llama TDH a presión de boca + fricción + nivel dinámico. Son dos definiciones. No se presentan como la misma cuenta.
- La presión de sensor está por encima de la presión de burbuja escrita (130 psi) en las cinco hojas: 732, 667, 821, 810 y 607 psi. Eso es una comparación de dos números de la hoja. No dice, por sí sola, que no haya gas en la admisión, porque la presión de sensor no está identificada como PIP.
