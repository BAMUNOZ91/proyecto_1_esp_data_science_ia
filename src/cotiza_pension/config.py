"""Constantes del proyecto: un solo lugar para rutas, variables y decisiones de modelado.

Las decisiones vienen del EDA (notebooks/01_preparacion_eda.ipynb, secciones 3, 5, 8 y 9).
"""

from pathlib import Path

# --- Rutas -------------------------------------------------------------------
PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_DIR / "models"

RAW_PATH = RAW_DIR / "geih_2025_ocupados_crudo.csv"
PROCESSED_PATH = PROCESSED_DIR / "geih_2025_ocupados_limpio.csv"
MODEL_PATH = MODELS_DIR / "modelo_cotiza_pension.joblib"

# --- Fuente ------------------------------------------------------------------
ANIO = 2025
SMMLV = 1_423_500  # salario mínimo mensual 2025

# Variables del DANE que se descargan (códigos originales)
VARIABLES_DANE = [
    # llaves y diseño muestral
    "DIRECTORIO", "SECUENCIA_P", "ORDEN", "HOGAR", "MES", "DPTO", "CLASE", "FEX_C18",
    # persona
    "P6040", "P3271", "P6050", "P6070", "P3042",
    # empleo (módulo ocupados)
    "OCI", "P6920", "P6430", "P3069", "P6880", "P6800", "P6426", "P6440", "INGLABO", "RAMA2D_R4",
    # vivienda
    "P4030S1A1",
]  # fmt: skip

# Código DANE (en minúscula) -> nombre claro. Ver diccionario en la sección 3 del EDA.
RENOMBRAR = {
    "dpto": "departamento",
    "clase": "zona",
    "fex_c18": "factor_expansion",
    "p6040": "edad",
    "p3271": "sexo",
    "p6050": "parentesco_jefe",
    "p6070": "estado_civil",
    "p3042": "nivel_educativo",
    "p6920": "cotiza_pension",
    "p6430": "posicion_ocupacional",
    "p3069": "tamano_empresa",
    "p6880": "lugar_trabajo",
    "p6800": "horas_semana",
    "p6426": "meses_en_empresa",
    "p6440": "tiene_contrato",
    "inglabo": "ingreso",
    "rama2d_r4": "rama_2d",
    "p4030s1a1": "estrato",
}

# --- Variable objetivo y features -------------------------------------------
TARGET = "cotiza_pension"  # 1 = cotiza, 0 = no cotiza (pensionados excluidos)

FEATURES_NUM = ["edad", "horas_semana", "meses_en_empresa", "ingreso_smmlv"]
FEATURES_CAT = [
    "departamento",
    "zona",
    "sexo",
    "parentesco_jefe",
    "estado_civil",
    "nivel_educativo",
    "posicion_ocupacional",
    "tamano_empresa",
    "lugar_trabajo",
    "rama_2d",
    "estrato",
]
# Se prueba con y sin ella: en los datos equivale casi a "es asalariado" (EDA, sección 8.4)
FEATURE_CONTRATO = "tiene_contrato"

# Nunca entran al modelo: identificadores, constantes, diseño muestral o derivadas del ingreso
NO_SON_FEATURES = [
    "anio", "mes", "directorio", "secuencia_p", "orden", "hogar",
    "factor_expansion", "ingreso", "gana_1_smmlv_o_mas",
]  # fmt: skip

# --- Split temporal ----------------------------------------------------------
COLUMNA_MES = "mes"
MESES_ENTRENAMIENTO = list(range(1, 10))  # enero a septiembre
MESES_PRUEBA = [10, 11, 12]  # octubre a diciembre

# --- Modelado ----------------------------------------------------------------
SEMILLA = 42
