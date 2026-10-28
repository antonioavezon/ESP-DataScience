"""Resultado trazable de un cálculo determinístico."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Resultado:
    """Salida de una evaluación.

    estado:
        calculable: todas las entradas esenciales estaban presentes y dentro
        del dominio declarado de la fórmula transcrita.
        no_calculable: falta una entrada esencial o el caso queda fuera de dominio.
    """

    estado: str
    motivo: str
    entradas: dict = field(default_factory=dict)
    resultados: dict = field(default_factory=dict)
    ecuaciones: list = field(default_factory=list)
    alertas: list = field(default_factory=list)
    advertencias: list = field(default_factory=list)

    def como_dict(self) -> dict:
        return {
            "estado": self.estado,
            "motivo": self.motivo,
            "entradas": self.entradas,
            "resultados": self.resultados,
            "ecuaciones": self.ecuaciones,
            "alertas": self.alertas,
            "advertencias": self.advertencias,
        }
