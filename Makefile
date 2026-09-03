.PHONY: help build test clean install lint format

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Compila módulos C e empacota
	python3 setup.py build_ext --inplace
	python3 -m build

test: ## Executa testes
	python3 -m pytest tests/ -v --cov=src/pts

lint: ## Executa linters
	flake8 src/pts tests/
	mypy src/pts

format: ## Formata código
	black src/pts tests/

clean: ## Limpa artefatos
	rm -rf build/ dist/ *.egg-info
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

install: build ## Instala localmente
	pip install -e .
