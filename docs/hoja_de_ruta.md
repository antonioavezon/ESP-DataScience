# Hoja de ruta

Secuencia prevista después de esta pasada. No es una autorización para saltar un paso.

1. **Cierre de BES-jun.** El cierre computacional de esta pasada está hecho. Falta la revisión humana del informe, de la ficha y de los cuadernos.
2. **Aprobación de reglas.** Un responsable acepta, rechaza o suspende RC-BES-01, 02 y 03, y responde CT-08 antes de tratar el escalamiento como válido. RC-BES-04 sigue no evaluable hasta haber curva de fabricante.
3. **Siguiente dataset.** Cuando se pida, se aplica `docs/guia_procesamiento_datasets.md` a RB-1521 o a RB-IA-2191. No antes, y sin copiar las ecuaciones de BES-jun si ese archivo no las trae.
4. **Consolidación de reglas.** Solo entran a un catálogo común las que tengan estado y ámbito explícitos. Una regla de un libro no se vuelve general por compartir el identificador.
5. **Catálogo central de pozos.** Hace falta la regla de identidad (qué código es el pozo) para no duplicar un pozo que aparezca en dos archivos.
6. **Aplicación.** Conectar `asesor-esp` al manifiesto y a `evaluar`, sin reescribir las ecuaciones en la interfaz.
7. **Modelo de lenguaje.** Implementar la capa descrita en `integracion/capa_linguistica.md`. Hasta entonces la aplicación usa los mensajes del JSON.
8. **Validación integral.** Comparar, con datos que no sean la caché del mismo libro, lo que el motor dice y lo que se mide. Eso no existe todavía para BES-jun.
