"""Opciones y textos del formulario de la app. La app solo dibuja; la lógica vive aquí.

Las opciones de las variables categóricas salen del modelo entrenado, y no de una lista
escrita a mano. Así la app ofrece exactamente los valores que el modelo vio al entrenar,
con el mismo formato (por ejemplo, el estrato llega como "1.0").
"""

import math

from .config import CODIGOS, FEATURES_CAT, FEATURES_NUM, SMMLV

# Nombres de las 15 ramas con más ocupados (EDA, sección 8.3). Las demás se muestran con
# su código CIIU Rev. 4 a dos dígitos.
NOMBRES_RAMA = {
    1: "Agricultura y ganadería",
    10: "Elaboración de alimentos",
    14: "Confección de prendas",
    41: "Construcción de edificios",
    45: "Comercio y reparación de vehículos",
    46: "Comercio al por mayor",
    47: "Comercio al por menor",
    49: "Transporte terrestre",
    56: "Restaurantes y comidas",
    81: "Servicios a edificios",
    84: "Administración pública",
    85: "Educación",
    86: "Salud humana",
    96: "Otros servicios personales",
    97: "Hogares con servicio doméstico",
}

# P6880 y P4030S1A1 según el diccionario oficial de la GEIH 2025 (catálogo 853 del DANE)
NOMBRES_LUGAR = {
    1: "En esta vivienda",
    2: "En otras viviendas",
    3: "En kiosco o caseta",
    4: "En un vehículo",
    5: "De puerta en puerta",
    6: "Sitio al descubierto en la calle",
    7: "Local fijo, oficina o fábrica",
    8: "En el campo o área rural, mar o río",
    9: "En una obra en construcción",
    10: "En una mina o cantera",
    11: "Otro",
}
NOMBRES_ESTRATO = {0: "Conexión pirata", 9: "No sabe o tiene planta eléctrica"}

# Textos que ve la persona para cada variable
ROTULOS = {
    "edad": "Edad (años)",
    "horas_semana": "Horas trabajadas a la semana",
    "meses_en_empresa": "Meses en la empresa o negocio",
    "ingreso_smmlv": "Ingreso laboral mensual (pesos)",
    "departamento": "Departamento",
    "zona": "Zona",
    "sexo": "Sexo",
    "parentesco_jefe": "Parentesco con el jefe(a) del hogar",
    "estado_civil": "Estado civil",
    "nivel_educativo": "Nivel educativo más alto alcanzado",
    "posicion_ocupacional": "Posición ocupacional",
    "tamano_empresa": "Personas en la empresa o negocio",
    "lugar_trabajo": "Lugar donde trabaja principalmente",
    "rama_2d": "Rama de actividad",
    "estrato": "Estrato de la vivienda",
}

NO_INFORMA = "No informa"


def es_nulo(valor) -> bool:
    """True para los nulos que guarda el modelo (NaN o None)."""
    return valor is None or (isinstance(valor, float) and math.isnan(valor))


def _codigo(valor) -> int | None:
    """Convierte "47.0" o 47.0 en 47. Devuelve None si no es un número."""
    try:
        return int(float(valor))
    except (TypeError, ValueError):
        return None


def opciones_categoricas(pipeline) -> dict[str, list]:
    """Valores que el modelo conoce para cada variable categórica, en un orden legible."""
    codificador = pipeline.named_steps["preprocesador"].named_transformers_["cat"][-1]
    opciones = {}
    for columna, valores in zip(FEATURES_CAT, codificador.categories_, strict=True):
        valores = list(valores)
        orden = list(CODIGOS.get(columna, {}).values())
        if orden:
            valores.sort(key=lambda v: orden.index(v) if v in orden else len(orden))
        elif all(_codigo(v) is not None for v in valores if not es_nulo(v)):
            valores.sort(key=lambda v: math.inf if es_nulo(v) else _codigo(v))
        else:
            valores.sort(key=lambda v: (es_nulo(v), str(v)))
        opciones[columna] = valores
    return opciones


def etiqueta(columna: str, valor) -> str:
    """Texto que ve la persona para un valor del modelo."""
    if es_nulo(valor):
        return NO_INFORMA
    codigo = _codigo(valor)
    if columna == "rama_2d" and codigo is not None:
        return f"{codigo} - {NOMBRES_RAMA.get(codigo, 'Otra rama (CIIU)')}"
    if columna == "estrato" and codigo is not None:
        return NOMBRES_ESTRATO.get(codigo, f"Estrato {codigo}")
    if columna == "lugar_trabajo" and codigo is not None:
        return NOMBRES_LUGAR.get(codigo, f"Código {codigo}")
    return str(valor)


def armar_datos(numericas: dict, categoricas: dict, ingreso_pesos: float | None) -> dict:
    """Junta lo que llenó la persona en el formato que espera `predict.predecir`.

    El ingreso se pide en pesos y se pasa a salarios mínimos. Si no se reporta, queda nulo,
    igual que en los datos (el modelo maneja los nulos).
    """
    datos = {**numericas, **categoricas}
    datos["ingreso_smmlv"] = math.nan if ingreso_pesos is None else ingreso_pesos / SMMLV
    faltan = [c for c in FEATURES_NUM + FEATURES_CAT if c not in datos]
    if faltan:
        raise ValueError(f"Faltan campos del formulario: {faltan}")
    return datos
