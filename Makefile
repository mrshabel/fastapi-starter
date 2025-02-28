
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

certs:
	# you can change the location to output the certificates
	@echo "Generating Self-Signed Certificates..."
	openssl req -x509 -noenc -days 365 -newkey rsa:2048 -keyout nginx/certs/server.key -out nginx/certs/server.crt

startup:
	@echo "Running startup scripts"
	python3 -m src.scripts.seed
	@echo "Data seeding complete"
