# Validación integral de ingeniería y robustez · BES-jun

Fecha: 2026-10-20. Expediente: `datasets/en_uso/BES-jun`. El dataset no se movió. No se abrieron RB-1521 ni RB-IA-2191. Ninguna regla quedó aprobada para operación.

## 1. Descripción

El objetivo era endurecer la entrada del modo simulación y auditar las ecuaciones que el motor realmente ejecuta. Cada ecuación E-01 a E-10 se comprobó por tres vías distintas cuando había material para hacerlo: la formulación y su fuente, un oráculo numérico escrito en la prueba, y un comportamiento físico o un contraste externo.

No se alteraron el Excel, las mediciones, la caché, los exponentes, los coeficientes, las constantes ni la interpolación. Una discrepancia se registró. No se cambió la fórmula para que la prueba quedara en verde.

## 2. Estado inicial

Antes de editar, en `logs/respaldo_previo_a_validacion_integral/`:

- pytest: 123 passed en 12.36 s.
- Excel `entrada/BES_jun.xlsx`: SHA-256 `ccb5a738baea13321993e8b6eccefd6cac90ecda86b1c4b9181f897fcfa83f85`. Coincide con la referencia conocida.
- `fluidos_bes_jun.py`: `db856bb28e7b84123bde0dae62df091e73016afb3c747c301768b11ebbed43c8`.
- `balance_bes_jun.py`: `3a7fdb6fd279aa6f2cf27a35c0bff9f72f49a058ca7569f3c869af8642ed7532`.
- `interseccion_bes_jun.py`: `09a989177ab574c748ad151c9f355b4e83aa544680e68ac51c8cf71c5c5005b6`.
- `hipotesis_ct03.py`: `5742ff43016673f11d1e95777941207ed21c597b3af6b34b650292818445f08a`.

Esas cuatro huellas de código siguieron iguales después de la intervención. El motor pasó de 0.4.0 a 0.4.1. El contrato sigue en 1.3.0: la salida no ganó campos obligatorios. Lo que cambió es que una solicitud 1.3.0 mal formada, que antes podía llegar al cálculo, ahora se rechaza.

## 3. Robustez

`parametros_escenario.curva = [123]` no es una curva. `_no_numerico` aceptaba cualquier lista no vacía. El número llegaba a la intersección.

La curva de escenario quedó definida como lista de al menos dos objetos, cada uno solo con `caudal_bfpd` y `head_ft` finitos. No se exigen los seis puntos de la tabla de BES-jun. Sí se exigen las condiciones de la interpolación de esta hoja: caudales distintos, head estrictamente descendente y sin campos extra. Un punto suelto, una cadena, un NaN, un caudal repetido o un head que no baja se rechazan como `entrada_invalida`. El modelo no se llama. Los puntos de la ficha, que además traen `brake_hp` y `eff_numero`, no se cuelan en el escenario: EFF sigue sin respaldo de fabricante (CT-06).

Un parámetro numérico solo admite `valor` y `unidad`. `etapas` con `campo_inesperado` se rechaza. No hay conversión de unidades.

Los identificadores se rechazan si, al quitar espacios exteriores, quedan vacíos o si traían esos espacios. No se recorta en silencio un pozo para buscar otra ficha. `fecha_observacion` es `AAAA-MM-DD` o esa fecha con hora `Thh:mm:ss`, y si hay hora puede llevar `Z` o `±HH:MM`. Una fecha inválida de calendario no pasa. No se convierte la zona y no se usa `=TODAY()` del Excel como fecha de medición.

## 4. Entradas

Válidas, entre otras: caudal, frecuencia, presiones, temperatura, °API y BS&W, una sola vez, con la unidad canónica. En simulación, además, los parámetros de ficha con `{valor, unidad}` y la curva descrita arriba. Fecha nula o ISO. Identificadores sin espacios exteriores.

Inválidas, rechazadas antes del cálculo: null, booleanos, texto donde va un número, listas u objetos en el nombre de una variable, curva vacía, curva de un número, puntos incompletos, campos extra, caudales duplicados, head no descendente, valores no finitos, unidad ausente o distinta, identificador vacío o con espacios, fecha `23/10/2026` o `2026-13-40`, JSON inválido, clave repetida y solicitudes que superan el tamaño admitido.

El mensaje de error lleva código, campo, detalle y, cuando aplica, el tipo o la unidad esperados. No propone un promedio ni un valor de reemplazo. No incluye la traza.

## 5. Simulaciones

Una curva de dos puntos descendentes, con etapas declaradas en unidad `1`, se evalúa como escenario hipotético. El resultado marca `hipotetico`, lista `curva` entre los parámetros modificados y no autoriza una recomendación. La curva de la ficha en memoria no cambia. El Excel no cambia.

Si la curva está bien formada pero la THD no corta el tramo, el estado puede ser `no_evaluable`. Eso es distinto de `[123]`, que es `entrada_invalida` y deja `modelos` vacío.

## 6. Excepciones

`evaluar`, `evaluar_solicitud` y `evaluar_json` capturan una excepción no prevista, escriben el tipo y la traza en `logs/incidentes.jsonl` y responden `error_interno` con `incidente_id`. La respuesta no lleva ruta ni traza. La prueba sustituye `calcular_hoja` por un fallo controlado y comprueba ese límite. Las pruebas de curva mal formada comprueban, además, que `calcular_hoja` no llega a ejecutarse.

## 7. Inventario de ecuaciones

Ejecutadas por el motor:

| ID | Función | Origen |
|---|---|---|
| E-01 | `gravedad_especifica_api` | Celda de gravedad a 60 °F. `141.5/(131.5+API)`. |
| E-02 | `gravedad_oil_a_temperatura` | Celda B98. |
| E-03 | `densidad_lb_por_galon` | Celda B100. |
| E-04 | `gradiente_psi_por_ft` | Celda B102. Factor 0.052. |
| E-05 | `pip_en_ft` | Celda G96. |
| E-06 | `thp_en_ft` | Celda G98. |
| E-07 | `friccion_hazen_williams_ft` | Celda G100. Exponente 4.8566. C = 120. L = TVD de descarga. |
| E-08 | `thd_total_ft` | Celda G102. |
| E-09 | `curva_a_velocidad` | Filas de curva a la velocidad actual. |
| E-10 | `caudal_a_producir` | MATCH descendente e interpolación lineal. |

Auxiliares, fuera de la cadena de una evaluación pero usadas por el análisis o las reglas: elasticidad al 1 %, derivada por pie, escalamiento `Q(f)=Q(60)·f/60`, curvatura mínima del survey e interpolación de TVD. El punto fijo del cuaderno 04b no está en el motor. Potencia, cable y el gradiente 0.433 del XLSM no se transcriben.

El detalle de métodos, oráculos y tolerancias está en `docs/matriz_ecuaciones_BES-jun.md`.

## 8. Tres verificaciones independientes

No son tres lecturas de la misma caché.

- A. La fórmula se escribe en la prueba o en la matriz con su celda, sus unidades y sus hipótesis.
- B. El número esperado lo calcula una función local del archivo de test (`_sg_api`, `_sg_temperatura`, `_densidad`, `_pip_celda`, `_hazen`, `_interpolar`), no la función de producción.
- C. Monotonía, límites de mezcla, contraste SI, diferencia hidrostática en los cinco pozos, desigualdad frente al exponente del PDF, o la declaración explícita de que no hay medición de banco.

Archivo: `tests/test_verificacion_ecuaciones.py`.

## 9. Resultados físicos

E-01 cumple la definición API. A 10 °API la gravedad específica es 1. No hay densidad medida de este crudo.

E-02 reproduce la celda. En 15.556 °C no corrige. La pendiente local es −0.00066. Los coeficientes no tienen otra fuente (CT-04).

E-03 es una mezcla lineal de las densidades de los componentes si el número de BS&W ya es fracción. El rótulo % no se convirtió (CT-02).

E-04 usa 0.052. Con las constantes SI escritas en la prueba el factor es 0.051948. La diferencia es menor que 0.0001. El código sigue usando 0.052. No es un error dimensional de la implementación: es el redondeo de la celda, registrado como SCI-08.

E-05 reproduce la caché y no coincide con la hidrostática simple. En las cinco hojas el sensor está más profundo que el intake. La diferencia es 51.3 ft (QF-084), 38.6 ft (QF-301), 51.1 ft (QF-147), 41.2 ft (QF-005) y 41.1 ft (QF-306). CT-03 sigue abierta. La fórmula no se tocó.

E-06 convierte psi a ft dividiendo por el gradiente. Duplicar la presión duplica la altura.

E-07 cumple los exponentes 1.85 y 4.8566 y la proporcionalidad con la longitud. El exponente 4.8655 del PDF no da el mismo número. No hay una pérdida medida. CT-05.

E-08 cierra la suma con los signos escritos. Eso no valida los términos.

E-09, con razón 1.5, escala el caudal con la frecuencia y el head con el cuadrado y las etapas, y recupera el punto al invertir la transformación. No es un ensayo de bomba. CT-08.

E-10, en el tramo de 100 ft a 0 ft, devuelve 50 BFPD cuando la THD es 50 ft. Fuera de la tabla no extrapola. La fricción de dos caudales distintos no coincide, así que la intersección de la hoja no es hidráulicamente autoconsistente. CT-06 y CT-09.

## 10. Interpretaciones

Los cuadernos ya tratan el signo de PIP como ambigüedad abierta, no como un hecho cerrado. El cuaderno 05 dice que el signo opuesto mueve el PIP entre 38 y 51 ft y que la evidencia para elegir signo es mixta (dos hojas de cinco). Esa lectura se mantiene. Esta pasada añade la diferencia algebraica exacta `2·(TVD_sensor−TVD_intake)` y los cinco valores.

No se interpretó la elasticidad como incertidumbre, ni la reproducción de la caché como validación física, ni la simulación como predicción, ni la tabla EFF como curva de fabricante. Q* no se presenta como el caudal que el pozo va a producir.

El informe consolidado incorpora la cuantificación de las cinco hojas y remite a esta auditoría. Los doce cuadernos no se regeneraron: sus fuentes no cambiaron y siguen distinguiendo la transcripción de la consulta CT-03.

## 11. Reglas

| Regla | Estado | Dependencia |
|---|---|---|
| RC-BES-01 | `pendiente_validacion` | Límites escritos y Q ∝ f. CT-06 y CT-08. |
| RC-BES-02 | `pendiente_validacion` | Igual. |
| RC-BES-03 | `pendiente_validacion` | Igual. En las cinco hojas, con los datos registrados, es la que se activa. En QF-084 el máximo escalado a 63 Hz es 10500 BFPD. |
| RC-BES-04 | `no_evaluable` | CT-06. No usa CT-09. |

Los umbrales no se movieron. `recomendacion_operacional_autorizada` sigue en falso. Un escenario no aprueba una regla ni escribe la ficha.

## 12. AutoTest

- Línea base: 123 passed, 12.36 s, motor 0.4.0.
- Suite posterior, pytest y AutoTest: 151/151, 0 fallos, 0 omitidas, 13.198 s, 2026-10-20T20:30:05+00:00. Estado del reporte: aprobado.
- Pruebas nuevas: curvas y parámetros de escenario, fechas e identificadores, y las diez ecuaciones con oráculo independiente. Están en `tests/test_adversarial.py` y `tests/test_verificacion_ecuaciones.py`.
- Las 123 anteriores siguen aprobadas. No se relajó una aserción física para conseguirlo.

Comando, desde la raíz del expediente, con el entorno del repositorio:

```bash
PYTHONPATH=src /home/antonio/projects/HUC/.venv/bin/python -m evaluacion.autotest
```

El reporte queda en `logs/autotest_reporte.md`.

## 13. Integridad

Excel sin cambios: `ccb5a738baea13321993e8b6eccefd6cac90ecda86b1c4b9181f897fcfa83f85`, 329308 bytes. Las huellas de los tres módulos de fórmulas y de `hipotesis_ct03.py` son las de la línea base, citadas en la sección 2.

Informe PDF regenerado: `pdf/informes/informe_analisis_BES-jun.pdf`, SHA-256 `7457125b457fbf8ed446f7ca1af97ece98faa089ace9dfea959e4bcf98c9afbe`, 9 páginas.

Guía PDF: `pdf/informes/guia_integracion_BES-jun.pdf`, SHA-256 `b8b0342f89f7be9a20d3be2d39e8bc38e8da8796bda42f4e27d478f541211c7d`, 5 páginas.

Manifiesto: `integracion/manifiesto_version.json`. Software 0.4.1, contrato 1.3.0, motor 0.4.1, 151 pruebas, aprobación operacional en falso.

## 14. Documentación regenerada

- `reports/informe_analisis_BES-jun.md` y su HTML y PDF.
- `integracion/README.md`, esquemas, ejemplo de QF-084, diez plantillas y el PDF de la guía.
- `docs/matriz_ecuaciones_BES-jun.md`.
- `docs/incidencias_cientificas_BES-jun.md`.
- `docs/manifiesto_version_BES-jun.md`.

Los doce cuadernos, sus HTML y sus PDF no se volvieron a exportar. Siguen siendo los de la pasada anterior y su lectura de CT-03 coincide con esta auditoría.

## 15. Bloqueos

Siguen abiertas CT-01 a CT-10 y P-14. Las que esta pasada volvió a medir, sin cerrarlas:

- CT-03, signo de PIP. SCI-01.
- CT-05, exponente y longitud de la fricción. SCI-02.
- CT-02, unidad de BS&W. SCI-03.
- CT-04, coeficientes térmicos. SCI-04.
- CT-08, afinidad aplicada a los límites. SCI-05.
- CT-06, curva y EFF. SCI-06.
- CT-09, Q* frente al caudal medido. SCI-07.
- SCI-08, factor 0.052 frente a 0.051948. No sustituye la celda.

Ninguna de esas consultas se presentó como una prueba física aprobada. Tampoco impidieron declarar aprobada la suite informática.

## 16. Estado final

**Dictamen informático.** Aprobado para el contrato 1.3.0 y el motor 0.4.1. 151 pruebas, 0 fallos. Una entrada mal formada no ejecuta fórmulas, no deja una excepción sin identificador en la interfaz pública y no modifica el Excel ni la ficha. Una simulación no autoriza una operación.

**Dictamen científico.** Parcialmente verificado. La álgebra de E-01, E-06, E-08, E-09 y E-10 es conforme a la formulación escrita. E-02, E-03, E-04 y E-07 son conformes a la celda y quedan con validación experimental pendiente o con una diferencia de fuente registrada. E-05 tiene una discrepancia de signo cuantificada en los cinco pozos. Ninguna regla puede usarse como recomendación operacional aprobada.

Paquete de revisión: esta nota, `docs/matriz_ecuaciones_BES-jun.md`, `docs/incidencias_cientificas_BES-jun.md`, `tests/test_verificacion_ecuaciones.py`, `tests/test_adversarial.py`, `logs/autotest_reporte.md`, `integracion/manifiesto_version.json` y los contratos en `integracion/`.
