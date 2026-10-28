"""Ficha de reproducibilidad: qué entorno y qué insumo produjeron una ejecución."""

from __future__ import annotations

import datetime as dt
import platform
import sys
from importlib import metadata

from ingesta.integridad import huellas
from ingesta.leer_bes_jun import COPIA_TRABAJO, raiz_expediente

PAQUETES = ("pandas", "numpy", "matplotlib", "openpyxl")


def ficha() -> dict:
    return {
        "fecha_ejecucion": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "sistema": f"{platform.system()} {platform.release()}",
        **{p: metadata.version(p) for p in PAQUETES},
        "expediente": raiz_expediente().name,
        "insumo": COPIA_TRABAJO.relative_to(raiz_expediente()).as_posix(),
        "insumo_sha256": huellas(COPIA_TRABAJO)["sha256"],
    }
