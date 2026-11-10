"""Inferencia: carga del modelo entrenado y predicción para una persona."""

import joblib
import pandas as pd

from .config import FEATURE_CONTRATO, FEATURES_CAT, FEATURES_NUM, MODEL_PATH, UMBRAL

_pipeline = None


def obtener_pipeline():
    """Carga el modelo una sola vez y lo deja en memoria para las siguientes llamadas."""
    global _pipeline
    if _pipeline is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"No se encontró el modelo en {MODEL_PATH}. Entrénalo primero con `make train`."
            )
        _pipeline = joblib.load(MODEL_PATH)
    return _pipeline


def predecir(datos: dict) -> dict:
    """Devuelve la probabilidad de que la persona cotice a pensión.

    Entrada: dict con todas las FEATURES_NUM y FEATURES_CAT (y `tiene_contrato` si el
    modelo la usa), por ejemplo {"edad": 35, "sexo": "Mujer", ...}.

    Salida: {"cotiza": 1, "probabilidad_cotizar": 0.73}. `cotiza` es 1 si la probabilidad
    llega a config.UMBRAL.
    """
    requeridas = FEATURES_NUM + FEATURES_CAT
    faltantes = [c for c in requeridas if c not in datos]
    if faltantes:
        raise ValueError(f"Faltan columnas: {faltantes}")

    pipeline = obtener_pipeline()
    columnas = list(getattr(pipeline, "feature_names_in_", requeridas))
    if FEATURE_CONTRATO in columnas and FEATURE_CONTRATO not in datos:
        raise ValueError(f"Este modelo necesita la columna {FEATURE_CONTRATO!r}")

    df = pd.DataFrame([datos], columns=columnas)
    probabilidad = float(pipeline.predict_proba(df)[0, 1])
    return {"cotiza": int(probabilidad >= UMBRAL), "probabilidad_cotizar": probabilidad}
