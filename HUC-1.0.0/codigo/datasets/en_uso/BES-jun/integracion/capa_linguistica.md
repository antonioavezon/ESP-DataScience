# Capa de lenguaje futura · BES-jun

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
