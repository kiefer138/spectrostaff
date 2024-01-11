# Declare phony targets
.PHONY: install typecheck typecheck-test test build clean docs view-docs help

# Install project in development mode
install:
	@echo "Installing project in development mode..."
	@poetry install

# Run type checks on source code
typecheck:
	@echo "Running type checks..."
	@poetry run mypy ./src/

# Run type checks on tests
typecheck-test:
	@echo "Running type checks on tests..."
	@poetry run mypy ./test/

# Run unit tests
unit-test:
	@echo "Running unit tests..."
	@poetry run pytest

# Run all tests
test: typecheck typecheck-test unit-test

# Build project
build:
	@echo "Building project..."
	@poetry build

# Generate documentation
docs:
	@echo "Generating documentation..."
	@cd docs && poetry run make html

# Open documentation in a web browser
view-docs:
	@echo "Opening documentation..."
	@open docs/build/html/index.html

# Clean project
clean:
	@echo "Cleaning project..."
	@rm -rf venv .venv .mypy_cache .pytest_cache dist dist requirements.txt docs/build
	@find . -name '*.egg-info' -type d -prune -exec rm -rf {} +
	@find . -name '__pycache__' -type d -prune -exec rm -rf {} +

# Display help information
help:
	@echo "Targets:"
	@echo "  install: Set up dev mode & install dependencies from pyproject.toml."
	@echo "  typecheck: Run mypy on source code."
	@echo "  typecheck-test: Run mypy on tests."
	@echo "  unit-test: Run pytest."
	@echo "  test: Run all tests."
	@echo "  build: Build package with poetry."
	@echo "  docs: Generate documentation with Sphinx."
	@echo "  view-docs: Open documentation in a web browser."
	@echo "  clean: Remove temp files & directories."
