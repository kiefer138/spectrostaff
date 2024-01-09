PROJ_BASE=$(shell pwd)
PYTHONVER=python3.11
PYTHONENV=$(PROJ_BASE)/venv
VENVPYTHON=$(PYTHONENV)/bin/$(PYTHONVER)

.PHONY: develop
develop: bootstrap
	@echo "Installing project in development mode..."
	@$(VENVPYTHON) -m pip install -e .
	@echo "Done."

.PHONY: bootstrap
bootstrap:
	@echo "Bootstrapping project..."
	@$(PYTHONVER) -m venv $(PYTHONENV)
	@$(VENVPYTHON) -m pip install --upgrade pip
	@$(VENVPYTHON) -m pip install -r requirements.txt
	@echo "Done."

.PHONY: clean
clean:
	@echo "Cleaning project..."
	@rm -rf $(PYTHONENV)
	@rm -rf .mypy_cache
	@rm -rf .pytest_cache
	@find . -name '*.egg-info' -type d -prune -exec rm -rf {} +
	@find . -name '__pycache__' -type d -prune -exec rm -rf {} +
	@rm -rf dist
	@echo "Done.""Done."
