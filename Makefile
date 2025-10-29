# Makefile for Google Calendar AI Agent

.PHONY: help install dev test clean docker-up docker-down docker-logs docker-restart lint format

help:
	@echo "Google Calendar AI Agent - Available Commands:"
	@echo ""
	@echo "  make install        - Install backend dependencies"
	@echo "  make dev            - Run development server"
	@echo "  make test           - Run tests"
	@echo "  make test-cov       - Run tests with coverage"
	@echo "  make lint           - Run linters"
	@echo "  make format         - Format code"
	@echo "  make docker-up      - Start Docker containers"
	@echo "  make docker-down    - Stop Docker containers"
	@echo "  make docker-logs    - View Docker logs"
	@echo "  make docker-restart - Restart Docker containers"
	@echo "  make clean          - Clean build artifacts"

install:
	cd backend && pip install -r requirements.txt

dev:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	cd backend && pytest -v

test-cov:
	cd backend && pytest --cov=app --cov-report=html --cov-report=term-missing

lint:
	cd backend && flake8 app tests
	cd backend && mypy app

format:
	cd backend && black app tests

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-restart:
	docker-compose restart

docker-build:
	docker-compose build --no-cache

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf backend/htmlcov
	rm -rf backend/.coverage
