.PHONY: help dev prod stop clean logs test

help:
	@echo "Plural Chat Web Edition - Make Commands"
	@echo ""
	@echo "  make dev      - Start development environment"
	@echo "  make prod     - Start production environment"
	@echo "  make stop     - Stop all services"
	@echo "  make clean    - Stop and remove all containers, volumes"
	@echo "  make logs     - View logs from all services"
	@echo "  make test     - Run tests"
	@echo ""

dev:
	@echo "🚀 Starting development environment..."
	docker-compose -f docker-compose.dev.yml up --build

prod:
	@echo "🚀 Starting production environment..."
	@if [ ! -f backend/.env ]; then \
		echo "⚠️  Backend .env not found. Creating from example..."; \
		cp backend/.env.example backend/.env; \
		echo "📝 Please edit backend/.env with your configuration"; \
		exit 1; \
	fi
	docker-compose up --build -d
	@echo "✅ Services started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

stop:
	@echo "🛑 Stopping all services..."
	docker-compose down
	docker-compose -f docker-compose.dev.yml down

clean:
	@echo "🧹 Cleaning up..."
	docker-compose down -v
	docker-compose -f docker-compose.dev.yml down -v
	@echo "✅ Cleanup complete!"

logs:
	@echo "📋 Viewing logs..."
	docker-compose logs -f

test:
	@echo "🧪 Running tests..."
	@echo "Backend tests:"
	cd backend && pytest
	@echo ""
	@echo "Frontend tests:"
	cd frontend && npm test
