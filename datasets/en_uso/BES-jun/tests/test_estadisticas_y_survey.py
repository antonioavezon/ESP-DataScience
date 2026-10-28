"""Estadística y survey de BES-jun. No abre otros Excel."""

from ingesta.leer_bes_jun import leer_libro
from ingesta.survey import leer_survey
from analisis.estadisticas import describir, tabla_operacion, tabla_survey


def test_un_punto_no_tiene_desviacion():
    stats = describir([10301.0])
    assert stats["n"] == 1
    assert stats["minimo"] == stats["maximo"] == stats["media"] == 10301.0
    assert stats["desviacion_estandar"] is None


def test_dato_incompleto_queda_en_faltantes():
    stats = describir([None, 10.0])
    assert stats["n"] == 1
    assert stats["faltantes"] == 1


def test_survey_tiene_las_estaciones_numericas_de_cada_hoja():
    estaciones = leer_survey()
    conteos = {}
    for fila in estaciones:
        conteos[fila["hoja"]] = conteos.get(fila["hoja"], 0) + 1
    assert conteos == {
        "QF-554H": 56,
        "QF-545H": 68,
        "QF-500H": 71,
        "QF-378HST": 59,
        "QF-549HST": 67,
    }
    resumen = tabla_survey(estaciones)
    md = [f for f in resumen if f["variable"] == "md_ft" and f["hoja"] == "QF-554H"][0]
    assert md["n"] == 56
    assert md["minimo"] == 0
    assert md["maximo"] == 4530
    assert md["desviacion_estandar"] is not None


def test_la_tabla_de_seis_puntos_coincide_dentro_de_cada_referencia():
    hojas = leer_libro()
    grupos = {}
    for hoja in hojas:
        puntos = tuple(
            (p["caudal_bfpd"], p["head_ft"], p["brake_hp"], p["eff_numero"])
            for p in hoja["curva"]
        )
        grupos.setdefault(hoja["bomba_referencia"], set()).add(puntos)
    assert set(grupos) == {"S 8000N", "S6000N"}
    assert all(len(valores) == 1 for valores in grupos.values())


def test_operacion_no_mezcla_hojas():
    hojas = leer_libro()
    filas = [f for f in tabla_operacion(hojas) if f["variable"] == "caudal_operacion_bfpd"]
    assert [f["pozo"] for f in filas] == ["QF-084", "QF-301", "QF-147", "QF-005", "QF-306"]
    assert all(f["n"] == 1 and f["desviacion_estandar"] is None for f in filas)
