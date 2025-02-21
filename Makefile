
.PHONY: lint format

lint:
	@echo "Linting code..."
	python3 ruff check --fix
	@echo "Linting complete"


format:
	@echo "Formatting code..."
	python3 ruff format
	@echo "Formatting complete"


all: format lint