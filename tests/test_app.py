"""Formulario y app de Streamlit, con un modelo entrenado sobre datos sintéticos."""

import math
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from cotiza_pension import predict
from cotiza_pension.config import FEATURES_CAT, SMMLV
from cotiza_pension.formulario import (
    NO_INFORMA,
    NOMBRES_RAMA,
    armar_datos,
    etiqueta,
    opciones_categoricas,
    texto_ingreso,
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


def test_ramas_sin_nombre_en_la_ciiu_no_se_ofrecen(generador_sinteticos):
    X, y = generador_sinteticos(300)
    X["rama_2d"] = X["rama_2d"].where(X.index % 10 != 0, 0.0)  # algunos con código 0
    pipeline = construir_pipeline_final().fit(X.drop(columns="tiene_contrato"), y)
    assert "0.0" not in opciones_categoricas(pipeline)["rama_2d"]
    assert "47.0" in opciones_categoricas(pipeline)["rama_2d"]


def test_etiquetas_legibles():
    assert etiqueta("rama_2d", "47.0") == "47 - Comercio al por menor"
    assert etiqueta("rama_2d", "5.0") == "5 - Extracción de carbón de piedra y lignito"
    assert etiqueta("rama_2d", "4.0") == "4 - Código sin nombre en la CIIU"
    assert etiqueta("estrato", "2.0") == "Estrato 2"
    assert etiqueta("estrato", "9.0") == "No sabe o tiene planta eléctrica"
    assert etiqueta("lugar_trabajo", "7.0") == "Local fijo, oficina o fábrica"
    assert etiqueta("estrato", math.nan) == NO_INFORMA
    assert etiqueta("sexo", "Mujer") == "Mujer"


def test_nombres_de_rama_completos_y_cortos():
    assert len(NOMBRES_RAMA) == 88
    assert max(len(nombre) for nombre in NOMBRES_RAMA.values()) <= 45


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
    assert app.sidebar.metric[0].label == "Probabilidad de cotizar"
    assert app.sidebar.metric[0].value.endswith("%")


def test_la_probabilidad_cambia_al_cambiar_un_campo(pipeline, monkeypatch):
    monkeypatch.setattr(predict, "_pipeline", pipeline)
    app = AppTest.from_file(APP, default_timeout=60).run()
    ingreso = next(n for n in app.number_input if n.label.startswith("Ingreso"))
    ingreso.set_value(0).run()  # sin clic en ningún botón
    bajo = app.sidebar.metric[0].value
    ingreso.set_value(20_000_000).run()
    assert not app.exception
    assert app.sidebar.metric[0].value != bajo


def test_texto_ingreso_con_punto_de_miles():
    assert texto_ingreso(1_423_500) == "$1.423.500 (1,00 SMMLV)"
    assert texto_ingreso(4_000_000) == "$4.000.000 (2,81 SMMLV)"


def test_el_ingreso_sube_de_100_mil_y_se_muestra_con_puntos(pipeline, monkeypatch):
    monkeypatch.setattr(predict, "_pipeline", pipeline)
    app = AppTest.from_file(APP, default_timeout=60).run()
    ingreso = next(n for n in app.number_input if n.label.startswith("Ingreso"))
    assert ingreso.step == 100_000
    ingreso.increment().run()
    assert not app.exception
    assert any("1.523.500" in m.value for m in app.markdown)


def test_la_app_avisa_si_no_hay_modelo(tmp_path, monkeypatch):
    monkeypatch.setattr(predict, "_pipeline", None)
    monkeypatch.setattr(predict, "MODEL_PATH", tmp_path / "no_existe.joblib")
    app = AppTest.from_file(APP, default_timeout=60).run()
    assert not app.exception
    assert "make train" in app.error[0].value
