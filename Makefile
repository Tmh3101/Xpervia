.PHONY: help build up down logs restart clean migrate shell test

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Xpervia Docker Management$(NC)"
	@echo ""
	@echo "$(GREEN)Available commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

setup: ## Initial setup - copy env files
	@echo "$(BLUE)Setting up environment files...$(NC)"
	@cp -n backend/.env.example backend/.env 2>/dev/null || echo "backend/.env already exists"
	@cp -n frontend/.env.example frontend/.env.local 2>/dev/null || echo "frontend/.env.local already exists"
	@cp -n chatbot_service/.env.example chatbot_service/.env 2>/dev/null || echo "chatbot_service/.env already exists"
	@echo "$(GREEN)✓ Environment files created. Please configure them with your settings.$(NC)"

build: ## Build all Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	docker-compose build

build-nc: ## Build without cache
	@echo "$(BLUE)Building Docker images (no cache)...$(NC)"
	docker-compose build --no-cache

up: ## Start all services
	@echo "$(BLUE)Starting services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Services started!$(NC)"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"
	@echo "Chatbot: http://localhost:8001"

dev: ## Start services with hot-reload
	@echo "$(BLUE)Starting services in development mode...$(NC)"
	docker-compose -f docker-compose.dev.yml up

down: ## Stop all services
	@echo "$(BLUE)Stopping services...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Services stopped$(NC)"

restart: ## Restart all services
	@echo "$(BLUE)Restarting services...$(NC)"
	docker-compose restart
	@echo "$(GREEN)✓ Services restarted$(NC)"

logs: ## View logs for all services
	docker-compose logs -f

logs-backend: ## View backend logs
	docker-compose logs -f backend

logs-frontend: ## View frontend logs
	docker-compose logs -f frontend

logs-chatbot: ## View chatbot logs
	docker-compose logs -f chatbot

ps: ## Show running containers
	docker-compose ps

migrate: ## Run Django migrations
	@echo "$(BLUE)Running migrations...$(NC)"
	docker-compose exec backend python manage.py migrate
	@echo "$(GREEN)✓ Migrations complete$(NC)"

makemigrations: ## Create Django migrations
	@echo "$(BLUE)Creating migrations...$(NC)"
	docker-compose exec backend python manage.py makemigrations

seed: ## Seed initial data
	@echo "$(BLUE)Seeding database...$(NC)"
	docker-compose exec backend python manage.py seed_admin
	@echo "$(GREEN)✓ Database seeded$(NC)"

shell: ## Open Django shell
	docker-compose exec backend python manage.py shell

shell-backend: ## Open bash in backend container
	docker-compose exec backend bash

shell-chatbot: ## Open bash in chatbot container
	docker-compose exec chatbot bash

shell-frontend: ## Open shell in frontend container
	docker-compose exec frontend sh

redis-cli: ## Open Redis CLI
	docker-compose exec redis redis-cli

test: ## Run backend tests
	@echo "$(BLUE)Running tests...$(NC)"
	docker-compose exec backend python manage.py test

test-chatbot: ## Run chatbot tests
	@echo "$(BLUE)Running chatbot tests...$(NC)"
	docker-compose exec chatbot pytest

celery-status: ## Check Celery worker status
	docker-compose exec celery-worker celery -A backend inspect active

celery-tasks: ## List registered Celery tasks
	docker-compose exec celery-worker celery -A backend inspect registered

clean: ## Stop and remove containers, volumes
	@echo "$(YELLOW)⚠️  This will remove all containers and volumes!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		echo "$(GREEN)✓ Cleaned up$(NC)"; \
	fi

clean-images: ## Remove all project images
	@echo "$(YELLOW)Removing project images...$(NC)"
	docker-compose down --rmi all

clean-all: ## Complete cleanup (containers, volumes, images)
	@echo "$(RED)⚠️  This will remove everything!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v --rmi all; \
		echo "$(GREEN)✓ Complete cleanup done$(NC)"; \
	fi

update: ## Pull latest images and rebuild
	@echo "$(BLUE)Updating images...$(NC)"
	docker-compose pull
	docker-compose build --pull
	@echo "$(GREEN)✓ Update complete$(NC)"

install: setup build up migrate seed ## Complete installation

deploy: ## Deploy to production
	@echo "$(BLUE)Deploying to production...$(NC)"
	docker-compose -f docker-compose.yml build
	docker-compose up -d
	docker-compose exec backend python manage.py migrate
	docker-compose exec backend python manage.py collectstatic --noinput
	@echo "$(GREEN)✓ Deployment complete$(NC)"

backup-redis: ## Backup Redis data
	@echo "$(BLUE)Backing up Redis data...$(NC)"
	docker run --rm -v xpervia_redis_data:/data -v $$(pwd):/backup alpine tar czf /backup/redis_backup_$$(date +%Y%m%d_%H%M%S).tar.gz -C /data .
	@echo "$(GREEN)✓ Redis backup created$(NC)"

status: ## Show service status
	@echo "$(BLUE)Service Status:$(NC)"
	@docker-compose ps
	@echo ""
	@echo "$(BLUE)Health Checks:$(NC)"
	@curl -s -o /dev/null -w "Backend:  %{http_code}\n" http://localhost:8000/api/ || echo "Backend:  DOWN"
	@curl -s -o /dev/null -w "Frontend: %{http_code}\n" http://localhost:3000/ || echo "Frontend: DOWN"
	@curl -s -o /dev/null -w "Chatbot:  %{http_code}\n" http://localhost:8001/health || echo "Chatbot:  DOWN"
	@docker-compose exec redis redis-cli ping > /dev/null && echo "Redis:    PONG" || echo "Redis:    DOWN"
