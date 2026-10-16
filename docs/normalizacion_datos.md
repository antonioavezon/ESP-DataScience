# Normalización de los datos experimentales

Actividad 2.12. El cuaderno que la ejecuta es `notebooks/02_normalizacion.ipynb`. No modifica `data/raw` y no entrena modelos.

## Decisiones

- Cada libro produce su propia tabla. Mapping y surging no se apilan.
- Se leen las tres hojas de cada libro con `header=None`. La primera fila de la hoja sigue siendo la fila 0, como en las actividades 2.1 a 2.11.
- Una fila de la tabla larga es un par numérico completo: las dos mediciones del bloque son números a la vez. Si las dos celdas están vacías, no se crea una fila. Si solo una fuera numérica, el cuaderno se detiene: rellenar la otra sería imputar. En estas seis hojas no apareció ningún par incompleto.
- `Flow rate` se guarda como `ql_bpd`. La unidad bpd es la lectura de la tesis, con certeza alta como interpretación, porque el encabezado del Excel no la imprime.
- `DP2-3` se guarda como `dp2_3_psi`. La certeza es media. El rótulo no está en la tesis.
- `GVF0` se guarda como `gvf0_porcentaje`. No se divide por 100. La certeza es media.
- La presión de la hoja se guarda como `psep_psig`, tomada del nombre `50psig`, `100psig` o `150psig`. Certeza alta.
- En mapping, la velocidad de `50psig` sale de la celda y `origen_velocidad` vale `celda`. En `100psig` y `150psig` la celda está vacía. `velocidad_rpm` recibe 1800 o 3500 según el conjunto de rótulos Qgd, y `origen_velocidad` vale `diseño_experimental`. `valor_celda_velocidad` queda vacío. El Excel no se rellena.
- En surging la velocidad está escrita en las tres columnas de cada franja. Las tres tienen que coincidir. `origen_velocidad` vale `celda`.
- No se calcula el caudal de líquido de surging a partir de la fracción de QBEP. 2700 bpd es el mejor punto a 3500 rpm. La tesis no da el equivalente a 1800 rpm.
- No se calcula QG. Qmax de 4900 bpd también está dado solo a 3500 rpm.
- `Single Phase` deja `qgd` vacío. El archivo no escribe un cero.

El conjunto que asigna 1800 rpm es `Qgd=0.005`, `Qgd=0.01` y `Qgd=0.015`. El que asigna 3500 rpm es `Qgd=0.01`, `Qgd=0.02`, `Qgd=0.03`, `Qgd=0.04` y `Qgd=0.05`. Es el diseño de la tesis, sección 2.3.3, y de Zhu et al. (2018b), sección 3.3.

## Resultados

| Tabla | Filas | 50 psig | 100 psig | 150 psig |
|---|---:|---:|---:|---:|
| `data/processed/mapping_long.csv` | 570 | 186 | 192 | 192 |
| `data/processed/surging_long.csv` | 387 | 119 | 129 | 139 |

Mapping/`50psig` repite la actividad 2.10: 186 pares, 10 condiciones, 62 a 1800 rpm y 124 a 3500 rpm. Esas dos velocidades salen de la celda.

Los totales de las otras cinco hojas coinciden con `docs/auditoria_preparacion_datos.md`. No hubo discrepancia que investigar. El reparto por velocidad, que la auditoría no tabulaba, queda así:

| Hoja | Protocolo | 1800 rpm | 3500 rpm | Origen de la velocidad |
|---|---|---:|---:|---|
| 50psig | mapping | 62 | 124 | celda |
| 100psig | mapping | 55 | 137 | diseño experimental |
| 150psig | mapping | 70 | 122 | diseño experimental |
| 50psig | surging | 38 | 81 | celda |
| 100psig | surging | 36 | 93 | celda |
| 150psig | surging | 49 | 90 | celda |

Los huecos en los que las dos celdas estaban vacías no entraron a la tabla: 50, 60 y 58 en las tres hojas de mapping, y 19, 42 y 17 en las de surging.

Rangos de las columnas, sin convertir unidades:

- Caudal de mapping: de 1,35 bpd a 4702 bpd. Queda por debajo de los 4900 bpd de caudal abierto a 3500 rpm.
- `DP2-3` de mapping: de 0,08 psi a 31,2 psi.
- `DP2-3` de surging: de 0,38 psi a 28,0 psi.
- `GVF0`: de 0,0006 a 19,1. Supera 1, así que no es una fracción entre 0 y 1.

La huella SHA-256 de `data/raw/mapping.xlsx` y de `data/raw/surging.xlsx` es la misma antes y después de escribir los CSV.

## Advertencias

- Los puntos de una misma curva no son ensayos independientes.
- La velocidad de dos hojas de mapping no fue medida en la celda. Usarla como si lo hubiera sido mezcla una asignación documental con una lectura instrumental.
- `DP2-3` y `GVF0` siguen sin aparecer con esas letras en la tesis.
- Estas tablas no están listas para un ajuste. La actividad 2.13 no se ha iniciado.
