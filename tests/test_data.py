"""Split temporal y separación X / y con un DataFrame sintético (no requiere descargar datos)."""

import pandas as pd
import pytest

from cotiza_pension.config import FEATURE_CONTRATO, FEATURES_CAT, FEATURES_NUM, TARGET
from cotiza_pension.data import separar_temporal, separar_X_y


@pytest.fixture
def df_sintetico() -> pd.DataFrame:
    """Una persona por mes, con todas las columnas que espera el modelo."""
    n = 12
    df = pd.DataFrame({"mes": range(1, n + 1), TARGET: [0, 1] * (n // 2)})
    for col in FEATURES_NUM:
        df[col] = 1.0
    for col in FEATURES_CAT:
        df[col] = "a"
    df[FEATURE_CONTRATO] = 1
    df["factor_expansion"] = 100.0
    return df


def test_split_temporal_separa_por_meses(df_sintetico):
    entrenamiento, prueba = separar_temporal(df_sintetico)
    assert set(entrenamiento["mes"]) == set(range(1, 10))
    assert set(prueba["mes"]) == {10, 11, 12}
    assert len(entrenamiento) + len(prueba) == len(df_sintetico)


def test_split_temporal_no_repite_filas(df_sintetico):
    entrenamiento, prueba = separar_temporal(df_sintetico)
    assert entrenamiento.index.intersection(prueba.index).empty


def test_separar_X_y_deja_solo_las_features(df_sintetico):
    X, y = separar_X_y(df_sintetico)
    assert list(X.columns) == FEATURES_NUM + FEATURES_CAT + [FEATURE_CONTRATO]
    assert y.name == TARGET
    assert "mes" not in X.columns and "factor_expansion" not in X.columns


def test_separar_X_y_sin_contrato(df_sintetico):
    X, _ = separar_X_y(df_sintetico, usar_contrato=False)
    assert FEATURE_CONTRATO not in X.columns
