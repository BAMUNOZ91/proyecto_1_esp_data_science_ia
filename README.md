# ¿Cotiza a pensión? Probabilidad de cotizar según el perfil del trabajador

Proyecto I de la Especialización en Ciencia de Datos e IA. Estima la probabilidad de que un trabajador colombiano cotice a pensión, a partir de su perfil personal, laboral y de hogar, con la GEIH 2025 del DANE.

## 1. ¿Qué problema resuelve?

En Colombia, casi 6 de cada 10 personas ocupadas no cotizan a pensión, y eso las deja sin protección en la vejez.

**Pregunta:** ¿qué probabilidad tiene un trabajador de cotizar a pensión, según su perfil?

**Variable objetivo:** `cotiza_pension` (1 = cotiza, 0 = no cotiza). Los ya pensionados se excluyen.

**Para quién sirve:**
- Fondos de pensiones y Colpensiones, para identificar perfiles con baja probabilidad de cotizar.
- La UGPP, para enfocar la fiscalización. Un grupo clave son las personas que ganan 1 SMMLV o más y no cotizan: son cerca del 25 % de ese grupo, unos 3 millones de personas.
- Política pública, para entender qué características se asocian con no cotizar.

## 2. ¿De dónde salen los datos?

- **Fuente:** Gran Encuesta Integrada de Hogares (GEIH) 2025 del DANE, módulo de ocupados, enero a diciembre. Archivo Nacional de Datos: https://microdatos.dane.gov.co
- **Descarga:** con la librería [`dane-data`](https://github.com/IntegralIndefinida/DANE-data), mediante `make data`.
- **Tamaño:** 358.029 ocupados en el archivo crudo y 351.721 después de quitar a los pensionados.
- **Detalle:** columnas, filtros, licencia y limitaciones en [dataset-card.md](dataset-card.md).

Los datos **no se suben a git**: se descargan y se generan con `make data`.

## 3. ¿Cómo se corre?

**Requisitos:** [uv](https://docs.astral.sh/uv/) y `make`. En Windows, `make` se instala con `winget install ezwinports.make`.

```bash
git clone git@github.com:BAMUNOZ91/proyecto_1_esp_data_science_ia.git
cd proyecto_1_esp_data_science_ia

make setup   # crea el entorno .venv e instala las dependencias
make data    # descarga la GEIH 2025 y genera data/processed/ (la primera vez tarda: son más de 1 GB)
make train   # entrena el modelo, lo evalúa y guarda models/ y reports/metricas_prueba.json
make test    # corre las pruebas
make app     # abre la app de Streamlit en el navegador
```

Si los datos no existen, `make train` corre `make data` primero, así que `make setup && make train && make test` funciona en una máquina limpia. `make app` necesita el modelo de `make train`.

En una prueba desde un clon limpio, `make setup`, `make data`, `make train` y `make test` tardaron unos 3 minutos en total; la descarga del DANE fue la parte más lenta, y depende de la conexión. Con `make` sin argumentos se ven todos los comandos.

Sin `make`, los mismos pasos son: `uv sync`, `uv run python -m cotiza_pension.data`, `uv run python -m cotiza_pension.train`, `uv run pytest` y `uv run streamlit run app/app.py`.

## 4. ¿Qué resultado se obtiene?

**La app:** un formulario de Streamlit donde se llena el perfil de una persona (edad, educación, posición ocupacional, tamaño de empresa, ingreso, etc.) y devuelve la probabilidad de que cotice a pensión.

**El modelo:** XGBoost, elegido entre 7 modelos con validación temporal por meses ([notebooks/02_seleccion_modelos.ipynb](notebooks/02_seleccion_modelos.ipynb)).

| Modelo | AUC en validación |
|---|---|
| **XGBoost (ajustado)** | **0,983** |
| HistGradientBoosting | 0,983 |
| Random Forest | 0,978 |
| Árbol de decisión | 0,971 |
| Regresión logística (L1 y L2) | 0,969 |
| Dummy (línea base) | 0,500 |

**Evaluación en prueba (octubre a diciembre, 89.733 personas, nunca vistas al entrenar):**

| Métrica | Valor |
|---|---|
| AUC | 0,982 |
| Acierto | 93,4 % |
| No cotizantes detectados | 94,8 % |
| Brier (error de la probabilidad, menor es mejor) | 0,049 |

Las cifras completas están en [reports/metricas_prueba.json](reports/metricas_prueba.json).

**Variables más importantes:** el tamaño de la empresa y el ingreso en salarios mínimos. Les siguen, muy lejos, la rama de actividad, la posición ocupacional y el nivel educativo.

**¿Por qué el AUC es tan alto?** No es fuga de información:
- Se quitaron las variables que solo existen si la persona ya cotiza: fondo de pensiones, quién paga el aporte, salud contributiva, ARL, caja de compensación e informalidad del DANE.
- El split es temporal: se entrena con enero a septiembre y se prueba con octubre a diciembre.
- El tamaño de empresa y el ingreso, cada uno por separado, ya logran un AUC de 0,92. El 0,98 sale de combinar variables que separan mucho, no de una variable que filtre la respuesta.

## 5. Limitaciones

- **Le cuesta el grupo que más interesa.** Entre quienes ganan 1 SMMLV o más, el AUC baja a 0,964 y el modelo detecta al 82,5 % de los no cotizantes. Entre los asalariados de empresa particular de ese grupo, solo detecta al 66,7 %, porque su perfil se parece mucho al de quienes sí cotizan.
- **Describe la muestra, no la población.** El modelo se entrena sin el factor de expansión de la encuesta.
- **Es una encuesta.** La respuesta de cotizar es declarada por la persona, no un registro administrativo.
- **Diccionario de datos:** algunos códigos del DANE se dedujeron de los datos y faltan por confirmar con el diccionario oficial (ver [dataset-card.md](dataset-card.md)).
- **Cambios en 2026:** la reducción de la jornada laboral (Ley 2101) puede cambiar el significado de `horas_semana`.
- **`tiene_contrato` no se usa.** En los datos vale 1 para todos los asalariados, así que repite la posición ocupacional y no mejoró ningún modelo.

## Estructura del proyecto

```
├── src/cotiza_pension/   código del proyecto
│   ├── config.py         rutas, variables y decisiones del modelo
│   ├── data.py           descarga, limpieza y split temporal
│   ├── features.py       preprocesamiento (se ajusta solo con entrenamiento)
│   ├── model.py          catálogo de modelos y pipeline final
│   ├── train.py          entrenamiento y evaluación
│   ├── predict.py        predicción para una persona
│   └── formulario.py     opciones y textos de la app
├── app/app.py            app de Streamlit
├── notebooks/            EDA y selección de modelos (experimentación)
├── tests/                pruebas automatizadas
├── reports/              métricas del modelo final
├── models/               modelo entrenado (no se sube a git)
├── dataset-card.md       ficha de los datos
├── Makefile              comandos del proyecto
└── pyproject.toml        dependencias (uv)
```

## Autores

Brayan Andrés Muñoz ([BAMUNOZ91](https://github.com/BAMUNOZ91)), Julián Andrés Urrea ([julianurreae](https://github.com/julianurreae)) y [diemiranda04](https://github.com/diemiranda04).
