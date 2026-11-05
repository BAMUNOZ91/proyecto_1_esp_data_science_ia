"""Entrenamiento, evaluación y guardado del modelo. Ejecutable desde la terminal:

uv run python -m cotiza_pension.train
"""


def entrenar(tipo: str = "logistica", usar_contrato: bool = True, verbose: bool = True) -> dict:
    """Entrena el pipeline con enero–septiembre, evalúa en octubre–diciembre y guarda MODEL_PATH.

    Pasos: data.cargar() -> data.separar_temporal() -> data.separar_X_y()
           -> model.construir_pipeline().fit(entrenamiento) -> métricas en prueba -> joblib.dump

    Devuelve un dict con las métricas (AUC, matriz de confusión, métricas en el grupo que
    gana 1 SMMLV o más) para que el notebook y los tests las puedan revisar.
    """
    # TODO (paso 4): implementar
    raise NotImplementedError("Pendiente: entrenamiento")


if __name__ == "__main__":
    entrenar()
