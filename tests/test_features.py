"""Pipeline de features: los dos preprocesadores (lineal y árboles), sin fuga de información."""

import numpy as np
import pytest

from cotiza_pension.config import FEATURE_CONTRATO, FEATURES_CAT, FEATURES_NUM
from cotiza_pension.features import (
    construir_preprocesador,
    construir_preprocesador_arboles,
    construir_preprocesador_lineal,
)


def _denso(matriz):
    """El one-hot puede devolver una matriz dispersa; la pasa a numpy normal."""
    return matriz.toarray() if hasattr(matriz, "toarray") else np.asarray(matriz)


def test_lineal_no_deja_nulos_y_marca_el_ingreso_no_reportado(X_y_sinteticos):
    X, _ = X_y_sinteticos
    pre = construir_preprocesador_lineal()
    salida = _denso(pre.fit_transform(X))
    assert not np.isnan(salida).any()
    nombres = pre.get_feature_names_out()
    assert any("missingindicator_ingreso_smmlv" in n for n in nombres)


def test_lineal_escala_las_numericas(X_y_sinteticos):
    X, _ = X_y_sinteticos
    salida = _denso(construir_preprocesador_lineal().fit_transform(X))
    numericas = salida[:, : len(FEATURES_NUM)]
    np.testing.assert_allclose(numericas.mean(axis=0), 0, atol=1e-9)
    np.testing.assert_allclose(numericas.std(axis=0), 1, atol=1e-9)


def test_arboles_deja_numericas_igual_y_codifica_categorias_como_enteros(X_y_sinteticos):
    X, _ = X_y_sinteticos
    salida = construir_preprocesador_arboles().fit_transform(X)
    np.testing.assert_array_equal(salida[:, : len(FEATURES_NUM)], X[FEATURES_NUM].to_numpy())
    categoricas = salida[:, len(FEATURES_NUM) :]
    assert categoricas.shape[1] == len(FEATURES_CAT)
    conocidas = categoricas[~np.isnan(categoricas)]
    assert (conocidas >= 0).all() and (conocidas == conocidas.round()).all()


def test_nulos_en_categoricas(X_y_sinteticos):
    """Árboles: el nulo queda como faltante. Lineal: el nulo es una categoría más."""
    X, _ = X_y_sinteticos
    hay_nulo = X["estrato"].isna().to_numpy()
    assert hay_nulo.any()

    salida = construir_preprocesador_arboles().fit_transform(X)
    col_estrato = len(FEATURES_NUM) + FEATURES_CAT.index("estrato")
    np.testing.assert_array_equal(np.isnan(salida[:, col_estrato]), hay_nulo)

    lineal = construir_preprocesador_lineal().fit(X)
    categorias_estrato = lineal.named_transformers_["cat"][-1].categories_[
        FEATURES_CAT.index("estrato")
    ]
    assert any(isinstance(c, float) and np.isnan(c) for c in categorias_estrato)


def test_categoria_nueva_no_rompe_la_transformacion(X_y_sinteticos):
    X, _ = X_y_sinteticos
    nuevas = X.head(3).copy()
    nuevas["departamento"] = "Departamento nuevo"
    nuevas["rama_2d"] = 999.0

    arboles = construir_preprocesador_arboles().fit(X)
    salida = arboles.transform(nuevas)
    col_depto = len(FEATURES_NUM) + FEATURES_CAT.index("departamento")
    assert (salida[:, col_depto] == -1).all()

    lineal = construir_preprocesador_lineal().fit(X)
    assert not np.isnan(_denso(lineal.transform(nuevas))).any()


def test_se_ajusta_solo_con_los_datos_de_entrenamiento(X_y_sinteticos):
    """La mediana para imputar sale de entrenamiento, no de los datos que se transforman."""
    X, _ = X_y_sinteticos
    entrenamiento, otros = X.iloc[:120], X.iloc[120:].copy()
    otros["edad"] = 99
    pre = construir_preprocesador_lineal().fit(entrenamiento)
    imputador = pre.named_transformers_["num"].named_steps["simpleimputer"]
    np.testing.assert_allclose(
        imputador.statistics_, entrenamiento[FEATURES_NUM].median().to_numpy()
    )
    pre.transform(otros)
    np.testing.assert_allclose(
        imputador.statistics_, entrenamiento[FEATURES_NUM].median().to_numpy()
    )


@pytest.mark.parametrize("tipo", ["lineal", "arboles"])
def test_usar_contrato_agrega_o_quita_la_columna(X_y_sinteticos, tipo):
    X, _ = X_y_sinteticos
    con = construir_preprocesador(tipo, usar_contrato=True).fit(X)
    sin = construir_preprocesador(tipo, usar_contrato=False).fit(X)
    assert len(con.get_feature_names_out()) == len(sin.get_feature_names_out()) + 1
    assert f"contrato__{FEATURE_CONTRATO}" in con.get_feature_names_out()


def test_tipo_invalido_da_error():
    with pytest.raises(ValueError, match="tipo debe ser"):
        construir_preprocesador("svm")
