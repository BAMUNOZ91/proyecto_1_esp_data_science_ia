"""Preprocesamiento. Separa el "qué hacer con las features" del "qué modelo usar".

Hay dos variantes, las mismas que se validaron en notebooks/02_seleccion_modelos.ipynb:

- lineal:  para modelos lineales (logística). Imputa y escala las numéricas y aplica
           one-hot a las categóricas.
- arboles: para modelos de árboles (árbol, random forest, boosting). Las numéricas pasan
           tal cual (los árboles aceptan nulos) y cada categoría se convierte en un entero.

Todo se ajusta con `fit` solo sobre los datos de entrenamiento, dentro del Pipeline: así no
hay fuga de información hacia validación o prueba.

Posibles mejoras que NO se probaron en la selección (y por eso no están aquí): log del
ingreso, recorte de atípicos, tramos de edad y agrupar estrato 0 / 9 / nulo.
"""

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, OrdinalEncoder, StandardScaler

from .config import FEATURE_CONTRATO, FEATURES_CAT, FEATURES_NUM, USAR_CONTRATO

TIPOS_PREPROCESADOR = ("lineal", "arboles")

# Categorías con menos casos que esto se agrupan en una sola columna en el one-hot
MIN_FRECUENCIA_CATEGORIA = 100


def a_texto(X):
    """Convierte las categóricas a texto, para que los códigos numéricos (rama, estrato,
    lugar de trabajo) se traten como categorías y no como cantidades.

    Con pandas 3 los nulos siguen siendo nulos (no el texto "nan"): el one-hot los trata
    como una categoría más y el preprocesador de árboles los deja como valor faltante,
    que XGBoost maneja de forma nativa. Así se entrenó y validó el modelo en el notebook 02.

    Está en el paquete (y no en un notebook) para que el modelo guardado con joblib se
    pueda cargar desde la app.
    """
    return X.astype(str)


def _a_texto_transformer() -> FunctionTransformer:
    """`a_texto` como paso de un Pipeline, conservando los nombres de las columnas."""
    return FunctionTransformer(a_texto, feature_names_out="one-to-one")


def _con_contrato(transformadores: list, usar_contrato: bool) -> list:
    """Agrega `tiene_contrato` al final, sin transformar, si se pide."""
    if usar_contrato:
        transformadores.append(("contrato", "passthrough", [FEATURE_CONTRATO]))
    return transformadores


def construir_preprocesador_lineal(usar_contrato: bool = USAR_CONTRATO) -> ColumnTransformer:
    """Numéricas: mediana + marca de "valor no reportado" + escalado. Categóricas: one-hot."""
    numerico = make_pipeline(
        SimpleImputer(strategy="median", add_indicator=True),
        StandardScaler(),
    )
    categorico = make_pipeline(
        _a_texto_transformer(),
        OneHotEncoder(handle_unknown="ignore", min_frequency=MIN_FRECUENCIA_CATEGORIA),
    )
    transformadores = [("num", numerico, FEATURES_NUM), ("cat", categorico, FEATURES_CAT)]
    return ColumnTransformer(_con_contrato(transformadores, usar_contrato))


def construir_preprocesador_arboles(usar_contrato: bool = USAR_CONTRATO) -> ColumnTransformer:
    """Numéricas sin cambios. Categóricas a enteros; una categoría nueva se codifica como -1.

    El orden de salida es: FEATURES_NUM, FEATURES_CAT y, si se usa, tiene_contrato.
    model.py depende de ese orden para indicar qué columnas son categóricas.
    """
    categorico = make_pipeline(
        _a_texto_transformer(),
        OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1),
    )
    transformadores = [("num", "passthrough", FEATURES_NUM), ("cat", categorico, FEATURES_CAT)]
    return ColumnTransformer(_con_contrato(transformadores, usar_contrato))


def construir_preprocesador(
    tipo: str = "arboles", usar_contrato: bool = USAR_CONTRATO
) -> ColumnTransformer:
    """Devuelve el preprocesador del tipo pedido: "lineal" o "arboles"."""
    if tipo == "lineal":
        return construir_preprocesador_lineal(usar_contrato)
    if tipo == "arboles":
        return construir_preprocesador_arboles(usar_contrato)
    raise ValueError(f"tipo debe ser uno de {TIPOS_PREPROCESADOR}, se recibió {tipo!r}")
