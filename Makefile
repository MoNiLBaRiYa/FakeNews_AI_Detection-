.PHONY: help install test run clean lint format docker-build docker-run

help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make test          - Run tests"
	@echo "  make test-cov      - Run tests with coverage"
	@echo "  make run           - Run development server"
	@echo "  make clean         - Clean cache and temp files"
	@echo "  make lint          - Run linter"
	@echo "  make format        - Format code"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-run    - Run Docker container"

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=Backend --cov-report=html --cov-report=term

run:
	python Backend/app.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

lint:
	flake8 Backend/ --max-line-length=120 --exclude=__pycache__

format:
	black Backend/ tests/ --line-length=120

docker-build:
	docker build -t fake-news-detector .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

setup-env:
	cp .env.example .env
	@echo "Please edit .env file with your configuration"
