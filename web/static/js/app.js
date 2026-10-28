document.addEventListener("submit", function (evento) {
  var boton = evento.target.querySelector("button[type=submit], button:not([type])");
  if (boton && !boton.dataset.original) {
    boton.dataset.original = boton.textContent;
    boton.textContent = "Procesando…";
  }
});
