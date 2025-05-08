.PHONY: install test lint clean build all

# Default target
all: install test lint build

# Install the package in development mode
install:
	pip install -e .
	pip install -r requirements-dev.txt

# Run tests with coverage
test:
	pytest --cov=deleter tests/ --cov-report=term --cov-report=html

# Run linting checks
lint:
	flake8 deleter/ tests/ setup.py delete_deployments.py

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf coverage.xml
	find . -name __pycache__ -type d -exec rm -rf {} +
	find . -name "*.pyc" -delete

# Build the package
build:
	python -m build

# Run tests with verbose output
test-verbose:
	pytest -vv --cov=deleter tests/ --cov-report=term --cov-report=html 