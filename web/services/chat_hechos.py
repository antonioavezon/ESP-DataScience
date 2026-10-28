"""Arma el texto de respaldo con los valores ya calculados. No inventa magnitudes."""

from __future__ import annotations

from services.escenario_inicial import escenario_de, listar_pozos, localizar
from services.formato_numero import formato_visible

CATALOGO = {
    "frecuencia_hz": ("Frecuencia de operación", "Hz", "Frecuencia registrada para el punto de la hoja.", "entrada"),
    "caudal_operacion_bfpd": ("Caudal de operación", "BFPD", "Caudal registrado en la hoja. No es el caudal de intersección.", "entrada"),
    "caudal_fluidos": ("Q-fluidos", "BFPD", "Caudal de fluidos usado en la partición.", "entrada"),
    "bsw": ("BSW", "fracción", "Fracción de agua y sedimentos del punto usado.", "entrada"),
    "presion_sensor_psi": ("Presión de sensor", "psi", "Presión medida en el sensor.", "medicion"),
    "thp_psi": ("THP", "psi", "Presión en la cabeza del pozo.", "medicion"),
    "pip_ft": ("PIP", "ft", "Presión de admisión calculada, en pies de fluido.", "resultado"),
    "thd_total_ft": ("THD", "ft", "Altura total de descarga calculada.", "resultado"),
    "caudal_a_producir_bfpd": ("Caudal calculado", "BFPD", "Caudal de intersección del balance. No es el caudal registrado.", "resultado"),
    "gradiente_psi_ft": ("Gradiente", "psi/ft", "Gradiente publicado por el cálculo.", "resultado"),
    "q_fluidos": ("Q-fluidos", "BFPD", "Caudal de fluidos del resultado.", "resultado"),
    "q_water": ("Q-water", "BFPD", "Caudal de agua de la partición.", "resultado"),
    "q_oil": ("Q-oil", "BFPD", "Caudal de petróleo de la partición.", "resultado"),
}


def pozos_de(dataset_id: str | None, *, solo_evaluables: bool = True) -> list[str]:
    """Lista pozos del alcance. Por defecto solo expedientes con motor operativo."""
    pozos = []
    for item in listar_pozos():
        if dataset_id and item.get("dataset_id") != dataset_id:
            continue
        if solo_evaluables and not item.get("evaluable"):
            continue
        if item.get("pozo_id"):
            pozos.append(item["pozo_id"])
    return pozos


def completar(fila: dict) -> dict:
    """Añade entradas y presiones de la ficha que el resultado no trae."""
    salida = dict(fila)
    presentes = {item["id"] for item in salida.get("magnitudes") or []}
    extra = []
    for nombre, valor in (fila.get("entradas") or {}).items():
        if nombre in presentes or valor is None:
            continue
        if isinstance(valor, dict):
            continue
        extra.append(_item(nombre, valor, CATALOGO.get(nombre, ("", "", "", ""))[1], "entrada"))
        presentes.add(nombre)
    encontrados = localizar(fila.get("pozo") or "")
    if len(encontrados) == 1:
        ficha, pozo = encontrados[0]
        salida["dataset_id"] = salida.get("dataset_id") or ficha.identificador
        salida["bomba"] = pozo.get("bomba_referencia") or ""
        escenario = escenario_de(pozo, ficha)
        for control in escenario.get("controles") or []:
            if control.get("id") in presentes or control.get("valor_inicial") is None:
                continue
            extra.append(_item(control["id"], control.get("valor_inicial"), control.get("unidad") or "", "entrada", control.get("nombre")))
            presentes.add(control["id"])
        condiciones = pozo.get("condiciones_registradas") if isinstance(pozo.get("condiciones_registradas"), dict) else {}
        for clave in ("presion_sensor_psi", "thp_psi"):
            if clave in presentes or condiciones.get(clave) is None:
                continue
            extra.append(_item(clave, condiciones[clave], CATALOGO[clave][1], "medicion", CATALOGO[clave][0]))
    salida["magnitudes"] = list(salida.get("magnitudes") or []) + extra
    return salida


def redactar(tema: str, filas: list[dict], dataset_id: str | None = None) -> str:
    filas = [completar(fila) for fila in filas]
    if tema == "inventario":
        return _inventario(filas, dataset_id)
    if not filas:
        return "No hay un resultado consultable para esa pregunta."
    if tema == "medidas":
        return _medidas(filas)
    if tema == "presiones":
        return _presiones(filas)
    if tema == "caudal":
        return _caudal(filas)
    if tema == "frecuencia":
        return _frecuencia(filas)
    return _estado(filas)


def corpus(filas: list[dict], respaldo: str) -> str:
    partes = [respaldo]
    for fila in filas:
        partes.append(str(fila.get("pozo") or ""))
        partes.append(str(fila.get("rotulo") or ""))
        for item in fila.get("magnitudes") or []:
            partes.append(str(item.get("visible") or ""))
            partes.append(str(item.get("unidad") or ""))
    return " ".join(partes)


def _item(identificador: str, valor, unidad: str, tipo: str, nombre: str | None = None) -> dict:
    ficha = CATALOGO.get(identificador)
    return {
        "id": identificador,
        "nombre": nombre or (ficha[0] if ficha else identificador),
        "visible": formato_visible(valor) if not isinstance(valor, str) else valor,
        "unidad": unidad or (ficha[1] if ficha else ""),
        "tipo": tipo,
        "descripcion": ficha[2] if ficha else "",
    }


def _lista(magnitudes: list[dict], tipos: set[str] | None = None) -> str:
    partes = []
    for item in magnitudes:
        if tipos and item.get("tipo") not in tipos:
            continue
        if not item.get("visible"):
            continue
        unidad = f" {item['unidad']}" if item.get("unidad") else ""
        partes.append(f"{item['nombre']} {item['visible']}{unidad}")
    return "; ".join(partes)


def _procedencia(fila: dict) -> str:
    if fila.get("modo") == "simulacion":
        return "Estos valores corresponden a una simulación y no se escribieron en la hoja."
    return "Estos valores corresponden al punto registrado en la hoja y al cálculo de ese punto."


def _significado(fila: dict) -> str:
    reglas = set(fila.get("reglas") or [])
    if fila.get("rotulo") == "NORMAL" or "RC-BES-03" in reglas:
        return "El caudal queda entre el mínimo y el máximo escritos a esta frecuencia."
    if fila.get("rotulo") == "REGISTRO":
        return "Hay un resultado calculado. Este expediente no clasifica el punto con una regla de caudal."
    if fila.get("codigo") == "INCIPIENTE" or fila.get("rotulo") == "INCIPIENTE":
        return "El caudal registrado queda fuera de uno de los límites escritos."
    if fila.get("codigo") == "CRITICO" or fila.get("rotulo") == "CRÍTICO":
        return "Una regla marcada como límite crítico está activa en este escenario."
    return ""


def _estado(filas: list[dict]) -> str:
    if len(filas) == 1:
        fila = filas[0]
        escenario = fila.get("escenario_id") or ""
        frase = f"El pozo {fila['pozo']} presenta el estado {fila.get('rotulo') or 'sin clasificación'}"
        if escenario:
            frase += f" en el escenario {escenario}"
        frase += "."
        valores = _lista(fila.get("magnitudes") or [])
        partes = [frase]
        if valores:
            partes.append(f"Sus valores son: {valores}.")
        significado = _significado(fila)
        if significado:
            partes.append(significado)
        partes.append(_procedencia(fila))
        return " ".join(partes)
    dataset = filas[0].get("dataset_id") or "el dataset"
    partes = [f"En {dataset} hay {len(filas)} pozos con resultado consultable."]
    for fila in filas:
        caudal = _lista(fila.get("magnitudes") or [], {"resultado", "entrada"})
        detalle = f"{fila['pozo']} está en {fila.get('rotulo') or 'sin clasificación'}"
        if caudal:
            detalle += f" ({caudal})"
        partes.append(detalle + ".")
    return " ".join(partes)


def _medidas(filas: list[dict]) -> str:
    if len(filas) == 1:
        fila = filas[0]
        valores = _lista(fila.get("magnitudes") or [])
        return (
            f"Para el pozo {fila['pozo']} las magnitudes disponibles, con su unidad, son: {valores}. "
            "Cada una conserva la unidad del registro o del cálculo."
        )
    nombres = []
    for fila in filas:
        for item in fila.get("magnitudes") or []:
            etiqueta = f"{item['nombre']} ({item['unidad']})" if item.get("unidad") else item["nombre"]
            if etiqueta not in nombres:
                nombres.append(etiqueta)
    dataset = filas[0].get("dataset_id") or "el dataset"
    return (
        f"En {dataset} hay {len(filas)} pozos. Las magnitudes comunes incluyen {', '.join(nombres)}. "
        + " ".join(f"{fila['pozo']}: {_lista(fila.get('magnitudes') or [])}." for fila in filas)
    )


def _presiones(filas: list[dict]) -> str:
    textos = []
    for fila in filas:
        en_psi = [item for item in fila.get("magnitudes") or [] if item.get("unidad") == "psi"]
        en_pies = [
            item for item in fila.get("magnitudes") or []
            if item.get("id") == "pip_ft" or (item.get("unidad") == "ft" and "PIP" in str(item.get("nombre") or "").upper())
        ]
        partes = [f"En el pozo {fila['pozo']}"]
        disponibles = []
        if en_psi:
            disponibles.append(_lista(en_psi))
        if en_pies:
            disponibles.append(_lista(en_pies) + " (en pies de fluido)")
        if disponibles:
            partes.append("las magnitudes de presión disponibles son " + "; ".join(disponibles) + ".")
            if en_pies:
                partes.append("La PIP publicada está en pies de fluido y se distingue de las lecturas en psi.")
        else:
            partes.append("todavía no hay una magnitud de presión publicada para este punto.")
        textos.append(" ".join(partes))
    return " ".join(textos)


def _caudal(filas: list[dict]) -> str:
    textos = []
    for fila in filas:
        por_id = {item["id"]: item for item in fila.get("magnitudes") or []}
        partes = [f"En el pozo {fila['pozo']}"]
        registrado = por_id.get("caudal_operacion_bfpd") or por_id.get("caudal_fluidos") or por_id.get("q_fluidos")
        calculado = por_id.get("caudal_a_producir_bfpd")
        if registrado:
            partes.append(f"el caudal registrado es {registrado['visible']} {registrado['unidad']}.")
        if calculado:
            partes.append(
                f"El caudal calculado de intersección es {calculado['visible']} {calculado['unidad']}. "
                "No es el mismo valor que el caudal registrado."
            )
        if not registrado and not calculado:
            partes.append("no hay un caudal publicado en el resultado.")
        textos.append(" ".join(partes))
    return " ".join(textos)


def _frecuencia(filas: list[dict]) -> str:
    textos = []
    for fila in filas:
        hallada = next((item for item in fila.get("magnitudes") or [] if item["id"] == "frecuencia_hz"), None)
        if hallada:
            textos.append(f"El pozo {fila['pozo']} utiliza una frecuencia de {hallada['visible']} {hallada['unidad']}.")
        else:
            textos.append(f"El pozo {fila['pozo']} no tiene una frecuencia publicada en el resultado.")
    return " ".join(textos)


def _inventario(filas: list[dict], dataset_id: str | None) -> str:
    vistos = listar_pozos()
    if dataset_id:
        vistos = [item for item in vistos if item.get("dataset_id") == dataset_id]
    if not vistos:
        return "No hay pozos cargados en el dataset seleccionado."
    grupos: dict[str, list[str]] = {}
    for item in vistos:
        grupos.setdefault(item.get("bomba_referencia") or "sin referencia de bomba", []).append(item["pozo_id"])
    dataset = dataset_id or vistos[0].get("dataset_id") or "el dataset"
    bombas = "; ".join(f"{bomba} ({', '.join(pozos)})" for bomba, pozos in grupos.items())
    return (
        f"En {dataset} hay {len(vistos)} pozos de bombeo electrosumergible. "
        f"Las referencias de bomba escritas son: {bombas}."
    )
