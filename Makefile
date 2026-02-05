.PHONY: help install test clean

VENV := .venv

help:
	@echo "Available targets:"
	@echo "  make install  - Create venv and install dependencies"
	@echo "  make test     - Run tests"
	@echo "  make clean    - Remove venv"

$(VENV)/pyvenv.cfg:
	python3 -m venv $(VENV)

install: $(VENV)/pyvenv.cfg
	$(VENV)/bin/pip install -qU pip
	$(VENV)/bin/pip install -qr requirements.txt

test:
	$(VENV)/bin/python -m pytest tests/

clean:
	rm -rf $(VENV)
