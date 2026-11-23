"""Opciones y textos del formulario de la app. La app solo dibuja; la lógica vive aquí.

Las opciones de las variables categóricas salen del modelo entrenado, y no de una lista
escrita a mano. Así la app ofrece exactamente los valores que el modelo vio al entrenar,
con el mismo formato (por ejemplo, el estrato llega como "1.0").
"""

import math

from .config import CODIGOS, FEATURES_CAT, FEATURES_NUM, SMMLV

# Nombres oficiales de las divisiones (2 dígitos) de la CIIU Rev. 4 A.C. (2022), DANE:
# https://www.dane.gov.co/files/sen/nomenclatura/ciiu/Estructura-detallada-CIIU-4AC-2022.xlsx
# Se usa esta fuente porque RAMA2D_R4 no trae categorías en el diccionario de la GEIH 2025
# (catálogo 853 del DANE).
NOMBRES_RAMA = {
    1: "Agricultura, ganadería, caza y actividades de servicios conexas",
    2: "Silvicultura y extracción de madera",
    3: "Pesca y acuicultura",
    5: "Extracción de carbón de piedra y lignito",
    6: "Extracción de petróleo crudo y gas natural",
    7: "Extracción de minerales metalíferos",
    8: "Extracción de otras minas y canteras",
    9: "Actividades de servicios de apoyo para la explotación de minas y canteras",
    10: "Elaboración de productos alimenticios",
    11: "Elaboración de bebidas",
    12: "Elaboración de productos de tabaco",
    13: "Fabricación de productos textiles",
    14: "Confección de prendas de vestir",
    15: (
        "Curtido y recurtido de cueros; fabricación de calzado; fabricación de artículos de viaje, "
        "maletas, bolsos de mano y artículos similares, y fabricación de artículos de talabartería "
        "y guarnicionería; adobo y teñido de pieles"
    ),
    16: (
        "Transformación de la madera y fabricación de productos de madera y de corcho, excepto "
        "muebles; fabricación de artículos de cestería y espartería"
    ),
    17: "Fabricación de papel, cartón y productos de papel y cartón",
    18: "Actividades de impresión y de producción de copias a partir de grabaciones originales",
    19: (
        "Coquización, fabricación de productos de la refinación del petróleo y actividad de mezcla "
        "de combustibles"
    ),
    20: "Fabricación de sustancias y productos químicos",
    21: (
        "Fabricación de productos farmacéuticos, sustancias químicas medicinales y productos "
        "botánicos de uso farmacéutico"
    ),
    22: "Fabricación de productos de caucho y de plástico",
    23: "Fabricación de otros productos minerales no metálicos",
    24: "Fabricación de productos metalúrgicos básicos",
    25: "Fabricación de productos elaborados de metal, excepto maquinaria y equipo",
    26: "Fabricación de productos informáticos, electrónicos y ópticos",
    27: "Fabricación de aparatos y equipo eléctrico",
    28: "Fabricación de maquinaria y equipo n.c.p.",
    29: "Fabricación de vehículos automotores, remolques y semirremolques",
    30: "Fabricación de otros tipos de equipo de transporte",
    31: "Fabricación de muebles, colchones y somieres",
    32: "Otras industrias manufactureras",
    33: "Instalación, mantenimiento y reparación especializado de maquinaria y equipo",
    35: "Suministro de electricidad, gas, vapor y aire acondicionado",
    36: "Captación, tratamiento y distribución de agua",
    37: "Evacuación y tratamiento de aguas residuales",
    38: "Recolección, tratamiento y disposición de desechos, recuperación de materiales",
    39: "Actividades de saneamiento ambiental y otros servicios de gestión de desechos",
    41: "Construcción de edificios",
    42: "Obras de ingeniería civil",
    43: "Actividades especializadas para la construcción de edificios y obras de ingeniería civil",
    45: (
        "Comercio, mantenimiento y reparación de vehículos automotores y motocicletas, sus partes, "
        "piezas y accesorios"
    ),
    46: (
        "Comercio al por mayor y en comisión o por contrata, excepto el comercio de vehículos "
        "automotores y motocicletas"
    ),
    47: (
        "Comercio al por menor (incluso el comercio al por menor de combustibles), excepto el de "
        "vehículos automotores y motocicletas"
    ),
    49: "Transporte terrestre; transporte por tuberías",
    50: "Transporte acuático",
    51: "Transporte aéreo",
    52: "Almacenamiento y actividades complementarias al transporte",
    53: "Correo y servicios de mensajería",
    55: "Alojamiento",
    56: "Actividades de servicios de comidas y bebidas",
    58: "Actividades de edición",
    59: (
        "Actividades cinematográficas, de video y producción de programas de televisión, grabación "
        "de sonido y edición de música"
    ),
    60: "Actividades de programación, transmisión y/o difusión",
    61: "Telecomunicaciones",
    62: (
        "Desarrollo de sistemas informáticos (planificación, análisis, diseño, programación, "
        "pruebas), consultoría informática y actividades relacionadas"
    ),
    63: "Actividades de servicios de información",
    64: "Actividades de servicios financieros, excepto las de seguros y de pensiones",
    65: (
        "Seguros (incluso el reaseguro), seguros sociales y fondos de pensiones, excepto la "
        "seguridad social"
    ),
    66: "Actividades auxiliares de las actividades de servicios financieros",
    68: "Actividades inmobiliarias",
    69: "Actividades jurídicas y de contabilidad",
    70: "Actividades de administración empresarial; actividades de consultoría de gestión",
    71: "Actividades de arquitectura e ingeniería; ensayos y análisis técnicos",
    72: "Investigación científica y desarrollo",
    73: "Publicidad y estudios de mercado",
    74: "Otras actividades profesionales, científicas y técnicas",
    75: "Actividades veterinarias",
    77: "Actividades de alquiler y arrendamiento",
    78: "Actividades de empleo",
    79: (
        "Actividades de las agencias de viajes, operadores turísticos, servicios de reserva y "
        "actividades relacionadas"
    ),
    80: "Actividades de seguridad e investigación privada",
    81: "Actividades de servicios a edificios y paisajismo (jardines, zonas verdes)",
    82: (
        "Actividades administrativas y de apoyo de oficina y otras actividades de apoyo a las "
        "empresas"
    ),
    84: "Administración pública y defensa; planes de seguridad social de afiliación obligatoria",
    85: "Educación",
    86: "Actividades de atención de la salud humana",
    87: "Actividades de atención residencial medicalizada",
    88: "Actividades de asistencia social sin alojamiento",
    90: "Actividades creativas, artísticas y de entretenimiento",
    91: "Actividades de bibliotecas, archivos, museos y otras actividades culturales",
    92: "Actividades de juegos de azar y apuestas",
    93: "Actividades deportivas y actividades recreativas y de esparcimiento",
    94: "Actividades de asociaciones",
    95: "Mantenimiento y reparación de computadores, efectos personales y enseres domésticos",
    96: "Otras actividades de servicios personales",
    97: "Actividades de los hogares individuales como empleadores de personal doméstico",
    98: (
        "Actividades no diferenciadas de los hogares individuales como productores de bienes y "
        "servicios para uso propio"
    ),
    99: "Actividades de organizaciones y entidades extraterritoriales",
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
        return f"{codigo} - {NOMBRES_RAMA.get(codigo, 'Código sin nombre en la CIIU')}"
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
