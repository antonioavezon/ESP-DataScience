"""Reconoce la consulta sin ejecutar nada. El modelo no elige la fórmula."""

from __future__ import annotations

import re

from services.escenario_inicial import listar_pozos

_POZO = re.compile(r"QF-\d{3}", re.IGNORECASE)
_HZ = re.compile(r"(\d+(?:[.,]\d+)?)\s*hz\b", re.IGNORECASE)
_BFPD = re.compile(r"(\d+(?:[.,]\d+)?)\s*bfpd\b", re.IGNORECASE)
_MOVIMIENTO = re.compile(
    r"\b(muevo|mover|cambio|cambiar|llevo|llevar|pongo|poner|subo|subir|aumento|aumentar|reduzco|reducir|modifico|modificar)\b",
    re.IGNORECASE,
)
_ESTADO = re.compile(r"qu[eé] significa (este|el|ese|dicho) (estado|resultado)")
_AJENO = re.compile(
    r"\b(d[oó]lar|dolares|d[oó]lares|euro|bitcoin|clima|f[uú]tbol|receta|pel[ií]cula)\b",
    re.IGNORECASE,
)
_ESP = re.compile(
    r"\b(pozos?|bombas?|esp|bes|electrosumergibles?|pip|thd|caudal|frecuencia|"
    r"cavitaci[oó]n|admisi[oó]n|presi[oó]n|bfpd|fluido|sensor|altura|etapa|etapas|tubing|curva)\b",
    re.IGNORECASE,
)


def interpretar(consulta: str, contexto: dict | None = None, pozo_formulario: str | None = None, ambito: str | None = None) -> dict:
    texto = (consulta or "").strip()
    bajo = texto.lower()
    contexto = contexto if isinstance(contexto, dict) else {}
    pozos = _pozos_nombrados(texto)
    datasets = _datasets_nombrados(texto)
    if not pozos and pozo_formulario and pozo_formulario in _conocidos():
        pozos_form = [pozo_formulario]
    else:
        pozos_form = []
    cambios = {}
    hz = _HZ.search(texto)
    if hz:
        cambios["frecuencia_hz"] = float(hz.group(1).replace(",", "."))
    bfpd = _BFPD.search(texto)
    if bfpd:
        cambios["caudal_operacion_bfpd"] = float(bfpd.group(1).replace(",", "."))

    # Desconocidos: códigos con patrón QF-/RB- que no están en el inventario.
    mencionados = _codigos_mencionados(texto)
    desconocidos = [pozo for pozo in mencionados if pozo not in _conocidos()]
    if _es_ajena(bajo):
        return _decision("fuera_de_alcance", [], {}, "", datasets)
    if _es_adversarial(bajo):
        return _decision("fuera_de_alcance", [], {}, "seguridad", datasets)
    if _pide_autorizacion(bajo):
        return _decision("rechazar_autorizacion", [], {}, "ninguna", datasets)
    if cambios and (_es_hipotesis(bajo) or _MOVIMIENTO.search(bajo)):
        if desconocidos:
            return _decision("pozo_desconocido", desconocidos, {}, "", datasets)
        destino = pozos or pozos_form or _ancla(contexto, ambito)
        if not destino:
            return _decision("aclarar", [], cambios, "pozo", datasets)
        variable = "caudal_operacion_bfpd" if "caudal_operacion_bfpd" in cambios else "frecuencia_hz"
        return _decision("simular", destino[:1], cambios, variable, datasets)
    if "cavit" in bajo:
        return _decision("conceptual", [], {}, "cavitacion", datasets)
    if _es_definicion(bajo) and not pozos and not desconocidos and not _solo_anáfora(bajo) and not _pide_explicar_estado(bajo):
        return _decision("conceptual", [], {}, "pip" if "pip" in bajo else "general", datasets)
    if desconocidos:
        return _decision("pozo_desconocido", desconocidos, {}, "", datasets)
    # Pozo nombrado + «por qué el caudal…»
    if pozos and _pide_explicar_caudal(bajo):
        return _decision("caudal", pozos[:1], {}, "motivo_caudal", datasets)
    # Pozo nombrado en el texto + pregunta por su estado / por qué → manda sobre el selector vacío.
    if pozos and (_pide_estado(bajo) or _pide_explicar_estado(bajo) or _pide_reglas(bajo)):
        variable = "motivo_estado" if _pide_explicar_estado(bajo) else "estado"
        return _decision("estado", pozos[:1], {}, variable, datasets)
    if _ESTADO.search(bajo) and not cambios:
        destino = pozos or _destino_previo(pozos_form, contexto, ambito)
        if destino or ambito == "dataset":
            return _decision("estado", destino if destino else [], {}, "estado", datasets)
        return _decision("explicar_estado", [], {}, "reglas", datasets)
    if _es_hipotesis(bajo) and any(giro in bajo for giro in ("profund", "tvd", "potencia", "etapa")):
        return _decision("aclarar", pozos or pozos_form, {}, "no_autorizada", datasets)
    if "hidrost" in bajo and "pip" in bajo:
        return _decision("diferencia_pip", pozos or pozos_form or _ancla(contexto, ambito), {}, "pip_ft", datasets)
    if "compar" in bajo and (len(pozos) >= 2 or (ambito == "dataset" and not pozos)):
        return _decision("comparar", pozos[:4] if pozos else [], {}, "pip_ft", datasets)
    if _es_seguimiento(bajo):
        destino = pozos or pozos_form or _ancla(contexto, ambito)
        if destino:
            return _decision("seguimiento", destino[:1], {}, contexto.get("variable") or "pip_ft", datasets)
    if _pide_mayor(bajo):
        if ambito == "dataset" and not (contexto.get("pozos") or []) and not pozos:
            return _decision("comparar", [], {}, contexto.get("variable") or "caudal", datasets)
        return _decision("comparar_contexto", list(contexto.get("pozos") or []) or pozos, {}, contexto.get("variable") or "pip_ft", datasets)
    if _es_hipotesis(bajo):
        destino = pozos or pozos_form or _ancla(contexto, ambito)
        if not cambios:
            return _decision("aclarar", destino, {}, "frecuencia_hz", datasets)
        return _decision("simular", destino[:1], cambios, "frecuencia_hz" if "frecuencia_hz" in cambios else "caudal_operacion_bfpd", datasets)
    if _pide_explicar_caudal(bajo):
        destino = _ambito_pozos(pozos, pozos_form, ambito)
        return _decision("caudal", destino[:1] if destino else destino, {}, "motivo_caudal", datasets)
    if _pide_estado(bajo) or _pide_explicar_estado(bajo):
        destino = _ambito_pozos(pozos, pozos_form, ambito)
        variable = "motivo_estado" if _pide_explicar_estado(bajo) or len(destino) == 1 else "estado"
        return _decision("estado", destino, {}, variable, datasets)
    if _pide_reglas(bajo):
        return _decision("estado", (pozos or pozos_form or _ancla(contexto, ambito))[:1], {}, "estado", datasets)
    if pozos and _pide_medidas(bajo):
        return _decision("medidas", pozos, {}, "medidas", datasets)
    if pozos and _pide_presiones(bajo):
        return _decision("presiones", pozos, {}, "presiones", datasets)
    if pozos and _pide_frecuencia(bajo) and "hz" not in cambios:
        return _decision("frecuencia", pozos, {}, "frecuencia_hz", datasets)
    if pozos and _pide_caudal_simple(bajo) and "caudal_operacion_bfpd" not in cambios:
        return _decision("caudal", pozos, {}, "caudal", datasets)
    if _pide_medidas(bajo):
        return _decision("medidas", _ambito_pozos(pozos, pozos_form, ambito), {}, "medidas", datasets)
    if _pide_presiones(bajo):
        return _decision("presiones", _ambito_pozos(pozos, pozos_form, ambito), {}, "presiones", datasets)
    if _pide_frecuencia(bajo) and "hz" not in cambios:
        return _decision("frecuencia", _ambito_pozos(pozos, pozos_form, ambito), {}, "frecuencia_hz", datasets)
    if _pide_caudal_simple(bajo) and "caudal_operacion_bfpd" not in cambios:
        return _decision("caudal", _ambito_pozos(pozos, pozos_form, ambito), {}, "caudal", datasets)
    if _pide_inventario(bajo) and not pozos:
        return _decision("inventario", [], {}, "inventario", datasets)
    if _pide_calculo(bajo):
        variable = _variable(bajo)
        return _decision("calcular", (pozos or pozos_form or _ancla(contexto, ambito))[:1], {}, variable, datasets)
    if "eficiencia" in bajo:
        return _decision("aclarar", pozos or pozos_form or _ancla(contexto, ambito), {}, "eficiencia", datasets)
    if any(giro in bajo for giro in (
        "modelo determinístico", "modelo deterministico", "intersección de curvas", "interseccion de curvas",
        "cómo se compara", "como se compara", "compara con",
    )):
        if "compara" in bajo or "compar" in bajo:
            destino = pozos or pozos_form or _ancla(contexto, ambito)
            if len(destino) >= 2 or (pozos and len(pozos) >= 2):
                return _decision("comparar", (pozos or destino)[:4], {}, "pip_ft", datasets)
            if destino:
                return _decision("estado", destino[:1], {}, "estado", datasets)
        return _decision("consulta_esp", [], {}, "expediente", datasets)
    # Pozo citado sin selector: no degradar a inventario genérico.
    if pozos:
        return _decision("estado", pozos[:1], {}, "estado", datasets)
    if _ESP.search(bajo):
        return _decision("consulta_esp", [], {}, "expediente", datasets)
    return _decision("fuera_de_alcance", [], {}, "", datasets)


def _decision(intencion: str, pozos: list[str], cambios: dict, variable: str, datasets: list[str] | None = None) -> dict:
    return {
        "intencion": intencion,
        "pozos": pozos,
        "cambios": cambios,
        "variable": variable,
        "datasets": list(datasets or []),
    }


def _conocidos() -> set[str]:
    return {item["pozo_id"] for item in listar_pozos()}


def _datasets_conocidos() -> set[str]:
    from services.dataset_registry import descubrir

    return {ficha.identificador for ficha in descubrir()}


def _pozos_nombrados(texto: str) -> list[str]:
    conocidos = sorted(_conocidos(), key=len, reverse=True)
    vistos = []
    for nombre in conocidos:
        if re.search(rf"(?<![A-Za-z0-9]){re.escape(nombre)}(?![A-Za-z0-9])", texto, re.IGNORECASE):
            canon = next(item for item in _conocidos() if item.lower() == nombre.lower())
            if canon not in vistos:
                vistos.append(canon)
    return vistos


def _datasets_nombrados(texto: str) -> list[str]:
    """Detecta expedientes citados en la pregunta (p. ej. BES-jun), aunque el selector diga Todos."""
    vistos = []
    for nombre in sorted(_datasets_conocidos(), key=len, reverse=True):
        if re.search(rf"(?<![A-Za-z0-9]){re.escape(nombre)}(?![A-Za-z0-9])", texto, re.IGNORECASE):
            if nombre not in vistos:
                vistos.append(nombre)
    return vistos


def _codigos_mencionados(texto: str) -> list[str]:
    """Códigos con forma de pozo, conocidos o no (QF-xxx, RB-xxxx, RB-IA-xxxx)."""
    hallados = re.findall(r"\b(?:QF-\d{3}|RB-IA-\d+|RB-\d{4})\b", texto, re.IGNORECASE)
    salida = []
    for item in hallados:
        canon = item.upper() if item.upper().startswith("QF-") else item.upper().replace("RB-IA-", "RB-IA-")
        # Normalizar manteniendo el patrón registrado si existe.
        conocidos = {c.upper(): c for c in _conocidos()}
        clave = item.upper()
        valor = conocidos.get(clave, item if item in _conocidos() else clave)
        # Preferir forma canónica del inventario.
        for original in _conocidos():
            if original.upper() == item.upper():
                valor = original
                break
        if valor not in salida:
            salida.append(valor)
    return salida


def _ancla(contexto: dict, ambito: str | None) -> list[str]:
    if ambito == "dataset":
        return []
    return _ultimo(contexto)


def _destino_previo(pozos_form: list[str], contexto: dict, ambito: str | None) -> list[str]:
    if ambito == "dataset":
        return []
    return pozos_form or _ultimo(contexto)


def _ambito_pozos(pozos: list[str], pozos_form: list[str], ambito: str | None) -> list[str]:
    if pozos:
        return pozos
    if ambito == "dataset":
        return []
    return pozos_form


def _solo_anáfora(bajo: str) -> bool:
    limpio = bajo.strip(" ¿?").strip()
    return limpio in (
        "qué significa", "que significa", "qué significa eso", "que significa eso",
        "qué significa esto", "que significa esto", "qué significa ese valor", "que significa ese valor",
        "y qué significa", "y que significa", "y qué significa eso", "y que significa eso",
    )


def _es_adversarial(bajo: str) -> bool:
    return any(giro in bajo for giro in (
        "ignora las reglas", "modifica la fórmula", "modifica la formula", "inventa un",
        "inventa una", "revela tu system", "system prompt", "rm -rf", "ejecuta rm",
        "inyect", "<script", "dataset no autorizado", "cambia el estado a",
        "aunque sea normal", "omite las restricciones",
    ))


def _ultimo(contexto: dict) -> list[str]:
    pozo = contexto.get("pozo")
    return [pozo] if isinstance(pozo, str) and pozo else []


def _es_definicion(bajo: str) -> bool:
    if _ESTADO.search(bajo):
        return False
    # Evitar que «qué es» coincida dentro de «qué está».
    patrones = (
        r"\bqu[eé] es\b(?!t[aá])",
        r"\bque es\b(?!t[aá])",
        r"\bqu[eé] significa\b",
        r"\bque significa\b",
        r"\bdefine\b",
        r"\bdefinici[oó]n\b",
        r"\bqu[eé] representa\b",
        r"\bque representa\b",
        r"\bpara qu[eé] se utiliza\b",
        r"\bpara que se utiliza\b",
    )
    return any(re.search(p, bajo) for p in patrones)


def _es_ajena(bajo: str) -> bool:
    return _AJENO.search(bajo) is not None


def _pide_autorizacion(bajo: str) -> bool:
    riesgo = any(giro in bajo for giro in ("sin riesgo", "sin daños", "sin danos", "puedo aumentar", "puedo subir", "es seguro"))
    return riesgo and "frecuen" in bajo


def _es_hipotesis(bajo: str) -> bool:
    return any(giro in bajo for giro in (
        "qué pasaría", "que pasaria", "qué pasa si", "que pasa si",
        "qué sucede", "que sucede", "qué ocurr", "que ocurr",
        "si aument", "si modific", "si la frecuencia", "si bajo", "si subo",
        "si muevo", "si cambio", "si llevo", "si pongo",
    ))


def _pide_reglas(bajo: str) -> bool:
    return any(giro in bajo for giro in (
        "dentro del rango", "según las reglas", "segun las reglas",
        "cómo está funcionando", "como esta funcionando", "como esta funcionando",
    ))


def _pide_estado(bajo: str) -> bool:
    return any(giro in bajo for giro in (
        "cómo está el pozo", "como esta el pozo", "cómo están los pozos", "como estan los pozos",
        "cómo está funcionando", "como esta funcionando", "cómo está", "como esta",
        "en qué estado", "en que estado", "cómo se encuentra", "como se encuentra",
        "condición actual", "condicion actual", "qué está ocurriendo", "que esta ocurriendo",
        "cómo va su operación", "como va su operacion", "resumen del pozo", "resumen de este pozo",
        "está funcionando bien", "esta funcionando bien", "dame un resumen",
        "qué tal va", "que tal va", "qué está pasando", "que esta pasando",
        "cuál es su estado", "cual es su estado", "cómo andan los pozos", "como andan los pozos",
        "estado operacional", "estado operativo", "situación del pozo", "situacion del pozo",
        "cómo están los cinco", "como estan los cinco",
        "está bien", "esta bien", "interpretar estos resultados", "interpreta esta tabla",
        "interpretar esta tabla", "explicación más técnica", "explicacion mas tecnica",
        "primera vez viendo", "resultados principales", "resume las principales",
        "principales diferencias", "parámetros de forma sencilla", "parametros de forma sencilla",
        "está en estado", "esta en estado", "está en registro", "esta en registro",
        "está en normal", "esta en normal", "estado registro", "estado normal",
        "estado «registro»", "estado \"registro\"", "estado 'registro'",
        "explica el estado", "explícame el estado", "explicame el estado",
        "resume bes-jun", "resumen de bes-jun", "resume el dataset",
    ))


def _pide_explicar_estado(bajo: str) -> bool:
    """Preguntas del tipo «por qué está en REGISTRO» aunque no digan «cómo está»."""
    if any(giro in bajo for giro in (
        "por qué", "porque", "por que", "a qué se debe", "a que se debe",
        "qué significa ese estado", "que significa ese estado",
        "porqué", "porqué está", "porque esta",
    )):
        if any(giro in bajo for giro in (
            "estado", "registro", "normal", "crítico", "critico", "incipiente",
            "rótulo", "rotulo", "está", "esta", "pozo",
        )):
            return True
    return False


def _pide_explicar_caudal(bajo: str) -> bool:
    """«Por qué entrega ese caudal», «por qué el caudal es X»."""
    if not any(giro in bajo for giro in ("por qué", "porque", "por que", "porqué", "a qué se debe", "a que se debe")):
        return False
    return any(giro in bajo for giro in (
        "caudal", "produce", "producción", "produccion", "bfpd", "intersección", "interseccion",
        "entrega", "cómo se obtiene el caudal", "como se obtiene el caudal",
    ))


def _pide_medidas(bajo: str) -> bool:
    if any(giro in bajo for giro in ("qué representa", "que representa", "qué significa", "que significa", "qué es ", "que es ")):
        return False
    if any(giro in bajo for giro in ("dimensión", "dimension", "diámetro", "diametro", "longitud", "profundidad geométrica")):
        return False
    return any(giro in bajo for giro in (
        "qué medidas", "que medidas", "qué mediciones", "que mediciones", "qué variables", "que variables",
        "qué parámetros", "que parametros", "cuáles son sus parámetros", "cuales son sus parametros",
        "muéstrame sus valores", "muestrame sus valores", "muéstrame sus variables", "muestrame sus variables",
        "qué datos tenemos", "que datos tenemos", "qué valores tenemos", "que valores tenemos",
        "valores de entrada", "resultados produce", "qué resultados", "que resultados",
        "información importante", "informacion importante", "qué puedes explicar", "que puedes explicar",
    ))


def _pide_presiones(bajo: str) -> bool:
    return any(giro in bajo for giro in (
        "qué presión", "que presion", "qué niveles de presión", "que niveles de presion",
        "niveles de presión", "niveles de presion", "presión de admisión", "presion de admision",
        "presión en superficie", "presion en superficie", "thp",
        "presiones se utilizan", "presión corresponde al sensor", "presion corresponde al sensor",
        "unidades tienen estas magnitudes",
    ))


def _pide_caudal_simple(bajo: str) -> bool:
    return any(giro in bajo for giro in (
        "cuál es su caudal", "cual es su caudal", "qué caudal", "que caudal",
        "cuánto produce", "cuanto produce", "cuál es el caudal", "cual es el caudal",
        "caudal calculado", "caudal registrado", "mayor caudal",
    ))


def _pide_frecuencia(bajo: str) -> bool:
    return any(giro in bajo for giro in (
        "qué frecuencia", "que frecuencia", "cuál es la frecuencia", "cual es la frecuencia",
        "cuál es su frecuencia", "cual es su frecuencia", "mayor frecuencia",
        "frecuencia utiliza", "frecuencia usa", "su frecuencia",
    )) and "pasaría" not in bajo and "pasaria" not in bajo and "sucede" not in bajo


def _pide_inventario(bajo: str) -> bool:
    return any(giro in bajo for giro in (
        "cuántos pozos", "cuantos pozos", "qué pozos están", "que pozos estan", "qué pozos hay", "que pozos hay",
        "qué bombas", "que bombas", "qué tipos de bombas", "que tipos de bombas",
        "pozos tienen el mismo estado", "cuántos hay", "cuantos hay",
    ))


def _pide_calculo(bajo: str) -> bool:
    return any(giro in bajo for giro in ("pip", "thd", "caudal", "calcula", "calcular", "altura", "presión de admisión", "presion de admision"))


def _es_seguimiento(bajo: str) -> bool:
    limpio = bajo.strip(" ¿?")
    return (
        limpio.startswith("y ")
        or limpio.startswith("y su ")
        or limpio.startswith("y la ")
        or limpio.startswith("y el ")
        or limpio.startswith("y en ")
        or limpio.startswith("¿y ")
        or "y la de" in bajo
        or "y el de" in bajo
        or limpio in ("qué significa", "que significa", "qué significa eso", "que significa eso", "qué significa ese valor", "que significa ese valor")
    )


def _pide_mayor(bajo: str) -> bool:
    return "mayor" in bajo or "más alta" in bajo or "mas alta" in bajo or "cuál tiene" in bajo or "cual tiene" in bajo


def _variable(bajo: str) -> str:
    if "thd" in bajo or "altura" in bajo:
        return "thd_total_ft"
    if "caudal" in bajo and "pip" not in bajo and "admisión" not in bajo and "admision" not in bajo:
        return "caudal_operacion_bfpd"
    return "pip_ft"
