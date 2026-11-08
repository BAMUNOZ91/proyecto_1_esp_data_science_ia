"""Datos: descarga, limpieza, split temporal y X / y, con datos sintéticos (sin descargar nada)."""

import sys
from types import SimpleNamespace

import pandas as pd
import pytest

from cotiza_pension import data
from cotiza_pension.config import (
    FEATURE_CONTRATO,
    FEATURES_CAT,
    FEATURES_NUM,
    RENOMBRAR,
    SMMLV,
    TARGET,
    VARIABLES_DANE,
)
from cotiza_pension.data import descargar, limpiar, separar_temporal, separar_X_y


@pytest.fixture
def df_crudo() -> pd.DataFrame:
    """Tres ocupados con códigos del DANE: cotiza, no cotiza y pensionado."""
    df = pd.DataFrame({col: [1, 1, 1] for col in ["anio", "mes", *VARIABLES_DANE]})
    df["DPTO"] = [5, 11, 99]
    df["P6920"] = [1, 2, 3]
    df["P6050"] = [1, 9, 1]  # 9 no tiene nombre confirmado: queda como "Otro"
    df["INGLABO"] = [SMMLV, None, SMMLV]
    return df


def test_limpiar_excluye_pensionados_y_deja_objetivo_en_1_0(df_crudo):
    limpio = limpiar(df_crudo)
    assert limpio[TARGET].tolist() == [1, 0]


def test_limpiar_traduce_codigos_y_renombra(df_crudo):
    limpio = limpiar(df_crudo)
    assert limpio["departamento"].tolist() == ["Antioquia", "Bogotá D.C."]
    assert limpio["parentesco_jefe"].tolist() == ["Jefe(a) del hogar", "Otro"]
    assert not {"MES", "OCI"} & set(limpio.columns)
    assert set(RENOMBRAR.values()) <= set(limpio.columns)


def test_limpiar_calcula_ingreso_y_respeta_nulos(df_crudo):
    limpio = limpiar(df_crudo)
    assert limpio["ingreso_smmlv"].iloc[0] == 1
    assert limpio["gana_1_smmlv_o_mas"].iloc[0] == 1
    assert limpio["gana_1_smmlv_o_mas"].isna().iloc[1]


def test_limpiar_no_modifica_el_original(df_crudo):
    copia = df_crudo.copy()
    limpiar(df_crudo)
    pd.testing.assert_frame_equal(df_crudo, copia)


def _dane_falso(df, fallidos=()):
    """Reemplaza `dane_data` para probar `descargar` sin conexión."""
    return SimpleNamespace(
        set_paths=lambda **_: None,
        geih=SimpleNamespace(download=lambda _: list(fallidos), load=lambda *_, **__: df),
    )


def test_descargar_deja_solo_ocupados_y_guarda(df_crudo, monkeypatch, tmp_path):
    df_crudo["OCI"] = [1, 1, 0]
    ruta = tmp_path / "crudo.csv"
    monkeypatch.setattr(data, "RAW_PATH", ruta)
    monkeypatch.setitem(sys.modules, "dane_data", _dane_falso(df_crudo))
    resultado = descargar()
    assert len(resultado) == 2
    assert len(pd.read_csv(ruta)) == 2


def test_descargar_falla_si_falta_un_mes(df_crudo, monkeypatch, tmp_path):
    monkeypatch.setattr(data, "RAW_PATH", tmp_path / "crudo.csv")
    monkeypatch.setitem(sys.modules, "dane_data", _dane_falso(df_crudo, fallidos=[3]))
    with pytest.raises(RuntimeError, match="No se pudo descargar"):
        descargar()


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
