# Decisión de modelo base

**Estado: borrador. No aprobado. El motor general está bloqueado.** Faltan la respuesta de P-14 y esta puerta de fórmulas (`docs/decisiones_pendientes.md`). La puerta G1 de `trabajo2.md` no se ha presentado ni aprobado. El código de `datasets/en_uso/BES-jun/src/` transcribe celdas de ese libro. No es un motor para los demás Excel.

## Qué se puede calcular ahora, con la fórmula escrita en BES-jun

Para cada hoja, con entradas de esa misma hoja:

1. Gravedad específica a 60 °F con F-01: `141.5 / (131.5 + API)`.
2. Corrección de gravedad a la temperatura de fondo, con la expresión de la celda (constantes 0.00066, 0.0000003 y 15.556, no definidas fuera de la celda).
3. Densidad de mezcla y gradiente `densidad * 0.052`, como están escritos.
4. `PIP en (ft)` a partir de la presión de sensor, las TVD de intake y de sensor, y el gradiente. Es una corrección de la medición, no una estimación sin sensor.
5. `THP en (ft)`, fricción de Hazen-Williams con el exponente 4.8566 de la hoja, y `THD TOTAL` con la suma que escribe la hoja.

Esas cuatro salidas del balance reproducen el valor cacheado de las cinco hojas (`tests/test_fluidos_y_balance_bes_jun.py`). Eso comprueba la transcripción. No comprueba que el resultado coincida con otra medición.

## Qué no se calcula

| Cálculo | Motivo |
|---|---|
| Método B de E1: resolver Q desde `P_in` | Faltan la curva `H0(Q)` como polinomio aprobado, `η_em`, `k_f`, `k_g` y `P_loss(N)`. La hoja no usa esa ecuación. |
| PIP sensorless de E1 §4.7 | La hoja ya trae presión de sensor. Aplicar F-38 exigiría parámetros que no están en el libro. |
| Observador EKF/MHE (F-40) | Queda fuera de esta iteración, igual que en el plan. |
| Predicción de un instante futuro | No hay serie temporal. Cuatro hojas tienen `=TODAY()`; el valor cacheado 2026-10-17 es la fecha en que Excel calculó el libro. Solo `QF-549HST` tiene una fecha escrita: 2017-09-06. |
| Curva de fabricante | Los puntos H-Q-HP-EFF están escritos en la hoja. No hay un certificado aparte en el proyecto. La columna EFF llega a 7.6 con rótulo «%», mientras el cociente de potencias de la misma hoja queda cerca de 0.81. No se igualan y no se corrige el 7.6. |

## Dos cadenas que no se mezclan

- **E1, secciones 4.1 a 4.8:** álgebra en unidades SI. Resuelve Q desde la potencia y luego PIP desde THP. Es el candidato a Método B del plan.
- **X1, hoja Prueba Sesnorless:** otra cadena, en psi, ft, bpd y hp, con constantes 136000 y 0.433. El plan la llama Método A y documenta diferencias (H-08 a H-16).
- **BES-jun:** una tercera cadena, de diseño por pozo. Usa presión de sensor, survey de TVD, Hazen-Williams y una tabla de bomba. No es D1 ni la hoja Prueba Sesnorless.

La formulación base del motor general sigue siendo la de E1 más las correcciones que G1 apruebe. Esta iteración no la aprueba. Solo deja reproducible la cadena que BES-jun ya calcula.

## Pregunta que bloquea la aprobación

¿Se adopta la cadena de BES-jun como un caso de diseño (al lado de R1 y X1) y se mantiene E1 como modelo sensorless, o alguna celda de BES-jun debe reemplazar una F-xx? Mientras no haya respuesta, el estado de este documento es borrador.
