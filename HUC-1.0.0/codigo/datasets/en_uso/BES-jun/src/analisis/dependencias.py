"""Rastreo de precedentes de una celda dentro de su hoja.

Responde: ¿de qué celdas depende, directa o indirectamente, este resultado?
Sirve para demostrar que un error cacheado en otra zona de la hoja no entra
en la cadena que se calcula.

Límites: solo lee referencias A1 escritas en la fórmula (con rangos). No evalúa
funciones, no sigue referencias a otras hojas (se informa si existen) ni
nombres definidos (el libro no tiene).
"""

from __future__ import annotations

import re

from openpyxl.utils import column_index_from_string, get_column_letter

_REF = re.compile(
    r"(?<![A-Za-z0-9_!'\.])\$?([A-Z]{1,3})\$?(\d+)(?::\$?([A-Z]{1,3})\$?(\d+))?(?![\d(A-Za-z_])"
)
_TEXTO = re.compile(r'"[^"]*"')


def celdas_citadas(formula: str) -> set[str]:
    """Coordenadas A1 que cita una fórmula, con los rangos expandidos."""
    if not (isinstance(formula, str) and formula.startswith("=")):
        return set()
    sin_texto = _TEXTO.sub("", formula)
    celdas: set[str] = set()
    for c1, f1, c2, f2 in _REF.findall(sin_texto):
        if c2:
            a, b = column_index_from_string(c1), column_index_from_string(c2)
            for col in range(min(a, b), max(a, b) + 1):
                for fila in range(min(int(f1), int(f2)), max(int(f1), int(f2)) + 1):
                    celdas.add(f"{get_column_letter(col)}{fila}")
        else:
            celdas.add(f"{c1}{f1}")
    return celdas


def precedentes(ws, celda_inicial: str) -> dict:
    """Celdas de las que depende ``celda_inicial``, recorriendo fórmulas.

    Devuelve {'formulas': {...}, 'constantes': {...}, 'cita_otra_hoja': bool}.
    """
    pendientes = [celda_inicial]
    vistas: set[str] = set()
    formulas: set[str] = set()
    constantes: set[str] = set()
    cita_otra_hoja = False
    while pendientes:
        actual = pendientes.pop()
        if actual in vistas:
            continue
        vistas.add(actual)
        valor = ws[actual].value
        if isinstance(valor, str) and valor.startswith("="):
            formulas.add(actual)
            if "!" in valor:
                cita_otra_hoja = True
            pendientes.extend(celdas_citadas(valor) - vistas)
        elif valor is not None:
            constantes.add(actual)
    return {"formulas": formulas, "constantes": constantes, "cita_otra_hoja": cita_otra_hoja}


_NUMERO = re.compile(r"(?<![A-Za-z0-9_\.])(\d+\.?\d*(?:[eE][-+]?\d+)?)(?![\d\.]*[A-Za-z_(])")


def constantes_literales(formula: str) -> list[float]:
    """Números escritos dentro de una fórmula, sin contar referencias de celda."""
    if not (isinstance(formula, str) and formula.startswith("=")):
        return []
    limpia = _REF.sub(" ", _TEXTO.sub(" ", formula))
    return [float(n) for n in _NUMERO.findall(limpia)]


def etiqueta_de_celda(ws, coordenada: str) -> str:
    """Rótulo de la fila de una celda: columna A para B-D y columna E para F-H.

    Para columnas I en adelante usa la columna I (bloques de la derecha).
    """
    col = "".join(ch for ch in coordenada if ch.isalpha())
    fila = int("".join(ch for ch in coordenada if ch.isdigit()))
    base = {"A": 1, "B": 1, "C": 1, "D": 1, "E": 5, "F": 5, "G": 5, "H": 5}.get(col, 9)
    texto = ws.cell(fila, base).value
    return "" if texto is None else str(texto).strip()


def firma_estructural(ws, celda: str) -> tuple:
    """Firma comparable entre hojas: esqueleto de la fórmula y columna|rótulo de cada referencia.

    El esqueleto sustituye cada referencia por «@»; conserva operadores, funciones
    y constantes. Dos hojas con la misma firma calculan lo mismo con las mismas
    constantes y leen los mismos conceptos, aunque estén en filas distintas.
    """
    formula = ws[celda].value
    if not (isinstance(formula, str) and formula.startswith("=")):
        return ("constante", formula)
    sin_texto = _TEXTO.sub('""', formula)
    esqueleto = _REF.sub("@", sin_texto).replace("$", "")
    refs = []
    for m in _REF.finditer(sin_texto):
        coord = f"{m.group(1)}{m.group(2)}"
        refs.append(f"{m.group(1)}|{etiqueta_de_celda(ws, coord)}")
    return (esqueleto, tuple(refs))
