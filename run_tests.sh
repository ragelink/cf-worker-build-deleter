#!/bin/bash
set -e

# Install test dependencies
pip install -e .
pip install -r requirements-dev.txt

# Run tests with coverage
pytest --cov=deleter tests/ --cov-report=term --cov-report=html

# Print coverage summary
echo -e "\nCoverage Summary:"
coverage report -m

echo -e "\nHTML coverage report generated in htmlcov/ directory" 