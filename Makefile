.PHONY: develop
develop:
	@echo "Installing project in development mode..."
	@poetry install
	@echo "Done."

.PHONY: clean
clean:
	@echo "Cleaning project..."
	@rm -rf venv
	@rm -rf .mypy_cache
	@rm -rf .pytest_cache
	@find . -name '*.egg-info' -type d -prune -exec rm -rf {} +
	@find . -name '__pycache__' -type d -prune -exec rm -rf {} +
	@rm -rf dist
	@echo "Done."
