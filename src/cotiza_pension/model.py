"""Pipeline completo: preprocesador + clasificador. Un solo objeto para entrenar y servir."""

from sklearn.pipeline import Pipeline

MODELOS = ("logistica", "boosting")


def construir_pipeline(tipo: str = "logistica", usar_contrato: bool = True) -> Pipeline:
    """Devuelve Pipeline([("preprocesador", ...), ("clasificador", ...)]).

    tipo:
        "logistica"  LogisticRegression con regularización L2 (línea base)
        "boosting"   HistGradientBoostingClassifier
    """
    if tipo not in MODELOS:
        raise ValueError(f"tipo debe ser uno de {MODELOS}, se recibió {tipo!r}")
    # TODO (paso 4): implementar usando features.construir_preprocesador(usar_contrato)
    raise NotImplementedError("Pendiente: construir el pipeline")
