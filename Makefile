.PHONY: help build up down logs test clean

help:
	@echo "Available commands:"
	@echo "  make build    - Build Docker containers"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make logs     - View logs"
	@echo "  make test     - Run tests"
	@echo "  make clean    - Clean up containers and volumes"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

test:
	cd backend && pytest

test-coverage:
	cd backend && pytest --cov=app --cov-report=html

lint-backend:
	cd backend && black app/ tests/ && isort app/ tests/ && flake8 app/ tests/

lint-frontend:
	cd frontend && npm run lint

clean:
	docker-compose down -v
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf backend/htmlcov
	rm -rf backend/.pytest_cache
	rm -rf frontend/node_modules
	rm -rf frontend/build

dev-backend:
	cd backend && uvicorn app.main:app --reload

dev-frontend:
	cd frontend && npm start

install-backend:
	cd backend && pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

install: install-backend install-frontend
