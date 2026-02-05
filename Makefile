.PHONY: install test clean help run-sse run-http run-stdio deploy logs

PYTHON := python3
VENV := .venv
VENV_BIN := $(VENV)/bin
PIP := $(VENV_BIN)/pip
PYTHON_VENV := $(VENV_BIN)/python

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

$(VENV)/pyvenv.cfg:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)

install: $(VENV)/pyvenv.cfg ## Create virtual environment and install dependencies
	$(PIP) install -qU pip
	$(PIP) install -qr requirements.txt

test: $(VENV)/pyvenv.cfg ## Run tests
	$(PYTHON_VENV) -m pytest tests/

run-sse: $(VENV)/pyvenv.cfg ## Run SSE server locally
	$(VENV_BIN)/uvicorn src.sse_server:app --reload

run-http: $(VENV)/pyvenv.cfg ## Run Streamable HTTP server locally
	$(VENV_BIN)/uvicorn src.streamable_http_server:app --reload

run-stdio: $(VENV)/pyvenv.cfg ## Run STDIO server locally
	$(PYTHON_VENV) -m src.stdio_server

deploy: ## Deploy to Heroku (requires APP_NAME env var)
	@if [ -z "$(APP_NAME)" ]; then \
		echo "❌ Please set APP_NAME. Usage: make deploy APP_NAME=your-app-name"; \
		exit 1; \
	fi
	@echo "🚀 Deploying to Heroku app: $(APP_NAME)"
	git push heroku main

logs: ## View Heroku logs (requires APP_NAME env var)
	@if [ -z "$(APP_NAME)" ]; then \
		echo "❌ Please set APP_NAME. Usage: make logs APP_NAME=your-app-name"; \
		exit 1; \
	fi
	heroku logs --tail -a $(APP_NAME)

clean: ## Remove virtual environment
	@echo "Removing virtual environment..."
	rm -rf $(VENV)
	@echo "Clean complete!"
