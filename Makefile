# Declare phony targets
.PHONY: install typecheck test build format clean docs view-docs help

# Install project in development mode
install: ## Install project in development mode
	@echo "Installing project in development mode..."
	@poetry install

# Run type checks on source code
type: ## Run type checks on source code
	@echo "Running type checks..."
	@poetry run mypy src/ test/

# Run unit tests
test: ## Run unit tests
	@echo "Running unit tests..."
	@poetry run pytest test/

# Build project
build: ## Build project
	@echo "Building project..."
	@poetry build

# Generate documentation
docs: ## Generate documentation
	@echo "Generating documentation..."
	@cd docs && poetry run make html

# Open documentation in a web browser
view-docs: ## Open documentation in a web browser
	@echo "Opening documentation..."
	@open docs/build/html/index.html

# Formats code in src/ and test/ using black
format: ## Format code with black
	@echo "Formatting code..."
	@poetry run black src/ test/

# Clean project
clean: ## Clean project
	@echo "Cleaning project..."
	@rm -rf venv .venv .mypy_cache .pytest_cache dist dist requirements.txt docs/build
	@find . -name '*.egg-info' -type d -prune -exec rm -rf {} +
	@find . -name '__pycache__' -type d -prune -exec rm -rf {} +

# Display help information
help: ## Display help information
	@echo "Targets:"
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)