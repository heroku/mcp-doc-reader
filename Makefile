.PHONY: install test clean

VENV := .venv

$(VENV)/pyvenv.cfg:
	python3 -m venv $(VENV)

install: $(VENV)/pyvenv.cfg
	$(VENV)/bin/pip install -qU pip
	$(VENV)/bin/pip install -qr requirements.txt

test: $(VENV)/pyvenv.cfg
	$(VENV)/bin/python -m pytest tests/

clean:
	rm -rf $(VENV)
