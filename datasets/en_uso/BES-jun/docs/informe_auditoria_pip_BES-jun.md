# Auditoría física y dimensional del PIP · BES-jun

Fecha: 2026-10-21. Fuente primaria: `fuentes/originales/Copia de FINAL BES-jun.xlsx`, SHA-256 `ccb5a738baea13321993e8b6eccefd6cac90ecda86b1c4b9181f897fcfa83f85`. La copia de trabajo `entrada/BES_jun.xlsx` tiene la misma huella. No se guardó el libro. No se modificó `pip_en_ft` ni ninguna otra fórmula de producción.

## Respuesta

La PIP de las cinco hojas está bien transcrita y es dimensionalmente coherente si el gradiente se lee como psi/ft. No está respaldada como presión de admisión física. En las cinco hojas el sensor está más profundo que el intake y la celda suma esa columna en vez de restarla. La procedencia de la presión no está confirmada. La confianza operacional, como presión real en la aspiración de la bomba, es baja. La confianza en la reproducción de la celda es alta.

Esa conclusión no autoriza cambiar el signo en el código. La propuesta queda al final, sin aplicar.

## Fórmula original y equivalente

En QF-554H, G96:

`=(B73-((C20-C24)*B102))/B102`

con unidad escrita `ft` en H96.

Algebra, con profundidad positiva hacia abajo:

`H_celda = P_sensor / G + TVD_sensor - TVD_intake`

La resta `(C20-C24)` es intake menos sensor. Como el sensor está más abajo, esa diferencia es negativa. Multiplicada por el gradiente y restada de la presión, equivale a sumar la columna.

La hidrostática de una columna estática, si el sensor mide la presión en su TVD y la PIP es la presión en el intake, es la opuesta:

`P_intake = P_sensor - G * (TVD_sensor - TVD_intake)`

`H_hidro = P_sensor / G - (TVD_sensor - TVD_intake)`

La diferencia es exacta:

`H_celda - H_hidro = 2 * (TVD_sensor - TVD_intake)`

El código productivo implementa la celda, no la hidrostática. `hipotesis_ct03.py` no entra en el motor.

## Desarrollo dimensional

1. `C20 - C24` está en ft. Son TVD, no MD.
2. `B102` sale de `densidad * 0.052`. Una densidad en lb/gal por 0,052 da psi/ft. El rótulo de las cinco hojas, en la columna C de esa fila, dice `psi*ft`.
3. Si se tomara el rótulo al pie de la letra, `(ft) * (psi*ft)` sería psi·ft² y no se podría restar de una presión en psi. La resta con B73 solo cierra si B102 es psi/ft. El rótulo `psi*ft` es inconsistente con la aritmética. La aritmética, leída como psi/ft, sí cierra.
4. El paréntesis queda en psi. Dividir por psi/ft da ft. H96 dice `ft`. Esa unidad del resultado es coherente.
5. El equivalente en psi es `H_PIP * G`. No es una segunda medición.

El factor 0,052 no se sustituyó. Un contraste con constantes del SI da 0,051948. La diferencia es de redondeo de campo y no explica el signo.

## Las celdas no coinciden entre hojas

La misma álgebra está escrita en otra fila en cada hoja. La TVD no es un número tecleado: la columna C dice `Calculada` y apunta a una interpolación del survey (columna H de ese bloque, que indexa la TVD del survey a la MD del equipo). La MD, columna B, dice `introducir` y es un número. La fórmula de PIP cita la columna C, no la B.

| Hoja | Pozo en B10 | Presión | MD / TVD intake | MD / TVD sensor | Gradiente | PIP | THD que resta el PIP |
|---|---|---|---|---|---|---|---|
| QF-554H | QF-084 | B73 = 732 psi | B20 = 2856.10 ft / C20 = 2653.177 ft, `=H365` | B24 = 2900.58 / C24 = 2678.822, `=H373` | B102 `=B100*0.052` = 0.43343073, rótulo `psi*ft` | G96 = 1714.496 ft = 743.115 psi | G102 `=C18+G100+G98-G96` = 2083.217 ft |
| QF-545H | QF-301 | B71 = 667 psi | B19 = 2994.87 / C19 = 2534.604, `=H351` | B23 = 3038.12 / C23 = 2553.917, `=H359` | B100 `=B98*0.052` = 0.43347492, rótulo `psi*ft` | G94 = 1558.042 ft = 675.372 psi | G100 `=C17+G98+G96-G94` = 1971.955 ft |
| QF-500H | QF-147 | B72 = 821 psi | B19 = 2813.57 / C19 = 2578.968, `=H323` | B23 = 2859.30 / C23 = 2604.498, `=H331` | B101 `=B99*0.052` = 0.43320001, rótulo `psi*ft` | G95 = 1920.729 ft = 832.060 psi | G101 `=C17+G99+G97-G95` = 1517.209 ft |
| QF-378HST | QF-005 | B70 = 810 psi | B19 = 3028.46 / C19 = 2769.659, `=H321` | B23 = 3061.68 / C23 = 2790.283, `=H329` | B99 `=B97*0.052` = 0.43301916, rótulo `psi*ft` | G93 = 1891.210 ft = 818.930 psi | G99 `=C17+G97+G95-G93` = 1592.463 ft |
| QF-549HST | QF-306 | B70 = 607 psi | B19 = 2796.27 / C19 = 2614.064, `=H321` | B23 = 2829.66 / C23 = 2634.603, `=H329` | B99 `=B97*0.052` = 0.43301916, rótulo `psi*ft` | G93 = 1422.325 ft = 615.894 psi | G99 `=C17+G97+G95-G93` = 1814.511 ft |

La fricción no depende del PIP. En QF-554H, G100 usa el caudal B71, el diámetro B38 y la TVD de descarga C18. El PIP solo entra, con signo menos, en el THD. Un PIP más alto reduce el THD en los mismos pies y, aguas abajo, mueve el caudal de intersección.

## Comparación celda contra hidrostática

En las cinco hojas `TVD_sensor > TVD_intake`. La celda queda por encima de `P/G`. La hidrostática queda por debajo.

| Hoja | ΔTVD sensor−intake ft | H celda ft | H hidrostática ft | Diferencia ft | PIP celda psi | PIP hidrostática psi | Sensor psi |
|---|---:|---:|---:|---:|---:|---:|---:|
| QF-554H | 25.645 | 1714.496 | 1663.206 | 51.291 | 743.115 | 720.885 | 732 |
| QF-545H | 19.314 | 1558.042 | 1519.414 | 38.627 | 675.372 | 658.628 | 667 |
| QF-500H | 25.530 | 1920.729 | 1869.668 | 51.060 | 832.060 | 809.940 | 821 |
| QF-378HST | 20.623 | 1891.210 | 1849.964 | 41.247 | 818.930 | 801.070 | 810 |
| QF-549HST | 20.539 | 1422.325 | 1381.246 | 41.078 | 615.894 | 598.106 | 607 |

La celda entrega una presión de intake mayor que la del sensor, aunque el intake está más somero. Bajo la convención de profundidad positiva hacia abajo, eso es inconsistente. La caché de Excel coincide con la celda, no con la hidrostática.

Si el sensor estuviera 100 ft por encima del intake, con 800 psi y 0,4 psi/ft, la celda daría 1900 ft y la hidrostática 2100 ft. A igual TVD las dos dan `P/G`. Esos dos casos no están en las hojas; están en `tests/test_auditoria_pip.py`.

## MD y TVD

Usar la MD en la misma álgebra no es intercambiable. La separación vertical es menor que la medida a lo largo del pozo.

| Hoja | ΔMD ft | ΔTVD ft | Pies de más si se corrigiera con MD |
|---|---:|---:|---:|
| QF-554H | 44.480 | 25.645 | 18.835 |
| QF-545H | 43.250 | 19.314 | 23.936 |
| QF-500H | 45.730 | 25.530 | 20.200 |
| QF-378HST | 33.220 | 20.623 | 12.597 |
| QF-549HST | 33.390 | 20.539 | 12.851 |

La hoja ya eligió la TVD. Ese elección es la adecuada para una corrección hidrostática. El problema demostrado no es MD contra TVD: es el signo con el que se combinan las dos TVD.

## Gradiente, densidad y gas

La densidad es una mezcla lineal, `8.33 * ((BS&W * ρ_agua / 8.33) + (1-BS&W) * sg_T)`. El rótulo de BS&W dice `%` y el número se multiplica como fracción. Es una densidad promedio de líquido, no una densidad in situ con gas libre.

Presión de burbuja: G20, G19 o la celda equivalente, 130 psi en las cinco hojas. °API = 12 y presión de yacimiento = 1100 psi también están repetidos. No hay evidencia de que sean un PVT medido de cada pozo.

Aun así, con los números escritos, la presión del sensor (607 a 821 psi) y las dos PIP en psi (la de la celda y la hidrostática, 598 psi la más baja) quedan muy por encima de 130 psi. En estos cinco puntos el modelo no muestra gas libre en el sensor ni en el intake. La limitación sigue: un gradiente líquido único no describe un flujo multifásico si la presión cayera bajo la de burbuja o si el gas ya estuviera libre por otra razón. Eso no está soportado por estas celdas. Queda pendiente, no confirmado como error de estos cinco cálculos.

## Procedencia de la presión

| Hoja | Celda | Qué hay en el archivo | Clasificación |
|---|---|---|---|
| QF-554H | B73 | Número 732, unidad `psi`, sin comentario, sin fórmula | No confirmado |
| QF-545H | B71 | Número 667, unidad `psi` | No confirmado |
| QF-500H | B72 | Número 821, unidad `psi` | No confirmado |
| QF-378HST | B70 | Número 810, unidad `psi` | No confirmado |
| QF-549HST | B70 | Número 607, unidad `psi` | No confirmado |

No hay identificador de instrumento, ni fecha de la medición, ni cita de un sistema de adquisición. B6 es `=TODAY()` en cuatro hojas. En QF-549HST B6 es la fecha 2017-09-06; eso no demuestra que sea el día de la presión. No se clasifica ningún pozo como sensorless. La existencia de un número llamado «Presión de Sensor» tampoco demuestra que sea una medición de fondo.

## Cinco planos, separados

| Plano | Dictamen | Evidencia |
|---|---|---|
| Álgebra | Confirmado | G96 y las celdas homólogas equivalen a `P/G + TVD_sensor - TVD_intake`. Python reproduce la caché. |
| Dimensiones | Confirmado para la operación psi/ft → ft. Inconsistente el rótulo `psi*ft` | La resta con B73 no cierra si el gradiente fuera un producto psi·ft. H96 dice ft. |
| Física bajo columna estática y TVD hacia abajo | Inconsistente | Las cinco hojas tienen el sensor más profundo y la celda aumenta la presión hacia el intake. |
| Procedencia de los datos | No confirmado | Valores tecleados, sin instrumento. PVT repetido en las cinco hojas. |
| Multifásico | Pendiente, sin gas libre visible en estos puntos | Sensor y ambas PIP en psi están sobre 130 psi. El gradiente es de líquido promedio. |

## Pruebas

`tests/test_auditoria_pip.py`, diez pruebas, sin tocar la fórmula. Cubren las cinco hojas, sensor más abajo, sensor más arriba, igual profundidad, gradiente nulo, presión ausente, la unidad `psi*ft` rechazada sin conversión, el rótulo del gradiente, MD distinta de TVD, y el menos del THD. El Excel conserva la huella citada.

## Propuesta, no aplicada

No cambiar el signo en `pip_en_ft` con esta auditoría sola. Falta confirmar que B73, B71, B72 o B70 es la presión sin corregir en la TVD del sensor, y no un valor que alguien ya hubiera llevado al intake.

Si esa confirmación llega, el cambio sería sustituir `(TVD_intake - TVD_sensor)` por `(TVD_sensor - TVD_intake)` dentro de la corrección, conservar la transcripción actual como referencia de la celda, y recalcular THD y Q* sin presentarlos como una orden de operación. Hasta entonces CT-03 sigue abierta.

Sí conviene, cuando se revise el modelo, dejar escrito que la unidad física de B102 es psi/ft y que el rótulo `psi*ft` no se usa. No hace falta tocar el 0,052 para explicar el signo.

No usar la MD en la corrección. No tratar la PIP en ft como si fuera psi. No inferir ausencia de sensor.
