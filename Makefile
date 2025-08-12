.PHONY: install install-dev format lint test pre-commit-install pre-commit-run clean

# Install production dependencies
install:
	pip install -r requirements.txt

# Install development dependencies
install-dev:
	pip install -r requirements.txt
	pip install pre-commit

# Format code with black and isort
format:
	black .
	isort .

# Run all linters
lint:
	flake8 .
	mypy .
	bandit -r . -f json -o bandit-report.json || true
	pylint src/ --disable=all --enable=unused-import,unused-variable,undefined-variable || true

# Run tests
test:
	python -m pytest tests/ -v

# Install pre-commit hooks
pre-commit-install:
	pre-commit install

# Run pre-commit on all files
pre-commit-run:
	pre-commit run --all-files

# Clean up generated files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -f bandit-report.json

# Setup development environment
setup-dev: install-dev pre-commit-install
	@echo "Development environment setup complete!"
	@echo "Run 'make pre-commit-run' to check all files"
