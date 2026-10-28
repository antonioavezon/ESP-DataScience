"""Consulta del catálogo de fórmulas implementadas. No las ejecuta."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SRC = RAIZ / "datasets" / "en_uso" / "BES-jun" / "src"


def _modelo(modulo: str) -> str:
    if "fluidos_bes_jun" in modulo:
        return "M-BES-FLUIDO"
    if "balance_bes_jun" in modulo:
        return "M-BES-BALANCE"
    if "interseccion_bes_jun" in modulo:
        return "M-BES-INTERSECCION"
    if "candidatas_bes_jun" in modulo:
        return "REGLAS-BES"
    return "BES-jun"


def disponibles() -> list[dict]:
    if str(SRC) not in sys.path:
        sys.path.insert(0, str(SRC))
    from catalogo.catastro_formulas_bes_jun import FORMULAS

    salida = []
    for formula in FORMULAS:
        if not formula.get("implementada") or not formula.get("modelo_activo"):
            continue
        if formula.get("hipotesis_alternativa"):
            continue
        funcion = formula.get("funcion") or ""
        if funcion and not _existe(funcion):
            continue
        salida.append(formula)
    return salida


def _existe(ruta: str) -> bool:
    modulo, _, nombre = ruta.rpartition(".")
    try:
        espacio = importlib.import_module(modulo)
    except Exception:
        return False
    return callable(getattr(espacio, nombre, None))


def _ascii(texto: str) -> str:
    return (
        texto.replace("°", " deg ")
        .replace("·", "*")
        .replace("²", "^2")
        .replace("ρ", "rho")
        .replace("Δ", "delta")
    )


def render(formula: dict) -> str:
    expresion = formula.get("expresion") or ""
    estado = formula.get("estado_matematico") or "implementada"
    if "pendiente" in estado.casefold():
        estado = "implementada"
    lineas = [
        f"{formula.get('id')}  {formula.get('nombre')}",
        f"modelo: {_modelo(formula.get('modulo') or '')}",
        f"expresion: {expresion}",
        f"ascii: {_ascii(expresion)}",
        f"variables: {formula.get('variables')}",
        f"unidades: {formula.get('unidades')}",
        f"archivo: datasets/en_uso/BES-jun/{formula.get('modulo')}",
        f"funcion: {formula.get('funcion')}",
        f"estado: {estado}",
        "",
    ]
    return "\n".join(lineas)


def listar() -> str:
    formulas = disponibles()
    if not formulas:
        return "No hay fórmulas implementadas en el catálogo activo.\n"
    return "".join(render(formula) for formula in formulas)


def main(argv: list[str]) -> int:
    if argv == ["list"]:
        sys.stdout.write(listar())
        return 0
    sys.stderr.write("Uso: python proceso/formulas.py list\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
