PROJ_BASE=$(shell pwd)
PYTHONVER=python3.11
PYTHONENV=$(PROJ_BASE)/venv
VENVPYTHON=$(PYTHONENV)/bin/$(PYTHONVER)

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
	@echo "Done."
