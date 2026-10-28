# Muestra de fórmulas — BES_jun

Perfilado de fórmulas. No es una predicción. Las fórmulas se citan desde el libro (`data_only=False`). El valor de al lado es la caché (`data_only=True`).

SHA-256 del archivo: `ccb5a738baea13321993e8b6eccefd6cac90ecda86b1c4b9181f897fcfa83f85`.

## Conteos

| Hoja | Celdas con fórmula | Caché nulo | Caché igual al texto de la fórmula | Coincidencias aritméticas simples | Desacuerdos aritméticos simples | Referencias simples coherentes con la celda citada | Referencias simples no coherentes |
|---|---:|---:|---:|---:|---:|---:|---:|
| `QF-554H` | 261 | 0 | 0 | 144 | 0 | 46 | 0 |
| `QF-545H` | 240 | 0 | 0 | 141 | 0 | 45 | 0 |
| `QF-500H` | 260 | 0 | 0 | 143 | 0 | 46 | 0 |
| `QF-378HST` | 263 | 0 | 0 | 147 | 0 | 46 | 0 |
| `QF-549HST` | 246 | 0 | 0 | 139 | 0 | 45 | 0 |

Totales: aritmética simple coherente con la caché = 714; desacuerdos = 0; fórmulas no evaluadas por tener función, hoja externa o referencia no numérica = 556. Referencias de una sola celda (`=B69`, `=+H361`, y similares) coherentes = 228; no coherentes = 0.

Una fórmula y su caché son lecturas distintas: la primera es texto que empieza por `=`, la segunda es el valor guardado por Excel. En todas las fórmulas leídas la caché existe y no es el texto de la fórmula.

## Funciones que aparecen en el texto de las fórmulas

Conteo de apariciones del nombre seguido de `(`, en las cinco hojas. No implica que la función se haya recalculado aquí.

| Función | Apariciones |
|---|---:|
| `INDEX` | 140 |
| `SQRT` | 91 |
| `AVERAGE` | 63 |
| `IF` | 45 |
| `MATCH` | 35 |
| `TODAY` | 4 |

## Patrones

Patrón = texto de la fórmula con cada número sustituido por `#`. Así, `E50` y `E51` caen en el mismo patrón. Se listan los patrones con 3 o más celdas, y además todo patrón que contenga `IF(`, `INDEX(`, `MATCH(`, `AVERAGE(`, `SQRT(` o `TODAY(` aunque sea único.

| Celdas | Patrón | Ejemplo (hoja, celda, fórmula, caché) |
|---:|---|---|
| 76 | `=B#` | `QF-554H` `B83` `=B69` → `63` |
| 48 | `=G#` | `QF-554H` `J88` `=G56` → `2500` |
| 40 | `=J#+#` | `QF-554H` `J143` `=J142+45` → `112.5` |
| 40 | `=M#+#` | `QF-554H` `M143` `=M142+45` → `112.5` |
| 36 | `=AVERAGE(D#:D#)` | `QF-554H` `D248` `=AVERAGE(D245:D247)` → `465` |
| 30 | `=E#*($J$#/$G$#)` | `QF-554H` `I72` `=E50*($J$69/$G$47)` → `0` |
| 30 | `=F#*(($J$#/$G$#)^#)*$H$#` | `QF-554H` `J72` `=F50*(($J$69/$G$47)^2)*$H$80` → `0` |
| 30 | `=G#*(($J$#/$G$#)^#)*$H$#` | `QF-554H` `K72` `=G50*(($J$69/$G$47)^3)*$H$80` → `0` |
| 30 | `=E#*($B$#/$G$#)` | `QF-554H` `A86` `=E50*($B$83/$G$47)` → `0` |
| 30 | `=F#*(($B$#/$G$#)^#)*$B$#` | `QF-554H` `B86` `=F50*(($B$83/$G$47)^2)*$B$46` → `3739.68` |
| 30 | `=G#*(($B$#/$G$#)^#)*$B$#` | `QF-554H` `C86` `=G50*(($B$83/$G$47)^3)*$B$46` → `153.385` |
| 27 | `=AVERAGE(F#:F#)` | `QF-554H` `F248` `=AVERAGE(F245:F247)` → `465` |
| 27 | `=+B#` | `QF-554H` `G361` `=+B18` → `2841.51` |
| 25 | `=H#` | `QF-554H` `C20` `=H365` → `2653.18` |
| 25 | `=J#*(I#/I#)` | `QF-554H` `J85` `=J88*(I85/I88)` → `1250` |
| 25 | `=K#*(I#/I#)^#` | `QF-554H` `K85` `=K88*(I85/I88)^2` → `821.5` |
| 25 | `=N#*(M#/M#)` | `QF-554H` `N85` `=N88*(M85/M88)` → `4000` |
| 25 | `=O#*(M#/M#)^#` | `QF-554H` `O85` `=O88*(M85/M88)^2` → `636` |
| 25 | `=R#*(Q#/Q#)` | `QF-554H` `R85` `=R88*(Q85/Q88)` → `5000` |
| 25 | `=S#*(Q#/Q#)^#` | `QF-554H` `S85` `=S88*(Q85/Q88)^2` → `477` |
| 25 | `=#+(#/#)` | `QF-554H` `J142` `=45+(45/2)` → `67.5` |
| 25 | `=C#` | `QF-554H` `B204` `=C171` → `242.634` |
| 25 | `=+H#+(((G#-G#)/(G#-G#))*(H#-H#))` | `QF-554H` `H361` `=+H363+(((G361-G363)/(G364-G363))*(H364-H363))` → `2644.78` |
| 25 | `=MATCH(G#,A#:A#,#)` | `QF-554H` `G362` `=MATCH(G361,A329:A384,1)` → `36` |
| 25 | `=INDEX(A#:A#,G#)` | `QF-554H` `G363` `=INDEX(A329:A384,G362)` → `2828` |
| 25 | `=INDEX(D#:D#,G#)` | `QF-554H` `H363` `=INDEX(D329:D384,G362)` → `2637` |
| 25 | `=INDEX(A#:A#,G#+#)` | `QF-554H` `G364` `=INDEX(A329:A384,G362+1)` → `2872` |
| 25 | `=INDEX(D#:D#,G#+#)` | `QF-554H` `H364` `=INDEX(D329:D384,G362+1)` → `2662.33` |
| 22 | `=D#*D#*SQRT(#)/#` | `QF-554H` `D201` `=D199*D197*SQRT(3)/1000` → `242.383` |
| 20 | `=#-(#/#)` | `QF-554H` `L147` `=150-(50/8)` → `143.75` |
| 15 | `=F#*B#` | `QF-554H` `K88` `=F51*B46` → `3286` |
| 15 | `=IF(G#>#,"Perdido",IF(G#<#,"Ganado"))` | `QF-554H` `F106` `=IF(G106>0,"Perdido",IF(G106<0,"Ganado"))` → `Perdido` |
| 11 | `=F#*F#*SQRT(#)/#` | `QF-554H` `F271` `=F262*F270*SQRT(3)/1000` → `216.757` |
| 10 | `=E#` | `QF-554H` `N88` `=E53` → `8000` |
| 10 | `=+K#+(((J#-J#)/(J#-J#))*(K#-K#))` | `QF-554H` `K94` `=+K96+(((J94-J96)/(J97-J96))*(K97-K96))` → `10535.2` |
| 10 | `=MATCH(J#,B#:B#,-#)` | `QF-554H` `J95` `=MATCH(J94,B86:B91,-1)` → `5` |
| 10 | `=INDEX(B#:B#,J#)` | `QF-554H` `J96` `=INDEX(B86:B91,J95)` → `2103.57` |
| 10 | `=INDEX(B#:B#,J#+#)` | `QF-554H` `J97` `=INDEX(B86:B91,J95+1)` → `584.325` |
| 10 | `=B#/B#` | `QF-554H` `G98` `=B75/B102` → `422.213` |
| 10 | `=K#` | `QF-554H` `B106` `=K94` → `10535.2` |
| 10 | `=K#-(#/#)` | `QF-554H` `K143` `=K142-(50/4)` → `237.5` |
| 10 | `=#+((#/#)*#)` | `QF-554H` `N143` `=150+((50/8)*3)` → `168.75` |
| 10 | `=+K#-((#/#)*#)` | `QF-554H` `K144` `=+K142-((50/8)*5)` → `218.75` |
| 10 | `=#+((#/#))` | `QF-554H` `L146` `=150+((50/4))` → `162.5` |
| 10 | `=B#*B#*SQRT(#)/#` | `QF-554H` `B271` `=B262*B270*SQRT(3)/1000` → `197.541` |
| 5 | `=+H#` | `QF-554H` `C18` `=+H361` → `2644.78` |
| 5 | `=(G#-#)/#.#` | `QF-554H` `G30` `=(G28-32)/1.8` → `65.5556` |
| 5 | `=#.#/(#.#+G#)` | `QF-554H` `B96` `=141.5/(131.5+G32)` → `0.986063` |
| 5 | `=(B#-((C#-C#)*B#))/B#` | `QF-554H` `G96` `=(B73-((C20-C24)*B102))/B102` → `1714.5` |
| 5 | `=INDEX(A#:A#,J#)` | `QF-554H` `K96` `=INDEX(A86:A91,J95)` → `10500` |
| 5 | `=INDEX(A#:A#,J#+#)` | `QF-554H` `K97` `=INDEX(A86:A91,J95+1)` → `13125` |
| 5 | `=B#-((#.#)*(G#-#.#))+((#.#*((G#-#.#)^#)))` | `QF-554H` `B98` `=B96-((0.00066)*(G30-15.556))+((0.0000003*((G30-15.556)^2)))` → `0.953813` |
| 5 | `=#.#*((G#*G#/#.#)+((#-G#)*B#))` | `QF-554H` `B100` `=8.33*((G26*G34/8.33)+((1-G26)*B98))` → `8.33521` |
| 5 | `=(#.#*((#/#)^#.#)*((B#/#.#)^#.#)*(#/(B#)^#.#))*(C#/#)` | `QF-554H` `G100` `=(2.083*((100/120)^1.85)*((B71/34.3)^1.85)*(1/(B38)^4.8566))*(C18/1000)` → `730.723` |
| 5 | `=B#*#.#` | `QF-554H` `B102` `=B100*0.052` → `0.433431` |
| 5 | `=C#+G#+G#-G#` | `QF-554H` `G102` `=C18+G100+G98-G96` → `2083.22` |
| 5 | `=B#-B#` | `QF-554H` `G106` `=B106-B71` → `234.167` |
| 5 | `=INDEX(C#:C#,J#)` | `QF-554H` `K106` `=INDEX(C86:C91,J105)` → `196.333` |
| 5 | `=INDEX(C#:C#,J#+#)` | `QF-554H` `K107` `=INDEX(C86:C91,J105+1)` → `214.739` |
| 5 | `=(B#-B#)*(#-G#)` | `QF-554H` `G108` `=(B106-B71)*(1-G26)` → `5.73708` |
| 5 | `=(B#*(#.#))*(G#/#.#)*(#.#*B#)*#.#/#*#.#` | `QF-554H` `B110` `=(B106*(0.0000018134))*(G102/3.281)*(119.826368*B100)*9.81/1000*1.341` → `159.379` |
| 5 | `=G#/B#` | `QF-554H` `G110` `=G106/B106` → `0.0222271` |
| 5 | `=(E#+E#)` | `QF-554H` `E129` `=(E127+E125)` → `204.58` |
| 5 | `=(E#/D#)/C#` | `QF-554H` `G133` `=(E129/D137)/C139` → `0.93515` |
| 5 | `=C#/#.#` | `QF-554H` `D137` `=C137/0.746` → `257.373` |
| 5 | `=E#*#.#/(G#*SQRT(#)*C#)*#/C#` | `QF-554H` `G137` `=E129*0.746/(G135*SQRT(3)*C141)*1000/C139` → `2975.73` |
| 5 | `=IF(G#=#,((#.#*G#)*(#+(#.#*(G#-#)))),IF(G#=#,((#.#*G#)*(#+(#.#*(G#-#)))),IF(G#=#,((#.#*G#)*(#+(#.#*(G#-#)))),"Seleccionar Calibre del Cable")))` | `QF-554H` `G141` `=IF(G38=1,((0.2413*G135)*(1+(0.00214*(G77-77)))),IF(G38=2,((0.2857*G135)*(1+(0.00214*(G77-77)))),IF(G38=4,((0.4583*G135)*(1+(0.00214*(G77-77)))),"Seleccionar Calibre del Cable")))` → `12.6239` |
| 5 | `=#-((#/#))` | `QF-554H` `K148` `=150-((50/4))` → `137.5` |
| 5 | `=#-(#/#*#)` | `QF-554H` `L148` `=150-(50/8*5)` → `118.75` |
| 5 | `=+J#+(#/#)` | `QF-554H` `J150` `=+J149+(45/4)` → `393.75` |
| 5 | `=+M#+(#/#)` | `QF-554H` `M150` `=+M149+(45/2)` → `405` |
| 5 | `=G#+(G#*B#/#)` | `QF-554H` `C157` `=G137+(G141*B22/1000)` → `3012` |
| 5 | `=+C#/C#` | `QF-554H` `D167` `=+C167/C161` → `6.34375` |
| 5 | `=(C#/(G#*SQRT(#))*#)+(G#*#/(SQRT(#)*G#))` | `QF-554H` `G167` `=(C175/(G159*SQRT(3))*1000)+(G165*1000/(SQRT(3)*G159))` → `249.633` |
| 5 | `=C#/D#*C#` | `QF-554H` `C169` `=C157/D167*C165` → `470.051` |
| 5 | `=(G#*G#*SQRT(#)/#/G#)` | `QF-554H` `G169` `=(G159*G167*SQRT(3)/1000/G163)` → `228.067` |
| 5 | `=G#*D#/C#` | `QF-554H` `C171` `=G135*D167/C165` → `242.634` |
| 5 | `=C#/C#` | `QF-554H` `C173` `=C171/C163` → `0.630219` |
| 5 | `=C#*C#*(SQRT(#))/#` | `QF-554H` `C175` `=C169*C171*(SQRT(3))/1000` → `197.541` |
| 5 | `=B#*B#*SQRT(#)*C#/#*#.#` | `QF-554H` `B215` `=B213*B211*SQRT(3)*C141/1000*0.85` → `154.477` |
| 5 | `=B#*B#*SQRT(#)/#/#.#` | `QF-554H` `B257` `=B256*B248*SQRT(3)/1000/0.93` → `223.162` |
| 5 | `=D#-D#` | `QF-554H` `D289` `=D257-D287` → `49.5187` |
| 5 | `=F#-F#` | `QF-554H` `F289` `=F257-F287` → `26.0914` |
| 4 | `=TODAY()` | `QF-554H` `B6` `=TODAY()` → `2026-10-17` |
| 4 | `=(#.#*(G#^#)+(#.#*(G#^#)-(#.#*(G#^#))+(#.#*(G#^#))+(#.#*G#)+(#.#)))*C#` | `QF-554H` `G135` `=(0.241*(G133^5)+(0.92*(G133^4)-(2.89*(G133^3))+(2.33*(G133^2))+(0.116*G133)+(0.281)))*C133` → `37.8653` |
| 4 | `=#.#*#` | `QF-554H` `D238` `=430.4*24` → `10329.6` |
| 3 | `=(D#*D#*SQRT(#)*C#/#*#.#)-(#+(G#*D#*SQRT(#)*C#/#*#.#))` | `QF-554H` `D215` `=(D213*D211*SQRT(3)*C141/746*0.85)-(8+(G141*D211*SQRT(3)*C141/746*0.85))` → `211.838` |
| 3 | `=#*#` | `QF-554H` `F238` `=434*24` → `10416` |
| 3 | `=D#*D#*SQRT(#)/#/#.#` | `QF-554H` `D257` `=D256*D248*SQRT(3)/1000/0.93` → `261.54` |
| 2 | `=F#*F#*SQRT(#)/#/#.#` | `QF-554H` `F257` `=F256*F248*SQRT(3)/1000/0.93` → `241.332` |
| 2 | `=D#*D#*SQRT(#)*C#/#*#.#-#` | `QF-378HST` `D205` `=D203*D201*SQRT(3)*C135/1000*0.9-8` → `90.1983` |

Filas de patrón mostradas: 91. Patrones distintos en total: 93.

## Diferencia de patrones entre hojas

Se compara el conteo del patrón normalizado. Un desplazamiento de filas no cambia el patrón. Una diferencia de conteo indica que esa forma de fórmula no está repetida el mismo número de veces.

| Patrón | QF-554H | QF-545H | QF-500H | QF-378HST | QF-549HST |
|---|---:|---:|---:|---:|---:|
| `=B#` | 15 | 15 | 16 | 15 | 15 |
| `=G#` | 9 | 9 | 10 | 10 | 10 |
| `=AVERAGE(D#:D#)` | 9 | 0 | 9 | 9 | 9 |
| `=AVERAGE(F#:F#)` | 9 | 0 | 9 | 9 | 0 |
| `=+B#` | 5 | 6 | 5 | 6 | 5 |
| `=D#*D#*SQRT(#)/#` | 4 | 4 | 5 | 5 | 4 |
| `=F#*F#*SQRT(#)/#` | 2 | 2 | 3 | 3 | 1 |
| `=TODAY()` | 1 | 1 | 1 | 1 | 0 |
| `=(#.#*(G#^#)+(#.#*(G#^#)-(#.#*(G#^#))+(#.#*(G#^#))+(#.#*G#)+(#.#)))*C#` | 1 | 1 | 1 | 0 | 1 |
| `=#.#*#` | 1 | 0 | 0 | 3 | 0 |
| `=(D#*D#*SQRT(#)*C#/#*#.#)-(#+(G#*D#*SQRT(#)*C#/#*#.#))` | 1 | 1 | 1 | 0 | 0 |
| `=#*#` | 1 | 0 | 1 | 1 | 0 |
| `=D#*D#*SQRT(#)/#/#.#` | 1 | 1 | 0 | 0 | 1 |
| `=+G#` | 2 | 0 | 0 | 0 | 0 |
| `=F#*F#*SQRT(#)/#/#.#` | 1 | 1 | 0 | 0 | 0 |
| `=D#*D#*SQRT(#)*C#/#*#.#-#` | 0 | 0 | 0 | 1 | 1 |
| `=+G#*C#` | 0 | 0 | 0 | 1 | 0 |

## Muestras con dirección de celda

Una muestra real por familia, tomada de la hoja donde aparece. Si la fórmula es larga, se corta a 300 caracteres en esta lista; el patrón completo está en la tabla anterior cuando entra en el límite de esa tabla.

### TODAY

- `QF-554H` `B6`: `=TODAY()`
  - Caché: `2026-10-17`.
- `QF-545H` `B6`: `=TODAY()`
  - Caché: `2026-10-17`.
- `QF-500H` `B6`: `=TODAY()`
  - Caché: `2026-10-17`.
- `QF-378HST` `B6`: `=TODAY()`
  - Caché: `2026-10-17`.

### IF

- `QF-554H` `F106`: `=IF(G106>0,"Perdido",IF(G106<0,"Ganado"))`
  - Caché: `Perdido`.
- `QF-554H` `F108`: `=IF(G108>0,"Perdido",IF(G108<0,"Ganado"))`
  - Caché: `Perdido`.
- `QF-554H` `F110`: `=IF(G106>0,"Perdido",IF(G106<0,"Ganado"))`
  - Caché: `Perdido`.
- `QF-554H` `G141`: `=IF(G38=1,((0.2413*G135)*(1+(0.00214*(G77-77)))),IF(G38=2,((0.2857*G135)*(1+(0.00214*(G77-77)))),IF(G38=4,((0.4583*G135)*(1+(0.00214*(G77-77)))),"Seleccionar Calibre del Cable")))`
  - Caché: `12.6239`.

### INDEX

- `QF-554H` `J96`: `=INDEX(B86:B91,J95)`
  - Caché: `2103.57`.
- `QF-554H` `K96`: `=INDEX(A86:A91,J95)`
  - Caché: `10500`.
- `QF-554H` `J97`: `=INDEX(B86:B91,J95+1)`
  - Caché: `584.325`.
- `QF-554H` `K97`: `=INDEX(A86:A91,J95+1)`
  - Caché: `13125`.

### MATCH

- `QF-554H` `J95`: `=MATCH(J94,B86:B91,-1)`
  - Caché: `5`.
- `QF-554H` `J105`: `=MATCH(J104,B86:B91,-1)`
  - Caché: `5`.
- `QF-554H` `G362`: `=MATCH(G361,A329:A384,1)`
  - Caché: `36`.
- `QF-554H` `G366`: `=MATCH(G365,A329:A384,1)`
  - Caché: `36`.

### AVERAGE

- `QF-554H` `D248`: `=AVERAGE(D245:D247)`
  - Caché: `465`.
- `QF-554H` `F248`: `=AVERAGE(F245:F247)`
  - Caché: `465`.
- `QF-554H` `D252`: `=AVERAGE(D249:D251)`
  - Caché: `268`.

### SQRT

- `QF-554H` `G137`: `=E129*0.746/(G135*SQRT(3)*C141)*1000/C139`
  - Caché: `2975.73`.
- `QF-554H` `G167`: `=(C175/(G159*SQRT(3))*1000)+(G165*1000/(SQRT(3)*G159))`
  - Caché: `249.633`.
- `QF-554H` `G169`: `=(G159*G167*SQRT(3)/1000/G163)`
  - Caché: `228.067`.

### aritmética de curva (potencia y cociente)

- `QF-554H` `J72`: `=F50*(($J$69/$G$47)^2)*$H$80`
  - Caché: `0`.
- `QF-554H` `K72`: `=G50*(($J$69/$G$47)^3)*$H$80`
  - Caché: `0`.
- `QF-554H` `J73`: `=F51*(($J$69/$G$47)^2)*$H$80`
  - Caché: `0`.

### referencia simple

- `QF-554H` `C18`: `=+H361`
  - Caché: `2644.78`.
- `QF-554H` `C20`: `=H365`
  - Caché: `2653.18`.
- `QF-554H` `C22`: `=H369`
  - Caché: `2663.32`.
- `QF-554H` `C24`: `=H373`
  - Caché: `2678.82`.

## Fórmula frente a valor cacheado

Comprobación local, no un recálculo de Excel:

- Si la fórmula solo tiene operaciones `+ - * /`, paréntesis y referencias a celdas con caché numérica, se evaluó esa expresión y se comparó con la caché (tolerancia relativa 1e-6, con suelo absoluto 1e-6).
- Resultado: 714 coincidencias, 0 desacuerdos.
- `TODAY()`, `IF`, `INDEX`, `MATCH`, `AVERAGE` y `SQRT` quedan fuera de esa cuenta.

No hubo desacuerdos en el subconjunto aritmético simple.

Las referencias de una sola celda que se pudieron comparar coinciden con la caché de la celda citada. Esa comparación incluye fórmulas como `=B69` y `=+H361`. También entran en el conteo aritmético cuando el operando es numérico.

## Errores de Excel en la caché

Celdas cuyo valor de fórmula o de caché contiene un error de Excel. Se listan las referencias que aparecen en la fórmula y la caché de esas referencias, sin atribuir una causa distinta de lo que se ve.

- `QF-549HST` `D237`: fórmula `=AVERAGE(D234:D236)`
  - Caché: `#DIV/0!`.
  - Referencias leídas en la caché: `D234`=``, `D236`=``.
- `QF-549HST` `D241`: fórmula `=AVERAGE(D238:D240)`
  - Caché: `#DIV/0!`.
  - Referencias leídas en la caché: `D238`=``, `D240`=``.
- `QF-549HST` `D245`: fórmula `=AVERAGE(D242:D244)`
  - Caché: `#DIV/0!`.
  - Referencias leídas en la caché: `D242`=``, `D244`=``.
- `QF-549HST` `D246`: fórmula `=D245*D237*SQRT(3)/1000/0.93`
  - Caché: `#DIV/0!`.
  - Referencias leídas en la caché: `D245`=`#DIV/0!`, `D237`=`#DIV/0!`.
- `QF-549HST` `D251`: fórmula `=AVERAGE(D248:D250)`
  - Caché: `#DIV/0!`.
  - Referencias leídas en la caché: `D248`=``, `D250`=``.
- `QF-549HST` `D255`: fórmula `=AVERAGE(D252:D254)`
  - Caché: `#DIV/0!`.
  - Referencias leídas en la caché: `D252`=``, `D254`=``.
- `QF-549HST` `D259`: fórmula `=AVERAGE(D256:D258)`
  - Caché: `#DIV/0!`.
  - Referencias leídas en la caché: `D256`=``, `D258`=``.
- `QF-549HST` `D260`: fórmula `=D251*D259*SQRT(3)/1000`
  - Caché: `#DIV/0!`.
  - Referencias leídas en la caché: `D251`=`#DIV/0!`, `D259`=`#DIV/0!`.
- `QF-549HST` `D265`: fórmula `=AVERAGE(D262:D264)`
  - Caché: `#DIV/0!`.
  - Referencias leídas en la caché: `D262`=``, `D264`=``.
- `QF-549HST` `D269`: fórmula `=AVERAGE(D266:D268)`
  - Caché: `#DIV/0!`.
  - Referencias leídas en la caché: `D266`=``, `D268`=``.
- `QF-549HST` `D273`: fórmula `=AVERAGE(D270:D272)`
  - Caché: `#DIV/0!`.
  - Referencias leídas en la caché: `D270`=``, `D272`=``.
- `QF-549HST` `D274`: fórmula `=D273*D265*SQRT(3)/1000`
  - Caché: `#DIV/0!`.
  - Referencias leídas en la caché: `D273`=`#DIV/0!`, `D265`=`#DIV/0!`.
- `QF-549HST` `D276`: fórmula `=D246-D274`
  - Caché: `#DIV/0!`.
  - Referencias leídas en la caché: `D246`=`#DIV/0!`, `D274`=`#DIV/0!`.

## Lectura que no se hizo

- No se recalcularon INDEX/MATCH, IF, AVERAGE, SQRT ni TODAY.
- No se abrió el libro en Excel en esta pasada.
- Los gráficos siguen dependiendo de los rangos citados en las series; no se comprobó que el dibujo coincida con esos rangos.

