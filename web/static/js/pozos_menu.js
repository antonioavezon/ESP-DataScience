(function () {
  var lista = document.getElementById("lista-pozos");
  if (!lista) return;
  var CLAVE = "huc.escenarios";
  var iniciales = [];

  function leer() {
    try {
      var mapa = JSON.parse(sessionStorage.getItem(CLAVE) || "{}");
      return mapa && typeof mapa === "object" ? mapa : {};
    } catch (error) {
      return {};
    }
  }

  function tonoDe(fila) {
    if (!fila || fila.clasificacion_valida !== true) return "sin-clasificacion";
    if (fila.tono === "normal" || fila.tono === "incipiente" || fila.tono === "critico") return fila.tono;
    return "sin-clasificacion";
  }

  function filaDom(fila) {
    var item = document.createElement("li");
    var boton = document.createElement("button");
    boton.type = "button";
    boton.className = "fila-estado";
    boton.dataset.pozo = fila.pozo_id;
    var luz = document.createElement("span");
    luz.className = "luz luz-" + tonoDe(fila);
    luz.setAttribute("aria-hidden", "true");
    var nombre = document.createElement("span");
    nombre.textContent = fila.pozo_id;
    boton.appendChild(luz);
    boton.appendChild(nombre);
    boton.title = fila.rotulo || "SIN RESULTADO";
    boton.setAttribute("aria-label", fila.pozo_id + ". " + (fila.rotulo || "SIN RESULTADO"));
    item.appendChild(boton);
    return item;
  }

  function pozoVisible() {
    var selector = document.getElementById("pozo");
    if (selector && selector.value) return selector.value;
    return new URLSearchParams(window.location.search).get("pozo") || "";
  }

  function marcar() {
    var activo = pozoVisible();
    document.querySelectorAll(".fila-estado").forEach(function (boton) {
      boton.classList.toggle("activo", boton.dataset.pozo === activo);
    });
  }

  function pintar(filas) {
    var simulados = leer();
    lista.textContent = "";
    filas.forEach(function (fila) {
      var vigente = simulados[fila.pozo_id] || fila;
      if (vigente.clasificacion_valida !== true) vigente = Object.assign({}, vigente, {tono: "sin-clasificacion", clasificacion_valida: false});
      lista.appendChild(filaDom(vigente));
    });
    marcar();
  }

  function aplicarUno(fila) {
    if (!fila || !fila.pozo_id) return;
    var boton = lista.querySelector('.fila-estado[data-pozo="' + fila.pozo_id + '"]');
    if (!boton) return;
    var luz = boton.querySelector(".luz");
    if (luz) luz.className = "luz luz-" + tonoDe(fila);
    boton.title = fila.rotulo || "SIN RESULTADO";
    boton.setAttribute("aria-label", fila.pozo_id + ". " + (fila.rotulo || "SIN RESULTADO"));
    marcar();
  }

  lista.addEventListener("click", function (evento) {
    var boton = evento.target.closest(".fila-estado");
    if (!boton) return;
    var selector = document.getElementById("pozo");
    if (selector) {
      selector.value = boton.dataset.pozo;
      selector.dispatchEvent(new Event("change"));
      return;
    }
    window.location.href = "/?pozo=" + encodeURIComponent(boton.dataset.pozo);
  });

  document.addEventListener("huc-estado", function (evento) {
    aplicarUno(evento.detail || {});
  });

  var selector = document.getElementById("pozo");
  if (selector) selector.addEventListener("change", marcar);

  fetch("/api/consola/estados/")
    .then(function (respuesta) { return respuesta.json(); })
    .then(function (cuerpo) {
      iniciales = cuerpo.pozos || [];
      var nota = document.getElementById("fuente-pozos");
      if (nota && cuerpo.nota) nota.textContent = cuerpo.nota;
      pintar(iniciales);
    })
    .catch(function () {
      lista.textContent = "";
      var aviso = document.createElement("li");
      aviso.className = "fuente-pozos";
      aviso.textContent = "No fue posible consultar los estados. Eso no clasifica las bombas.";
      lista.appendChild(aviso);
    });
})();
