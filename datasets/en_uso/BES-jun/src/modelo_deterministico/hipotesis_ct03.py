"""Hipótesis hidrostática simple para comparar con la celda de PIP.

No es la transcripción de BES-jun. `evaluar` no la llama y ninguna regla la usa.
CT-03 sigue abierta: esta función no decide el signo.
"""

from __future__ import annotations


def pip_ft_si_el_sensor_esta_mas_profundo(
    presion_sensor_psi: float,
    tvd_intake_ft: float,
    tvd_sensor_ft: float,
    gradiente_psi_ft: float,
) -> float:
    """Altura de intake si la presión crece con la profundidad.

    PIP_ft = P_sensor / gradiente - (TVD_sensor - TVD_intake).
    """
    return presion_sensor_psi / gradiente_psi_ft - (tvd_sensor_ft - tvd_intake_ft)
