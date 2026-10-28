"""Figuras de este libro. Cada panel es una hoja. No se ajusta una curva común."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ingesta.leer_bes_jun import raiz_expediente


def figura_elasticidades(por_pozo: dict[str, dict[str, float]], ruta: Path) -> Path:
    """Barras del valor absoluto medio de la elasticidad de Q* por variable. No es una incertidumbre."""
    if not por_pozo:
        raise ValueError("no hay elasticidades")
    claves = list(next(iter(por_pozo.values())))
    medias = []
    for clave in claves:
        valores = [abs(por_pozo[pozo][clave]) for pozo in por_pozo]
        medias.append((clave, sum(valores) / len(valores)))
    medias.sort(key=lambda par: par[1])
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    ax.barh([nombre for nombre, _ in medias], [valor for _, valor in medias], color="#4c78a8")
    ax.set_xlabel("|elasticidad| media de Q* en las cinco hojas")
    ax.set_title("Peso local de cada entrada sobre el caudal calculado")
    fig.tight_layout()
    fig.savefig(ruta, dpi=120)
    plt.close(fig)
    return ruta


def guardar_figuras(hojas: list[dict], estaciones: list[dict]) -> list[Path]:
    destino = raiz_expediente() / "reports" / "figuras"
    destino.mkdir(parents=True, exist_ok=True)
    rutas = [
        _caudal(hojas, destino / "caudal_limites_por_hoja.png"),
        _head(hojas, destino / "head_puntos_60hz.png"),
        _survey(hojas, estaciones, destino / "survey_md_tvd_por_hoja.png"),
        _inclinacion(hojas, estaciones, destino / "inclinacion_survey_por_hoja.png"),
        _interseccion(hojas, destino / "interseccion_sistema_bomba.png"),
        _impacto(hojas, destino / "impacto_ambiguedades_en_caudal.png"),
    ]
    return rutas


def _thd(h: dict) -> float:
    from modelo_deterministico.balance_bes_jun import evaluar_balance
    from modelo_deterministico.fluidos_bes_jun import evaluar_fluido

    g = evaluar_fluido(h["api_deg"], h["temperatura_c"], h["bsw_numero"], h["densidad_agua_lb_gal"])
    g = g.resultados["gradiente_psi_ft"]["valor"]
    b = evaluar_balance(
        h["presion_sensor_psi"], h["thp_psi"], h["tvd_intake_ft"], h["tvd_sensor_ft"],
        h["tvd_descarga_ft"], g, h["caudal_operacion_bfpd"], h["id_tubing_in"],
    )
    return b.resultados["thd_total_ft"]["valor"]


def _interseccion(hojas: list[dict], ruta: Path) -> Path:
    from modelo_deterministico.interseccion_bes_jun import caudal_a_producir, curva_a_velocidad

    fig, axes = plt.subplots(1, len(hojas), figsize=(13, 3.8))
    for ax, h in zip(axes, hojas):
        pts = curva_a_velocidad(h["curva"], h["frecuencia_hz"], h["frecuencia_curva_hz"], h["etapas"])
        thd = _thd(h)
        q = caudal_a_producir(thd, h["curva"], h["frecuencia_hz"], h["frecuencia_curva_hz"], h["etapas"])
        ax.plot([p["caudal_bfpd"] for p in pts], [p["head_ft"] for p in pts], "o-", color="#4c78a8", ms=3, label="Head de la bomba a f")
        ax.axhline(thd, color="#e45756", lw=1.2, label="THD total de la hoja")
        ax.axvline(h["caudal_operacion_bfpd"], color="#54a24b", ls="--", lw=1.2, label="Caudal medido")
        if q.estado == "calculable":
            ax.axvline(q.resultados["caudal_a_producir_bfpd"]["valor"], color="#f58518", ls=":", lw=1.4, label="Caudal a producir")
        ax.set_title(f"{h['hoja']}\n{h['frecuencia_hz']:g} Hz, {h['etapas']:g} etapas", fontsize=9)
        ax.set_xlabel("Caudal (BFPD)")
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("Altura (ft)")
    axes[0].legend(fontsize=6)
    fig.suptitle("Intersección sistema-bomba tal como la calcula la hoja (no es validación)")
    fig.tight_layout()
    fig.savefig(ruta, dpi=120)
    plt.close(fig)
    return ruta


def _impacto(hojas: list[dict], ruta: Path) -> Path:
    from analisis.sensibilidad import tabla_de_impacto

    escenarios = ["CT-03", "CT-04", "CT-05"]
    nombres = {"CT-03": "Signo PIP", "CT-04": "Sin corrección T", "CT-05": "Exponente 4.8655"}
    colores = {"CT-03": "#e45756", "CT-04": "#f58518", "CT-05": "#4c78a8"}
    tablas = {h["hoja"]: {f["consulta"]: f for f in tabla_de_impacto(h)} for h in hojas}
    fig, ax = plt.subplots(figsize=(9, 4.6))
    ancho = 0.25
    for i, ct in enumerate(escenarios):
        ax.bar(
            [j + (i - 1) * ancho for j in range(len(hojas))],
            [tablas[h["hoja"]][ct]["d_q_bfpd"] for h in hojas],
            width=ancho, color=colores[ct], label=nombres[ct],
        )
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xticks(range(len(hojas)), [h["hoja"] for h in hojas])
    ax.set_ylabel("Cambio en «Caudal a producir» (BFPD)")
    ax.set_title("Cuánto movería cada ambigüedad abierta al caudal calculado")
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(ruta, dpi=120)
    plt.close(fig)
    return ruta


def _caudal(hojas: list[dict], ruta: Path) -> Path:
    from reglas.candidatas_bes_jun import limites_a_frecuencia

    fig, ax = plt.subplots(figsize=(8.5, 5.6))
    etiquetas = [f"{h['pozo']}\n{h['hoja']}\n{h['frecuencia_hz']:g} Hz" for h in hojas]
    x = list(range(len(hojas)))
    lim = [limites_a_frecuencia(h) for h in hojas]
    ax.bar(x, [h["caudal_operacion_bfpd"] for h in hojas], color="#4c78a8", label="Caudal de operación")
    ax.plot(x, [l["maximo_bfpd"] for l in lim], "o", color="#e45756", label="Límite máximo a la frecuencia de operación")
    ax.plot(x, [l["minimo_bfpd"] for l in lim], "s", color="#54a24b", label="Límite mínimo a la frecuencia de operación")
    ax.plot(x, [h["limite_maximo_bfpd"] for h in hojas], "o", mfc="none", color="#e45756", alpha=0.7, label="Límite máximo escrito (a 60 Hz)")
    ax.set_xticks(x, etiquetas)
    ax.set_ylabel("Caudal (BFPD)")
    ax.set_xlabel("Pozo, hoja y frecuencia de operación")
    ax.set_title("Caudal de operación y límites en la misma base de frecuencia")
    ax.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.27), ncol=2)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(ruta, dpi=120)
    plt.close(fig)
    return ruta


def _head(hojas: list[dict], ruta: Path) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(8, 4.2), sharey=False)
    grupos: dict[str, dict] = {}
    for hoja in hojas:
        grupo = grupos.setdefault(hoja["bomba_referencia"], {"curva": hoja["curva"], "hojas": []})
        grupo["hojas"].append(hoja["hoja"])
    for ax, (nombre, grupo) in zip(axes, grupos.items()):
        qs = [p["caudal_bfpd"] for p in grupo["curva"]]
        hs = [p["head_ft"] for p in grupo["curva"]]
        ax.plot(qs, hs, "o-", color="#4c78a8", label="Puntos escritos")
        ax.set_title(f"{nombre}\n{', '.join(grupo['hojas'])}")
        ax.set_xlabel("Caudal (BFPD)")
        ax.set_ylabel("Head (ft)")
        ax.legend()
        ax.grid(alpha=0.3)
    fig.suptitle("Head a 60 Hz, puntos de la hoja. No es curva de fabricante")
    fig.tight_layout()
    fig.savefig(ruta, dpi=120)
    plt.close(fig)
    return ruta


def _survey(hojas: list[dict], estaciones: list[dict], ruta: Path) -> Path:
    fig, axes = plt.subplots(1, len(hojas), figsize=(11, 4), sharey=False)
    for ax, hoja in zip(axes, hojas):
        pts = [e for e in estaciones if e["hoja"] == hoja["hoja"]]
        ax.plot([e["md_ft"] for e in pts], [e["vertical_ft"] for e in pts], color="#4c78a8")
        ax.set_title(hoja["hoja"])
        ax.set_xlabel("MD (ft)")
        ax.set_ylabel("Vertical (ft)")
        ax.grid(alpha=0.3)
    fig.suptitle("Survey por hoja. Vertical es el valor almacenado, no un cálculo nuevo")
    fig.tight_layout()
    fig.savefig(ruta, dpi=120)
    plt.close(fig)
    return ruta


def _inclinacion(hojas: list[dict], estaciones: list[dict], ruta: Path) -> Path:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    datos = []
    etiquetas = []
    for hoja in hojas:
        vals = [e["inclinacion_deg"] for e in estaciones if e["hoja"] == hoja["hoja"] and e["inclinacion_deg"] is not None]
        datos.append(vals)
        etiquetas.append(hoja["hoja"])
    ax.boxplot(datos, tick_labels=etiquetas, showfliers=True)
    ax.set_ylabel("Inclinación (deg)")
    ax.set_xlabel("Hoja")
    ax.set_title("Inclinación del survey de cada hoja")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(ruta, dpi=120)
    plt.close(fig)
    return ruta
