"""Escribe ``integracion/`` a partir del código y del libro. No inventa pozos ni umbrales."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from catalogo.variables_bes_jun import con_rangos_observados
from evaluacion.contratos import VERSION_CONTRATO, esquema_entrada, esquema_salida
from evaluacion.motor import MODELOS, VERSION_MOTOR, evaluar, evaluar_solicitud
from informes.ficha_maestra import escribir as escribir_ficha
from ingesta.integridad import huellas
from ingesta.leer_bes_jun import COPIA_TRABAJO, leer_libro, raiz_expediente
from reglas.catalogo import REGLAS, VERSION_CATALOGO, markdown_reglas

VERSION_PAQUETE = "0.4.2"


def construir(raiz: Path | None = None) -> Path:
    raiz = Path(raiz) if raiz is not None else raiz_expediente()
    hojas = leer_libro()
    destino = raiz / "integracion"
    ejemplos = destino / "ejemplos"
    destino.mkdir(parents=True, exist_ok=True)
    ejemplos.mkdir(parents=True, exist_ok=True)
    (destino / "pruebas").mkdir(parents=True, exist_ok=True)

    pozos = [_pozo(h) for h in hojas]
    variables = con_rangos_observados(hojas)
    reglas = [dict(r) for r in REGLAS]
    huella = huellas(COPIA_TRABAJO)
    manifiesto = {
        "dataset_id": "BES-jun",
        "version": VERSION_PAQUETE,
        "esquema_contrato": VERSION_CONTRATO,
        "estado_dataset": "validacion_pendiente",
        "estado_reglas": "pendiente_validacion",
        "archivo_entrada": "entrada/BES_jun.xlsx",
        "sha256_entrada": huella["sha256"],
        "bytes_entrada": huella["bytes"],
        "fecha_construccion": date.today().isoformat(),
        "modelos": [m["id"] for m in MODELOS],
        "reglas": [r["id"] for r in REGLAS],
        "reglas_aprobadas": [r["id"] for r in REGLAS if r["aprobada_para_uso_operacional"]],
        "pozos": [p["pozo_rotulo"] for p in pozos],
        "dependencias": ["Python del entorno del proyecto", "openpyxl", "sin red", "sin modelo de lenguaje"],
        "limitaciones": [
            "La identidad Cluster/Pozo no está confirmada.",
            "Ninguna regla está aprobada para uso operacional.",
            "CT-01 a CT-10 siguen abiertas.",
            "El rango observado de frecuencia no es un límite autorizado.",
        ],
        "compatibilidad": {"contrato": VERSION_CONTRATO, "motor": VERSION_MOTOR, "catalogo_reglas": VERSION_CATALOGO},
    }
    _json(destino / "manifiesto.json", manifiesto)
    _json(destino / "pozos.json", {"dataset_id": "BES-jun", "pozos": pozos})
    _json(destino / "variables.json", {"dataset_id": "BES-jun", "variables": variables})
    _json(destino / "modelos.json", {"dataset_id": "BES-jun", "modelos": list(MODELOS)})
    _json(destino / "reglas.json", {"dataset_id": "BES-jun", "version": VERSION_CATALOGO, "reglas": reglas})
    _json(destino / "contrato_entrada.schema.json", esquema_entrada())
    _json(destino / "contrato_salida.schema.json", esquema_salida())

    solicitud = {
        "dataset_id": "BES-jun",
        "pozo_id": "QF-084",
        "version_configuracion": VERSION_CONTRATO,
        "fecha_observacion": None,
        "variables": [],
    }
    _json(ejemplos / "solicitud_qf084.json", solicitud)
    _json(ejemplos / "resultado_qf084.json", evaluar("BES-jun", "QF-084", hojas=hojas))
    _plantillas(ejemplos / "plantillas", hojas)

    (destino / "README.md").write_text(_guia(pozos), encoding="utf-8")
    (destino / "capa_linguistica.md").write_text(_capa(), encoding="utf-8")
    (destino / "pruebas" / "LEEME.md").write_text(
        "Las pruebas ejecutables están en `tests/`.\n"
        "No hay un doble de esas pruebas aquí: una copia se desalinea.\n"
        "Desde la raíz del expediente, sin Jupyter:\n\n"
        "    PYTHONPATH=src /home/antonio/projects/HUC/.venv/bin/python -m evaluacion.autotest\n",
        encoding="utf-8",
    )
    (raiz / "docs" / "reglas_candidatas.md").write_text(markdown_reglas(), encoding="utf-8")
    (raiz / "docs" / "catalogo_variables_BES-jun.md").write_text(_variables_md(variables), encoding="utf-8")
    (raiz / "docs" / "linaje_artefactos.md").write_text(_linaje(raiz), encoding="utf-8")
    escribir_ficha()
    return destino


def _pozo(h: dict) -> dict:
    return {
        "dataset_id": "BES-jun",
        "hoja": h["hoja"],
        "cluster": h["cluster"],
        "pozo_rotulo": h["pozo"],
        "estado_identidad": "provisional",
        "motivo_identidad": "El libro no declara si la llave es la hoja, el Cluster o el Pozo.",
        "bomba_referencia": h["bomba_referencia"],
        "etapas": h["etapas"],
        "id_tubing_in": h["id_tubing_in"],
        "profundidades_ft": {
            "tvd_descarga": h["tvd_descarga_ft"],
            "tvd_intake": h["tvd_intake_ft"],
            "tvd_sensor": h["tvd_sensor_ft"],
            "md_descarga": h["md_descarga_ft"],
            "md_intake": h["md_intake_ft"],
            "md_sensor": h["md_sensor_ft"],
        },
        "curva_60hz": h["curva"],
        "fluido": {
            "api_deg": h["api_deg"],
            "bsw_numero": h["bsw_numero"],
            "bsw_unidad_rotulo": h["bsw_unidad_rotulo"],
            "temperatura_c": h["temperatura_c"],
            "densidad_agua_lb_gal": h["densidad_agua_lb_gal"],
            "nota": "Si el valor coincide con el de otras hojas, no es una medición independiente comprobada.",
        },
        "condiciones_registradas": {
            "frecuencia_hz": h["frecuencia_hz"],
            "caudal_operacion_bfpd": h["caudal_operacion_bfpd"],
            "presion_sensor_psi": h["presion_sensor_psi"],
            "thp_psi": h["thp_psi"],
            "limite_minimo_bfpd_a_60hz": h["limite_minimo_bfpd"],
            "limite_maximo_bfpd_a_60hz": h["limite_maximo_bfpd"],
            "cono_eficiencia_bfpd": h["cono_eficiencia_bfpd"],
        },
        "fuente": "entrada/BES_jun.xlsx",
        "fecha_medicion": None,
        "fecha_en_la_hoja": h["fecha_cache"],
        "fecha_es_today": h["fecha_es_today"],
        "fecha_procesamiento": date.today().isoformat(),
        "calidad": "punto único; reproducción contra la caché de la misma hoja",
        "limitaciones": [
            "Sin fecha de medición comprobada.",
            "Límites escritos, no de fabricante confirmado.",
            "Curva de seis puntos, no una curva de catálogo verificada.",
        ],
    }


def _plantillas(destino: Path, hojas: list[dict]) -> None:
    """Ejemplos ejecutados contra el motor. Los caudales son los de la hoja, no una consigna."""
    destino.mkdir(parents=True, exist_ok=True)
    med = lambda nombre, valor, unidad: {"nombre": nombre, "valor": valor, "unidad": unidad, "procedencia": "operador"}
    base = {"dataset_id": "BES-jun", "pozo_id": "QF-084", "version_configuracion": VERSION_CONTRATO}
    casos = [
        ("01_minima_valida", {**base, "variables": []}, "Solicitud mínima. Usa la ficha registrada."),
        ("02_completa_valida", {**base, "variables": [med("caudal_operacion_bfpd", 10301, "BFPD"), med("frecuencia_hz", 63, "Hz")]}, "Caudal y frecuencia registrados de QF-084. No son una recomendación."),
        ("03_dato_nulo", {**base, "variables": [med("caudal_operacion_bfpd", None, "BFPD")]}, "Un nulo no se reemplaza por un promedio."),
        ("04_unidad_incorrecta", {**base, "variables": [med("caudal_operacion_bfpd", 10301, "m3/d")]}, "No hay conversión de unidades."),
        ("05_tipo_incorrecto", {**base, "variables": [{"nombre": ["frecuencia_hz"], "valor": 63, "unidad": "Hz", "procedencia": "operador"}]}, "El nombre de la variable es un texto."),
        ("06_dataset_desconocido", {**base, "dataset_id": "RB-1521", "variables": []}, "No se procesa otro dataset."),
        ("07_pozo_desconocido", {**base, "pozo_id": "NO-EXISTE", "variables": []}, "El identificador no está en las cinco hojas."),
        ("08_simulacion", {**base, "modo": "simulacion", "escenario_id": "ESC-PRUEBA", "variables": [med("caudal_operacion_bfpd", 11000, "BFPD")], "parametros_escenario": {"limite_maximo_bfpd": {"valor": 20000, "unidad": "BFPD"}}}, "Escenario hipotético. No actualiza la ficha ni autoriza operación. 11000 y 20000 son datos de prueba."),
        ("09_evaluacion_preliminar", {**base, "variables": []}, "La regla activada con la ficha registrada es preliminar."),
        ("10_regla_no_evaluable", {**base, "variables": []}, "RC-BES-04 viaja en la respuesta como no evaluable."),
    ]
    for nombre, solicitud, nota in casos:
        _json(destino / f"{nombre}.json", {
            "nota": nota,
            "solicitud": solicitud,
            "resultado": evaluar_solicitud(solicitud, hojas=hojas),
        })


def _json(ruta: Path, documento) -> None:
    ruta.write_text(json.dumps(documento, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _variables_md(variables: list[dict]) -> str:
    lineas = [
        "# Catálogo de variables · BES-jun",
        "",
        "Generado desde `catalogo.variables_bes_jun`. El rango observado no es un límite de operación.",
        "Los límites de frecuencia autorizados no están en el libro y no se inventan.",
        "",
        "| Nombre | Función | Unidad canónica | Obligatoria | Estado | Rango observado |",
        "|---|---|---|---|---|---|",
    ]
    for v in variables:
        rango = v.get("rango_observado")
        texto = "—" if not rango else f"{rango['minimo']:g} … {rango['maximo']:g} (n={rango['n']})"
        lineas.append(
            f"| `{v['nombre']}` | {v['funcion']} | {v['unidad'] or '—'} | "
            f"{'sí' if v['obligatoria'] else 'no'} | {v['estado_aprobacion']} | {texto} |"
        )
    lineas += [
        "",
        "La aplicación no debe pedir de nuevo un valor que ya está en `integracion/pozos.json` y que el operador no está corrigiendo. "
        "Si lo corrige, la solicitud lo declara en `variables` con su unidad.",
        "",
    ]
    return "\n".join(lineas)


def _linaje(raiz: Path) -> str:
    vigentes = {
        "reports/figuras/caudal_limites_por_hoja.png": "analisis.graficos.guardar_figuras",
        "reports/figuras/head_puntos_60hz.png": "analisis.graficos.guardar_figuras",
        "reports/figuras/survey_md_tvd_por_hoja.png": "analisis.graficos.guardar_figuras",
        "reports/figuras/inclinacion_survey_por_hoja.png": "analisis.graficos.guardar_figuras",
        "reports/figuras/interseccion_sistema_bomba.png": "analisis.graficos.guardar_figuras",
        "reports/figuras/impacto_ambiguedades_en_caudal.png": "analisis.graficos.guardar_figuras",
        "reports/figuras/elasticidad_q_estrella.png": "informes.escribir_informe, vía analisis.graficos.figura_elasticidades",
    }
    huerfanos = []
    for ruta in sorted((raiz / "reports" / "figuras").glob("*.png")):
        rel = str(ruta.relative_to(raiz))
        if rel not in vigentes:
            huerfanos.append(rel)
    lineas = [
        "# Linaje de artefactos derivados · BES-jun",
        "",
        "No se borró ningún archivo. Los huérfanos quedan nombrados para no usarlos en el informe.",
        "",
        "## Figuras vigentes",
        "",
        "| Archivo | Productor |",
        "|---|---|",
    ]
    for ruta, productor in vigentes.items():
        lineas.append(f"| `{ruta}` | `{productor}` |")
    lineas += ["", "## Figuras sin productor vigente", ""]
    for ruta in huerfanos:
        lineas.append(f"- `{ruta}`: versión anterior. El informe no la referencia.")
    if not huerfanos:
        lineas.append("- Ninguna en esta corrida.")
    lineas += [
        "",
        "## Datos procesados",
        "",
        "`data_procesados/resultados_deterministicos.csv` lo escribe el cuaderno `04_calculos_deterministicos`. "
        "`curvas_bomba_60hz.csv` lo escribe `03_mapeo_y_preparacion_BES_jun`. "
        "El resto de CSV y Markdown de esa carpeta sale de los cuadernos de inventario, calidad y mapeo. "
        "El informe consolidado no lee cifras de esos CSV: las recalcula al generarse.",
        "",
    ]
    return "\n".join(lineas)


def _guia(pozos: list[dict]) -> str:
    qf = next(p for p in pozos if p["pozo_rotulo"] == "QF-084")
    q = qf["condiciones_registradas"]["caudal_operacion_bfpd"]
    f = qf["condiciones_registradas"]["frecuencia_hz"]
    qmax = qf["condiciones_registradas"]["limite_maximo_bfpd_a_60hz"]
    filas = "\n".join(
        f"| {p['pozo_rotulo']} | {p['hoja']} | {p['cluster']} | {p['bomba_referencia']} | {p['estado_identidad']} |"
        for p in pozos
    )
    return f"""# Guía de integración del dataset BES-jun con el futuro sistema Asesor ESP

Esta guía es para quien vaya a conectar una aplicación con este expediente y no participó en el análisis.
El cálculo ya está hecho en Python. La aplicación no debe reimplementar las ecuaciones.

## Qué contiene el dataset

BES-jun es un libro de cinco hojas. Cada hoja es un punto de operación de una bomba electrosumergible: presiones, caudal, frecuencia, profundidades, una tabla de bomba de seis puntos a 60 Hz y un survey de trayectoria. No es una serie temporal. No es un catálogo de fabricante.

El archivo analizado es Copia de FINAL BES-jun.xlsx. La copia de trabajo, de solo cálculo, es `entrada/BES_jun.xlsx`. Su huella está en `manifiesto.json`.

## Qué pozos identifica

La identificación es provisional. En cada hoja el rótulo Cluster coincide con el nombre de la hoja y el rótulo Pozo es otro código. El libro no dice cuál es la llave. Dentro de este archivo cada código aparece una sola vez, así que el motor puede resolver la hoja. No debe fusionarse con un pozo de otro dataset solo porque el texto coincida, hasta que alguien confirme la llave.

| Pozo (rótulo) | Hoja | Cluster | Bomba escrita | Identidad |
|---|---|---|---|---|
{filas}

## Qué modelos hay

Tres, versión `transcripcion-1`, en `modelos.json`:

- `M-BES-FLUIDO`: gravedad, densidad y gradiente, como los escribe la hoja.
- `M-BES-BALANCE`: PIP, THP, fricción y THD.
- `M-BES-INTERSECCION`: caudal en el que la altura de la bomba iguala la THD.

Reproducen la caché de la hoja. Eso no aprueba la física. El signo del PIP, el exponente de la fricción y la unidad de BS&W tienen consultas abiertas.

## Qué reglas hay y cuáles están pendientes

`reglas.json` trae RC-BES-01, RC-BES-02, RC-BES-03 y RC-BES-04.

- RC-BES-01: caudal por encima del máximo escrito, ambos en la misma frecuencia.
- RC-BES-02: caudal por debajo del mínimo escrito, en la misma frecuencia.
- RC-BES-03: caudal entre esos dos límites, en la misma frecuencia.
- RC-BES-04: cercanía a la máxima eficiencia. **No evaluable.** No hay curva de fabricante.

Las tres primeras están en `pendiente_validacion`. Ninguna está aprobada. En las cinco hojas, con los datos registrados, la regla que se activa es RC-BES-03. En QF-084 el caudal es {q:.0f} BFPD a {f:.0f} Hz y el máximo a 60 Hz es {qmax:.0f} BFPD; escalado, el máximo es {qmax * f / 60:.0f} BFPD. Comparar el caudal de operación con el máximo de 60 Hz es un artefacto de la primera versión y no debe volver a mostrarse como la clasificación vigente. El escalamiento no valida el límite ni la afinidad.

## Qué variables hace falta

`variables.json` clasifica cada una. Para evaluar el punto ya registrado no hay que volver a teclear los parámetros de la hoja: están en `pozos.json`.

La aplicación pide una variable solo cuando el operador está corrigiendo una medición o cuando falta en la configuración. Si la envía, declara nombre, valor, unidad y procedencia (`configuracion_del_pozo`, `operador`, `sensor` o `no_declarada`).

En modo operacional el operador puede enviar caudal, frecuencia, presiones, temperatura, °API y BS&W, cada uno una sola vez y con su unidad canónica: caudal en BFPD, frecuencia en Hz, presiones en psi, temperatura en °C, BS&W como fracción, °API en °API. Límites, etapas, diámetro, profundidades, frecuencia de la curva, referencia de bomba y la tabla de seis puntos salen de la ficha del pozo. Enviarlos como medición produce `PARAMETRO_PROTEGIDO` y no se calcula. Una variable repetida, aunque los dos valores coincidan, produce `VARIABLE_DUPLICADA`: no se usa el primero ni el último. Un JSON con la misma clave dos veces se rechaza antes de construir el diccionario (`CLAVE_JSON_DUPLICADA`).

Un escenario hipotético pide `modo` = `simulacion`, un `escenario_id` y los cambios en `parametros_escenario`. El resultado lleva `hipotetico: true`, no actualiza la ficha y no autoriza una recomendación. La curva del escenario es una lista de al menos dos puntos, cada uno solo con `caudal_bfpd` y `head_ft` numéricos y finitos, en BFPD y ft, sin campos extra. En el orden enviado el caudal tiene que ser estrictamente creciente y el head estrictamente descendente. Es el contrato de esta representación, no una ley de todas las bombas. No se reordena, no se redondea para declarar un duplicado y no se elimina ningún punto. Un número suelto, un punto incompleto o un campo inesperado se rechazan como `entrada_invalida` y no llegan al cálculo. Un parámetro numérico del escenario solo admite `valor` y `unidad` canónica; no hay conversión. `fecha_observacion` es `AAAA-MM-DD` o esa fecha con hora ISO 8601. Si hay hora, puede llevar `Z` o `±HH:MM`. No se cambia de zona y no se usa la fecha `=TODAY()` del Excel. Los identificadores van sin espacios exteriores.

El contrato {VERSION_CONTRATO} rechaza la solicitud —estado `entrada_invalida`, `dataset_evaluado` nulo, cero reglas— si falta la versión, falta la unidad, el campo no existe, donde va un número llega un texto, el dataset no es BES-jun o se intenta usar la ficha de otro pozo. La salida distingue `dataset_solicitado` de `dataset_evaluado`. Un dataset ajeno no queda registrado como si se hubiera procesado.

`frecuencia_hz` es la frecuencia registrada. El rango observado de las cinco hojas no es el rango autorizado. El límite autorizado de frecuencia no está en el libro y el catálogo lo deja en null.

## Cómo se invoca el motor

Desde la raíz del expediente, con el entorno del proyecto:

    PYTHONPATH=src /home/antonio/projects/HUC/.venv/bin/python -m evaluacion.motor --dataset BES-jun --pozo QF-084

En código:

    from evaluacion.motor import evaluar, evaluar_solicitud
    evaluar("BES-jun", "QF-084")
    evaluar_solicitud(solicitud)

No hace falta Jupyter ni una pantalla. No llama a la red. No llama a un modelo de lenguaje.

## Cómo se lee el resultado

`estado_evaluacion` vale:

- `completada_preliminar`: se calculó y se aplicó la regla candidata. El resultado es preliminar.
- `no_evaluable`: falta un dato de la ficha, el pozo no está, la identidad es ambigua, el modelo no calculó o la regla no puede ejecutarse. No hay un sí ni un no forzados.
- `entrada_invalida`: la solicitud no pasó el esquema, la unidad, el dominio, la unicidad o la protección de la ficha. `errores` lista campo, código y detalle. `dataset_evaluado` es nulo y no se llama a los modelos.
- `error_interno`: la solicitud era válida y el modelo falló después. No es una entrada inválida y no es un resultado operacional.

Cada elemento de `reglas` trae `id`, `estado_regla`, `resultado`, `evaluable`, `aprobada_para_uso_operacional`, `evidencia` y `limitaciones`. La evidencia numérica está en `evidencia`, no en el texto del mensaje.

`recomendacion_operacional_autorizada` es falso mientras no exista una regla aprobada para ese uso. La aplicación no debe convertir una advertencia preliminar en una orden de bajar o subir la frecuencia.

## Códigos de error

Cada elemento de `errores` trae `campo`, `codigo`, `detalle` y `mensaje`. Si aplica, también `tipo_esperado` y `unidad_esperada`. El valor recibido no se copia a un campo de la respuesta que no acepte ese tipo.

| Código | Cuándo |
|---|---|
| `TIPO_INVALIDO` | El dato no es del tipo del contrato |
| `UNIDAD_AUSENTE` / `UNIDAD_INCOMPATIBLE` | Falta la unidad o no es la canónica. No hay conversión |
| `VARIABLE_DUPLICADA` / `CLAVE_JSON_DUPLICADA` | La misma variable o la misma clave JSON aparece más de una vez |
| `PARAMETRO_PROTEGIDO` | Se intenta cambiar la ficha en modo operacional |
| `ENTRADA` inválida por `LIMITE_TAMANO` | El JSON, la profundidad o el número de elementos supera el límite y no se recorre |
| `DATASET_DESCONOCIDO` / `VERSION_INCOMPATIBLE` | Dataset o contrato que este motor no evalúa |
| `FISICAMENTE_INADMISIBLE` / `VALOR_NO_FINITO` | Dominio de la fórmula, no un límite operacional aprobado |
| `ERROR_INTERNO` | Fallo imprevisto. `incidente_id` identifica el registro interno. No hay recomendación |

Una regla `pendiente_validacion` es una observación preliminar. `no_evaluable` significa que falta evidencia, no que el pozo esté bien ni mal. No se completa una medición ausente con un promedio.

Las plantillas ejecutables están en `ejemplos/plantillas/`. Cada archivo trae la solicitud y el resultado que produjo este motor. Los números de QF-084 son los registrados en la hoja, no una recomendación.

Desde Python, en la raíz del expediente:

    from evaluacion.motor import evaluar_solicitud
    evaluar_solicitud(solicitud)

## Errores y datos insuficientes

Un error de validación y un caso no evaluable no se presentan igual. El primero rechaza la solicitud. El segundo acepta la solicitud y dice qué falta. Los dos dejan la recomendación operacional en falso.

La evidencia de la comparación sin escalar viaja dentro de la regla, marcada como no vigente, para que se pueda auditar el artefacto sin volver a usarlo como resultado.

## Qué puede hacer la aplicación

Puede listar los pozos de `pozos.json`, mostrar los parámetros registrados, enviar una corrección con unidad y pintar el JSON de salida campo por campo. Puede guardar la versión del motor y de la regla que aparecen en la respuesta.

## Qué no puede hacer

- Inventar un límite de frecuencia o un límite de fabricante.
- Tratar una regla pendiente como si estuviera aprobada.
- Ordenar un cambio de frecuencia, de etapas o de tubing a partir de RC-BES-01, 02 o 03.
- Declarar que el pozo está sano porque el caudal quedó entre los números de la hoja.
- Usar `=TODAY()` como fecha de la medición.
- Usar el nombre de la hoja como identificador global definitivo.
- Llamar a un modelo de lenguaje para que calcule o apruebe.
- Leer `reports/figuras/caudal_y_limites.png` ni `head_tabulado.png`: son figuras viejas. El linaje está en `docs/linaje_artefactos.md`.

## Modelo de lenguaje, más adelante

`capa_linguistica.md` dice qué JSON puede recibir y qué no puede redactar. Hasta que esa capa exista, la aplicación usa los campos `mensaje` de la respuesta. Esos textos ya distinguen observación, advertencia y condición no evaluable.

## Qué probar antes de usarlo

    PYTHONPATH=src /home/antonio/projects/HUC/.venv/bin/python -m evaluacion.autotest

Ese comando corre pytest sobre `tests/` y escribe `logs/autotest_reporte.json` y `logs/autotest_reporte.md`. Tiene que quedar en estado `aprobado`. En particular, con los datos registrados de QF-084 el resultado es RC-BES-03 y `recomendacion_operacional_autorizada` es falso.

## Cómo se regenera este paquete

    PYTHONPATH=src /home/antonio/projects/HUC/.venv/bin/python -m integracion.construir_paquete

Ese comando reescribe los JSON, esta guía, la ficha maestra y el catálogo de reglas. No mueve el expediente a `procesadas`.
"""


def _capa() -> str:
    return """# Capa de lenguaje futura · BES-jun

No hay integración con un proveedor. No hay una llamada simulada que parezca un servicio. Esta nota fija el contrato para cuando esa capa se construya. Mientras tanto, la aplicación muestra los mensajes que ya trae el JSON del motor.

## Qué puede recibir

Solo el resultado estructurado de `evaluacion.motor`, más la identificación provisional del pozo:

- hoja, cluster y rótulo de pozo, con el estado de identidad;
- variables enviadas y su unidad;
- valores de los modelos (`pip_ft`, `thd_total_ft`, `caudal_a_producir_bfpd`) tal como vienen;
- reglas evaluadas, si se activaron, y su evidencia numérica;
- advertencias, incluido el aviso de dominio observado;
- estado de aprobación de cada regla;
- el texto técnico ya redactado por el motor.

## Qué puede producir

- Una explicación en lenguaje corriente del JSON.
- Un resumen de las observaciones.
- La razón por la que una condición se marcó, citando el identificador de la regla.
- La lista de datos que faltan, si el estado es `no_evaluable`.
- La frase de que la regla no está aprobada, cuando `aprobada_para_uso_operacional` es falso.

## Qué no puede hacer

- Inventar un dato que no esté en el JSON.
- Cambiar un número.
- Inventar un límite.
- Cambiar una ecuación.
- Presentar una regla `pendiente_validacion` como aprobada.
- Indicar que se suba o se baje la frecuencia.
- Decir que el pozo está seguro.
- Omitir una advertencia o un dato faltante.
- Concluir algo sobre potencia, motor, cable o yacimiento: esos modelos no están en este expediente.

## Ejemplo con el punto registrado de QF-084

El motor devuelve RC-BES-03, estado de regla `pendiente_validacion`, y `recomendacion_operacional_autorizada` en falso. Un texto aceptable sería:

> En la hoja QF-554H, el caudal registrado queda entre el mínimo y el máximo escritos en esa hoja, después de llevarlos a la frecuencia de operación. La regla RC-BES-03 no está aprobada. Esto no autoriza a operar el pozo ni a cambiar la frecuencia. La identidad del pozo (QF-084 frente al nombre de la hoja) sigue sin confirmar.

Un texto inaceptable sería: «El pozo está en rango. Baje la frecuencia para alejarse del máximo.»

## Ejemplo si faltara el caudal

El estado sería `no_evaluable`. Un texto aceptable nombra el dato que falta y no elige RC-BES-01 ni RC-BES-03.

## Mensajes sin modelo de lenguaje

Cada regla del JSON trae `mensaje` y `tipo_mensaje` (`observacion`, `advertencia`, `informacion` o `condicion_no_evaluable`). La aplicación puede mostrarlos tal cual.
"""


def main() -> None:
    print(construir())


if __name__ == "__main__":
    main()
