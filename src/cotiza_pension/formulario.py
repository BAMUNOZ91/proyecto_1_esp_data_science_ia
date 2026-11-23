"""Opciones y textos del formulario de la app. La app solo dibuja; la lógica vive aquí.

Las opciones de las variables categóricas salen del modelo entrenado, y no de una lista
escrita a mano. Así la app ofrece exactamente los valores que el modelo vio al entrenar,
con el mismo formato (por ejemplo, el estrato llega como "1.0").
"""

import math

from .config import CODIGOS, FEATURES_CAT, FEATURES_NUM, SMMLV

# Divisiones (2 dígitos) de la CIIU Rev. 4 A.C. (2022), DANE:
# https://www.dane.gov.co/files/sen/nomenclatura/ciiu/Estructura-detallada-CIIU-4AC-2022.xlsx
# Se usa esta fuente porque RAMA2D_R4 no trae categorías en el diccionario de la GEIH 2025
# (catálogo 853 del DANE). Para que se lean bien en la app, los nombres oficiales de más de
# 45 caracteres se abrevian: se deja la actividad principal y se quitan los paréntesis y las
# excepciones. Los demás son el nombre oficial exacto.
NOMBRES_RAMA = {
    1: "Agricultura, ganadería y caza",
    2: "Silvicultura y extracción de madera",
    3: "Pesca y acuicultura",
    5: "Extracción de carbón de piedra y lignito",
    6: "Extracción de petróleo crudo y gas natural",
    7: "Extracción de minerales metalíferos",
    8: "Extracción de otras minas y canteras",
    9: "Servicios de apoyo a la minería",
    10: "Elaboración de productos alimenticios",
    11: "Elaboración de bebidas",
    12: "Elaboración de productos de tabaco",
    13: "Fabricación de productos textiles",
    14: "Confección de prendas de vestir",
    15: "Cuero, calzado y artículos de viaje",
    16: "Productos de madera, corcho y cestería",
    17: "Fabricación de papel y cartón",
    18: "Impresión y copia de grabaciones",
    19: "Refinación de petróleo y coquización",
    20: "Fabricación de productos químicos",
    21: "Fabricación de productos farmacéuticos",
    22: "Fabricación de productos de caucho y plástico",
    23: "Fabricación de minerales no metálicos",
    24: "Fabricación de productos metalúrgicos básicos",
    25: "Fabricación de productos de metal",
    26: "Fabricación de productos electrónicos",
    27: "Fabricación de aparatos y equipo eléctrico",
    28: "Fabricación de maquinaria y equipo n.c.p.",
    29: "Fabricación de vehículos automotores",
    30: "Fabricación de otro equipo de transporte",
    31: "Fabricación de muebles, colchones y somieres",
    32: "Otras industrias manufactureras",
    33: "Instalación y reparación de maquinaria",
    35: "Suministro de electricidad, gas y vapor",
    36: "Captación, tratamiento y distribución de agua",
    37: "Evacuación y tratamiento de aguas residuales",
    38: "Recolección y tratamiento de desechos",
    39: "Saneamiento ambiental",
    41: "Construcción de edificios",
    42: "Obras de ingeniería civil",
    43: "Actividades especializadas de construcción",
    45: "Comercio y reparación de vehículos",
    46: "Comercio al por mayor",
    47: "Comercio al por menor",
    49: "Transporte terrestre; transporte por tuberías",
    50: "Transporte acuático",
    51: "Transporte aéreo",
    52: "Almacenamiento y apoyo al transporte",
    53: "Correo y servicios de mensajería",
    55: "Alojamiento",
    56: "Actividades de servicios de comidas y bebidas",
    58: "Actividades de edición",
    59: "Cine, televisión, sonido y música",
    60: "Programación, transmisión y difusión",
    61: "Telecomunicaciones",
    62: "Desarrollo de software e informática",
    63: "Actividades de servicios de información",
    64: "Servicios financieros, excepto seguros",
    65: "Seguros y fondos de pensiones",
    66: "Actividades auxiliares financieras",
    68: "Actividades inmobiliarias",
    69: "Actividades jurídicas y de contabilidad",
    70: "Administración empresarial y consultoría",
    71: "Arquitectura, ingeniería y ensayos técnicos",
    72: "Investigación científica y desarrollo",
    73: "Publicidad y estudios de mercado",
    74: "Otras actividades profesionales y técnicas",
    75: "Actividades veterinarias",
    77: "Actividades de alquiler y arrendamiento",
    78: "Actividades de empleo",
    79: "Agencias de viajes y operadores turísticos",
    80: "Seguridad e investigación privada",
    81: "Servicios a edificios y paisajismo",
    82: "Apoyo administrativo a las empresas",
    84: "Administración pública y defensa",
    85: "Educación",
    86: "Actividades de atención de la salud humana",
    87: "Atención residencial medicalizada",
    88: "Asistencia social sin alojamiento",
    90: "Actividades artísticas y de entretenimiento",
    91: "Bibliotecas, archivos y museos",
    92: "Actividades de juegos de azar y apuestas",
    93: "Actividades deportivas y recreativas",
    94: "Actividades de asociaciones",
    95: "Reparación de computadores y enseres",
    96: "Otras actividades de servicios personales",
    97: "Hogares empleadores de servicio doméstico",
    98: "Hogares productores para uso propio",
    99: "Organizaciones extraterritoriales",
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
        if columna == "rama_2d":
            # Se ocultan los códigos que no existen en la CIIU (en los datos, solo el 0, con 6
            # personas). El modelo los sigue conociendo; solo no se ofrecen en el formulario.
            valores = [v for v in valores if _codigo(v) in NOMBRES_RAMA]
        opciones[columna] = valores
    return opciones


def etiqueta(columna: str, valor) -> str:
    """Texto que ve la persona para un valor del modelo."""
    if es_nulo(valor):
        return NO_INFORMA
    codigo = _codigo(valor)
    if columna == "rama_2d" and codigo is not None:
        return f"{codigo} - {NOMBRES_RAMA.get(codigo, 'Código sin nombre en la CIIU')}"
    if columna == "estrato" and codigo is not None:
        return NOMBRES_ESTRATO.get(codigo, f"Estrato {codigo}")
    if columna == "lugar_trabajo" and codigo is not None:
        return NOMBRES_LUGAR.get(codigo, f"Código {codigo}")
    return str(valor)


def texto_ingreso(pesos: float) -> str:
    """Ingreso con punto de miles y en salarios mínimos, p. ej. "$1.423.500 (1,00 SMMLV)"."""
    en_pesos = f"{pesos:,.0f}".replace(",", ".")
    en_smmlv = f"{pesos / SMMLV:.2f}".replace(".", ",")
    return f"${en_pesos} ({en_smmlv} SMMLV)"


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
