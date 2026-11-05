"""Coherencia de las decisiones declaradas en config.py."""

from cotiza_pension import config


def test_objetivo_no_esta_en_las_features():
    features = config.FEATURES_NUM + config.FEATURES_CAT + [config.FEATURE_CONTRATO]
    assert config.TARGET not in features


def test_columnas_excluidas_no_entran_al_modelo():
    features = set(config.FEATURES_NUM + config.FEATURES_CAT + [config.FEATURE_CONTRATO])
    assert features.isdisjoint(config.NO_SON_FEATURES)


def test_features_no_estan_repetidas():
    features = config.FEATURES_NUM + config.FEATURES_CAT + [config.FEATURE_CONTRATO]
    assert len(features) == len(set(features))


def test_meses_de_entrenamiento_y_prueba_cubren_el_anio_sin_cruzarse():
    entrenamiento = set(config.MESES_ENTRENAMIENTO)
    prueba = set(config.MESES_PRUEBA)
    assert entrenamiento.isdisjoint(prueba)
    assert entrenamiento | prueba == set(range(1, 13))
    assert max(entrenamiento) < min(prueba), "la prueba debe ser posterior al entrenamiento"


def test_las_features_salen_del_renombre_o_se_calculan():
    nombres_limpios = set(config.RENOMBRAR.values()) | {"ingreso_smmlv"}
    features = config.FEATURES_NUM + config.FEATURES_CAT + [config.FEATURE_CONTRATO]
    assert set(features) <= nombres_limpios
