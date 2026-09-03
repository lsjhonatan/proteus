.PHONY: build install clean test

PYTHON = python3
PIP = pip3

build:
	$(PYTHON) setup.py build_ext --inplace

install: build
	sudo $(PIP) install -e . --break-system-packages

clean:
	sudo rm -rf build/ dist/ *.egg-info
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	sudo rm -rf src/pts/modules/*.so

test:
	$(PYTHON) -m pytest tests/ -v
