"""Fórmulas de fluido transcritas desde la planilla BES-jun.

No corrigen la planilla. Donde la unidad escrita y el uso aritmético
difieren, la función sigue la aritmética de la celda y deja la diferencia
como advertencia del llamador.
"""

from __future__ import annotations

from modelo_deterministico.resultado import Resultado


def gravedad_especifica_api(api_deg: float) -> float:
    """Gravedad específica del crudo a 60 °F.

    Fórmula F-01: gamma = 141.5 / (131.5 + API).
    Fuente: «Copia de FINAL BES-jun.xlsx», celda de «Gravedad Oil @ 60ºF»
    (p. ej. QF-554H!B96) y XLSM J4.
    Entrada: api_deg en °API. Salida: adimensional.
    """
    return 141.5 / (131.5 + api_deg)


def gravedad_oil_a_temperatura(sg_60: float, temperatura_c: float) -> float:
    """Corrección de gravedad específica escrita en BES-jun.

    Expresión de la celda, sin reinterpretar constantes:
    sg_T = sg_60 - 0.00066*(T - 15.556) + 0.0000003*(T - 15.556)^2
    Fuente: QF-554H!B98 y la celda equivalente de las otras hojas.
    T en °C. Las constantes 0.00066, 0.0000003 y 15.556 no tienen
    otra definición en los documentos leídos.
    """
    delta = temperatura_c - 15.556
    return sg_60 - (0.00066 * delta) + (0.0000003 * (delta**2))


def densidad_lb_por_galon(
    bsw_como_fraccion: float,
    densidad_agua_lb_gal: float,
    sg_oil_t: float,
) -> float:
    """Densidad de mezcla tal como la escribe la hoja.

    8.33 * ((BSW * densidad_agua / 8.33) + (1 - BSW) * sg_oil_T)
    Fuente: QF-554H!B100. Salida rotulada en la hoja como Lb/Gln.
    BSW entra como el número que la fórmula multiplica: la hoja lo usa
    como fracción aunque la celda de unidad diga «%».
    """
    return 8.33 * (
        (bsw_como_fraccion * densidad_agua_lb_gal / 8.33)
        + ((1.0 - bsw_como_fraccion) * sg_oil_t)
    )


def gradiente_psi_por_ft(densidad_lb_gal: float) -> float:
    """Gradiente = densidad_lb/gal * 0.052.

    Fuente: QF-554H!B102. La hoja rotula la salida como «psi*ft».
    El factor 0.052 está escrito en la celda; no se sustituye por 0.433/8.34.
    """
    return densidad_lb_gal * 0.052


def evaluar_fluido(
    api_deg: float | None,
    temperatura_c: float | None,
    bsw_numero: float | None,
    densidad_agua_lb_gal: float | None,
) -> Resultado:
    """Cadena gravedad → densidad → gradiente, o estado no calculable."""
    entradas = {
        "api_deg": {"valor": api_deg, "unidad": "°API", "origen": "celda API de la hoja"},
        "temperatura_c": {"valor": temperatura_c, "unidad": "°C", "origen": "celda Temperatura de fondo en °C"},
        "bsw_numero": {
            "valor": bsw_numero,
            "unidad": "número de la celda; la hoja lo usa como fracción y rotula %",
            "origen": "celda BS&W",
        },
        "densidad_agua_lb_gal": {
            "valor": densidad_agua_lb_gal,
            "unidad": "lb/gal según el rótulo de la hoja",
            "origen": "celda Densidad del Agua",
        },
    }
    faltan = [k for k, v in entradas.items() if v["valor"] is None]
    if faltan:
        return Resultado(
            estado="no_calculable",
            motivo="Faltan entradas esenciales del fluido: " + ", ".join(faltan),
            entradas=entradas,
            ecuaciones=["F-01", "BES-jun densidad B100", "BES-jun gradiente B102"],
            alertas=["dato_faltante"],
        )
    if api_deg <= -131.5:
        return Resultado(
            estado="no_calculable",
            motivo="°API deja el denominador de F-01 en cero o negativo.",
            entradas=entradas,
            alertas=["fuera_de_dominio"],
        )
    sg = gravedad_especifica_api(api_deg)
    sg_t = gravedad_oil_a_temperatura(sg, temperatura_c)
    rho = densidad_lb_por_galon(bsw_numero, densidad_agua_lb_gal, sg_t)
    grad = gradiente_psi_por_ft(rho)
    advertencias = []
    if bsw_numero < 0 or bsw_numero > 1:
        advertencias.append(
            "El número de BS&W está fuera de 0 a 1. La fórmula lo usa como fracción; "
            "la celda de unidad dice «%». No se convirtió."
        )
    return Resultado(
        estado="calculable",
        motivo="Cadena de fluido transcrita de la hoja y evaluada con las entradas indicadas.",
        entradas=entradas,
        resultados={
            "sg_60": {"valor": sg, "unidad": "adimensional", "formula": "F-01"},
            "sg_temperatura": {
                "valor": sg_t,
                "unidad": "adimensional",
                "formula": "BES-jun B98",
            },
            "densidad_lb_gal": {"valor": rho, "unidad": "lb/gal", "formula": "BES-jun B100"},
            "gradiente_psi_ft": {"valor": grad, "unidad": "psi/ft", "formula": "BES-jun B102"},
        },
        ecuaciones=["F-01", "BES-jun B98", "BES-jun B100", "BES-jun B102"],
        advertencias=advertencias,
    )
