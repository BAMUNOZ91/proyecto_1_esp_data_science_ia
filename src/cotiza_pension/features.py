"""Pipeline de preprocesamiento. Separa el "qué hacer con las features" del "qué modelo usar".

Todo se ajusta con `fit` solo sobre entrenamiento, dentro del Pipeline: así no hay fuga.
"""

from sklearn.compose import ColumnTransformer


def construir_preprocesador(usar_contrato: bool = True) -> ColumnTransformer:
    """Devuelve el ColumnTransformer con las transformaciones de la sección 9 del EDA.

    Numéricas:
        - ingreso_smmlv: imputar (mediana) + marca de "ingreso no reportado" + log(1 + x)
        - horas_semana y meses_en_empresa: recortar en el percentil 99 de entrenamiento
        - edad: tramos o edad² (la relación con el objetivo tiene forma de montaña)
        - escalar (para la regresión logística)
    Categóricas:
        - estrato 0 / 9 / nulo -> "Sin estrato / no informa"
        - ramas con pocos casos -> "Otra"
        - OneHotEncoder(handle_unknown="ignore")
    """
    # TODO (paso 3): implementar
    raise NotImplementedError("Pendiente: construir el preprocesador")
