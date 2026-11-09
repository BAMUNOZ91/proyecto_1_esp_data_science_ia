"""Pipeline completo: preprocesador + clasificador. Un solo objeto para entrenar y servir.

El catálogo tiene los 7 modelos comparados en notebooks/02_seleccion_modelos.ipynb, con
sus valores por defecto de esa comparación. El modelo final (config.MODELO_FINAL) usa
además los hiperparámetros ajustados de config.HIPERPARAMETROS_FINALES.
"""

from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

from .config import (
    FEATURES_CAT,
    FEATURES_NUM,
    HIPERPARAMETROS_FINALES,
    MODELO_FINAL,
    SEMILLA,
    USAR_CONTRATO,
)
from .features import construir_preprocesador


def _indices_categoricas() -> list[int]:
    """Posición de las categóricas en la salida del preprocesador de árboles."""
    inicio = len(FEATURES_NUM)
    return list(range(inicio, inicio + len(FEATURES_CAT)))


def _tipos_xgboost(usar_contrato: bool) -> list[str]:
    """Le dice a XGBoost qué columnas son numéricas ("q") y cuáles categóricas ("c")."""
    tipos = ["q"] * len(FEATURES_NUM) + ["c"] * len(FEATURES_CAT)
    return tipos + ["q"] if usar_contrato else tipos


# nombre -> (tipo de preprocesador, función que crea el clasificador según usar_contrato).
# Se guardan funciones, no modelos ya creados: cada llamada devuelve un modelo nuevo.
CATALOGO = {
    "dummy": ("lineal", lambda usar_contrato: DummyClassifier(strategy="prior")),
    "logistica_l2": ("lineal", lambda usar_contrato: LogisticRegression(max_iter=1000)),
    "logistica_l1": (
        "lineal",
        lambda usar_contrato: LogisticRegression(solver="liblinear", l1_ratio=1, C=0.5),
    ),
    "arbol": (
        "arboles",
        lambda usar_contrato: DecisionTreeClassifier(
            max_depth=8, min_samples_leaf=50, random_state=SEMILLA
        ),
    ),
    "random_forest": (
        "arboles",
        lambda usar_contrato: RandomForestClassifier(
            n_estimators=200, min_samples_leaf=20, n_jobs=-1, random_state=SEMILLA
        ),
    ),
    "hist_boosting": (
        "arboles",
        lambda usar_contrato: HistGradientBoostingClassifier(
            categorical_features=_indices_categoricas(), random_state=SEMILLA
        ),
    ),
    "xgboost": (
        "arboles",
        lambda usar_contrato: XGBClassifier(
            n_estimators=300,
            learning_rate=0.1,
            max_depth=6,
            tree_method="hist",
            enable_categorical=True,
            max_cat_to_onehot=1,
            feature_types=_tipos_xgboost(usar_contrato),
            n_jobs=-1,
            random_state=SEMILLA,
        ),
    ),
}

MODELOS = tuple(CATALOGO)


def construir_pipeline(
    nombre: str = MODELO_FINAL, usar_contrato: bool = USAR_CONTRATO, **hiperparametros
) -> Pipeline:
    """Devuelve Pipeline([("preprocesador", ...), ("clasificador", ...)]).

    `hiperparametros` cambia los valores por defecto del clasificador, por ejemplo
    construir_pipeline("xgboost", learning_rate=0.05).
    """
    if nombre not in CATALOGO:
        raise ValueError(f"nombre debe ser uno de {MODELOS}, se recibió {nombre!r}")
    tipo, crear_clasificador = CATALOGO[nombre]
    clasificador = crear_clasificador(usar_contrato)
    if hiperparametros:
        clasificador.set_params(**hiperparametros)
    return Pipeline(
        [
            ("preprocesador", construir_preprocesador(tipo, usar_contrato)),
            ("clasificador", clasificador),
        ]
    )


def construir_pipeline_final() -> Pipeline:
    """El modelo elegido: MODELO_FINAL con HIPERPARAMETROS_FINALES, sin tiene_contrato."""
    return construir_pipeline(MODELO_FINAL, USAR_CONTRATO, **HIPERPARAMETROS_FINALES)
