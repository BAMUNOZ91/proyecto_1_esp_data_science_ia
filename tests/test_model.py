"""Catálogo de modelos y pipeline final."""

import pytest
from xgboost import XGBClassifier

from cotiza_pension.config import FEATURE_CONTRATO, HIPERPARAMETROS_FINALES, USAR_CONTRATO
from cotiza_pension.model import MODELOS, construir_pipeline, construir_pipeline_final


@pytest.mark.parametrize("nombre", MODELOS)
def test_cada_modelo_del_catalogo_entrena_y_predice(X_y_sinteticos, nombre):
    X, y = X_y_sinteticos
    pipeline = construir_pipeline(nombre).fit(X, y)
    probabilidades = pipeline.predict_proba(X)[:, 1]
    assert len(probabilidades) == len(X)
    assert ((probabilidades >= 0) & (probabilidades <= 1)).all()


@pytest.mark.parametrize("nombre", ["hist_boosting", "xgboost"])
def test_boosting_funciona_con_y_sin_contrato(X_y_sinteticos, nombre):
    X, y = X_y_sinteticos
    for usar_contrato in (True, False):
        construir_pipeline(nombre, usar_contrato=usar_contrato).fit(X, y)


def test_cada_llamada_devuelve_un_modelo_nuevo():
    assert construir_pipeline("xgboost") is not construir_pipeline("xgboost")
    a = construir_pipeline("xgboost").named_steps["clasificador"]
    b = construir_pipeline("xgboost").named_steps["clasificador"]
    assert a is not b


def test_nombre_invalido_da_error():
    with pytest.raises(ValueError, match="nombre debe ser"):
        construir_pipeline("svm")


def test_hiperparametros_cambian_los_valores_por_defecto():
    clasificador = construir_pipeline("xgboost", learning_rate=0.05).named_steps["clasificador"]
    assert clasificador.learning_rate == 0.05


def test_pipeline_final_usa_la_decision_del_notebook(X_y_sinteticos):
    pipeline = construir_pipeline_final()
    clasificador = pipeline.named_steps["clasificador"]
    assert isinstance(clasificador, XGBClassifier)
    for parametro, valor in HIPERPARAMETROS_FINALES.items():
        assert clasificador.get_params()[parametro] == valor

    X, y = X_y_sinteticos
    pipeline.fit(X, y)
    columnas = pipeline.named_steps["preprocesador"].get_feature_names_out()
    assert any(FEATURE_CONTRATO in c for c in columnas) == USAR_CONTRATO
