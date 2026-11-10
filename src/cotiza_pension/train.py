"""Entrenamiento, evaluación y guardado del modelo final. Ejecutable desde la terminal:

    uv run python -m cotiza_pension.train      (o `make train`)

1. Entrena el modelo final (config.MODELO_FINAL) con enero–septiembre.
2. Lo evalúa una vez en octubre–diciembre (prueba).
3. Guarda el modelo en models/ y las métricas en reports/metricas_prueba.json.

El JSON se versiona en git: si un cambio mejora o empeora el modelo, se ve en el diff del PR.
"""

import json
import sys
from importlib.metadata import version
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    recall_score,
    roc_auc_score,
)

from .config import (
    COLUMNA_MES,
    HIPERPARAMETROS_FINALES,
    METRICAS_PATH,
    MODEL_PATH,
    MODELO_FINAL,
    UMBRAL,
    USAR_CONTRATO,
)
from .data import cargar, separar_temporal, separar_X_y
from .model import construir_pipeline_final

DECIMALES = 4
GRUPO_INTERES = "gana_1_smmlv_o_mas"


def _redondear(valor):
    return None if valor is None else round(float(valor), DECIMALES)


def _auc(y, p):
    """AUC, o None si solo hay una clase (el AUC no está definido)."""
    return roc_auc_score(y, p) if len(np.unique(y)) == 2 else None


def _metricas(y: np.ndarray, p: np.ndarray, umbral: float = UMBRAL) -> dict:
    """Métricas de un grupo de personas, a partir del objetivo real y la probabilidad."""
    prediccion = (p >= umbral).astype(int)
    hay_no_cotizantes = (y == 0).any()
    return {
        "personas": int(len(y)),
        "roc_auc": _redondear(_auc(y, p)),
        "pr_auc": _redondear(average_precision_score(y, p) if y.any() else None),
        "brier": _redondear(brier_score_loss(y, p)),
        "acierto": _redondear(accuracy_score(y, prediccion)),
        # De quienes NO cotizan, qué proporción detecta el modelo
        "no_cotizantes_detectados": _redondear(
            recall_score(y, prediccion, pos_label=0) if hay_no_cotizantes else None
        ),
    }


def evaluar(pipeline, prueba: pd.DataFrame, umbral: float = UMBRAL) -> dict:
    """Evalúa el pipeline en el conjunto de prueba: general, por mes y en el grupo de interés."""
    X, y = separar_X_y(prueba)
    y = y.to_numpy()
    p = pipeline.predict_proba(X)[:, 1]
    prediccion = (p >= umbral).astype(int)

    vn, fp, fn, vp = confusion_matrix(y, prediccion, labels=[0, 1]).ravel()
    meses = prueba[COLUMNA_MES].to_numpy()
    resultado = {
        "general": _metricas(y, p, umbral),
        "matriz_confusion": {
            "no_cotiza_predicho_no_cotiza": int(vn),
            "no_cotiza_predicho_cotiza": int(fp),
            "cotiza_predicho_no_cotiza": int(fn),
            "cotiza_predicho_cotiza": int(vp),
        },
        "roc_auc_por_mes": {
            str(mes): _redondear(_auc(y[meses == mes], p[meses == mes]))
            for mes in sorted(np.unique(meses))
        },
    }
    if GRUPO_INTERES in prueba.columns:
        en_grupo = (prueba[GRUPO_INTERES] == 1).to_numpy()
        resultado["gana_1_smmlv_o_mas"] = _metricas(y[en_grupo], p[en_grupo], umbral)
    return resultado


def entrenar(
    df: pd.DataFrame | None = None,
    guardar: bool = True,
    ruta_modelo: Path = MODEL_PATH,
    ruta_metricas: Path = METRICAS_PATH,
    verbose: bool = True,
) -> dict:
    """Entrena el modelo final con enero–septiembre, lo evalúa en octubre–diciembre y lo guarda.

    `df` permite entrenar con otros datos (por ejemplo, datos sintéticos en los tests);
    si no se pasa, se usa el dataset limpio de data/processed/.
    Devuelve el mismo dict de métricas que se guarda en el JSON.
    """
    if df is None:
        df = cargar()
    entrenamiento, prueba = separar_temporal(df)
    X_train, y_train = separar_X_y(entrenamiento)

    pipeline = construir_pipeline_final()
    pipeline.fit(X_train, y_train)

    metricas = {
        "modelo": MODELO_FINAL,
        "usar_contrato": USAR_CONTRATO,
        "hiperparametros": {
            k: _redondear(v) if isinstance(v, float) else v
            for k, v in HIPERPARAMETROS_FINALES.items()
        },
        "umbral": UMBRAL,
        "datos": {
            "filas_entrenamiento": int(len(entrenamiento)),
            "filas_prueba": int(len(prueba)),
            "meses_entrenamiento": sorted(int(m) for m in entrenamiento[COLUMNA_MES].unique()),
            "meses_prueba": sorted(int(m) for m in prueba[COLUMNA_MES].unique()),
        },
        "prueba": evaluar(pipeline, prueba),
        "versiones": {lib: version(lib) for lib in ("scikit-learn", "xgboost-cpu", "pandas")},
    }

    if guardar:
        ruta_modelo.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(pipeline, ruta_modelo)
        ruta_metricas.parent.mkdir(parents=True, exist_ok=True)
        ruta_metricas.write_text(
            json.dumps(metricas, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )

    if verbose:
        _imprimir_resumen(metricas, ruta_modelo if guardar else None, ruta_metricas)
    return metricas


def _imprimir_resumen(metricas: dict, ruta_modelo: Path | None, ruta_metricas: Path) -> None:
    datos, general = metricas["datos"], metricas["prueba"]["general"]
    print(f"Modelo: {metricas['modelo']} (usar_contrato={metricas['usar_contrato']})")
    print(f"Entrenamiento: {datos['filas_entrenamiento']:,} filas, ", end="")
    print(f"meses {datos['meses_entrenamiento']}")
    print(f"Prueba:        {datos['filas_prueba']:,} filas, meses {datos['meses_prueba']}")
    print()
    print("Prueba (octubre–diciembre):")
    for nombre in ("roc_auc", "pr_auc", "brier", "acierto", "no_cotizantes_detectados"):
        print(f"  {nombre:26s} {general[nombre]}")
    grupo = metricas["prueba"].get("gana_1_smmlv_o_mas")
    if grupo:
        print(f"Grupo que gana 1 SMMLV o más ({grupo['personas']:,} personas):")
        print(f"  {'roc_auc':26s} {grupo['roc_auc']}")
        print(f"  {'no_cotizantes_detectados':26s} {grupo['no_cotizantes_detectados']}")
    print()
    if ruta_modelo:
        print(f"Modelo guardado en:   {ruta_modelo}")
        print(f"Métricas guardadas en: {ruta_metricas}")


if __name__ == "__main__":
    # En Windows la terminal puede no usar UTF-8 y mostrar mal las tildes del resumen
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    entrenar()
