"""Explicaciones determinísticas del «por qué». No inventan cifras ni rehacen el motor."""

from __future__ import annotations

from services.chat_hechos import CATALOGO
from services.chat_presentacion import formato_es, magnitud


def explicar_estado(fila: dict) -> dict:
    """Devuelve título, resumen, párrafos y fórmulas comentadas para el rótulo del pozo."""
    rotulo = str(fila.get("rotulo") or "sin clasificación")
    pozo = fila.get("pozo") or "el pozo"
    dataset = fila.get("dataset_id") or "el expediente"
    freq, u_f = magnitud(fila, "frecuencia_hz")
    q_reg, u_qr = magnitud(fila, "caudal_operacion_bfpd")
    if not q_reg:
        q_reg, u_qr = magnitud(fila, "caudal_fluidos")
    q_calc, u_qc = magnitud(fila, "caudal_a_producir_bfpd")
    pip, u_p = magnitud(fila, "pip_ft")
    thd, u_t = magnitud(fila, "thd_total_ft")

    hechos = []
    if freq:
        hechos.append(f"frecuencia {formato_es(freq)} {u_f}".strip())
    if q_reg:
        hechos.append(f"caudal registrado {formato_es(q_reg)} {u_qr}".strip())
    if q_calc:
        hechos.append(f"caudal calculado {formato_es(q_calc)} {u_qc}".strip())
    if pip:
        hechos.append(f"PIP {formato_es(pip)} {u_p}".strip())
    if thd:
        hechos.append(f"THD {formato_es(thd)} {u_t}".strip())
    hechos_txt = "; ".join(hechos) if hechos else "los valores publicados del resultado"

    if rotulo == "NORMAL":
        resumen = (
            f"{pozo} está en NORMAL porque el caudal queda entre el mínimo y el máximo "
            f"escritos para esta frecuencia en {dataset}."
        )
        parrafos = [
            resumen,
            f"En el resultado consultado intervienen: {hechos_txt}.",
            "Ese rótulo describe la comparación con los límites de la hoja. "
            "No autoriza una maniobra ni certifica la operación en campo.",
        ]
        formulas = _formulas_bes_limites(freq, q_calc, u_qc)
        return {
            "titulo": f"Por qué {pozo} está en NORMAL",
            "resumen": resumen,
            "parrafos": parrafos,
            "formulas": formulas,
            "cierre": "En BES-jun, NORMAL equivale a cumplir la comparación de caudal a la frecuencia del punto.",
        }

    if rotulo == "REGISTRO":
        resumen = (
            f"{pozo} está en REGISTRO porque el motor sí calculó el punto, "
            f"pero el expediente {dataset} no aplica umbrales de caudal para clasificarlo."
        )
        parrafos = [
            "Hay un resultado numérico disponible: el cálculo se completó.",
            (
                "Este dataset no compara ese caudal con un mínimo y un máximo de hoja "
                "(como hace BES-jun). Sin esa comparación, el sistema no puede etiquetar "
                "el punto como operación dentro o fuera de rango."
            ),
            f"En el resultado actual figuran: {hechos_txt}.",
            (
                "REGISTRO no indica fallo ni que el pozo esté sin procesar: "
                "es la etiqueta prevista cuando hay cálculo y no hay regla de caudal."
            ),
        ]
        formulas = [
            {
                "nombre": "Etiqueta REGISTRO",
                "expresion": "resultado calculado + sin regla de caudal → REGISTRO",
                "comentario": (
                    "En expedientes sin RC-BES (p. ej. RB-1521 o RB-IA-2191) el motor "
                    "aplica solo su identidad verificada. No usa las reglas de caudal de BES-jun."
                ),
            },
        ]
        return {
            "titulo": f"Por qué {pozo} está en REGISTRO",
            "resumen": resumen,
            "parrafos": parrafos,
            "formulas": formulas,
            "cierre": (
                "Si se necesita una etiqueta por límites de caudal, hace falta un expediente "
                "que defina esa regla (por ejemplo BES-jun)."
            ),
        }

    if rotulo in ("INCIPIENTE",):
        resumen = (
            f"{pozo} está en INCIPIENTE porque el caudal queda fuera de uno de los límites "
            f"escritos a esta frecuencia."
        )
        parrafos = [
            resumen,
            f"Magnitudes del punto: {hechos_txt}.",
            "INCIPIENTE avisa de un desvío respecto del texto de la hoja. "
            "No es, por sí solo, un límite crítico validado para operar.",
        ]
        return {
            "titulo": f"Por qué {pozo} está en INCIPIENTE",
            "resumen": resumen,
            "parrafos": parrafos,
            "formulas": _formulas_bes_limites(freq, q_calc, u_qc),
            "cierre": "Conviene revisar si el caudal registrado o el calculado quedó bajo el mínimo o sobre el máximo.",
        }

    if rotulo in ("CRÍTICO", "CRITICO"):
        resumen = f"{pozo} está en CRÍTICO porque una regla marcada como límite crítico validado está activa."
        return {
            "titulo": f"Por qué {pozo} está en CRÍTICO",
            "resumen": resumen,
            "parrafos": [
                resumen,
                f"Magnitudes del punto: {hechos_txt}.",
                "En BES-jun esa marca crítica validada no se emite en la versión actual.",
            ],
            "formulas": [],
            "cierre": "No interprete este rótulo como autorización o como orden de campo.",
        }

    return {
        "titulo": f"Estado de {pozo}",
        "resumen": f"El pozo {pozo} presenta el estado {rotulo}.",
        "parrafos": [
            f"El pozo {pozo} presenta el estado {rotulo}.",
            f"Magnitudes publicadas: {hechos_txt}.",
        ],
        "formulas": [],
        "cierre": "El estado corresponde al último resultado calculado del expediente.",
    }


def explicar_caudal(fila: dict) -> dict:
    """Explica por qué aparece el caudal registrado y/o el calculado."""
    pozo = fila.get("pozo") or "el pozo"
    dataset = fila.get("dataset_id") or "el expediente"
    freq, u_f = magnitud(fila, "frecuencia_hz")
    q_reg, u_qr = magnitud(fila, "caudal_operacion_bfpd")
    if not q_reg:
        q_reg, u_qr = magnitud(fila, "caudal_fluidos")
    q_calc, u_qc = magnitud(fila, "caudal_a_producir_bfpd")
    thd, u_t = magnitud(fila, "thd_total_ft")

    parrafos = [
        f"En {pozo} ({dataset}) conviene separar dos caudales distintos.",
    ]
    if q_reg:
        parrafos.append(
            f"El caudal registrado es {formato_es(q_reg)} {u_qr}. "
            "Sale de la hoja o del escenario; no lo inventa el asistente."
        )
    if q_calc:
        parrafos.append(
            f"El caudal calculado es {formato_es(q_calc)} {u_qc}. "
            "Es el punto de intersección entre la curva de la bomba (ajustada a la frecuencia) "
            "y la curva del sistema (altura total)."
        )
    if freq:
        parrafos.append(
            f"La frecuencia usada en este punto es {formato_es(freq)} {u_f}."
        )
    if thd:
        parrafos.append(
            f"La altura total (THD) publicada es {formato_es(thd)} {u_t}. "
            "Esa altura es la carga que el sistema opone a la bomba."
        )
    if not q_reg and not q_calc:
        parrafos.append("En este resultado todavía no hay un caudal publicado.")

    formulas = [
        {
            "nombre": "Idea del caudal calculado",
            "expresion": "Q_calculado = intersección(curva_bomba(f), curva_sistema)",
            "comentario": (
                "A mayor frecuencia, la curva de la bomba se desplaza. "
                "La curva del sistema usa la altura total del balance. "
                "Donde ambas se cruzan aparece el caudal calculado."
            ),
        },
        {
            "nombre": "Caudal registrado frente al calculado",
            "expresion": "Q_registrado ≠ Q_calculado (en general)",
            "comentario": (
                "El registrado es el valor escrito en la hoja. "
                "El calculado es el de la intersección. Compararlos ayuda a interpretar el punto, "
                "pero uno no sustituye al otro."
            ),
        },
    ]
    if dataset == "RB-1521":
        formulas = [
            {
                "nombre": "Caudal en RB-1521",
                "expresion": "reparto de caudales del motor propio del expediente",
                "comentario": (
                    "RB-1521 no usa la intersección RC-BES de BES-jun. "
                    "El valor mostrado sale de su motor de partición."
                ),
            },
        ]

    resumen = (
        f"El caudal de {pozo} se explica con los valores del expediente"
        + (f": calculado {formato_es(q_calc)} {u_qc}" if q_calc else "")
        + (f" y registrado {formato_es(q_reg)} {u_qr}" if q_reg else "")
        + "."
    )
    return {
        "titulo": f"Por qué {pozo} entrega ese caudal",
        "resumen": resumen,
        "parrafos": parrafos,
        "formulas": formulas,
        "cierre": "Las cifras anteriores son las del resultado ya calculado; no son una simulación nueva.",
    }


def _formulas_bes_limites(freq, q_calc, u_qc) -> list[dict]:
    formulas = [
        {
            "nombre": "Comparación de estado (BES-jun)",
            "expresion": "Q_min(f) ≤ Q ≤ Q_max(f)  →  NORMAL",
            "comentario": (
                "Los límites mínimo y máximo se toman de la hoja y se ajustan a la frecuencia f del punto. "
                "Si el caudal de la comparación queda dentro, el rótulo es NORMAL."
            ),
        },
        {
            "nombre": "Fuera de un límite",
            "expresion": "Q < Q_min(f)  o  Q > Q_max(f)  →  INCIPIENTE",
            "comentario": (
                "Quedar bajo el mínimo o sobre el máximo activa la alerta temprana. "
                "No es automáticamente un crítico validado."
            ),
        },
        {
            "nombre": "Cadena de cálculo (lectura sencilla)",
            "expresion": "fluido → balance (THD, PIP, …) → intersección (Q_calculado)",
            "comentario": (
                "Primero se resuelven propiedades de fluido, luego el balance de alturas "
                "y al final la intersección que entrega el caudal calculado."
            ),
        },
    ]
    if q_calc:
        formulas.append({
            "nombre": "Valor usado en este pozo",
            "expresion": f"Q_calculado ≈ {formato_es(q_calc)} {u_qc or 'BFPD'}".strip(),
            "comentario": (
                f"A frecuencia {formato_es(freq)} Hz." if freq else
                "Es el caudal de intersección publicado para este punto."
            ),
        })
    return formulas


def bloques_para_presentacion(explicacion: dict) -> list[dict]:
    """Convierte la explicación en secciones compatibles con chat_presentacion."""
    resumen = str(explicacion.get("resumen") or "").strip()
    parrafos = []
    for item in explicacion.get("parrafos") or []:
        texto = str(item).strip()
        if not texto or texto == resumen:
            continue
        parrafos.append(texto)
    secciones = [{
        "titulo": "Argumentación",
        "parrafos": parrafos,
        "tabla": None,
        "lista": [],
    }]
    formulas = explicacion.get("formulas") or []
    if formulas:
        lista = []
        for item in formulas:
            lista.append(
                f"{item.get('nombre')}: {item.get('expresion')}. {item.get('comentario')}"
            )
        secciones.append({
            "titulo": "Relación usada (comentada)",
            "parrafos": [
                "Las expresiones siguientes resumen la lógica del expediente. "
                "No sustituyen al cálculo del motor ni autorizan una maniobra."
            ],
            "tabla": None,
            "lista": lista,
        })
    if explicacion.get("cierre"):
        secciones.append({
            "titulo": "En resumen",
            "parrafos": [explicacion["cierre"]],
            "tabla": None,
            "lista": [],
        })
    return secciones
