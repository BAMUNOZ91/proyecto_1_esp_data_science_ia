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
REPORTS_DIR = PROJECT_DIR / "reports"

RAW_PATH = RAW_DIR / "geih_2025_ocupados_crudo.csv"
PROCESSED_PATH = PROCESSED_DIR / "geih_2025_ocupados_limpio.csv"
MODEL_PATH = MODELS_DIR / "modelo_cotiza_pension.joblib"
# Se versiona en git: el diff de cada PR muestra si el modelo mejora o empeora
METRICAS_PATH = REPORTS_DIR / "metricas_prueba.json"

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

# Código del DANE -> valor legible, por columna. Ver secciones 3 y 4 del EDA.
CODIGOS = {
    "sexo": {1: "Hombre", 2: "Mujer"},
    "zona": {1: "Urbano", 2: "Rural"},
    "estado_civil": {
        1: "Unión libre menos de 2 años",
        2: "Unión libre 2 años o más",
        3: "Casado(a)",
        4: "Separado(a) o divorciado(a)",
        5: "Viudo(a)",
        6: "Soltero(a)",
    },
    "nivel_educativo": {
        1: "Ninguno",
        2: "Preescolar",
        3: "Básica primaria",
        4: "Básica secundaria",
        5: "Media académica",
        6: "Media técnica",
        7: "Normalista",
        8: "Técnica profesional",
        9: "Tecnológica",
        10: "Universitaria",
        11: "Especialización",
        12: "Maestría",
        13: "Doctorado",
        99: "No sabe",
    },
    "posicion_ocupacional": {
        1: "Empleado empresa particular",
        2: "Empleado del gobierno",
        3: "Empleado doméstico",
        4: "Cuenta propia",
        5: "Patrón o empleador",
        6: "Familiar sin remuneración",
        7: "Jornalero o peón",
        8: "Otro",
    },
    "tamano_empresa": {
        1: "Trabaja solo",
        2: "2 a 3",
        3: "4 a 5",
        4: "6 a 10",
        5: "11 a 19",
        6: "20 a 30",
        7: "31 a 50",
        8: "51 a 100",
        9: "101 a 200",
        10: "201 o más",
    },
    "parentesco_jefe": {1: "Jefe(a) del hogar", 2: "Pareja del jefe(a)", 3: "Hijo(a)"},
    "tiene_contrato": {1: 1, 2: 0},
    "departamento": {
        5: "Antioquia",
        8: "Atlántico",
        11: "Bogotá D.C.",
        13: "Bolívar",
        15: "Boyacá",
        17: "Caldas",
        18: "Caquetá",
        19: "Cauca",
        20: "Cesar",
        23: "Córdoba",
        25: "Cundinamarca",
        27: "Chocó",
        41: "Huila",
        44: "La Guajira",
        47: "Magdalena",
        50: "Meta",
        52: "Nariño",
        54: "Norte de Santander",
        63: "Quindío",
        66: "Risaralda",
        68: "Santander",
        70: "Sucre",
        73: "Tolima",
        76: "Valle del Cauca",
        81: "Arauca",
        85: "Casanare",
        86: "Putumayo",
        88: "San Andrés",
        91: "Amazonas",
        94: "Guainía",
        95: "Guaviare",
        97: "Vaupés",
        99: "Vichada",
    },
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
# Opcional: en los datos equivale casi a "es asalariado" (EDA, sección 8.4) y no mejoró
# ningún modelo (notebook 02). El modelo final no la usa: ver USAR_CONTRATO.
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

# Modelo final elegido en notebooks/02_seleccion_modelos.ipynb: mejor AUC (0,9829) y Brier
# (0,0477) en la validación temporal por meses. HistGradientBoosting quedó casi empatado.
MODELO_FINAL = "xgboost"
USAR_CONTRATO = False

# Mejor combinación de RandomizedSearchCV (20 combinaciones, random_state=42, cv por meses)
HIPERPARAMETROS_FINALES = {
    "n_estimators": 755,
    "learning_rate": 0.026613431317616388,
    "max_depth": 6,
    "min_child_weight": 23.196088229293604,
    "subsample": 0.9533121035675474,
    "colsample_bytree": 0.7182534743350856,
    "reg_lambda": 0.6808005465661973,
}

# Probabilidad a partir de la cual se predice "cotiza"
UMBRAL = 0.5
