"""Datos: descarga de la GEIH, limpieza, carga y split temporal.

Ejecutable desde la terminal (descarga, limpia y guarda en data/processed/):

    uv run python -m cotiza_pension.data
"""

import pandas as pd

from .config import (
    ANIO,
    CODIGOS,
    COLUMNA_MES,
    FEATURE_CONTRATO,
    FEATURES_CAT,
    FEATURES_NUM,
    MESES_ENTRENAMIENTO,
    MESES_PRUEBA,
    PROCESSED_PATH,
    RAW_DIR,
    RAW_PATH,
    RENOMBRAR,
    SMMLV,
    TARGET,
    USAR_CONTRATO,
    VARIABLES_DANE,
)


def descargar() -> pd.DataFrame:
    """Descarga la GEIH 2025 con `dane_data`, deja solo ocupados y guarda RAW_PATH.

    Devuelve el DataFrame crudo (códigos originales del DANE, VARIABLES_DANE). Se detiene
    si falta un mes o una variable, para no generar un dataset incompleto sin avisar.
    """
    import dane_data as dd  # se importa aquí porque solo hace falta al descargar

    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    dd.set_paths(geih=str(RAW_DIR / "geih"))

    fallidos = dd.geih.download(ANIO)
    if fallidos:
        raise RuntimeError(f"No se pudo descargar: {fallidos}")

    df = dd.geih.load(ANIO, months=None, columns=VARIABLES_DANE, harmonize_vars=False)
    columnas = ["anio", "mes", *VARIABLES_DANE]
    faltan = [c for c in columnas if c not in df.columns]
    if faltan:
        raise RuntimeError(f"No vinieron estas variables: {faltan}")

    df = df.loc[df["OCI"] == 1, columnas]  # solo ocupados
    df.to_csv(RAW_PATH, index=False, encoding="utf-8")
    return df


def limpiar(df_crudo: pd.DataFrame) -> pd.DataFrame:
    """Aplica la limpieza de la sección 4 del EDA y devuelve el dataset listo para modelar.

    Quita MES y OCI, renombra con RENOMBRAR, excluye pensionados (P6920 = 3), deja el
    objetivo en 1/0, traduce códigos a texto y calcula `ingreso_smmlv` y
    `gana_1_smmlv_o_mas`.
    """
    df = df_crudo.drop(columns=["MES", "OCI"])
    df.columns = df.columns.str.lower()
    df = df.rename(columns=RENOMBRAR)

    df = df[df[TARGET] != 3].copy()
    df[TARGET] = df[TARGET].map({1: 1, 2: 0})

    for columna, codigos in CODIGOS.items():
        df[columna] = df[columna].map(codigos)
    df["parentesco_jefe"] = df["parentesco_jefe"].fillna("Otro")

    df["ingreso_smmlv"] = df["ingreso"] / SMMLV
    df["gana_1_smmlv_o_mas"] = (df["ingreso_smmlv"] >= 1).astype(float).where(df["ingreso"].notna())
    return df


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


def separar_X_y(
    df: pd.DataFrame, usar_contrato: bool = USAR_CONTRATO
) -> tuple[pd.DataFrame, pd.Series]:
    """Separa features (X) y objetivo (y). Solo deja las columnas declaradas en config.

    Por defecto sigue la decisión del modelo final (config.USAR_CONTRATO).
    """
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
