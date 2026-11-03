"""Persistencia temporal de valores en uso. No toca datasets."""

from data.simuladores import valores_en_uso as vu


def setup_function():
    vu.limpiar_todo()


def test_guardar_y_obtener_por_pozo():
    vu.guardar("QF-084", {"frecuencia_hz": 55.0})
    vu.guardar("QF-301", {"frecuencia_hz": 40.0})
    assert vu.obtener("QF-084")["frecuencia_hz"] == 55.0
    assert vu.obtener("QF-301")["frecuencia_hz"] == 40.0


def test_limpiar_pozo_no_afecta_otro():
    vu.guardar("QF-084", {"frecuencia_hz": 55.0})
    vu.guardar("QF-301", {"frecuencia_hz": 40.0})
    vu.limpiar("QF-084")
    assert vu.obtener("QF-084") is None
    assert vu.obtener("QF-301")["frecuencia_hz"] == 40.0


def test_limpiar_todo():
    vu.guardar("QF-084", {"frecuencia_hz": 55.0})
    vu.limpiar_todo()
    assert vu.activos() == []
