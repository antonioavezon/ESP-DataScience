(function () {
  var pozo = document.getElementById("pozo");
  if (!pozo || !window.HucMandos) return;
  var token = (document.querySelector('meta[name="csrf-token"]') || {}).content || "";
  var mandos = document.getElementById("mandos");

  function nota(texto) {
    document.getElementById("publicacion").textContent = texto;
  }

  function cargar() {
    if (!pozo.value) return;
    fetch("/api/pozos/" + encodeURIComponent(pozo.value) + "/base/")
      .then(function (respuesta) { return respuesta.json(); })
      .then(function (cuerpo) {
        if (!cuerpo.evaluable) {
          mandos.innerHTML = "";
          nota("Este pozo no está disponible para cálculo.");
          return;
        }
        HucMandos.dibujar(mandos, cuerpo.controles);
        nota("Valores originales cargados. Sin publicar.");
      });
  }

  function vigilar(identificador) {
    var intentos = 0;
    var reloj = window.setInterval(function () {
      intentos += 1;
      fetch("/api/pozos/" + encodeURIComponent(pozo.value) + "/acuse/" + encodeURIComponent(identificador) + "/")
        .then(function (respuesta) { return respuesta.json(); })
        .then(function (cuerpo) {
          if (!cuerpo.recibido) return;
          window.clearInterval(reloj);
          nota(cuerpo.estado_publicacion === "calculo_exitoso" ? "Escenario aceptado." : "Escenario rechazado: " + (cuerpo.estado_publicacion || "error"));
        });
      if (intentos > 20) {
        window.clearInterval(reloj);
        nota("Publicado. Sin acuse del proceso.");
      }
    }, 500);
  }

  function post(url, cuerpo) {
    return fetch(url, {
      method: "POST",
      headers: {"Content-Type": "application/json", "X-CSRFToken": token},
      body: JSON.stringify(cuerpo || {})
    }).then(function (respuesta) {
      return respuesta.json().then(function (dato) {
        dato._ok = respuesta.ok;
        return dato;
      });
    });
  }

  var acceso = document.getElementById("acceso");
  if (acceso) {
    acceso.addEventListener("submit", function (evento) {
      evento.preventDefault();
      post("/api/acceder/", {
        usuario: document.getElementById("usuario").value,
        clave: document.getElementById("clave").value
      }).then(function (dato) {
        if (!dato._ok) {
          document.getElementById("acceso-estado").textContent = dato.error || "No se pudo entrar.";
          return;
        }
        acceso.hidden = true;
        document.getElementById("panel").hidden = false;
        cargar();
      });
    });
  }

  document.getElementById("aplicar").addEventListener("click", function () {
    post("/api/pozos/" + encodeURIComponent(pozo.value) + "/aplicar/", {valores: HucMandos.valores(mandos)})
      .then(function (cuerpo) {
        if (!cuerpo._ok) {
          nota(cuerpo.error || "No se publicó.");
          return;
        }
        nota("Publicado. Esperando acuse.");
        vigilar(cuerpo.evaluacion_id);
      });
  });

  document.getElementById("restaurar-todo").addEventListener("click", function () {
    post("/api/pozos/" + encodeURIComponent(pozo.value) + "/restaurar/", {})
      .then(function (cuerpo) {
        if (!cuerpo._ok) {
          nota(cuerpo.error || "No se restauró.");
          return;
        }
        cargar();
        nota("Restauración publicada.");
        vigilar(cuerpo.evaluacion_id);
      });
  });

  function automatica(accion) {
    var cuerpo = {accion: accion};
    if (accion === "iniciar") {
      cuerpo.intervalo_s = Number(document.getElementById("intervalo").value);
      cuerpo.duracion_s = Number(document.getElementById("duracion").value);
      cuerpo.semilla = Number(document.getElementById("semilla").value);
    }
    post("/api/pozos/" + encodeURIComponent(pozo.value) + "/automatica/", cuerpo)
      .then(function (dato) {
        document.getElementById("fase").textContent = dato.error || ("Fase: " + (dato.fase || accion));
      });
  }

  document.getElementById("auto-iniciar").addEventListener("click", function () { automatica("iniciar"); });
  document.getElementById("auto-pausar").addEventListener("click", function () { automatica("pausar"); });
  document.getElementById("auto-reanudar").addEventListener("click", function () { automatica("reanudar"); });
  document.getElementById("auto-detener").addEventListener("click", function () { automatica("detener"); });
  pozo.addEventListener("change", cargar);
  if (pozo.value) cargar();
})();
