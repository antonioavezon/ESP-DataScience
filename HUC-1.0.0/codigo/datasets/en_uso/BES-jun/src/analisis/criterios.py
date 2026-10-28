"""Criterios de aceptación ejecutables.

Cada cuaderno declara qué debe cumplirse y lo comprueba con código. Un
criterio que falla detiene la ejecución: no se entrega un resultado cuyo
criterio de aceptación no se cumplió.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Criterios:
    cuaderno: str
    filas: list = field(default_factory=list)

    def comprobar(self, id_: str, descripcion: str, cumple: bool, evidencia: str) -> bool:
        self.filas.append(
            {
                "id": id_,
                "criterio": descripcion,
                "resultado": "CUMPLE" if cumple else "NO CUMPLE",
                "evidencia": evidencia,
            }
        )
        return bool(cumple)

    def tabla(self):
        import pandas as pd

        return pd.DataFrame(self.filas)

    def exigir(self) -> None:
        """Lanza AssertionError si algún criterio no se cumplió."""
        falla = [f for f in self.filas if f["resultado"] != "CUMPLE"]
        if falla:
            raise AssertionError(
                f"{self.cuaderno}: {len(falla)} criterio(s) no cumplido(s): "
                + "; ".join(f"{f['id']} ({f['evidencia']})" for f in falla)
            )
