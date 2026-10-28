"""Mandos de la consola. Un recorrido de slider no es un límite del equipo."""

from __future__ import annotations

# Recorrido gráfico, no un límite de bomba, motor ni variador.
FACTOR_RECORRIDO_FRECUENCIA = (0.5, 1.5)
RECORRIDO_TVD_FT = 100.0

CONTROLES = (
    {
        "id": "frecuencia_hz",
        "nombre": "Frecuencia de operación",
        "unidad": "Hz",
        "rol": "entrada",
        "via": "variable",
        "visible": True,
        "convencion": (
            "Hertz escritos en la hoja de este pozo. El expediente no trae límite de motor ni de variador. "
            "El dominio observado del dataset no es un límite autorizado."
        ),
        "es_limite_operacional": False,
    },
    {
        "id": "tvd_intake_ft",
        "nombre": "Profundidad TVD de la admisión",
        "unidad": "ft",
        "rol": "entrada",
        "via": "parametro_escenario",
        "visible": True,
        "convencion": (
            "Profundidad vertical de la admisión, en ft, positiva hacia abajo. No es MD ni head. "
            "Moverla respecto del sensor cambia el PIP de la celda. CT-03 sigue abierta: el signo no está confirmado."
        ),
        "es_limite_operacional": False,
    },
    {
        "id": "potencia",
        "nombre": "Potencia",
        "unidad": None,
        "rol": "no_es_entrada",
        "via": None,
        "visible": True,
        "convencion": (
            "brake_hp figura en los puntos de la curva de 60 Hz de la ficha. "
            "No es una entrada del motor ni un resultado de la evaluación. No se simula como magnitud independiente."
        ),
        "es_limite_operacional": False,
    },
    {
        "id": "head",
        "nombre": "Head",
        "unidad": "ft",
        "rol": "calculado",
        "via": None,
        "visible": True,
        "salida": "thd_total_ft",
        "convencion": (
            "El head de la curva no es un punto de consigna. "
            "La pantalla muestra el THD total que calcula el balance, en ft, cuando la evaluación lo produce."
        ),
        "es_limite_operacional": False,
    },
)

# Previstos. No se dibujan hasta que el expediente los tenga como entrada verificada.
RESERVA = (
    "caudal_operacion_bfpd",
    "presion_sensor_psi",
    "thp_psi",
    "temperatura_c",
    "api_deg",
    "bsw_numero",
)


def definicion(identificador: str) -> dict | None:
    for control in CONTROLES:
        if control["id"] == identificador:
            return control
    return None


def recorrido(identificador: str, valor: float | None) -> dict | None:
    """Extremos del mando gráfico. No son límites operacionales."""
    if valor is None:
        return None
    if identificador == "frecuencia_hz":
        bajo, alto = FACTOR_RECORRIDO_FRECUENCIA
        return {
            "minimo": round(valor * bajo, 4),
            "maximo": round(valor * alto, 4),
            "es_limite_operacional": False,
            "leyenda": "Recorrido del mando: 50 % a 150 % del valor registrado en esta hoja. No es un límite del equipo.",
        }
    if identificador == "tvd_intake_ft":
        return {
            "minimo": round(valor - RECORRIDO_TVD_FT, 4),
            "maximo": round(valor + RECORRIDO_TVD_FT, 4),
            "es_limite_operacional": False,
            "leyenda": "Recorrido del mando: ±100 ft alrededor de la TVD registrada. No es un límite de asentamiento.",
        }
    return None
