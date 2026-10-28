# Reglas candidatas de BES-jun

Versión del catálogo: `1.1.0`. Fuente: `src/reglas/catalogo.py`.
La comparación numérica la hace `reglas.candidatas_bes_jun.comparar_caudal_con_limites` (una sola implementación).

Ninguna regla está aprobada para uso operacional. El resultado es una evaluación preliminar de coherencia
respecto de los números escritos en la hoja, en la misma base de frecuencia.
No autoriza cambiar la frecuencia ni ninguna otra consigna.

La primera versión comparaba el caudal de operación (a la frecuencia de la hoja) con el límite escrito a 60 Hz.
En QF-084 eso enfrentaba 10 301 BFPD a 63 Hz con 10 000 BFPD a 60 Hz y activaba RC-BES-01.
Con el escalamiento de la propia hoja, Qmax(63 Hz) = 10 000 × 63 / 60 = 10 500 BFPD, y el caudal queda dentro.
Esa corrección aritmética no valida el límite del fabricante ni las leyes de afinidad (CT-08).
`escalar=False` se conserva solo para reproducir el artefacto.

## RC-BES-01

- **Nombre:** Caudal por encima del máximo escrito, en la misma frecuencia
- **Versión:** 1.1.0
- **Estado de validación:** `pendiente_validacion`
- **Aprobada para uso operacional:** no
- **Confianza:** bajo
- **Descripción:** Compara el caudal de operación con el límite máximo de la misma hoja, llevado a la frecuencia de operación con Q(f) = Q(60) · f / f_base.
- **Condición:** `{'operador': 'mayor_que', 'izquierda': 'caudal_operacion_bfpd', 'derecha': 'limite_maximo_a_frecuencia_bfpd'}`
- **Umbral y procedencia:** celda «Limite maximo», escalada por f/f_base (texto de la misma hoja; no es un límite de fabricante confirmado)
- **Mensaje:** El caudal registrado queda por encima del máximo escrito, llevado a la misma frecuencia. Es una observación preliminar: el límite no está aprobado como límite de seguridad.
- **Limitaciones:** no autoriza cambiar la frecuencia; el escalamiento no está validado para esta bomba (CT-08)
- **Consultas:** CT-06, CT-08
- **Responsable y fecha de aprobación:** no hay.

## RC-BES-02

- **Nombre:** Caudal por debajo del mínimo escrito, en la misma frecuencia
- **Versión:** 1.1.0
- **Estado de validación:** `pendiente_validacion`
- **Aprobada para uso operacional:** no
- **Confianza:** bajo
- **Descripción:** Compara el caudal de operación con el límite mínimo escalado a la frecuencia de operación.
- **Condición:** `{'operador': 'menor_que', 'izquierda': 'caudal_operacion_bfpd', 'derecha': 'limite_minimo_a_frecuencia_bfpd'}`
- **Umbral y procedencia:** celda «Limite minimo», escalada por f/f_base (texto de la misma hoja)
- **Mensaje:** El caudal registrado queda por debajo del mínimo escrito, llevado a la misma frecuencia. Es una observación preliminar.
- **Limitaciones:** no autoriza cambiar la frecuencia; en las cinco hojas de BES-jun esta condición no se activa
- **Consultas:** CT-06, CT-08
- **Responsable y fecha de aprobación:** no hay.

## RC-BES-03

- **Nombre:** Caudal dentro de los límites escritos, en la misma frecuencia
- **Versión:** 1.1.0
- **Estado de validación:** `pendiente_validacion`
- **Aprobada para uso operacional:** no
- **Confianza:** bajo
- **Descripción:** El caudal de operación está entre el mínimo y el máximo escritos, ambos llevados a la frecuencia de operación. Los extremos inclusive (solo se sale con > máximo o < mínimo).
- **Condición:** `{'operador': 'entre_inclusive', 'valor': 'caudal_operacion_bfpd', 'minimo': 'limite_minimo_a_frecuencia_bfpd', 'maximo': 'limite_maximo_a_frecuencia_bfpd'}`
- **Umbral y procedencia:** celdas «Limite minimo» y «Limite maximo», escaladas (texto de la misma hoja)
- **Mensaje:** El caudal registrado queda entre el mínimo y el máximo escritos, en la misma frecuencia. No autoriza operar el pozo.
- **Limitaciones:** estar entre dos números de la hoja no es un dictamen de seguridad; CT-08 sigue abierta
- **Consultas:** CT-06, CT-08
- **Responsable y fecha de aprobación:** no hay.

## RC-BES-04

- **Nombre:** Cercanía al punto de máxima eficiencia
- **Versión:** 1.1.0
- **Estado de validación:** `no_evaluable`
- **Aprobada para uso operacional:** no
- **Confianza:** ninguno
- **Descripción:** La celda «Cono de eficiencia» coincide con el caudal de mayor EFF de la tabla de seis puntos. No se convirtió en regla de proximidad al BEP.
- **Condición:** no evaluable; no hay operador.
- **Umbral y procedencia:** None (celda «Cono de eficiencia»; no reconciliada con un BEP)
- **Mensaje:** No evaluable: falta la curva de fabricante y la reconciliación de la columna EFF.
- **Limitaciones:** no produce verdadero ni falso
- **Consultas:** CT-06
- **Responsable y fecha de aprobación:** no hay.

## Lo que no se propone

No se propone subir ni bajar hertz, ni un umbral de sumergencia, ni una comparación con cifras de otros documentos.
