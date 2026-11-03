"""Estructura visual de respuestas del asistente. No calcula ni inventa magnitudes."""

from __future__ import annotations

from html import escape

from services.chat_hechos import CATALOGO, completar, pozos_de
from services.dataset_registry import descubrir
from services.formato_numero import formato_visible


def formato_es(valor) -> str:
    """Presentación con separador decimal español. No altera el valor interno."""
    if valor is None or isinstance(valor, bool):
        return "—"
    if isinstance(valor, str):
        texto = valor.strip()
        if not texto:
            return "—"
        try:
            numero = float(texto.replace(",", "."))
        except ValueError:
            return texto
    elif isinstance(valor, (int, float)):
        numero = float(valor)
    else:
        return str(valor)
    entero = abs(int(numero))
    resto = abs(numero) - entero
    miles = f"{entero:,}".replace(",", ".")
    if resto < 1e-9:
        cuerpo = miles
    else:
        dec = f"{resto:.2f}"[1:].replace(".", ",")
        dec = dec.rstrip("0").rstrip(",")
        cuerpo = miles + (dec if dec else "")
    return f"-{cuerpo}" if numero < 0 else cuerpo


def magnitud(fila: dict, clave: str) -> tuple[str, str]:
    from services.unidades_caudal import unidad_de

    for item in fila.get("magnitudes") or []:
        if item.get("id") == clave and item.get("visible") is not None:
            return str(item["visible"]), unidad_de(clave, item.get("unidad"))
    alias = {
        "pip_ft": ("pip_visible", "ft"),
        "thd_total_ft": ("thd_visible", "ft"),
        "caudal_a_producir_bfpd": ("caudal_visible", "BFPD"),
    }
    if clave in alias:
        campo, unidad = alias[clave]
        if fila.get(campo):
            return str(fila[campo]), unidad_de(clave, unidad)
    return "", ""


def estructurar(tema: str, filas: list[dict], *, dataset_id: str | None, alcance: dict) -> dict:
    filas = [completar(fila) for fila in filas]
    if tema == "inventario":
        return _inventario(filas, dataset_id, alcance)
    if not filas:
        return _vacio(alcance, "No hay un resultado consultable para esa pregunta.")
    if tema == "motivo_estado":
        return _motivo_estado(filas, alcance)
    if tema == "motivo_caudal":
        return _motivo_caudal(filas, alcance)
    if tema == "medidas":
        return _medidas(filas, alcance)
    if tema == "presiones":
        return _presiones(filas, alcance)
    if tema == "caudal":
        return _caudal(filas, alcance)
    if tema == "caudal_agua":
        return _caudal_agua(filas, alcance)
    if tema == "bopd":
        return _bopd(filas, alcance)
    if tema == "frecuencia":
        return _frecuencia(filas, alcance)
    return _estado(filas, alcance)


def texto_plano(estructura: dict) -> str:
    partes = []
    if estructura.get("titulo"):
        partes.append(str(estructura["titulo"]))
    if estructura.get("resumen"):
        partes.append(str(estructura["resumen"]))
    for seccion in estructura.get("secciones") or []:
        if seccion.get("titulo"):
            partes.append(str(seccion["titulo"]))
        for parrafo in seccion.get("parrafos") or []:
            partes.append(str(parrafo))
        tabla = seccion.get("tabla")
        if isinstance(tabla, dict):
            columnas = tabla.get("columnas") or []
            partes.append(" | ".join(str(c) for c in columnas))
            for fila in tabla.get("filas") or []:
                partes.append(" | ".join(str(c) for c in fila))
        for item in seccion.get("lista") or []:
            partes.append(f"- {item}")
    if estructura.get("explicacion"):
        partes.append(str(estructura["explicacion"]))
    return "\n\n".join(p for p in partes if p)


def render_html(estructura: dict) -> str:
    """HTML escapado. No pasa por |safe contenido de Ollama."""
    if not isinstance(estructura, dict) or not estructura:
        return ""
    bloques = ['<div class="asistente-estructura">']
    if estructura.get("titulo"):
        bloques.append(f'<h3 class="asistente-titulo">{escape(str(estructura["titulo"]))}</h3>')
    if estructura.get("resumen"):
        bloques.append(f'<p class="asistente-resumen">{escape(str(estructura["resumen"]))}</p>')
    for seccion in estructura.get("secciones") or []:
        if not isinstance(seccion, dict):
            continue
        bloques.append('<section class="asistente-seccion">')
        if seccion.get("titulo"):
            bloques.append(f"<h4>{escape(str(seccion['titulo']))}</h4>")
        for parrafo in seccion.get("parrafos") or []:
            bloques.append(f"<p>{escape(str(parrafo))}</p>")
        tabla = seccion.get("tabla")
        if isinstance(tabla, dict) and tabla.get("filas"):
            bloques.append('<div class="asistente-tabla-wrap"><table class="asistente-tabla">')
            columnas = tabla.get("columnas") or []
            if columnas:
                bloques.append("<thead><tr>" + "".join(f"<th>{escape(str(c))}</th>" for c in columnas) + "</tr></thead>")
            bloques.append("<tbody>")
            for fila in tabla.get("filas") or []:
                celdas = "".join(f'<td>{escape(str(c))}</td>' for c in fila)
                bloques.append(f"<tr>{celdas}</tr>")
            bloques.append("</tbody></table></div>")
        lista = seccion.get("lista") or []
        if lista:
            bloques.append("<ul>")
            for item in lista:
                bloques.append(f"<li>{escape(str(item))}</li>")
            bloques.append("</ul>")
        bloques.append("</section>")
    if estructura.get("explicacion"):
        bloques.append(f'<p class="asistente-explicacion">{escape(str(estructura["explicacion"]))}</p>')
    bloques.append("</div>")
    return "".join(bloques)


def etiqueta_alcance(alcance: dict) -> str:
    dataset = alcance.get("dataset") or "Todos"
    pozo = alcance.get("pozo") or "Todos"
    if dataset in ("", "all", "ALL", "Todos"):
        dataset = "Todos"
    if pozo in ("", "all", "ALL", "Todos"):
        return f"Dataset: {dataset} · Pozos: Todos"
    return f"Dataset: {dataset} · Pozo: {pozo}"


def datasets_disponibles() -> list[dict]:
    salida = [{"id": "ALL", "nombre": "Todos"}]
    for ficha in descubrir():
        salida.append({
            "id": ficha.identificador,
            "nombre": ficha.identificador,
            "evaluable": ficha.puede_evaluar,
            "ciclo": ficha.ciclo,
        })
    return salida


def pozos_disponibles(dataset_id: str | None) -> list[dict]:
    from services.escenario_inicial import listar_pozos

    salida = []
    for item in listar_pozos():
        if dataset_id and dataset_id not in ("ALL", "all", "") and item.get("dataset_id") != dataset_id:
            continue
        salida.append({
            "pozo_id": item["pozo_id"],
            "dataset_id": item.get("dataset_id") or "",
            "evaluable": bool(item.get("evaluable")),
            "etiqueta": item["pozo_id"] if not dataset_id or dataset_id in ("ALL", "all", "") else item["pozo_id"],
            "clave": f"{item.get('dataset_id') or ''}::{item['pozo_id']}",
        })
    return salida


def _vacio(alcance: dict, mensaje: str) -> dict:
    return {
        "tipo": "vacio",
        "titulo": "Sin resultado consultable",
        "resumen": mensaje,
        "secciones": [],
        "explicacion": "",
        "alcance": alcance,
        "fuentes": [],
    }


def _motivo_estado(filas: list[dict], alcance: dict) -> dict:
    from services.chat_explicaciones import bloques_para_presentacion, explicar_estado

    fila = filas[0]
    exp = explicar_estado(fila)
    valores = []
    for clave in ("frecuencia_hz", "caudal_operacion_bfpd", "caudal_a_producir_bfpd", "pip_ft", "thd_total_ft"):
        visible, unidad = magnitud(fila, clave)
        if not visible:
            continue
        nombre = CATALOGO.get(clave, (clave, "", "", ""))[0]
        valores.append([nombre, f"{formato_es(visible)} {unidad}".strip()])
    secciones = bloques_para_presentacion(exp)
    if valores:
        secciones.insert(1, {
            "titulo": "Valores del punto",
            "parrafos": [],
            "tabla": {"columnas": ["Magnitud", "Valor"], "filas": valores},
            "lista": [],
        })
    return {
        "tipo": "estado_pozo",
        "titulo": exp["titulo"],
        "resumen": exp["resumen"],
        "rotulo": fila.get("rotulo") or "",
        "secciones": secciones,
        # El cierre ya está en la sección «En resumen»; no repetirlo como explicación suelta.
        "explicacion": "",
        "alcance": alcance,
        "fuentes": _fuentes(filas),
    }


def _motivo_caudal(filas: list[dict], alcance: dict) -> dict:
    from services.chat_explicaciones import bloques_para_presentacion, explicar_caudal

    fila = filas[0]
    exp = explicar_caudal(fila)
    return {
        "tipo": "caudal",
        "titulo": exp["titulo"],
        "resumen": exp["resumen"],
        "secciones": bloques_para_presentacion(exp),
        "explicacion": "",
        "alcance": alcance,
        "fuentes": _fuentes(filas),
    }


def _estado(filas: list[dict], alcance: dict) -> dict:
    if len(filas) == 1:
        # Una pregunta de estado de un pozo incluye siempre el «por qué» breve.
        return _motivo_estado(filas, alcance)

    por_dataset: dict[str, list[dict]] = {}
    for fila in filas:
        por_dataset.setdefault(fila.get("dataset_id") or "sin dataset", []).append(fila)
    resumen = _resumen_estados(filas, por_dataset, alcance)
    multi_dataset = len(por_dataset) > 1 or (alcance.get("dataset") in ("Todos", "ALL", "all", ""))
    filas_tabla = []
    for fila in filas:
        freq, u_f = magnitud(fila, "frecuencia_hz")
        caudal, u_c = magnitud(fila, "caudal_a_producir_bfpd")
        if not caudal:
            caudal, u_c = magnitud(fila, "q_fluidos")
        fila_tabla = []
        if multi_dataset:
            fila_tabla.append(fila.get("dataset_id") or "—")
        fila_tabla.extend([
            fila["pozo"],
            fila.get("rotulo") or "—",
            f"{formato_es(freq)} {u_f}".strip() if freq else "—",
            f"{formato_es(caudal)} {u_c}".strip() if caudal else "—",
        ])
        filas_tabla.append(fila_tabla)
    columnas = (["Dataset"] if multi_dataset else []) + ["Pozo", "Estado", "Frecuencia", "Caudal calculado"]
    secciones = [{
        "titulo": "Resultados consultables",
        "parrafos": [],
        "tabla": {
            "columnas": columnas,
            "filas": filas_tabla,
        },
        "lista": [],
    }, {
        "titulo": "Otras magnitudes disponibles",
        "parrafos": [
            "Los resultados incluyen valores de PIP, THD, gradiente y caudal de operación cuando el expediente los publica.",
            "Estas magnitudes describen las condiciones usadas en la evaluación de cada pozo.",
        ],
        "tabla": None,
        "lista": [],
    }]
    return {
        "tipo": "estado_general",
        "titulo": "Estado general de los pozos",
        "resumen": resumen,
        "secciones": secciones,
        "explicacion": "Los estados mostrados corresponden a resultados ya calculados del expediente indicado, no a telemetría en vivo.",
        "alcance": alcance,
        "fuentes": _fuentes(filas),
    }


def _medidas(filas: list[dict], alcance: dict) -> dict:
    if len(filas) == 1:
        fila = filas[0]
        filas_tabla = []
        for item in fila.get("magnitudes") or []:
            if not item.get("visible"):
                continue
            filas_tabla.append([
                item.get("nombre") or item.get("id"),
                f"{formato_es(item['visible'])} {item.get('unidad') or ''}".strip(),
                item.get("tipo") or "",
            ])
        return {
            "tipo": "medidas_pozo",
            "titulo": f"Medidas de {fila['pozo']}",
            "resumen": f"Magnitudes disponibles para el pozo {fila['pozo']}, con su unidad.",
            "secciones": [{
                "titulo": "Valores publicados",
                "parrafos": [],
                "tabla": {"columnas": ["Magnitud", "Valor", "Tipo"], "filas": filas_tabla},
                "lista": [],
            }],
            "explicacion": "Cada magnitud conserva la unidad del registro o del cálculo.",
            "alcance": alcance,
            "fuentes": _fuentes(filas),
        }
    nombres = []
    for fila in filas:
        for item in fila.get("magnitudes") or []:
            etiqueta = f"{item['nombre']} ({item['unidad']})" if item.get("unidad") else item["nombre"]
            if etiqueta not in nombres:
                nombres.append(etiqueta)
    filas_tabla = []
    for fila in filas:
        freq, _ = magnitud(fila, "frecuencia_hz")
        caudal, _ = magnitud(fila, "caudal_a_producir_bfpd")
        pip, _ = magnitud(fila, "pip_ft")
        filas_tabla.append([
            fila.get("dataset_id") or "—",
            fila["pozo"],
            formato_es(freq) if freq else "—",
            formato_es(caudal) if caudal else "—",
            formato_es(pip) if pip else "—",
        ])
    return {
        "tipo": "medidas_general",
        "titulo": "Medidas de los pozos",
        "resumen": f"Se consultaron {len(filas)} pozos. Las magnitudes comunes incluyen {', '.join(nombres[:8])}{'…' if len(nombres) > 8 else ''}.",
        "secciones": [{
            "titulo": "Comparación principal",
            "parrafos": [],
            "tabla": {
                "columnas": ["Dataset", "Pozo", "Frecuencia (Hz)", "Caudal calc. (BFPD)", "PIP (ft)"],
                "filas": filas_tabla,
            },
            "lista": [],
        }],
        "explicacion": "La tabla resume las magnitudes más solicitadas. Otras variables permanecen disponibles en cada resultado.",
        "alcance": alcance,
        "fuentes": _fuentes(filas),
    }


def _presiones(filas: list[dict], alcance: dict) -> dict:
    filas_tabla = []
    for fila in filas:
        sensor, u_s = magnitud(fila, "presion_sensor_psi")
        thp, u_t = magnitud(fila, "thp_psi")
        pip, u_p = magnitud(fila, "pip_ft")
        filas_tabla.append([
            fila.get("dataset_id") or "—",
            fila["pozo"],
            f"{formato_es(sensor)} {u_s}".strip() if sensor else "—",
            f"{formato_es(thp)} {u_t}".strip() if thp else "—",
            f"{formato_es(pip)} {u_p}".strip() if pip else "—",
        ])
    return {
        "tipo": "presiones",
        "titulo": "Presiones disponibles",
        "resumen": "Se muestran las lecturas en psi y la PIP publicada en pies de fluido.",
        "secciones": [{
            "titulo": "Magnitudes de presión",
            "parrafos": [
                "La PIP no se presenta como psi: en este expediente se publica en pies de fluido.",
            ],
            "tabla": {
                "columnas": ["Dataset", "Pozo", "Sensor (psi)", "THP (psi)", "PIP (ft)"],
                "filas": filas_tabla,
            },
            "lista": [],
        }],
        "explicacion": "",
        "alcance": alcance,
        "fuentes": _fuentes(filas),
    }


def _caudal(filas: list[dict], alcance: dict) -> dict:
    filas_tabla = []
    for fila in filas:
        reg, u_r = magnitud(fila, "caudal_operacion_bfpd")
        if not reg:
            reg, u_r = magnitud(fila, "caudal_fluidos")
        if not reg:
            reg, u_r = magnitud(fila, "q_fluidos")
        if not reg:
            reg, u_r = magnitud(fila, "bfpd")
        calc, u_c = magnitud(fila, "caudal_a_producir_bfpd")
        filas_tabla.append([
            fila.get("dataset_id") or "—",
            fila["pozo"],
            f"{formato_es(reg)} {u_r}".strip() if reg else "—",
            f"{formato_es(calc)} {u_c}".strip() if calc else "—",
        ])
    return {
        "tipo": "caudal",
        "titulo": "Caudales",
        "resumen": "Se distingue el caudal registrado del caudal calculado de intersección.",
        "secciones": [{
            "titulo": "Comparación de caudales",
            "parrafos": [],
            "tabla": {
                "columnas": ["Dataset", "Pozo", "Caudal registrado", "Caudal calculado"],
                "filas": filas_tabla,
            },
            "lista": [],
        }],
        "explicacion": "El caudal calculado no sustituye al caudal registrado de la hoja.",
        "alcance": alcance,
        "fuentes": _fuentes(filas),
    }


def _caudal_agua(filas: list[dict], alcance: dict) -> dict:
    filas_tabla = []
    for fila in filas:
        agua, u_a = magnitud(fila, "q_water")
        if not agua:
            agua, u_a = magnitud(fila, "bwpd")
        total, u_t = magnitud(fila, "q_fluidos")
        if not total:
            total, u_t = magnitud(fila, "caudal_fluidos")
        if not total:
            total, u_t = magnitud(fila, "bfpd")
        filas_tabla.append([
            fila.get("dataset_id") or "—",
            fila["pozo"],
            f"{formato_es(agua)} {u_a}".strip() if agua else "—",
            f"{formato_es(total)} {u_t}".strip() if total else "—",
        ])
    disponibles = any(fila[2] != "—" for fila in filas_tabla)
    return {
        "tipo": "caudal",
        "titulo": "Caudal de agua",
        "resumen": (
            "Caudal de agua publicado para el pozo consultado."
            if disponibles
            else "No hay un caudal de agua publicado en el resultado de ese pozo."
        ),
        "secciones": [{
            "titulo": "Partición de caudales",
            "parrafos": [],
            "tabla": {
                "columnas": ["Dataset", "Pozo", "Caudal de agua", "Caudal total"],
                "filas": filas_tabla,
            },
            "lista": [],
        }],
        "explicacion": (
            ""
            if disponibles
            else "Este expediente no publica Q-water ni BWPD para esa consulta."
        ),
        "alcance": alcance,
        "fuentes": _fuentes(filas),
    }


def _bopd(filas: list[dict], alcance: dict) -> dict:
    filas_tabla = []
    for fila in filas:
        bopd, u_b = magnitud(fila, "bopd")
        if not bopd:
            bopd, u_b = magnitud(fila, "q_oil")
        bfpd, u_f = magnitud(fila, "bfpd")
        if not bfpd:
            bfpd, u_f = magnitud(fila, "q_fluidos")
        bwpd, u_w = magnitud(fila, "bwpd")
        if not bwpd:
            bwpd, u_w = magnitud(fila, "q_water")
        filas_tabla.append([
            fila.get("dataset_id") or "—",
            fila["pozo"],
            f"{formato_es(bopd)} {u_b}".strip() if bopd else "—",
            f"{formato_es(bfpd)} {u_f}".strip() if bfpd else "—",
            f"{formato_es(bwpd)} {u_w}".strip() if bwpd else "—",
        ])
    disponibles = any(fila[2] != "—" for fila in filas_tabla)
    return {
        "tipo": "caudal",
        "titulo": "BOPD",
        "resumen": (
            "BOPD publicado para el pozo consultado."
            if disponibles
            else "No hay un BOPD publicado en el resultado de ese pozo."
        ),
        "secciones": [{
            "titulo": "Caudales de petróleo",
            "parrafos": [],
            "tabla": {
                "columnas": ["Dataset", "Pozo", "BOPD / Q-oil", "BFPD / Q-fluidos", "BWPD / Q-water"],
                "filas": filas_tabla,
            },
            "lista": [],
        }],
        "explicacion": (
            ""
            if disponibles
            else "Este expediente no publica BOPD ni Q-oil para esa consulta."
        ),
        "alcance": alcance,
        "fuentes": _fuentes(filas),
    }


def _frecuencia(filas: list[dict], alcance: dict) -> dict:
    filas_tabla = []
    for fila in filas:
        freq, unidad = magnitud(fila, "frecuencia_hz")
        filas_tabla.append([
            fila.get("dataset_id") or "—",
            fila["pozo"],
            f"{formato_es(freq)} {unidad}".strip() if freq else "—",
        ])
    return {
        "tipo": "frecuencia",
        "titulo": "Frecuencia de operación",
        "resumen": f"Frecuencia publicada para {len(filas)} pozo(s).",
        "secciones": [{
            "titulo": "Valores",
            "parrafos": [],
            "tabla": {"columnas": ["Dataset", "Pozo", "Frecuencia"], "filas": filas_tabla},
            "lista": [],
        }],
        "explicacion": "",
        "alcance": alcance,
        "fuentes": _fuentes(filas),
    }


def _inventario(filas: list[dict], dataset_id: str | None, alcance: dict) -> dict:
    from services.escenario_inicial import listar_pozos

    vistos = listar_pozos()
    if dataset_id and dataset_id not in ("ALL", "all", ""):
        vistos = [item for item in vistos if item.get("dataset_id") == dataset_id]
    evaluables = [item for item in vistos if item.get("evaluable")]
    grupos: dict[str, list[str]] = {}
    for item in vistos:
        clave = f"{item.get('dataset_id') or '—'} · {item.get('bomba_referencia') or 'sin referencia'}"
        grupos.setdefault(clave, []).append(item["pozo_id"])
    filas_tabla = [[clave, ", ".join(pozos)] for clave, pozos in grupos.items()]
    if alcance.get("dataset") in ("Todos", "ALL", "all", ""):
        resumen = (
            f"Hay {len(vistos)} pozos registrados en los datasets disponibles. "
            f"{len(evaluables)} tienen motor consultable en este momento."
        )
    else:
        dataset = dataset_id or alcance.get("dataset") or "el dataset"
        resumen = f"En {dataset} hay {len(vistos)} pozos registrados."
    return {
        "tipo": "inventario",
        "titulo": "Inventario de pozos",
        "resumen": resumen,
        "secciones": [{
            "titulo": "Referencias de bomba",
            "parrafos": [],
            "tabla": {"columnas": ["Dataset · bomba", "Pozos"], "filas": filas_tabla},
            "lista": [],
        }],
        "explicacion": (
            "Las bombas de estos pozos son de bombeo electrosumergible según la referencia de cada hoja. "
            "Solo los expedientes con motor integrado aportan estados calculados."
        ),
        "alcance": alcance,
        "fuentes": sorted({item.get("dataset_id") or "" for item in vistos if item.get("dataset_id")}),
    }


def _resumen_estados(filas: list[dict], por_dataset: dict, alcance: dict) -> str:
    conteos: dict[str, int] = {}
    for fila in filas:
        rotulo = str(fila.get("rotulo") or "sin clasificación")
        conteos[rotulo] = conteos.get(rotulo, 0) + 1
    estados = ", ".join(f"{n} en {rotulo}" for rotulo, n in sorted(conteos.items()))
    datasets = ", ".join(sorted(por_dataset))
    if alcance.get("dataset") in ("Todos", "ALL", "all", ""):
        return (
            f"Se consultaron {len(filas)} pozos con resultado disponible "
            f"({estados}). Proceden de: {datasets}."
        )
    return f"En {datasets} hay {len(filas)} pozos con resultado consultable ({estados})."


def _explicacion_estado(fila: dict) -> str:
    if fila.get("rotulo") == "NORMAL":
        return "El caudal queda entre el mínimo y el máximo escritos a esta frecuencia."
    if fila.get("rotulo") == "REGISTRO":
        return (
            "El rótulo REGISTRO indica que el motor calculó el punto, pero este expediente "
            "no aplica una regla de caudal (como NORMAL/INCIPIENTE/CRÍTICO). "
            "No significa que el pozo esté sin procesar: es la clasificación prevista para este dataset."
        )
    return "El estado mostrado corresponde al último resultado publicado para este pozo."


def _fuentes(filas: list[dict]) -> list[str]:
    return sorted({fila.get("dataset_id") for fila in filas if fila.get("dataset_id")})
