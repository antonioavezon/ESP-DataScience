# ESP-DataScience
## Introducción a la Ciencia de Datos aplicada a bombas electrosumergibles

Laboratorio para aprender a explorar datos experimentales con Python y, al mismo tiempo, dejar registrada la primera lectura de un conjunto real de ensayos de bombas electrosumergibles.

La ciencia de datos, en este laboratorio, consiste en localizar los archivos, entender cómo están organizados, describir lo que contienen y separar una cuenta numérica de una conclusión física. Los cuadernos 00 a 03 no ajustan modelos. La actividad 2.14 estimó la recta, el polinomio de grado 2 con cresta, la recta por condición y un bosque aleatorio de profundidad limitada. En mapping también estimó, solo donde el agua de entrenamiento lo permite, el cociente respecto de la curva de agua.

## Qué es un sistema ESP

ESP significa *electrical submersible pump*: una bomba electrosumergible. Es una bomba que trabaja dentro del pozo y eleva el fluido hacia la superficie. Cuando el líquido llega mezclado con gas, el comportamiento de la bomba cambia. El conjunto de datos de este laboratorio registra ensayos de ese tipo de flujo, llamado flujo con gas.

Este repositorio no diseña la bomba ni sustituye una aplicación de simulación. Sirve para estudiar las tablas experimentales publicadas por otros investigadores.

## Objetivos

Objetivos de aprendizaje:

- Abrir libros de Excel que no vienen como una tabla plana.
- Usar `pathlib` para encontrar los archivos desde la raíz del proyecto, sin escribir la carpeta personal de un computador.
- Contar observaciones completas y distinguirlas de un resultado físico ya validado.
- Dejar el trabajo en Git para continuarlo desde otro equipo Fedora.

El laboratorio empezó por la hoja `50psig` de mapping y por el diccionario. La actividad 2.11 está cerrada, la 2.12 también, y la 2.13 quedó cerrada como selección, sin entrenamiento. La fase A de la 2.14 está congelada. La fase B está cerrada. La fase C estimó M3, M4 y la referencia parcial M5. La fase D los comparó sin nombrar un ganador. La actividad 2.14 no está cerrada. La línea más amplia sigue siendo el modelado híbrido de ESP, que aquí todavía no se implementa.

## Tecnologías

| Herramienta | Para qué se usa aquí |
|---|---|
| Fedora | Sistema operativo de los dos computadores |
| Python | Lenguaje del análisis |
| Cursor | Editor en el que se abren los cuadernos |
| Jupyter | Formato de los cuadernos y su kernel de ejecución |
| pandas | Lectura de Excel y tablas |
| NumPy | Arreglos numéricos |
| Matplotlib | Gráficos |
| SciPy | Biblioteca científica disponible en el entorno |
| scikit-learn | Recta, polinomio con cresta, recta por condición y bosque aleatorio de la actividad 2.14. Los cuadernos 00 a 03 no ajustan modelos |
| openpyxl | Motor con el que pandas lee los archivos `.xlsx` |
| Git y GitHub | Historial y copia compartida entre equipos |

El kernel es el proceso de Python que ejecuta las celdas del cuaderno. Cada computador crea el suyo dentro de su propia carpeta `.venv`. Esa carpeta no se copia por Git.

## Estructura de directorios

```text
ESP-DataScience/
- archive/                  el ZIP original se guarda aquí solo en cada equipo
- data/raw/                 Excel de trabajo
- data/processed/           tablas largas de la actividad 2.12
- docs/                     bitácora, diccionario, normalización, estudio de modelos y guía de sincronización
- notebooks/00_validacion_entorno.ipynb
- notebooks/01_exploracion_inicial.ipynb
- notebooks/02_normalizacion.ipynb
- notebooks/03_seleccion_modelos.ipynb
- notebooks/04_entrenamiento_evaluacion_modelos.ipynb
- src/esp_datascience/      funciones de normalización, particiones y entrenamiento de M1 y M2
- tests/                    pruebas de esa copia, con unittest
- results/figures/          reservado
- results/models/           reservado; Git ignora los modelos generados
- requirements-direct.txt   paquetes que el laboratorio pide instalar
- requirements.txt          versiones completas usadas en el equipo de trabajo
- .venv/                    entorno local; no está en Git
```

Los cuadernos conservan el código, las explicaciones y los resultados. `src/esp_datascience/` repite las funciones de lectura, normalización, validación, particiones y el entrenamiento de M1 y M2. No sustituye al cuaderno.

| Módulo | Funciones |
|---|---|
| `rutas.py` | `encontrar_raiz_laboratorio`, `huella_sha256` |
| `lectura.py` | `es_numero`, `filas_de_franja_mapping`, `psep_de_hoja` |
| `normalizacion.py` | `velocidad_segun_diseno`, `columnas_separadoras_vacias`, `normalizar_mapping`, `filas_de_franja_surging`, `normalizar_surging` |
| `validacion.py` | `pares_por_hoja`, `comprobar_conteos_publicados` |

Desde la raíz del laboratorio, con el entorno ya creado:

```bash
.venv/bin/python -m unittest tests.test_normalizacion -v
```

`unittest` pertenece a la biblioteca estándar de Python. No hace falta instalar otro paquete.

## Instalación en Fedora

Sirve para Fedora del trabajo (Python 3.14.7) y para Fedora de casa (Python 3.14.8). No hace falta cambiar el Python del sistema. Las dos versiones usan el mismo identificador de ruedas, `cp314`, así que los paquetes fijados en este repositorio se instalan en ambas.

En una terminal, dentro de la carpeta del repositorio:

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-direct.txt
```

`requirements-direct.txt` instala JupyterLab, ipykernel, NumPy, pandas, Matplotlib, openpyxl, SciPy y scikit-learn en las versiones ya probadas.

`requirements.txt` es el registro completo, incluidas las dependencias que esos paquetes arrastran. Se generó con `pip freeze` en Python 3.14.7. No sustituye al archivo directo para una instalación normal.

Comprobación:

```bash
python -m pip check
```

## Kernel de Jupyter en Cursor

1. Abra la carpeta `ESP-DataScience`.
2. Seleccione el intérprete `.venv/bin/python`. La configuración de `.vscode/settings.json` usa `${workspaceFolder}`, una ruta relativa al proyecto, no una carpeta fija de un computador.
3. Abra el cuaderno y elija el kernel de ese entorno.

El nombre visible puede ser `.venv` o Python 3. Lo importante es que el ejecutable quede dentro de `.venv` de esta copia del proyecto.

## Cómo ejecutar los cuadernos

Orden recomendado:

1. `notebooks/00_validacion_entorno.ipynb`
2. `notebooks/01_exploracion_inicial.ipynb`
3. `notebooks/02_normalizacion.ipynb`
4. `notebooks/03_seleccion_modelos.ipynb`
5. `notebooks/04_entrenamiento_evaluacion_modelos.ipynb`

Cada cuaderno nuevo se agrega al final de esta lista, con el número siguiente. Ejecute las celdas de arriba hacia abajo. Los cuadernos `01` y `02` buscan `data/raw/mapping.xlsx` y `data/raw/surging.xlsx` subiendo desde el directorio de trabajo hasta la raíz del laboratorio.

El primer cuaderno dibuja un gráfico de práctica. Esos puntos son ficticios y lo dicen el título y los ejes.

## Procedencia de los datos experimentales

Los archivos de mapping y de surging no fueron medidos por el autor de este laboratorio. Pertenecen al conjunto publicado por Jianjun Zhu:

- Título: *Data for: Modeling Flow Pattern Transitions in Electrical Submersible Pump under Gassy Flow Conditions*
- Repositorio: Mendeley Data, versión 1, 4 de junio de 2019
- DOI: [10.17632/fk2b4r69bs.1](https://doi.org/10.17632/fk2b4r69bs.1)
- Licencia de los datos: [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)

CC BY 4.0 permite copiar y compartir el conjunto si se da crédito, se enlaza la licencia y se indica si hubo cambios. En este laboratorio los archivos se renombraron y no se editó su contenido:

| Nombre en Mendeley Data | Nombre en el laboratorio | SHA-256 |
|---|---|---|
| `Mapping Test Data_zero IPA.xlsx` | `data/raw/mapping.xlsx` | `3b933ca84911484f5d912a44b025f5589abaf5ebc2b0426bf80c083869762bda` |
| `Surging Test Data_zero IPA.xlsx` | `data/raw/surging.xlsx` | `acdcc6c5fc3d8969280c8712c45657fbb863f163a60829584fece5abf75f28cd` |

Esos dos SHA-256 coinciden con los publicados por Mendeley Data. SHA-256 es una huella digital del archivo: si un solo byte cambia, la huella cambia.

El artículo asociado es *Modeling flow pattern transitions in electrical submersible pump under gassy flow conditions*, Journal of Petroleum Science and Engineering, volumen 180 (2019), páginas 471-484, DOI [10.1016/j.petrol.2019.05.059](https://doi.org/10.1016/j.petrol.2019.05.059). El PDF es material de Elsevier. No está en este repositorio. Cada persona lo consulta con el acceso de su institución, o lo guarda solo en su equipo, en `docs/esp_gassy_flow_paper.pdf`. Git ignora ese PDF y también `archive/dataset_original.zip`.

## Actividades realizadas

| Cuaderno | Contenido |
|---|---|
| `00_validacion_entorno.ipynb` | Intérprete, versiones y un gráfico con datos ficticios |
| `01_exploracion_inicial.ipynb` | Actividades 2.1 a 2.11 |
| `02_normalizacion.ipynb` | Actividad 2.12, dos tablas largas |
| `03_seleccion_modelos.ipynb` | Actividad 2.13, exploración y selección de modelos, sin entrenamiento |
| `04_entrenamiento_evaluacion_modelos.ipynb` | Actividad 2.14: fases A a D, sin ganador y sin fase E |

Las actividades 2.3 a 2.10 usan solo `mapping.xlsx`, hoja `50psig`. La actividad 2.12 lee las seis hojas y deja el resultado en `data/processed/`.

Resultados verificados en esa hoja:

| Indicador | Resultado |
|---|---:|
| Dimensiones originales | 50 filas, 18 columnas |
| Velocidades registradas | 1800 y 3500 |
| Condiciones experimentales | 10 |
| Pares numéricos completos | 186 |
| Pares a velocidad 1800 | 62 |
| Pares a velocidad 3500 | 124 |
| Columnas completamente vacías | 3, 6, 9, 12, 15 |

Un par numérico completo es una fila en la que el caudal y `DP2-3` se leen como números a la vez. No equivale, por sí solo, a una medición físicamente validada ni a un experimento independiente. El diccionario de la actividad 2.11 está en `docs/diccionario_variables.md`: caudal en bpd, `DP2-3` en psi y `GVF0` en porcentaje, con la certeza que cada entrada declara.

El detalle está en `docs/progreso_investigacion.md`.

## Plan de investigación

La actividad 2.11 está cerrada. El diccionario está en `docs/diccionario_variables.md`. Qmax de la TE-2700 a 3500 rpm es 4900 bpd. `Flow rate` se lee en bpd, `DP2-3` en psi y `GVF0` en porcentaje.

La actividad 2.12 también está cerrada. Las tablas son `data/processed/mapping_long.csv` y `data/processed/surging_long.csv`. El procedimiento está en `docs/normalizacion_datos.md`.

La actividad 2.13 también está cerrada, y solo como selección metodológica. La síntesis es `docs/estudio_modelos_2_13.md`. La exploración reproducible es `notebooks/03_seleccion_modelos.ipynb`. No se entrenó ningún modelo, no hay un candidato principal único y no hay un modelo ganador.

La actividad 2.14 está autorizada y no está cerrada. La fase A está congelada en `2.14-A`. La fase B está cerrada: 26 pruebas automatizadas terminaron correctamente y el cuaderno se ejecutó con nbconvert. La fase C estimó la recta por condición, el bosque de profundidad limitada y, en mapping, el cociente respecto del agua donde esa referencia no usa una curva de prueba. La fase D comparó esos modelos con intervalos por curva y no nombró un ganador. El informe es `docs/resultados_modelos_2_14.md`. La fase E no está iniciada.

**2.14 — Desarrollo y evaluación experimental de los modelos ya elegidos.**

El plan está en `docs/plan_implementacion.md`. No se guarda un archivo de modelo ajustado: las predicciones externas quedan en el cuaderno 04.

Para pasar el trabajo de un Fedora al otro, siga `docs/sincronizacion_fedora.md`. GitHub no copia los archivos solo por tener el repositorio abierto: hace falta `git push` al terminar y `git pull` al empezar.

## Limitaciones

- Las actividades 2.3 a 2.10 no se generalizan a `100psig`, `150psig` ni al libro de surging.
- Surging, hoja `50psig`, tiene 9 columnas, no 18.
- La tesis fija las unidades de trabajo en bpd y psi. Los rótulos `DP2-3` y `GVF0` no aparecen en esa tesis; su enlace está declarado como interpretación.
- El gráfico del primer cuaderno es didáctico.
- Los entornos `.venv` de cada computador son independientes.
- Este repositorio no incluye una licencia de software. La licencia CC BY 4.0 se aplica a los datos experimentales citados arriba, no al código ni a los cuadernos.

## Créditos

Laboratorio y cuadernos de exploración: antonioavezon (`antonio.avezon@gmail.com`).

Datos experimentales: Jianjun Zhu, Mendeley Data, DOI 10.17632/fk2b4r69bs.1, licencia CC BY 4.0. El autor de este laboratorio no es el autor de esas mediciones.

Artículo de referencia, no redistribuido aquí: DOI 10.1016/j.petrol.2019.05.059.
