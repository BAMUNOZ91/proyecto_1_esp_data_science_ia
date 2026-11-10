"""Test de principio a fin: entrenar -> guardar -> cargar -> predecir, con datos sintéticos.

No necesita los datos reales ni `make train`: entrena un modelo con 1.200 personas
sintéticas y lo guarda en una carpeta temporal, sin tocar models/ ni reports/.
"""

import json

import numpy as np
import pandas as pd
import pytest

from cotiza_pension import predict
from cotiza_pension.config import FEATURE_CONTRATO, TARGET
from cotiza_pension.train import entrenar


@pytest.fixture
def df_sintetico(generador_sinteticos) -> pd.DataFrame:
    """Dataset con la forma del limpio: 100 personas por mes, de enero a diciembre.

    Hacen falta más personas que en los otros tests: el modelo final usa
    min_child_weight=23 (ajustado para 260 mil filas) y con muy pocos datos no aprende.
    """
    X, y = generador_sinteticos(1200)
    df = X.copy()
    df[TARGET] = y
    df["mes"] = np.tile(np.arange(1, 13), len(df) // 12)
    df["gana_1_smmlv_o_mas"] = (df["ingreso_smmlv"] >= 1).astype(float)
    return df


@pytest.fixture
def entrenado(df_sintetico, tmp_path):
    rutas = {"ruta_modelo": tmp_path / "modelo.joblib", "ruta_metricas": tmp_path / "metricas.json"}
    metricas = entrenar(df=df_sintetico, verbose=False, **rutas)
    return metricas, rutas


def test_entrena_con_enero_septiembre_y_evalua_en_octubre_diciembre(entrenado):
    metricas, _ = entrenado
    assert metricas["datos"]["meses_entrenamiento"] == list(range(1, 10))
    assert metricas["datos"]["meses_prueba"] == [10, 11, 12]
    assert metricas["datos"]["filas_entrenamiento"] == 900
    assert metricas["datos"]["filas_prueba"] == 300


def test_metricas_estan_entre_0_y_1(entrenado):
    metricas, _ = entrenado
    for nombre in ("roc_auc", "pr_auc", "brier", "acierto", "no_cotizantes_detectados"):
        assert 0 <= metricas["prueba"]["general"][nombre] <= 1, nombre
    # Con una relación clara entre features y objetivo, el modelo debe superar el azar
    assert metricas["prueba"]["general"]["roc_auc"] > 0.7


def test_guarda_el_modelo_y_las_metricas(entrenado):
    metricas, rutas = entrenado
    assert rutas["ruta_modelo"].exists()
    guardadas = json.loads(rutas["ruta_metricas"].read_text(encoding="utf-8"))
    assert guardadas == metricas


def test_sin_guardar_no_escribe_archivos(df_sintetico, tmp_path):
    entrenar(
        df=df_sintetico,
        guardar=False,
        verbose=False,
        ruta_modelo=tmp_path / "m.joblib",
        ruta_metricas=tmp_path / "m.json",
    )
    assert not any(tmp_path.iterdir())


def test_predice_una_persona_con_el_modelo_guardado(entrenado, df_sintetico, monkeypatch):
    _, rutas = entrenado
    monkeypatch.setattr(predict, "MODEL_PATH", rutas["ruta_modelo"])
    monkeypatch.setattr(predict, "_pipeline", None)  # obliga a cargar el modelo desde el archivo

    persona = df_sintetico.drop(columns=[TARGET, "mes", "gana_1_smmlv_o_mas", FEATURE_CONTRATO])
    resultado = predict.predecir(persona.iloc[0].to_dict())
    assert 0 <= resultado["probabilidad_cotizar"] <= 1
    assert resultado["cotiza"] in (0, 1)


def test_predecir_avisa_si_faltan_columnas(entrenado, monkeypatch):
    _, rutas = entrenado
    monkeypatch.setattr(predict, "MODEL_PATH", rutas["ruta_modelo"])
    monkeypatch.setattr(predict, "_pipeline", None)
    with pytest.raises(ValueError, match="Faltan columnas"):
        predict.predecir({"edad": 35})


def test_predecir_sin_modelo_da_un_error_claro(tmp_path, monkeypatch):
    monkeypatch.setattr(predict, "MODEL_PATH", tmp_path / "no_existe.joblib")
    monkeypatch.setattr(predict, "_pipeline", None)
    persona = {c: 1 for c in predict.FEATURES_NUM + predict.FEATURES_CAT}
    with pytest.raises(FileNotFoundError, match="make train"):
        predict.predecir(persona)
