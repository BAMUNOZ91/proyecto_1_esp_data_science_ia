"""Probabilidad de que un trabajador colombiano cotice a pensión.

Datos: Gran Encuesta Integrada de Hogares (GEIH) 2025 del DANE, módulo de ocupados.

Módulos:
    config    rutas, variables, features, split temporal e hiperparámetros
    data      descarga, limpieza, carga y split temporal
    features  pipeline de preprocesamiento (sin fuga: se ajusta solo con entrenamiento)
    model     preprocesador + clasificador en un solo Pipeline
    train     entrenamiento, evaluación y guardado del modelo
    predict   carga del modelo y predicción para una persona
"""
