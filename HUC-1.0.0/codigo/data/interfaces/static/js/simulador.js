(function () {
  var pozo = document.getElementById("pozo");
  if (!pozo || !window.HucMandos) return;
  var token = (document.querySelector('meta[name="csrf-token"]') || {}).content || "";
  var mandos = document.getElementById("mandos");
  var relojFase = null;
  var ultimaFase = "";

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
        if (cuerpo.tiene_valores_en_uso) {
          nota("Valores en uso activos (sesión de simulación).");
        } else {
          nota("Valores de referencia cargados. Sin publicar.");
        }
        ultimaFase = cuerpo.fase_secuencia || "detenida";
        document.getElementById("fase").textContent = "Fase: " + ultimaFase;
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

  function detenerPollFase() {
    if (relojFase) {
      window.clearInterval(relojFase);
      relojFase = null;
    }
  }

  function vigilarFase() {
    detenerPollFase();
    relojFase = window.setInterval(function () {
      fetch("/api/pozos/" + encodeURIComponent(pozo.value) + "/fase/")
        .then(function (respuesta) { return respuesta.json(); })
        .then(function (dato) {
          var fase = dato.fase || "detenida";
          document.getElementById("fase").textContent = "Fase: " + fase;
          if (ultimaFase === "en_curso" && fase === "detenida") {
            detenerPollFase();
            cargar();
            nota("Secuencia finalizada. Los últimos valores en uso permanecen activos.");
          }
          ultimaFase = fase;
          if (fase === "detenida") detenerPollFase();
        });
    }, 1000);
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
        cargar();
        nota("Publicado. Valores en uso conservados. Esperando acuse.");
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
        detenerPollFase();
        cargar();
        nota("Restauración publicada. Valores de referencia activos.");
        vigilar(cuerpo.evaluacion_id);
      });
  });

  var cerrar = document.getElementById("cerrar-sesion");
  if (cerrar) {
    cerrar.addEventListener("click", function () {
      post("/api/cerrar-sesion/", {}).then(function () {
        detenerPollFase();
        document.getElementById("panel").hidden = true;
        if (acceso) acceso.hidden = false;
        mandos.innerHTML = "";
        nota("Sesión cerrada. La próxima entrada inicia desde los valores de referencia.");
      });
    });
  }

  function automatica(accion) {
    var cuerpo = {accion: accion};
    if (accion === "iniciar") {
      cuerpo.intervalo_s = Number(document.getElementById("intervalo").value);
      cuerpo.duracion_s = Number(document.getElementById("duracion").value);
      cuerpo.semilla = Number(document.getElementById("semilla").value);
    }
    post("/api/pozos/" + encodeURIComponent(pozo.value) + "/automatica/", cuerpo)
      .then(function (dato) {
        if (!dato._ok) {
          document.getElementById("fase").textContent = dato.error || "No se pudo ejecutar.";
          return;
        }
        ultimaFase = dato.fase || accion;
        document.getElementById("fase").textContent = "Fase: " + ultimaFase;
        if (accion === "iniciar" && ultimaFase === "en_curso") {
          vigilarFase();
        }
        if (accion === "detener") {
          detenerPollFase();
          cargar();
          nota("Secuencia detenida. Se conservan los últimos valores en uso.");
        }
      });
  }

  document.getElementById("auto-iniciar").addEventListener("click", function () { automatica("iniciar"); });
  document.getElementById("auto-detener").addEventListener("click", function () { automatica("detener"); });
  pozo.addEventListener("change", function () {
    detenerPollFase();
    cargar();
  });
  if (pozo.value && !document.getElementById("panel").hidden) cargar();
})();
