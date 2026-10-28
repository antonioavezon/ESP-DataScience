# Trazabilidad de ecuaciones

Estado: borrador para revisión. Los identificadores F-xx son los del Anexo A de `trabajo2.md`. La expresión se copia de la fuente. Si una unidad no está en la fuente, se dice.

Los cuatro DOCX de ecuaciones son el mismo archivo. Abajo se cita como E1.

## Comparación breve

| Tema | E1 | X1 «Prueba Sesnorless» y hojas hermanas | BES-jun | PDF R1 |
|---|---|---|---|---|
| PIP | `PIP = THP + ρ·g·Δz + ΔP_tub − ΔP_pump` (§4.7) | J58 = `(L41 − L55) * 0.433`; otra celda N58 usa 13600 | `(P_sensor − (TVD_intake − TVD_sensor) * gradiente) / gradiente`, en ft | No calcula PIP sensorless |
| Caudal | Incógnita de `F(Q) = P_in − P_in,pred = 0` | Dato o `Q_prueba * Hz/60` | Dato de la hoja, a veces `número*24` | Ejemplo 340 m³/d |
| Fricción | `k_f · Q²` | Darcy con `f = 64/Re` aunque el Re sea alto (H-08 del plan) | Hazen-Williams con exponente 4.8566 y C=120 | Hazen-Williams con exponente 4.8655, página 2 |
| Curva de bomba | `H0(Q)` y `η0(Q)` del fabricante, no incluidas | Puntos escritos a mano (54 ft/etapa, 62 %, 1.4 HP) | Tabla de 6 puntos a 60 Hz | DX-3000, ejemplo de diseño |
| Unidades internas pedidas | SI (Pa, m³/s, W), §7 | psi, ft, bpd, hp | psi, ft, BFPD, hp, y rótulos mezclados | m, kg/cm², m³/d |

No se unificó ninguna de esas diferencias.

## F-01 · Gravedad específica

- **Fuente:** X1 J4 en todas las hojas de datos; BES-jun, celda «Gravedad Oil @ 60ºF» (`QF-554H!B96` = `141.5/(131.5+G32)`).
- **Expresión:** `γ = 141.5 / (131.5 + °API)`.
- **Variables:** °API, gravedad específica adimensional. La tabla de E1 no redefine esta cuenta; la planilla sí.
- **Unidades:** °API de entrada. Salida adimensional.
- **Supuestos escritos:** ninguno adicional en la celda.
- **Dominio:** denominador distinto de cero. El código rechaza °API ≤ −131.5.
- **¿Con datos de BES-jun?** Sí. API = 12 en las cinco hojas.
- **Comprobación:** `141.5/143.5 = 0.9860627177700348`, igual al valor cacheado.
- **Diferencias:** ninguna entre X1 y BES-jun en esta expresión.

## Corrección de gravedad con temperatura · sin F-xx en el anexo

- **Fuente:** `QF-554H!B98` y la celda equivalente de las otras hojas.
- **Expresión:** `sg - 0.00066*(T - 15.556) + 0.0000003*(T - 15.556)^2`. T es la celda de temperatura en °C.
- **Unidades:** la entrada de temperatura está rotulada °C. Las tres constantes no tienen unidad escrita fuera de la fórmula.
- **Dominio:** no declarado.
- **Comprobación:** entra en la cadena que reproduce el gradiente usado por el balance cacheado.
- **Pendiente:** origen de 0.00066, 0.0000003 y 15.556.

## Densidad y gradiente de BES-jun · relacionadas con F-02 y F-03, no iguales

- **Densidad, `QF-554H!B100`:** `8.33*((BSW*ρ_agua/8.33)+((1-BSW)*sg_T))`. Salida rotulada Lb/Gln.
- **Gradiente, `QF-554H!B102`:** `densidad * 0.052`. Salida rotulada `psi*ft`.
- **F-02** es `ρ [lb/ft³] = γ · 62.4`. **F-03** es `gradiente = γ · 0.433`. BES-jun no usa esas dos expresiones.
- **BS&W:** rótulo «%»; la resta `(1-BSW)` solo cierra como fracción si el número ya está entre 0 y 1. No se convirtió.
- **Implementable:** sí, como transcripción. Hecho en `fluidos_bes_jun.py`.

## F-26 · Afinidad

- **Fuente E1 §4.2:** `λ = N/N0`, `Q* = Q/λ`, `H_ideal = λ² · H0(Q*)`, `η = η0(Q*)`.
- **Fuente BES-jun:** `Q = Q60 * (f/f60)`, `H = H60 * (f/f60)^2 * etapas`, `HP = HP60 * (f/f60)^3 * etapas`. Ejemplo `QF-554H!A86:C86`.
- **Diferencia:** E1 no multiplica la altura de una etapa por el número de etapas dentro de la misma línea; BES-jun sí, en la celda de cabeza. El BHP ∝ N³ está en el plan como extensión, no como línea literal de E1 §4.2.
- **Esta iteración:** no se reimplementó la afinidad como función del motor. Las celdas quedan documentadas. El gráfico usa los puntos a 60 Hz, sin desplazarlos.

## F-20 y la fricción de BES-jun

- **PDF, página 2:** `F [ft/1000 ft] = 2.083 · (100/C)^1.85 · (Q/34.3)^1.85 / ID^4.8655`, con C = 120 en el ejemplo. El texto dice que Hazen-Williams aplica a agua a 20 °C.
- **BES-jun, `QF-554H!G100`:** el mismo arreglo con exponente **4.8566**, C = 120 escrito en la fórmula, Q = caudal de operación en BFPD, ID en pulgadas, y el resultado se multiplica por `TVD_descarga/1000`.
- **Diferencia:** el exponente no coincide. La longitud es la TVD de descarga, no una longitud de tubing medida. El fluido de la hoja no es agua a 20 °C (API 12, temperatura de fondo 144 °F o 150 °F).
- **Comprobación:** con Q = 10301 BFPD, ID = 2.996 in y TVD = 2644.7774613636366 ft, el código reproduce el cache 730.7231971339377 ft.
- **X1:** no usa Hazen-Williams. Usa `f·ρ·V²/(2·g·D)/144` con `f = 64/Re`.

## PIP en ft de BES-jun · no es F-38 ni F-41

- **Expresión:** `(P_sensor - ((TVD_intake - TVD_sensor) * gradiente)) / gradiente`.
- **Fuente:** `QF-554H!G96`. En las otras hojas cambia la fila, no la forma.
- **Unidades:** presión en psi, TVD en ft, gradiente en la unidad de la celda B102, salida en ft.
- **Supuesto no escrito:** que restar esas TVD corrige la presión del sensor a la admisión. F-12 del plan escribe la corrección con el signo contrario si el sensor está más profundo: `PIP = P_sensor - gradiente * (Z_sensor - Z_intake)`. La celda hace `P_sensor - gradiente * (Z_intake - Z_sensor)`. En QF-084 el sensor está más profundo (TVD 2678.82 ft frente a intake 2653.18 ft) y el cache da 1714.50 ft. El código conserva el signo de la celda. La prueba `test_signo_de_pip_es_el_de_la_celda_y_no_el_opuesto` fija esa diferencia.
- **No es predicción:** la presión de sensor es una entrada.

## THD TOTAL de BES-jun · emparentado con F-22, no igual

- **Expresión de la hoja:** `TVD_descarga + fricción_ft + THP_ft - PIP_ft`.
- **F-22 / PDF página 2:** `TDH = Pbdp + Pcf + Nd`.
- **Diferencia:** la hoja usa la TVD de la descarga donde el PDF usa el nivel dinámico, y resta el PIP en ft. El nombre en la hoja es THD TOTAL, con el rótulo «Perdidad por Fricción».
- **Comprobación:** el cache de las cinco hojas se reproduce al encadenar fluido y balance.

## F-36 a F-39 · Modelo algebraico de E1

- **F-36:** `P_in,pred = P_hyd / (η_p · η_em) + P_loss(N)`.
- **F-37:** `P_loss = a0 + a1·N + a2·N²`.
- **F-38:** `PIP = THP + ρ·g·Δz + k_f·Q² − ρ·g·H`.
- **F-39:** `F(Q) = P_in - P_in,pred = 0`, bisección en un rango.
- **Unidades de la tabla de E1:** W, rpm, m³/s, m, Pa. `g = 9.80665 m/s²`. `k_g` entre 0 y 0.4 en el ejemplo `C_H = 1 - k_g`. `β ≈ 1` está escrito con el signo de aproximado.
- **¿Con BES-jun?** No como sistema cerrado. Faltan coeficientes de `P_loss`, `k_f`, `η_em` y la función `H0(Q)` aprobada. Hay voltaje, corriente y factor de potencia en otras filas de la hoja; no se armaron como `P_in` de E1 porque la cadena que la hoja calcula es otra.
- **Prueba numérica en E1:** no hay ejemplo numérico en el DOCX.
- **Estado:** no implementadas en esta iteración.

## F-41 · PIP inferido de X1

- **Expresión:** `(TDH_ft - H_ft) * 0.433` en J58. Cache de la hoja Prueba Sesnorless: 670.78075548892048 psi.
- **Otra celda, N58:** `J41 - (J55*13600*J9)/J12`, cache 1423.351245356323. El plan marca el 13600 como hallazgo H-11.
- **No se aplicó a BES-jun.** Son libros distintos.

## F-42 y el artículo

`ε = |PIP_est − PIP_ref| / PIP_ref · 100` es la métrica del artículo. La mediana 4.3 % es de otro campo y otros pozos. No se calculó sobre BES-jun.

## Revisión de ecuaciones del XLSM

[Ecuaciones y fuentes](731c493b-cfa7-4628-be37-8155d2b8a000) dejó el inventario en `logs/notas_agente_dominio.md`. Confirma que los cuatro DOCX son el mismo archivo y que la hoja `Prueba Sesnorless` no calcula el PIP de E1. Añade un pendiente que esta trazabilidad no había separado: `J64` es `=J58+((C11-C29)*J9)` (signo más, caché 757.22 psi) y el dibujo de la misma hoja escribe el Pwf inferido con signo menos. `J23` sí usa el signo menos. No se eligió un signo. Esas celdas pertenecen al XLSM, no a BES-jun.

## Estado frente al Excel activo BES-jun

Esta tabla no aprueba la puerta G1. Dice qué hace el expediente `datasets/en_uso/BES-jun/` con cada expresión. La misma lista está en `datasets/en_uso/BES-jun/src/analisis/catalogo_bes_jun.py`.

| ID | Estado | Variables en BES-jun | Discrepancia que no bloquea el resto |
|---|---|---|---|
| F-01 | utilizable | API = 12 °API | Ninguna con el XLSM en esta expresión |
| B98, corrección de temperatura | requiere aclaración | Temperatura de fondo en °C | Constantes 0.00066, 0.0000003 y 15.556 sin definición fuera de la celda. Se transcribe la celda |
| B100 y B102 | utilizable | BS&W, densidad de agua, gravedad | BS&W rotulado «%» y usado como fracción. No es F-02 ni F-03 |
| G96, PIP en ft | utilizable | Presión de sensor, TVD, gradiente | El signo es el de la celda y no el de la analogía F-12 |
| G100, Hazen-Williams | utilizable | Caudal BFPD, ID in, TVD de descarga | Exponente 4.8566 en la hoja y 4.8655 en el PDF |
| G102, THD | utilizable | TVD, fricción, THP en ft, PIP en ft | El PDF define TDH con nivel dinámico, no con esta resta |
| F-02 y F-03 | fuera del alcance actual | No son la fórmula de la hoja | Gradiente 0.433 del XLSM |
| F-26, afinidad | fuera del alcance actual | Celdas a 60 Hz | No se usa para simular otra fecha |
| F-36 a F-40 | fuera del alcance actual | Faltan parámetros | La hoja ya trae presión de sensor |
| F-41 y J64 | fuera del alcance actual | Pertenecen al XLSM | Signo de J64 sin resolver; no se aplica aquí |

## VBA

El XLSM contiene un proyecto VBA. No se ejecutó. El plan dice que la macro escribe un Pwf de ejemplo en J21. Esa celda, en la lectura estática, tiene el valor 735.42166666666662. No se volvió a calcular con la macro.
