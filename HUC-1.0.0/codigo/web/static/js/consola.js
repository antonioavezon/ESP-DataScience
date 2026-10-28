(function () {
  var pozo = document.getElementById("pozo");
  if (!pozo) return;
  var seq = 0;
  var controlador = null;
  var visto = "";
  var ultimaMarca = "";
  var previo = null;

  function $(id) { return document.getElementById(id); }

  function formatoVisible(valor, decimales) {
    var numero = Number(valor);
    if (!Number.isFinite(numero)) return "No disponible";
    var cifras = decimales == null ? 2 : decimales;
    var factor = Math.pow(10, cifras);
    var texto = (Math.round(numero * factor) / factor).toFixed(cifras);
    return texto.replace(/0+$/, "").replace(/\.$/, "");
  }

  function distinto(a, b) {
    var na = Number(a);
    var nb = Number(b);
    if (!Number.isFinite(na) || !Number.isFinite(nb)) return String(a) !== String(b);
    return Math.abs(na - nb) > 1e-6;
  }

  function linea(texto, cambio) {
    var p = document.createElement("p");
    if (cambio) p.className = "cambio";
    p.textContent = texto;
    return p;
  }

  function pintarVariables(cuerpo) {
    var caja = $("variables");
    caja.replaceChildren();
    var referencia = cuerpo.referencia || {};
    var entradas = cuerpo.entradas || {};
    Object.keys(referencia).forEach(function (id) {
      var base = referencia[id] || {};
      var tieneEntrada = Object.prototype.hasOwnProperty.call(entradas, id);
      var actual = tieneEntrada ? entradas[id] : base.valor;
      var cambio = cuerpo.modo === "simulacion" && tieneEntrada && distinto(actual, base.valor);
      var texto = (base.nombre || id) + " " + formatoVisible(actual, base.decimales) + (base.unidad ? " " + base.unidad : "");
      if (cambio) texto += " · antes " + formatoVisible(base.valor, base.decimales);
      caja.appendChild(linea(texto, cambio));
    });
  }

  function pintarResultados(cuerpo) {
    var caja = $("resultados");
    caja.replaceChildren();
    var resultados = cuerpo.resultados || {};
    var anterior = (previo && previo.resultados) || {};
    var preferidas = ["pip_ft", "thd_total_ft", "caudal_a_producir_bfpd", "gradiente_psi_ft"];
    var nombres = {pip_ft: "PIP", thd_total_ft: "THD", caudal_a_producir_bfpd: "Caudal calculado", gradiente_psi_ft: "Gradiente"};
    var claves = preferidas.filter(function (clave) { return resultados[clave]; }).concat(Object.keys(resultados).filter(function (clave) {
      return preferidas.indexOf(clave) < 0;
    }));
    claves.forEach(function (clave) {
      var item = resultados[clave] || {};
      if (item.valor === null || item.valor === undefined || item.valor === "") return;
      var antes = anterior[clave] || {};
      var cambio = previo && previo.evaluacion_id !== cuerpo.evaluacion_id && distinto(item.valor, antes.valor);
      var texto = (item.nombre || nombres[clave] || clave) + " " + (item.valor_visible || formatoVisible(item.valor)) + (item.unidad ? " " + item.unidad : "");
      if (cambio && antes.valor !== undefined) texto += " · antes " + (antes.valor_visible || formatoVisible(antes.valor));
      caja.appendChild(linea(texto, cambio));
    });
  }

  function pintar(cuerpo, conservarMensaje) {
    if (!cuerpo) return;
    var marca = String(cuerpo.emitido_en || "");
    if (cuerpo.disponible && marca && ultimaMarca && marca < ultimaMarca) return;
    if (marca) ultimaMarca = marca;
    var pantalla = $("pantalla");
    var estado = cuerpo.estado || {};
    var tono = estado.clasificacion_valida ? estado.tono : "sin-clasificacion";
    var comunicacion = cuerpo.proceso_disponible === false ? " comunicacion-perdida" : "";
    pantalla.className = "tarjeta pantalla tono-" + (tono || "sin-clasificacion") + comunicacion;
    $("rotulo").textContent = estado.rotulo || "SIN RESULTADO";
    $("lampara").className = "lampara" + (cuerpo.disponible ? " viva" : "");
    $("comunicacion").textContent = cuerpo.proceso_disponible === false ? "Sin comunicación con el proceso" : "Proceso en comunicación";
    $("identidad-dataset").textContent = "Dataset " + (cuerpo.dataset_id || "—");
    $("identidad-escenario").textContent = "Escenario " + (cuerpo.escenario_id || "—") + " · " + (cuerpo.origen_valores || "sin resultado");
    $("identidad-momento").textContent = "Actualización " + (cuerpo.emitido_en || "—");
    if (!conservarMensaje) $("mensaje").textContent = (cuerpo.texto && cuerpo.texto.mensaje) || "";
    pintarVariables(cuerpo);
    pintarResultados(cuerpo);
    previo = cuerpo;
    try {
      var mapa = JSON.parse(sessionStorage.getItem("huc.escenarios") || "{}");
      var ficha = {pozo_id: cuerpo.pozo_id || pozo.value, rotulo: estado.rotulo || "SIN RESULTADO", tono: tono, clasificacion_valida: estado.clasificacion_valida === true, origen_valores: cuerpo.origen_valores || ""};
      if (cuerpo.origen_valores === "simulado") mapa[ficha.pozo_id] = ficha;
      else delete mapa[ficha.pozo_id];
      sessionStorage.setItem("huc.escenarios", JSON.stringify(mapa));
    } catch (error) { /* la luz sigue el evento */ }
    document.dispatchEvent(new CustomEvent("huc-estado", {detail: {
      pozo_id: cuerpo.pozo_id || pozo.value,
      codigo: estado.codigo || "",
      rotulo: estado.rotulo || "SIN RESULTADO",
      tono: tono,
      clasificacion_valida: estado.clasificacion_valida === true,
      origen_valores: cuerpo.origen_valores || ""
    }}));
  }

  function pedirExplicacion(identificador) {
    fetch("/api/consola/pozos/" + encodeURIComponent(pozo.value) + "/explicacion/")
      .then(function (respuesta) { return respuesta.json(); })
      .then(function (cuerpo) {
        if (identificador && cuerpo.evaluacion_id && String(cuerpo.evaluacion_id) !== String(identificador)) return;
        if (cuerpo.explicacion) $("mensaje").textContent = cuerpo.explicacion;
      })
      .catch(function () { /* el texto del proceso permanece */ });
  }

  function cargar() {
    if (!pozo.value) return;
    if (controlador) controlador.abort();
    controlador = new AbortController();
    var id = String(++seq);
    fetch("/api/consola/pozos/" + encodeURIComponent(pozo.value) + "/resultado/", {signal: controlador.signal})
      .then(function (respuesta) { return respuesta.json(); })
      .then(function (cuerpo) {
        if (String(seq) !== id) return;
        var evaluacion = cuerpo.evaluacion_id || "";
        pintar(cuerpo, Boolean(evaluacion) && evaluacion === visto);
        if (cuerpo.disponible && evaluacion && evaluacion !== visto) {
          visto = evaluacion;
          pedirExplicacion(evaluacion);
        }
      })
      .catch(function (error) {
        if (error.name === "AbortError") return;
        pintar({
          evaluacion_id: id,
          proceso_disponible: false,
          disponible: false,
          estado: {rotulo: "SIN COMUNICACIÓN", clasificacion_valida: false, tono: "sin-clasificacion"},
          texto: {mensaje: "No se pudo consultar el último resultado."},
          resultados: {}
        });
      });
  }

  pozo.addEventListener("change", function () {
    window.history.replaceState(null, "", "/?pozo=" + encodeURIComponent(pozo.value));
    visto = "";
    ultimaMarca = "";
    previo = null;
    cargar();
  });
  var pedido = new URLSearchParams(window.location.search).get("pozo");
  if (pedido) {
    Array.prototype.forEach.call(pozo.options, function (opcion) {
      if (opcion.value === pedido) pozo.value = pedido;
    });
  }
  if (pozo.value) cargar();
  window.setInterval(cargar, 1000);
})();
