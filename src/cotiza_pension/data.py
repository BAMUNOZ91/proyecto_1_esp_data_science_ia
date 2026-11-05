"""Datos: descarga de la GEIH, limpieza, carga y split temporal.

Ejecutable desde la terminal (descarga, limpia y guarda en data/processed/):

    uv run python -m cotiza_pension.data
"""

import pandas as pd

from .config import (
    COLUMNA_MES,
    FEATURE_CONTRATO,
    FEATURES_CAT,
    FEATURES_NUM,
    MESES_ENTRENAMIENTO,
    MESES_PRUEBA,
    PROCESSED_PATH,
    RAW_PATH,
    TARGET,
)


def descargar() -> pd.DataFrame:
    """Descarga la GEIH 2025 con `dane_data`, deja solo ocupados y guarda RAW_PATH.

    Devuelve el DataFrame crudo (códigos originales del DANE, VARIABLES_DANE).
    """
    # TODO (paso 3): migrar desde notebooks/generacion_dataset_DANE_geih.ipynb
    raise NotImplementedError("Pendiente: migrar desde generacion_dataset_DANE_geih.ipynb")


def limpiar(df_crudo: pd.DataFrame) -> pd.DataFrame:
    """Aplica la limpieza de la sección 4 del EDA y devuelve el dataset listo para modelar.

    Quita MES y OCI, renombra con RENOMBRAR, excluye pensionados (P6920 = 3), deja el
    objetivo en 1/0, traduce códigos a texto y calcula `ingreso_smmlv` y
    `gana_1_smmlv_o_mas`.
    """
    # TODO (paso 3): migrar desde notebooks/01_preparacion_eda.ipynb, sección 4
    raise NotImplementedError("Pendiente: migrar desde 01_preparacion_eda.ipynb, sección 4")


def cargar() -> pd.DataFrame:
    """Lee el dataset limpio de PROCESSED_PATH. Si no existe, pide correr `make data`."""
    if not PROCESSED_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró {PROCESSED_PATH}. Genéralo con `make data` "
            "(o `uv run python -m cotiza_pension.data`)."
        )
    return pd.read_csv(PROCESSED_PATH)


def separar_temporal(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split temporal: enero–septiembre para entrenamiento, octubre–diciembre para prueba.

    Se hace ANTES de cualquier preprocesamiento para que no haya fuga de información.
    """
    entrenamiento = df[df[COLUMNA_MES].isin(MESES_ENTRENAMIENTO)].copy()
    prueba = df[df[COLUMNA_MES].isin(MESES_PRUEBA)].copy()
    return entrenamiento, prueba


def separar_X_y(df: pd.DataFrame, usar_contrato: bool = True) -> tuple[pd.DataFrame, pd.Series]:
    """Separa features (X) y objetivo (y). Solo deja las columnas declaradas en config."""
    columnas = FEATURES_NUM + FEATURES_CAT + ([FEATURE_CONTRATO] if usar_contrato else [])
    return df[columnas].copy(), df[TARGET].copy()


def main() -> None:
    """Descarga, limpia y guarda el dataset procesado."""
    df_crudo = pd.read_csv(RAW_PATH) if RAW_PATH.exists() else descargar()
    df = limpiar(df_crudo)
    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_PATH, index=False, encoding="utf-8")
    print(f"Dataset limpio: {len(df):,} filas -> {PROCESSED_PATH}")


if __name__ == "__main__":
    main()
