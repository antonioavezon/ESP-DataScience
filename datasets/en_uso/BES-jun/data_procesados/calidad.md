# Calidad del libro — BES_jun

Observaciones de perfilado. No es una predicción y no se clasifica ninguna celda como falla.

SHA-256: `ccb5a738baea13321993e8b6eccefd6cac90ecda86b1c4b9181f897fcfa83f85`. Hojas: 5. Fórmulas presentes: sí (1270 celdas).

## Posibles pozos

El libro separa la información en cinco hojas visibles. En cada hoja hay dos textos distintos junto a dos etiquetas distintas:

| Hoja (nombre de pestaña) | Texto en B junto a la etiqueta `Cluster:` | Texto en B junto a la etiqueta `Pozo:` | ¿El nombre de hoja es igual al texto de Cluster? | ¿El texto de Pozo es igual al de Cluster? |
|---|---|---|---|---|
| `QF-554H` | `QF-554H` | `QF-084` | sí | no |
| `QF-545H` | `QF-545H` | `QF-301` | sí | no |
| `QF-500H` | `QF-500H` | `QF-147` | sí | no |
| `QF-378HST` | `QF-378HST` | `QF-005` | sí | no |
| `QF-549HST` | `QF-549HST` | `QF-306` | sí | no |

Los cinco textos de Cluster son distintos entre sí. Los cinco textos de Pozo son distintos entre sí. Ningún texto de Pozo se repite como Cluster. El libro no dice cuál de los dos es la llave del pozo, ni si el nombre de la hoja es una llave. **No se pudo determinar la llave.** No se agruparon filas ni hojas por una clave supuesta.

Textos que coinciden con el patrón `QF-` (celda y texto completo de la celda si aporta contexto corto):

- `QF-554H` `B8`: token `QF-554H` dentro de `QF-554H`.
- `QF-554H` `B10`: token `QF-084` dentro de `QF-084`.
- `QF-545H` `B8`: token `QF-545H` dentro de `QF-545H`.
- `QF-545H` `B10`: token `QF-301` dentro de `QF-301`.
- `QF-500H` `B8`: token `QF-500H` dentro de `QF-500H`.
- `QF-500H` `B10`: token `QF-147` dentro de `QF-147`.
- `QF-378HST` `B8`: token `QF-378HST` dentro de `QF-378HST`.
- `QF-378HST` `B10`: token `QF-005` dentro de `QF-005`.
- `QF-549HST` `B8`: token `QF-549HST` dentro de `QF-549HST`.
- `QF-549HST` `B10`: token `QF-306` dentro de `QF-306`.

Significado de `Cluster`, `Pozo` y de esos tokens: pendiente de documentación.

## Duplicados

- No hay dos hojas con el mismo texto de Cluster ni con el mismo texto de Pozo.
- Las cinco hojas repiten el mismo formulario: los mismos títulos de sección y, en la columna A, la misma secuencia de etiquetas, con `QF-554H` desplazada una fila desde `Información Mecánica del Pozo`.
- Dentro de cada hoja hay etiquetas de la columna A repetidas (`Caudal`, `Promedio`, `Velocidad`, `Potencia KVA`, `U-V`, `V-W`, `U-W`, `I Promedio`, y otras). La lista de filas está en `perfil_hojas.md`. Son etiquetas de bloques distintos del formulario, no dos columnas de una tabla con el mismo nombre.
- `Temperatura de fondo` aparece dos veces en la columna E de la zona de producción: una con texto de unidad `ºF` y valor constante, y otra con texto de unidad `ºC` y fórmula. El libro escribe la misma etiqueta en las dos filas.

Celdas numéricas constantes, en las primeras 120 filas, iguales a la celda de arriba, con la columna A vacía en esa fila:

- `QF-554H` `G39` = 2, igual que `G38`.
- `QF-545H` `G38` = 2, igual que `G37`.
- `QF-500H` `G38` = 2, igual que `G37`.
- `QF-378HST` `G38` = 2, igual que `G37`.
- `QF-549HST` `G38` = 2, igual que `G37`.

Bloque `Measured`: el detalle de profundidades repetidas y de tuplas A–E repetidas está en `perfil_hojas.md` (sección de cada hoja). El generador de este perfil no halló, en la redacción automática de esa sección, una marca distinta: revisar allí la frase sobre valores repetidos de la columna A y sobre tuplas A–E.

## Constantes

Etiquetas de la zona mecánica cuyo valor cacheado de B es el mismo número o el mismo texto en las cinco hojas:

- Etiqueta A `OD`: el valor cacheado de B es el mismo en las cinco hojas (3.5). Unidad en C de la primera hoja: inch.
- Etiqueta A `Peso`: el valor cacheado de B es el mismo en las cinco hojas (9.3). Unidad en C de la primera hoja: LB/ft.
- Etiqueta A `Grado`: el valor cacheado de B es el mismo en las cinco hojas (N80). Unidad en C de la primera hoja: —.
- Etiqueta A `ID`: el valor cacheado de B es el mismo en las cinco hojas (2.996). Unidad en C de la primera hoja: inch.
- Etiqueta A `Fabricante`: el valor cacheado de B es el mismo en las cinco hojas (Schlumberger). Unidad en C de la primera hoja: —.

Etiquetas de esa zona cuyo valor cacheado de B cambia entre hojas:

- `Descarga`: `QF-554H`=2841.51 (C==+H361), `QF-545H`=2978.66 (C==+H347), `QF-500H`=2801.9 (C==+H319), `QF-378HST`=3018.77 (C==+H317), `QF-549HST`=2787.17 (C==+H317).
- `Intake`: `QF-554H`=2856.1 (C==H365), `QF-545H`=2994.87 (C==H351), `QF-500H`=2813.57 (C==H323), `QF-378HST`=3028.46 (C==H321), `QF-549HST`=2796.27 (C==H321).
- `Motor`: `QF-554H`=2873.71 (C==H369), `QF-545H`=3011.25 (C==H355), `QF-500H`=2857.43 (C==H327), `QF-378HST`=3046.09 (C==H325), `QF-549HST`=2805.98 (C==H325).
- `Sensor`: `QF-554H`=2900.58 (C==H373), `QF-545H`=3038.12 (C==H359), `QF-500H`=2859.3 (C==H331), `QF-378HST`=3061.68 (C==H329), `QF-549HST`=2829.66 (C==H329).
- `Perforados`: `QF-554H`=3780 (C==H377), `QF-545H`=3933 (C==H363), `QF-500H`=3977 (C==H335), `QF-378HST`=4166 (C==H333), `QF-549HST`=3712 (C==H333).
- `Referencia`: `QF-554H`=S 8000N (C=—), `QF-545H`=S 8000N (C=—), `QF-500H`=S 8000N (C=—), `QF-378HST`=S6000N (C=—), `QF-549HST`=S6000N (C=—).
- `Etapas`: `QF-554H`=53 (C=Nº), `QF-545H`=50 (C=Nº), `QF-500H`=36 (C=Nº), `QF-378HST`=31 (C=Nº), `QF-549HST`=31 (C=Nº).

Ceros constantes (no fórmula) en el bloque de las 20 filas posteriores a `Condiciones de Operación Actuales`:

- `QF-554H` fila 77 `Vibración del Motor` (A-B), valor 0, texto vecino de unidad G.
- `QF-545H` fila 75 `Vibración del Motor` (A-B), valor 0, texto vecino de unidad G.
- `QF-500H` fila 76 `Vibración del Motor` (A-B), valor 0, texto vecino de unidad G.
- `QF-378HST` fila 74 `Vibración del Motor` (A-B), valor 0, texto vecino de unidad G.
- `QF-549HST` fila 74 `Vibración del Motor` (A-B), valor 0, texto vecino de unidad G.

Estos ceros están guardados como número. No se les asigna una causa.

Textos de unidad en H para `Densidad del Agua` y texto de unidad en C para `Densidad de Fluido`, por hoja (grafía real):

- `Densidad del Agua`:
  - `QF-554H` fila 34: H=`Lb/gln`, G=`8.345`.
  - `QF-545H` fila 33: H=`Lb/galn`, G=`8.345`.
  - `QF-500H` fila 33: H=`Lb/gln`, G=`8.345`.
  - `QF-378HST` fila 33: H=`Lb/gln`, G=`8.345`.
  - `QF-549HST` fila 33: H=`Lb/gln`, G=`8.345`.
- `Densidad de Fluido`:
  - `QF-554H` fila 100: C=`Lb/Gln`, B=`8.33521` (fórmula=True).
  - `QF-545H` fila 98: C=`Lb/Gln`, B=`8.33606` (fórmula=True).
  - `QF-500H` fila 99: C=`Lb/Gln`, B=`8.33077` (fórmula=True).
  - `QF-378HST` fila 97: C=`Lb/Gln`, B=`8.32729` (fórmula=True).
  - `QF-549HST` fila 97: C=`Lb/Galn`, B=`8.32729` (fórmula=True).

## Fechas

Propiedad `created` del libro: `2017-09-06 19:13:28`. Propiedad `modified`: `2026-10-17 16:06:09`.

Celdas con tipo fecha, o fórmula con caché de tipo fecha. En la misma fila se cita el texto de A, de B y de E para situar la celda, sin interpretar el rótulo.

### QF-554H

- `B6`: constante/fórmula `=TODAY()`, caché `2026-10-17`. A=`Fecha:`, B=`=TODAY()`, E=`SLACOL R&D`. E de la fila anterior=``.
- `G189`: constante/fórmula `2017-08-07`, caché `2017-08-07`. A=``, B=`Simulación`, E=`Fecha Prueba de Pozo`. E de la fila anterior=``.
- `G195`: constante/fórmula `2017-08-10`, caché `2017-08-10`. A=`Entrada VSD`, B=``, E=`Fecha Predictivo`. E de la fila anterior=``.

### QF-545H

- `B6`: constante/fórmula `=TODAY()`, caché `2026-10-17`. A=`Fecha:`, B=`=TODAY()`, E=`SLACOL R&D`. E de la fila anterior=``.
- `G183`: constante/fórmula `2017-08-06`, caché `2017-08-06`. A=``, B=`Simulación`, E=`Fecha Prueba de Pozo`. E de la fila anterior=``.
- `G189`: constante/fórmula `2017-08-01`, caché `2017-08-01`. A=`Entrada VSD`, B=``, E=`Fecha Predictivo`. E de la fila anterior=``.

### QF-500H

- `B6`: constante/fórmula `=TODAY()`, caché `2026-10-17`. A=`Fecha:`, B=`=TODAY()`, E=`SLACOL R&D`. E de la fila anterior=``.
- `G181`: constante/fórmula `2017-08-07`, caché `2017-08-07`. A=``, B=`Simulación`, E=`Fecha Prueba de Pozo`. E de la fila anterior=``.
- `G187`: constante/fórmula `2017-08-01`, caché `2017-08-01`. A=`Entrada VSD`, B=``, E=`Fecha Predictivo`. E de la fila anterior=``.

### QF-378HST

- `B6`: constante/fórmula `=TODAY()`, caché `2026-10-17`. A=`Fecha:`, B=`=TODAY()`, E=`SLACOL R&D`. E de la fila anterior=``.
- `G179`: constante/fórmula `2017-08-07`, caché `2017-08-07`. A=``, B=`Simulación`, E=`Fecha Prueba de Pozo`. E de la fila anterior=``.
- `G185`: constante/fórmula `2017-08-01`, caché `2017-08-01`. A=`Entrada VSD`, B=``, E=`Fecha Predictivo`. E de la fila anterior=``.

### QF-549HST

- `B6`: constante/fórmula `2017-09-06`, caché `2017-09-06`. A=`Fecha:`, B=`2017-09-06`, E=`SLACOL R&D`. E de la fila anterior=``.
- `G179`: constante/fórmula `2017-08-07`, caché `2017-08-07`. A=``, B=`Simulación`, E=`Fecha Prueba de Pozo`. E de la fila anterior=``.
- `G185`: constante/fórmula `2017-08-01`, caché `2017-08-01`. A=`Entrada VSD`, B=``, E=`Fecha Predictivo`. E de la fila anterior=``.

En cuatro hojas, B6 es la fórmula `=TODAY()` y la caché es 2026-10-17. En `QF-549HST`, B6 es la constante de fecha 2017-09-06, la misma fecha calendario que `created` (la hora de `created` es 19:13:28; la celda está a medianoche).

Secuencia de las dos fechas cacheadas que están bajo los rótulos de la fila `Fecha Prueba de Pozo` / `Fecha Predictivo` (esos rótulos están en la fila anterior o en la columna E, según la hoja; aquí se usan las celdas de tipo fecha distintas de B6):

- `QF-554H`: `G189`=2017-08-07 (E de la fila=`Fecha Prueba de Pozo`, E fila anterior=``) y `G195`=2017-08-10 (E=`Fecha Predictivo`, E fila anterior=``).
- `QF-545H`: `G183`=2017-08-06 (E de la fila=`Fecha Prueba de Pozo`, E fila anterior=``) y `G189`=2017-08-01 (E=`Fecha Predictivo`, E fila anterior=``).
- `QF-500H`: `G181`=2017-08-07 (E de la fila=`Fecha Prueba de Pozo`, E fila anterior=``) y `G187`=2017-08-01 (E=`Fecha Predictivo`, E fila anterior=``).
- `QF-378HST`: `G179`=2017-08-07 (E de la fila=`Fecha Prueba de Pozo`, E fila anterior=``) y `G185`=2017-08-01 (E=`Fecha Predictivo`, E fila anterior=``).
- `QF-549HST`: `G179`=2017-08-07 (E de la fila=`Fecha Prueba de Pozo`, E fila anterior=``) y `G185`=2017-08-01 (E=`Fecha Predictivo`, E fila anterior=``).

En `QF-554H` la segunda de esas fechas es posterior a la primera. En las otras cuatro hojas, la fecha de la celda asociada en el perfil a la segunda posición es anterior a la primera. Eso es el orden leído. No se afirma que deban ir en un orden determinado: el libro no lo dice.

El título `Actividad de Revisión Equipos 10/08/2017` es texto, no un tipo fecha. Aparece en las cinco hojas.

No hay una columna temporal de muchas fechas (serie diaria u horaria) en este libro. El bloque `Measured` está ordenado por el número de la columna A, no por fechas.

## Datos faltantes

Celdas de `Cargo:`, `Correo:` y `Responsable:` y las cuatro celdas a su derecha (vista de fórmula):

### QF-554H

- `A6` `Fecha:` → `B6`=`=TODAY()`, `C6`=`Responsable:`, `D6`=``, `E6`=`SLACOL R&D`.
- `C6` `Responsable:` → `D6`=``, `E6`=`SLACOL R&D`, `F6`=``, `G6`=``.
- `D8` `Cargo:` → `E8`=``, `F8`=``, `G8`=``, `H8`=``.
- `D10` `Correo:` → `E10`=``, `F10`=``, `G10`=``, `H10`=``.

### QF-545H

- `A6` `Fecha:` → `B6`=`=TODAY()`, `C6`=``, `D6`=`Responsable:`, `E6`=`SLACOL R&D`.
- `D6` `Responsable:` → `E6`=`SLACOL R&D`, `F6`=``, `G6`=``, `H6`=``.
- `D8` `Cargo:` → `E8`=``, `F8`=``, `G8`=``, `H8`=``.
- `D10` `Correo:` → `E10`=``, `F10`=``, `G10`=``, `H10`=``.

### QF-500H

- `A6` `Fecha:` → `B6`=`=TODAY()`, `C6`=`Responsable:`, `D6`=``, `E6`=`SLACOL R&D`.
- `C6` `Responsable:` → `D6`=``, `E6`=`SLACOL R&D`, `F6`=``, `G6`=``.
- `D8` `Cargo:` → `E8`=``, `F8`=``, `G8`=``, `H8`=``.
- `D10` `Correo:` → `E10`=``, `F10`=``, `G10`=``, `H10`=``.

### QF-378HST

- `A6` `Fecha:` → `B6`=`=TODAY()`, `C6`=``, `D6`=`Responsable:`, `E6`=`SLACOL R&D`.
- `D6` `Responsable:` → `E6`=`SLACOL R&D`, `F6`=``, `G6`=``, `H6`=``.
- `D8` `Cargo:` → `E8`=``, `F8`=``, `G8`=``, `H8`=``.
- `D10` `Correo:` → `E10`=``, `F10`=``, `G10`=``, `H10`=``.

### QF-549HST

- `A6` `Fecha:` → `B6`=`2017-09-06`, `C6`=``, `D6`=`Responsable:`, `E6`=`SLACOL R&D`.
- `D6` `Responsable:` → `E6`=`SLACOL R&D`, `F6`=``, `G6`=``, `H6`=``.
- `D8` `Cargo:` → `E8`=``, `F8`=``, `G8`=``, `H8`=``.
- `D10` `Correo:` → `E10`=``, `F10`=``, `G10`=``, `H10`=``.

Pares con etiqueta, texto corto de unidad en la columna vecina prevista (C si la etiqueta está en A, H si está en E) y valor vacío en B o G:

- `QF-554H`: 1.
  - fila 236 `Temperatura Motor` (A-B), unidad `ºF`.
- `QF-545H`: 1.
  - fila 230 `Temperatura Motor` (A-B), unidad `ºF`.
- `QF-500H`: 1.
  - fila 227 `Temperatura Motor` (A-B), unidad `ºF`.
- `QF-378HST`: 1.
  - fila 225 `Temperatura Motor` (A-B), unidad `ºF`.
- `QF-549HST`: 1.
  - fila 225 `Temperatura Motor` (A-B), unidad `ºF`.

Un título de sección sin número al lado no entra en esta lista, porque no tiene texto de unidad en esa celda vecina. Los huecos del formulario sí entran en `pct_faltantes` de `resumen_columnas.csv`, porque ese porcentaje usa toda la columna hasta `max_row`.

## Errores de Excel

Celdas con error en la vista de fórmulas o en la caché: 13.

Están listadas con fórmula y referencias en `formulas_muestra.md`. Resumen:

- `QF-554H`: 0 celdas.
- `QF-545H`: 0 celdas.
- `QF-500H`: 0 celdas.
- `QF-378HST`: 0 celdas.
- `QF-549HST`: 13 celdas.

Todas las halladas son `#DIV/0!` en la caché de `QF-549HST`. La vista de fórmulas de esas celdas contiene una división; la caché de al menos una referencia usada como denominador es 0 en los casos listados en `formulas_muestra.md`. No se recalculó el libro para reproducir el error.

## Secuencias

Criterio de espaciamiento irregular en la columna A del bloque `Measured`: diferencia entre filas consecutivas ≤ 0, o mayor que 3 veces la mediana de esas diferencias, o positiva y menor que la mediana dividida por 3. El resultado por hoja está en `perfil_hojas.md`.

Criterio adicional, solo descriptivo, en las columnas B y C de ese bloque: pasos consecutivos con valor absoluto de la diferencia mayor que 180. También está en `perfil_hojas.md`.

En los puntos constantes de la curva `Caudal`/`Head`/`Brake`/`EFF`, la columna E y la monotonía de F se describen por hoja en `perfil_hojas.md`. Son 6 puntos por hoja en la lectura hecha; con n=6 no se aplicó Tukey.

## Rangos atípicos

Criterio: dentro de un solo bloque y una sola columna, cerca de Tukey. Con n≥4 y IQR>0, se marcan los valores estrictamente menores que Q1−1.5·IQR o estrictamente mayores que Q3+1.5·IQR. Los percentiles 5 y 95 se informan como descripción del bloque; los extremos de un percentil fijo no se tratan como hallazgo, porque un corte p05–p95 siempre deja fuera una fracción de los puntos.

El criterio se aplicó a las columnas numéricas B, C, D y E del bloque `Measured` de cada hoja. Los conteos y los ejemplos están en `perfil_hojas.md`, en la sección de cada hoja. No se aplicó a columnas enteras del formulario, porque mezclan etiquetas, unidades y cantidades distintas.

## Qué queda pendiente

- Definición de cada etiqueta, incluida la diferencia entre el texto de `Cluster:` y el de `Pozo:`.
- Si los textos de unidad con distinta grafía (`Lb/gln`, `Lb/galn`, `Lb/Galn`, `Lb/Gln`) son la misma unidad.
- Si el cero guardado en algunas condiciones de operación es un dato medido.
- Recálculo de Excel de las funciones no evaluadas aquí, y de los gráficos.

