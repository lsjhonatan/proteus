.PHONY: build install clean test

PYTHON = python3

build:
	$(PYTHON) setup.py build_ext --inplace

install: build
	$(PYTHON) setup.py install --skip-build

clean:
	rm -rf build/ dist/ *.egg-info
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	rm -rf src/pts/modules/*.so

test:
	$(PYTHON) -m pytest tests/ -v
