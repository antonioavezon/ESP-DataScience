"""Estado de las fórmulas frente a este Excel. No aprueba la puerta G1.

Estados:
- utilizable: transcrita, reproduce la caché y no tiene consulta abierta que cambie el sentido.
- utilizable con reserva: transcrita y reproduce la caché; hay una consulta abierta (CT-xx).
- fuera del alcance actual: existe en las fuentes o en el libro y no se transcribe.
"""

FORMULAS = (
    {
        "id": "F-01",
        "celda": "Gravedad Oil @ 60ºF",
        "estado": "utilizable",
        "aplica": "gravedad específica a 60 °F desde API",
        "en_excel": "sí, API = 12 °API",
        "consulta": "",
    },
    {
        "id": "B98-temperatura",
        "celda": "Gravedad Oil @ T fondo",
        "estado": "utilizable con reserva",
        "aplica": "corrección de temperatura de la gravedad; el gradiente de la hoja la usa",
        "en_excel": "sí; constantes 0.00066, 0.0000003 y 15.556 sin definición fuera de la celda",
        "consulta": "CT-04",
    },
    {
        "id": "B100-B102",
        "celda": "Densidad de Fluido; Gradiente de Presión",
        "estado": "utilizable con reserva",
        "aplica": "densidad y gradiente tal como los escribe la hoja",
        "en_excel": "sí; BS&W rotulado % y usado como fracción; salida del gradiente rotulada psi*ft",
        "consulta": "CT-02",
    },
    {
        "id": "G96-PIP",
        "celda": "PIP en (ft)",
        "estado": "utilizable con reserva",
        "aplica": "cálculo directo desde la presión de sensor, no estimación sin sensor",
        "en_excel": "sí; el signo es el de la celda y entrega en el intake una presión mayor que la del sensor aunque el intake esté más somero",
        "consulta": "CT-03",
    },
    {
        "id": "G98-THP",
        "celda": "THP en (ft)",
        "estado": "utilizable",
        "aplica": "THP en psi dividido por el gradiente",
        "en_excel": "sí",
        "consulta": "",
    },
    {
        "id": "G100-Hazen",
        "celda": "Perdidad por Fricción",
        "estado": "utilizable con reserva",
        "aplica": "fricción de la hoja, exponente 4.8566, C = 120 dentro de la fórmula, longitud = TVD de descarga",
        "en_excel": "sí; el PDF usa 4.8655 y no se sustituyó",
        "consulta": "CT-05",
    },
    {
        "id": "G102-THD",
        "celda": "THD TOTAL",
        "estado": "utilizable con reserva",
        "aplica": "THD de la hoja = TVD descarga + fricción + THP − PIP",
        "en_excel": "sí; hereda las reservas de PIP y fricción",
        "consulta": "CT-03, CT-05",
    },
    {
        "id": "F-26-afinidad",
        "celda": "Curva de bomba a velocidad actual; límites a otra frecuencia",
        "estado": "utilizable con reserva",
        "aplica": "la hoja escala Q con f/f_curva, head con (f/f_curva)^2 por etapas, y los límites con f/60",
        "en_excel": "sí; se transcribe, no se verificó que aplique a esta bomba",
        "consulta": "CT-08",
    },
    {
        "id": "Q-interseccion",
        "celda": "Caudal a producir",
        "estado": "utilizable con reserva",
        "aplica": "intersección de la THD con la curva de bomba a velocidad actual (MATCH/INDEX, interpolación lineal)",
        "en_excel": "sí; reproduce las cinco celdas; no es validación independiente",
        "consulta": "CT-03, CT-08, CT-09",
    },
    {
        "id": "F-02-F-03",
        "celda": "—",
        "estado": "fuera del alcance actual",
        "aplica": "gradiente 0.433 del XLSM; la hoja usa 0.052 por densidad",
        "en_excel": "no es la fórmula escrita en BES-jun",
        "consulta": "",
    },
    {
        "id": "Potencia-motor-cable",
        "celda": "Potencia a consumir, potencia transferida, eficiencia, bloque de motor y cable",
        "estado": "fuera del alcance actual",
        "aplica": "cadena eléctrica y de potencia de la hoja, con constantes (0.0000018134, 119.826368, 0.746, 0.241...) sin documentar",
        "en_excel": "sí; no se transcribe hasta tener origen de las constantes",
        "consulta": "",
    },
    {
        "id": "F-36-F-40",
        "celda": "—",
        "estado": "fuera del alcance actual",
        "aplica": "Método B y observador de E1",
        "en_excel": "faltan parámetros; la hoja ya trae presión de sensor",
        "consulta": "",
    },
    {
        "id": "F-41-J64",
        "celda": "—",
        "estado": "fuera del alcance actual",
        "aplica": "cadena del XLSM, incluido el signo de J64",
        "en_excel": "no; es otro libro",
        "consulta": "",
    },
)

ESTADOS_VALIDOS = {"utilizable", "utilizable con reserva", "fuera del alcance actual"}
