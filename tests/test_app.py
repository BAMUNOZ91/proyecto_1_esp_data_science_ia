"""Formulario y app de Streamlit, con un modelo entrenado sobre datos sintéticos."""

import math
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from cotiza_pension import predict
from cotiza_pension.config import FEATURES_CAT, SMMLV
from cotiza_pension.formulario import (
    NO_INFORMA,
    armar_datos,
    etiqueta,
    opciones_categoricas,
)
from cotiza_pension.model import construir_pipeline_final

APP = str(Path(__file__).parents[1] / "app" / "app.py")


@pytest.fixture
def pipeline(generador_sinteticos):
    X, y = generador_sinteticos(300)
    return construir_pipeline_final().fit(X.drop(columns="tiene_contrato"), y)


def test_opciones_salen_del_modelo(pipeline):
    opciones = opciones_categoricas(pipeline)
    assert list(opciones) == FEATURES_CAT
    assert {"1.0", "2.0", "3.0"} <= set(opciones["estrato"])


def test_etiquetas_legibles():
    assert etiqueta("rama_2d", "47.0") == "47 - Comercio al por menor"
    assert etiqueta("rama_2d", "5.0") == "5 - Otra rama (CIIU)"
    assert etiqueta("estrato", "2.0") == "Estrato 2"
    assert etiqueta("estrato", "9.0") == "No sabe o tiene planta eléctrica"
    assert etiqueta("lugar_trabajo", "7.0") == "Local fijo, oficina o fábrica"
    assert etiqueta("estrato", math.nan) == NO_INFORMA
    assert etiqueta("sexo", "Mujer") == "Mujer"


def test_armar_datos_pasa_el_ingreso_a_salarios_minimos():
    datos = armar_datos(
        {"edad": 30, "horas_semana": 48.0, "meses_en_empresa": 12.0},
        {c: "a" for c in FEATURES_CAT},
        SMMLV * 2,
    )
    assert datos["ingreso_smmlv"] == 2
    sin_ingreso = armar_datos(
        {"edad": 30, "horas_semana": 48.0, "meses_en_empresa": 12.0},
        {c: "a" for c in FEATURES_CAT},
        None,
    )
    assert math.isnan(sin_ingreso["ingreso_smmlv"])


def test_la_app_calcula_una_probabilidad(pipeline, monkeypatch):
    monkeypatch.setattr(predict, "_pipeline", pipeline)
    app = AppTest.from_file(APP, default_timeout=60).run()
    assert not app.exception
    app.button[0].click().run()
    assert not app.exception
    assert app.metric[0].label == "Probabilidad de cotizar"
    assert app.metric[0].value.endswith("%")


def test_la_app_avisa_si_no_hay_modelo(tmp_path, monkeypatch):
    monkeypatch.setattr(predict, "_pipeline", None)
    monkeypatch.setattr(predict, "MODEL_PATH", tmp_path / "no_existe.joblib")
    app = AppTest.from_file(APP, default_timeout=60).run()
    assert not app.exception
    assert "make train" in app.error[0].value
