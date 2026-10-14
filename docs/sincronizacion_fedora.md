# Sincronización entre los dos equipos Fedora

Git guarda el historial. GitHub guarda una copia de ese historial en internet. Ninguno de los dos actualiza el otro computador por sí solo. Para traer cambios se usa `git pull`. Para enviarlos se usa `git push`.

Hay dos copias de trabajo previstas:

| Equipo | Carpeta |
|---|---|
| Fedora del trabajo | `/home/antonio/Documentos/FISICA/ESP-Investigación UAndes/software/ESP-DataScience` |
| Fedora de casa | `/home/antoniofedora/Documentos/ESP-DataScience` |

El repositorio remoto es privado: `https://github.com/antonioavezon/ESP-DataScience`. La rama de trabajo se llama `main`.

Cada equipo tiene su propio entorno `.venv` y su propio Python del sistema. Esas carpetas no viajan en Git. El equipo de trabajo usa Python 3.14.7 y el de casa Python 3.14.8. Los dos pueden instalar `requirements-direct.txt`.

## Qué no se sincroniza

Git ignora:

- `.venv/` y cualquier otro entorno virtual
- archivos `__pycache__`, checkpoints de Jupyter y `.env`
- `results/models/`, salvo el archivo `.gitkeep` que conserva la carpeta
- `docs/esp_gassy_flow_paper.pdf`
- `archive/dataset_original.zip`

El PDF del artículo es material de Elsevier. El ZIP local tampoco se publica. Los Excel de `data/raw/` sí están en el repositorio porque el conjunto de Mendeley Data está bajo CC BY 4.0. El crédito correspondiente está en el `README.md`.

Si en un equipo existe el PDF, se deja en `docs/esp_gassy_flow_paper.pdf` y Git no lo sube. Lo mismo ocurre con el ZIP en `archive/`.

## Al empezar una sesión

Entre en la carpeta del laboratorio y mire el estado antes de editar:

```bash
git status
git branch --show-current
git pull --ff-only
```

`git branch --show-current` muestra la rama. Debe ser `main`.

`git pull --ff-only` trae los commits del otro equipo solo si Git puede avanzar en línea recta. Si alguien editó los mismos archivos en los dos equipos, Git se detiene en lugar de mezclar a ciegas. Eso es lo que se quiere: revisar el conflicto con calma.

`git status` muestra tres grupos útiles: cambios sin preparar, cambios preparados para el commit y archivos que Git ignora. Un entorno virtual no debe aparecer como archivo preparado.

## Al terminar una sesión

```bash
git status
git add README.md docs/progreso_investigacion.md notebooks/01_exploracion_inicial.ipynb
git commit -m "docs: avance investigacion ESP"
git push
```

`git add` del ejemplo nombra archivos concretos. Sustituya esa lista por los archivos que realmente revisó. Evite `git add -A` si no miró antes la lista completa.

Revise el mensaje de `git status` y busque que no figuren `.venv`, `.env`, el PDF ni el ZIP.

El primer `git push` de una copia nueva, si todavía no sigue a la rama remota, es:

```bash
git push -u origin main
```

Los siguientes pueden ser `git push`.

No use `git push --force`. Un force push reescribe el historial que el otro computador ya pudo descargar.

## Identidad de los commits

Dentro de este repositorio, y solo aquí, el autor es:

```bash
git config --local user.name "antonioavezon"
git config --local user.email "antonio.avezon@gmail.com"
```

No cambie `~/.gitconfig` para este laboratorio. Compruebe la identidad local con:

```bash
git config --local --get user.name
git config --local --get user.email
```

## Cómo leer el historial

```bash
git log --oneline --decorate -n 15
git diff
git diff --staged
```

`git log` muestra los commits. `git diff` muestra lo que aún no está preparado. `git diff --staged` muestra lo que entrará en el próximo commit.

Un commit debe describir un avance reconocible: una actividad del cuaderno, una corrección de la bitácora o un ajuste de la instalación. Así el historial sirve como bitácora científica, no solo como copia de seguridad.

## Conflictos

Un conflicto aparece cuando los dos equipos cambiaron las mismas líneas. Git marca el archivo y detiene la operación.

1. Abra el archivo y busque las marcas `<<<<<<<`, `=======` y `>>>>>>>`.
2. Conserve el texto que debe quedar. En un cuaderno, compare las celdas y no borre una actividad solo porque llegó después.
3. Quite las marcas.
4. `git add` del archivo ya resuelto.
5. `git commit` para cerrar la fusión.
6. `git push`.

No use `git reset --hard`, `git checkout --` sobre un cuaderno con trabajo nuevo, ni `git clean` para “arreglar” una diferencia. Esos comandos pueden borrar cambios que no están en otro commit.

Si `git pull --ff-only` se niega a avanzar, el otro equipo tiene commits y este equipo también. En ese caso:

```bash
git fetch origin
git log --oneline --left-right HEAD...origin/main
```

Ese log muestra qué commits están solo en este equipo y cuáles están solo en GitHub. Decida la fusión cuando haya visto esa lista. Una fusión ordinaria, `git merge origin/main`, conserva los dos lados y señala los conflictos. No reescribe la historia.

## Cuadernos

Un cuaderno Jupyter guarda el código y también las salidas de la última ejecución. Dos ediciones del mismo cuaderno producen conflictos difíciles de leer.

Para reducirlos:

- Trabaje un cuaderno en un solo equipo cada vez.
- Haga `git pull --ff-only` antes de abrirlo.
- Al terminar, revise `git diff` y confirme que las salidas no incluyen contraseñas, tokens ni la ruta completa de su carpeta personal.
- Haga commit del cuaderno junto con la nota de `docs/progreso_investigacion.md` que explica qué cambió.

Las salidas publicadas en el commit inicial muestran rutas relativas a la raíz del proyecto, por ejemplo `.venv/bin/python`, y no la carpeta `/home` de un equipo.

## Fedora de casa: la carpeta ya tiene cuadernos

La carpeta `/home/antoniofedora/Documentos/ESP-DataScience` ya contiene cuadernos con avances. No clone el repositorio encima de esa carpeta. Un clon encima mezclaría archivos sin comparar y podría ocultar notas que solo existen en casa.

Haga esto en el equipo de casa:

1. Respalde la carpeta actual, por ejemplo copiándola a `ESP-DataScience-respaldo-casa`. No borre el original hasta terminar la comparación.
2. Clone en una carpeta temporal distinta:

```bash
cd "/home/antoniofedora/Documentos"
git clone https://github.com/antonioavezon/ESP-DataScience.git ESP-DataScience-github
```

3. Compare cuadernos y documentación, sin copiar a ciegas:

```bash
diff -ru \
  "/home/antoniofedora/Documentos/ESP-DataScience/notebooks" \
  "/home/antoniofedora/Documentos/ESP-DataScience-github/notebooks"
diff -ru \
  "/home/antoniofedora/Documentos/ESP-DataScience/docs" \
  "/home/antoniofedora/Documentos/ESP-DataScience-github/docs"
```

4. Anote ejercicios, celdas o frases que estén en el respaldo de casa y no en el clon.
5. Incorpore esas diferencias dentro de `ESP-DataScience-github`, editando los archivos a mano o con un comparador. Conserve el trabajo de los dos equipos. Si una actividad de casa no está en los cuadernos `00` y `01`, agréguela en una celda nueva o en la bitácora, sin borrar las validaciones 186, 10, 62 y 124 salvo que una revisión de los Excel demuestre otra cifra.
6. En el clon, cree el entorno y compruebe la identidad local:

```bash
cd "/home/antoniofedora/Documentos/ESP-DataScience-github"
git config --local user.name "antonioavezon"
git config --local user.email "antonio.avezon@gmail.com"
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-direct.txt
python -m pip check
```

7. Compruebe la sincronización:

```bash
git status
git pull --ff-only
git add <archivos_revisados>
git commit -m "docs: avance investigacion ESP"
git push
```

8. En el equipo de trabajo, `git pull --ff-only` debe traer ese commit.

Cuando el clon ya contenga los avances de casa y el `push` haya funcionado, puede pasar a usar `ESP-DataScience-github` como carpeta de trabajo. Conserve el respaldo hasta haber abierto los cuadernos y visto que no falta ninguna anotación. No hace falta borrar la carpeta antigua para que Git funcione.

El remoto de ese clon se llama `origin` y apunta al repositorio privado. Compruébelo con:

```bash
git remote -v
git status -sb
```

`git status -sb` resume la rama y si está por delante o por detrás de `origin/main`.
