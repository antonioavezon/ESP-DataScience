"""Ficha Maestra de BES-jun. Los números salen del libro y del motor, no de una tabla copiada."""

from __future__ import annotations

import hashlib
from datetime import date

from analisis.cadena import calcular_hoja
from analisis.catalogo_bes_jun import FORMULAS
from evaluacion.motor import evaluar
from ingesta.integridad import huellas
from ingesta.leer_bes_jun import COPIA_TRABAJO, leer_libro, raiz_expediente
from reglas.candidatas_bes_jun import comparar_caudal_con_limites, limites_a_frecuencia
from reglas.catalogo import REGLAS


def construir(hojas: list[dict] | None = None) -> str:
    hojas = hojas if hojas is not None else leer_libro()
    huella = huellas(COPIA_TRABAJO)["sha256"]
    hoy = date.today().isoformat()
    lineas = [
        "# Ficha Maestra · BES-jun",
        "",
        "Presentación técnica del primer dataset del proyecto HUC. "
        "No declara aprobadas las reglas ni cierra el expediente.",
        "",
        f"**Fecha de esta ficha:** {hoy}. **Estado del expediente:** validación pendiente, en `datasets/en_uso/`.",
        "",
        "## 1. Identificador",
        "",
        "`BES-jun`. No reutilizar este identificador para otro archivo.",
        "",
        "## 2. Archivo analizado",
        "",
        "Se analizó el archivo **Copia de FINAL BES-jun.xlsx**.",
        f"La copia de trabajo es `entrada/BES_jun.xlsx`, SHA-256 `{huella}`, {COPIA_TRABAJO.stat().st_size} bytes.",
        "La coincidencia de huella con el archivo recibido y con `fuentes/originales/` está documentada en el cuaderno `00_inventario_y_fuentes`. "
        "Identidad de bytes no califica las mediciones.",
        "",
        "## 3. Procedencia",
        "",
        "Archivo entregado en la raíz del proyecto, distinto de RB-1521 (D1) y de RB-IA-2191 (D2). "
        "No se mezcló con esos libros. Esos datasets siguen en `en_espera` y no se abrieron en este cierre.",
        "",
        "## 4. Huella",
        "",
        f"`{huella}`",
        "",
        "## 5. Fecha de análisis",
        "",
        f"Ficha regenerada el {hoy}. Las fechas dentro del Excel no son fechas de medición comprobadas: "
        "cuatro hojas tienen `=TODAY()` y QF-549HST tiene una fecha escrita (2017-09-06) sin contraste externo.",
        "",
        "## 6. Estado",
        "",
        "Dataset: `validacion_pendiente`. Reglas: `pendiente_validacion` (RC-BES-04: `no_evaluable`). "
        "No está en `procesadas`. El cierre computacional no sustituye la aprobación operacional.",
        "",
        "## 7. Objetivos",
        "",
        "Transcribir y contrastar la cadena de cálculo de las cinco hojas, dejar explícitas las ambigüedades "
        "y exponer un evaluador determinístico que una aplicación pueda llamar sin un modelo de lenguaje.",
        "",
        "## 8. Dominios",
        "",
        "Hidráulica de una BES (fluido, balance de alturas, intersección con una curva tabulada) y calidad de datos de un libro de cálculo. "
        "Quedan fuera potencia, motor, cable, Método B y cualquier control automático del variador.",
        "",
        "## 9. Alcance",
        "",
        "Cinco puntos de operación, uno por hoja. No hay serie temporal. Las estaciones de survey no son observaciones independientes de la bomba.",
        "",
        "## 10. Hojas",
        "",
        "Cinco hojas visibles. Ninguna oculta.",
        "",
        "## 11. Pozos",
        "",
        "Cinco rótulos de pozo, uno por hoja. La identificación definitiva queda condicionada a resolver si la llave es el nombre de la hoja, el Cluster o el Pozo.",
        "",
        "## 12. Identificadores",
        "",
        "| Hoja | Cluster | Pozo |",
        "|---|---|---|",
    ]
    for h in hojas:
        lineas.append(f"| {h['hoja']} | {h['cluster']} | {h['pozo']} |")
    lineas += [
        "",
        "Pozos encontrados, con la reserva anterior:",
        "",
        "- QF-084 / hoja QF-554H.",
        "- QF-301 / hoja QF-545H.",
        "- QF-147 / hoja QF-500H.",
        "- QF-005 / hoja QF-378HST.",
        "- QF-306 / hoja QF-549HST.",
        "",
        "## 13. Bombas de referencia",
        "",
        "Texto de la hoja, no un modelo de catálogo verificado.",
        "",
        "| Hoja | Referencia escrita | Etapas | Frecuencia Hz |",
        "|---|---|---:|---:|",
    ]
    for h in hojas:
        lineas.append(f"| {h['hoja']} | {h['bomba_referencia']} | {h['etapas']:.0f} | {h['frecuencia_hz']:.0f} |")
    lineas += [
        "",
        "## 14. Datos utilizados",
        "",
        "Los que el lector `ingesta.leer_bes_jun` extrae por rótulo: presiones, caudales, profundidades, fluido, curva de seis puntos y límites escritos. "
        "El catálogo formal está en `integracion/variables.json`.",
        "",
        "## 15. Diccionario",
        "",
        "El diccionario narrativo sigue en `docs/diccionario_datos_BES_jun.md`. "
        "El catálogo que consume el software es `integracion/variables.json`, generado desde `catalogo.variables_bes_jun`. "
        "El rango observado no es un límite de operación.",
        "",
        "## 16. Mediciones registradas",
        "",
        "Por hoja: frecuencia, caudal de operación, presión de sensor y THP. Son un punto, no una historia.",
        "",
        "## 17. Parámetros asumidos por la hoja",
        "",
        "°API, temperatura, BS&W, densidad del agua, presión de yacimiento y presión de burbuja aparecen escritos. "
        "Varios son idénticos en las cinco hojas (CT-10): no se cuentan como cinco mediciones independientes.",
        "",
        "## 18. Ecuaciones",
        "",
        "| ID | Estado | Consulta |",
        "|---|---|---|",
    ]
    for formula in FORMULAS:
        lineas.append(f"| {formula['id']} | {formula['estado']} | {formula['consulta'] or '—'} |")
    lineas += [
        "",
        "Lo «utilizable» significa que el código reproduce la celda. No significa que la física esté aprobada.",
        "",
        "## 19. Modelos",
        "",
        "`M-BES-FLUIDO`, `M-BES-BALANCE` y `M-BES-INTERSECCION`, versión `transcripcion-1`. "
        "Orquestados por `analisis.cadena.calcular_hoja`.",
        "",
        "## 20. Resultados calculados",
        "",
        "| Hoja | Pozo | PIP ft | THD ft | Q medido | Q* | Regla preliminar |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for h in hojas:
        cadena = calcular_hoja(h)
        pip = cadena["ba"].resultados["pip_ft"]["valor"]
        thd = cadena["ba"].resultados["thd_total_ft"]["valor"]
        q = cadena["q"].resultados["caudal_a_producir_bfpd"]["valor"]
        regla = comparar_caudal_con_limites(h)[0]
        lineas.append(
            f"| {h['hoja']} | {h['pozo']} | {pip:.1f} | {thd:.1f} | {h['caudal_operacion_bfpd']:.0f} | {q:.0f} | {regla['id']} |"
        )
    qf = next(h for h in hojas if h["pozo"] == "QF-084")
    lim = limites_a_frecuencia(qf)
    lineas += [
        "",
        f"QF-084 opera a {qf['frecuencia_hz']:.0f} Hz con {qf['caudal_operacion_bfpd']:.0f} BFPD. "
        f"El máximo escrito a 60 Hz es {qf['limite_maximo_bfpd']:.0f} BFPD. "
        f"A la frecuencia de operación el máximo escalado es {lim['maximo_bfpd']:.0f} BFPD. "
        "La clasificación preliminar es RC-BES-03. RC-BES-01 solo aparece si se compara sin escalar, y esa comparación no es la vigente.",
        "",
        "## 21. Análisis exploratorio",
        "",
        "Con un punto por hoja no hay distribución del comportamiento de la bomba. "
        "El survey tiene muchas estaciones de profundidad; sirven para describir la trayectoria escrita, no para estimar una correlación con el caudal.",
        "",
        "## 22. Sensibilidad",
        "",
        "El cuaderno `04_modelo_deterministico` y el informe calculan la elasticidad local de Q*. "
        "La frecuencia pesa más que el resto de las entradas en el entorno del punto. Eso no autoriza a mover la frecuencia.",
        "",
        "## 23. Hallazgos",
        "",
        "El registro narrativo está en el cuaderno `06_hallazgos_y_reglas_candidatas` (H-01 a H-13). "
        "El hallazgo que esta ficha fija para el software es H-01: la alerta de caudal de QF-084 era un efecto de comparar dos frecuencias.",
        "",
        "## 24. Reglas candidatas",
        "",
    ]
    for regla in REGLAS:
        lineas.append(f"- **{regla['id']}** ({regla['estado_validacion']}): {regla['nombre']}.")
    lineas += [
        "",
        "Reglas aprobadas para uso operacional: ninguna.",
        "",
        "## 25. Consultas técnicas",
        "",
        "CT-01 a CT-10, en `docs/consultas_tecnicas_pendientes.md`. P-14 sigue sin respuesta y no se resuelve aquí.",
        "",
        "## 26. Riesgos",
        "",
        "Un número que reproduce la hoja puede leerse como si el pozo estuviera diagnosticado. No lo está. "
        "El signo del PIP (CT-03) y la fricción (CT-05) cambian el sentido físico aunque el residual contra la caché sea nulo.",
        "",
        "## 27. Límite estadístico",
        "",
        "n = 5 puntos heterogéneos. No hay modelo estadístico ni de aprendizaje automático en este expediente, a propósito.",
        "",
        "## 28. Validación",
        "",
        "Validado contra la caché de la propia hoja (reproducción). No hay validación independiente de PIP ni aprobación de reglas.",
        "",
        "## 29. Artefactos",
        "",
        "Doce cuadernos con HTML y PDF en `pdf/notebooks/`. Informe en `reports/` y `pdf/informes/`. "
        "Paquete `integracion/`. Pruebas en `tests/`. Respaldo previo a la auditoría de cuadernos en `logs/respaldo_previo_a_auditoria/`.",
        "",
        "## 30. Integración",
        "",
        "Guía: `integracion/README.md`. Llamada: `evaluacion.motor.evaluar('BES-jun', 'QF-084')`. "
        "El resultado trae `recomendacion_operacional_autorizada: false`.",
        "",
        "Ejemplo de esa llamada para QF-084, resumido:",
        "",
    ]
    resultado = evaluar("BES-jun", "QF-084", hojas=hojas)
    activa = next(r for r in resultado["reglas"] if r.get("activada"))
    lineas += [
        f"- Estado de la evaluación: `{resultado['estado_evaluacion']}`.",
        f"- Regla activada: `{activa['id']}` / `{activa['resultado']}`.",
        f"- Recomendación operacional autorizada: `{resultado['recomendacion_operacional_autorizada']}`.",
        "",
    ]
    return "\n".join(lineas)


def escribir() -> str:
    raiz = raiz_expediente()
    texto = construir()
    destino = raiz / "docs" / "ficha_maestra_BES-jun.md"
    destino.write_text(texto, encoding="utf-8")
    return str(destino)


def _huella_texto(texto: str) -> str:
    return hashlib.sha256(texto.encode()).hexdigest()
