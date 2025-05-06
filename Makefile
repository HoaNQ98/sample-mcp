.PHONY: help install run test lint clean build up down logs

# Default target
help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make run        - Run the application locally"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linting"
	@echo "  make clean      - Clean up temporary files"
	@echo "  make build      - Build Docker image"
	@echo "  make up         - Start Docker containers"
	@echo "  make down       - Stop Docker containers"
	@echo "  make logs       - View Docker container logs"

# Install dependencies
install:
	pip install -r requirements.txt

# Run the application locally
run:
	python -m services.sample.main

# Run tests
test:
	pytest services/sample/tests

# Run linting
lint:
	flake8 services
	mypy services

# Clean up temporary files
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

# Build Docker image
build:
	docker-compose build

# Start Docker containers
up:
	docker-compose up -d

# Stop Docker containers
down:
	docker-compose down

# View Docker container logs
logs:
	docker-compose logs -f
