(function () {
  function formatoVisible(valor) {
    var numero = Number(valor);
    if (!Number.isFinite(numero)) return "No disponible";
    var texto = (Math.round(numero * 100) / 100).toFixed(2);
    return texto.replace(/0+$/, "").replace(/\.$/, "");
  }

  function mandoEditable(control, alCambiar) {
    var articulo = document.createElement("article");
    articulo.className = "tarjeta mando";
    var valor = control.valor_original;
    if (valor === null || valor === undefined) {
      articulo.innerHTML = "<h2></h2><p class='valor-grande'>No disponible</p>";
      articulo.querySelector("h2").textContent = control.nombre;
      return articulo;
    }
    var recorrido = control.recorrido || {};
    articulo.innerHTML =
      "<header><h2></h2><button type='button' class='inicio'>Inicio</button></header>" +
      "<p class='nota'>Original</p><p class='original'></p>" +
      "<p class='valor-grande' data-mando=''></p>" +
      "<input type='range' aria-label=''>" +
      "<div class='extremos'><span></span><span></span></div>" +
      "<label class='exacto'>Exacto <input type='number' step='any' inputmode='decimal'></label>";
    articulo.querySelector("h2").textContent = control.nombre;
    articulo.querySelector(".original").textContent = formatoVisible(valor) + " " + (control.unidad || "");
    var grande = articulo.querySelector(".valor-grande");
    var rango = articulo.querySelector("input[type=range]");
    var numero = articulo.querySelector("input[type=number]");
    grande.dataset.mando = control.id;
    grande.dataset.inicial = String(valor);
    grande.dataset.valor = String(valor);
    rango.min = recorrido.minimo;
    rango.max = recorrido.maximo;
    rango.step = control.paso || "any";
    rango.dataset.dominio = control.id;
    rango.value = valor;
    rango.setAttribute("aria-label", control.nombre);
    articulo.querySelector(".extremos").children[0].textContent = formatoVisible(recorrido.minimo);
    articulo.querySelector(".extremos").children[1].textContent = formatoVisible(recorrido.maximo);
    numero.setAttribute("aria-label", "Valor exacto de " + control.nombre);
    function reflejar(nuevo, avisar) {
      var numeroNuevo = Number(nuevo);
      if (!Number.isFinite(numeroNuevo)) return;
      var topeMin = Number(rango.min);
      var topeMax = Number(rango.max);
      if (numeroNuevo < topeMin || numeroNuevo > topeMax) return;
      grande.dataset.valor = String(numeroNuevo);
      grande.textContent = formatoVisible(numeroNuevo) + " " + control.unidad;
      rango.value = numeroNuevo;
      if (document.activeElement !== numero) numero.value = formatoVisible(numeroNuevo);
      if (avisar && alCambiar) alCambiar();
    }
    reflejar(valor, false);
    rango.addEventListener("input", function () { reflejar(rango.value, true); });
    numero.addEventListener("change", function () { reflejar(numero.value, true); });
    articulo.querySelector(".inicio").addEventListener("click", function () { reflejar(valor, true); });
    return articulo;
  }

  function dibujar(caja, controles, alCambiar) {
    caja.innerHTML = "";
    (controles || []).forEach(function (control) {
      caja.appendChild(mandoEditable(control, alCambiar));
    });
  }

  function valores(caja) {
    var controles = {};
    caja.querySelectorAll("[data-mando]").forEach(function (nodo) {
      if (nodo.dataset.valor === "") return;
      controles[nodo.dataset.mando] = Number(nodo.dataset.valor);
    });
    return controles;
  }

  window.HucMandos = { formatoVisible: formatoVisible, dibujar: dibujar, valores: valores };
})();
