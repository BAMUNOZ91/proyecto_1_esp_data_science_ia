"""Datos sintéticos para los tests de features y modelos (no requieren descargar nada)."""

import numpy as np
import pandas as pd
import pytest

from cotiza_pension.config import FEATURE_CONTRATO, FEATURES_CAT, FEATURES_NUM

# Algunas categóricas vienen como códigos numéricos en los datos reales (con nulos)
CODIGOS_NUMERICOS = {
    "lugar_trabajo": [1.0, 2.0, 7.0],
    "rama_2d": [1.0, 47.0, 84.0],
    "estrato": [1.0, 2.0, 3.0, np.nan],
}


@pytest.fixture
def X_y_sinteticos() -> tuple[pd.DataFrame, pd.Series]:
    """240 personas con las mismas columnas y tipos que el dataset limpio.

    Cotiza quien gana más de 1 SMMLV o es empleado del gobierno, para que haya una
    relación clara entre las features y el objetivo.
    """
    rng = np.random.default_rng(0)
    n = 240
    X = pd.DataFrame(
        {
            "edad": rng.integers(18, 70, n),
            "horas_semana": rng.integers(10, 60, n).astype(float),
            "meses_en_empresa": rng.integers(0, 300, n).astype(float),
            "ingreso_smmlv": rng.gamma(2.0, 0.6, n),
        }
    )
    for col in FEATURES_CAT:
        valores = CODIGOS_NUMERICOS.get(col, ["a", "b", "c"])
        X[col] = rng.choice(valores, n)
    X["posicion_ocupacional"] = rng.choice(["Cuenta propia", "Empleado del gobierno"], n)
    X[FEATURE_CONTRATO] = rng.integers(0, 2, n)
    X.loc[::17, "ingreso_smmlv"] = np.nan  # ingreso no reportado

    y = (
        (X["ingreso_smmlv"].fillna(0) > 1) | (X["posicion_ocupacional"] == "Empleado del gobierno")
    ).astype(int)
    assert list(X.columns) == FEATURES_NUM + FEATURES_CAT + [FEATURE_CONTRATO]
    return X, y.rename("cotiza_pension")
