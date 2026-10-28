"""Construye los cuadernos del expediente a partir de los módulos de ``informes.cuadernos``.

Uso (desde la raíz del expediente):
    PYTHONPATH=src python -m informes.construir_cuadernos [00 01 ...]
Escribe notebooks/*.ipynb sin ejecutar. La ejecución se hace aparte con
``jupyter nbconvert --to notebook --execute --inplace``.
"""

from __future__ import annotations

import importlib
import sys

MODULOS = ("nb00", "nb00b", "nb01", "nb01b", "nb02", "nb02b", "nb03", "nb03b", "nb04", "nb04b", "nb05", "nb06")


def main(argumentos: list[str]) -> None:
    elegidos = [m for m in MODULOS if not argumentos or m[2:] in argumentos]
    for nombre in elegidos:
        try:
            modulo = importlib.import_module(f"informes.cuadernos.{nombre}")
        except ModuleNotFoundError:
            print(f"{nombre}: aún no existe")
            continue
        print(modulo.guardar(modulo.NOMBRE, modulo.construir()))


if __name__ == "__main__":
    main(sys.argv[1:])
