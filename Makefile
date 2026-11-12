# Comandos del proyecto. Corre `make` sin argumentos para ver la ayuda.

.DEFAULT_GOAL := help
.PHONY: help setup data train app test lint format clean

help:  ## Lista los comandos disponibles.
	@echo "Comandos del proyecto cotiza-pension:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'
	@echo ""

setup:  ## Crea el entorno .venv e instala las dependencias (incluye las de desarrollo).
	uv sync

DATOS := data/processed/geih_2025_ocupados_limpio.csv

data:  ## Descarga la GEIH 2025 del DANE y genera data/processed/ (la primera vez tarda).
	uv run python -m cotiza_pension.data

# Si no existe el dataset limpio, `make train` lo genera primero
$(DATOS):
	uv run python -m cotiza_pension.data

train: $(DATOS)  ## Entrena el modelo final (si faltan los datos, los descarga primero).
	uv run python -m cotiza_pension.train

app:  ## Abre la app de predicción en el navegador (requiere `make train`).
	uv run streamlit run app/app.py

test:  ## Corre las pruebas automatizadas.
	uv run pytest

lint:  ## Revisa el estilo del código con ruff.
	uv run ruff check src tests

format:  ## Formatea el código con ruff.
	uv run ruff format src tests
	uv run ruff check --fix src tests

clean:  ## Borra caches y el modelo entrenado.
	find . -type d \( -name "__pycache__" -o -name ".pytest_cache" -o -name ".ruff_cache" \) -prune -exec rm -rf {} +
	rm -f models/*.joblib
