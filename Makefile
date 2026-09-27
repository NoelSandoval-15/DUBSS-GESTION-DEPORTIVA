# =============================================================================
# Makefile — Comandos del proyecto DUBSS
# Uso: make <comando>
# =============================================================================

DC      = docker compose -f docker-compose.dev.yml
DC_PROD = docker compose -f docker-compose.yml
BE      = $(DC) exec backend
FE      = $(DC) exec frontend

.PHONY: help up down build logs shell migrate makemigrations \
        createsuperuser test lint format collectstatic prod-up prod-down

help: ## Muestra esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Contenedores ─────────────────────────────────────────────────────────────
up: ## Levantar entorno de desarrollo
	$(DC) up -d --build

down: ## Detener contenedores de desarrollo
	$(DC) down

build: ## Reconstruir imágenes
	$(DC) build

logs: ## Ver logs en tiempo real
	$(DC) logs -f

logs-be: ## Logs solo del backend
	$(DC) logs -f backend

logs-fe: ## Logs solo del frontend
	$(DC) logs -f frontend

restart-be: ## Reiniciar solo el backend
	$(DC) restart backend

# ── Django ───────────────────────────────────────────────────────────────────
migrate: ## Aplicar migraciones
	$(BE) python manage.py migrate

makemigrations: ## Crear migraciones
	$(BE) python manage.py makemigrations

createsuperuser: ## Crear superusuario
	$(BE) python manage.py createsuperuser

shell: ## Django shell interactivo
	$(BE) python manage.py shell

shell-plus: ## Django shell con auto-imports (requiere django-extensions)
	$(BE) python manage.py shell_plus

collectstatic: ## Recolectar archivos estáticos
	$(BE) python manage.py collectstatic --noinput

dbshell: ## Conectar a la base de datos
	$(BE) python manage.py dbshell

# ── Tests ────────────────────────────────────────────────────────────────────
test: ## Ejecutar todos los tests
	$(BE) pytest -v

test-cov: ## Tests con cobertura
	$(BE) pytest --cov=apps --cov-report=html -v

test-app: ## Tests de una app específica (make test-app APP=users)
	$(BE) pytest apps/$(APP)/ -v

# ── Calidad de código ─────────────────────────────────────────────────────────
lint: ## Revisar estilo con flake8
	$(BE) flake8 apps/ config/

format: ## Formatear con black e isort
	$(BE) black apps/ config/
	$(BE) isort apps/ config/

# ── Producción ────────────────────────────────────────────────────────────────
prod-up: ## Levantar en modo producción
	$(DC_PROD) up -d --build

prod-down: ## Detener producción
	$(DC_PROD) down

prod-logs: ## Logs de producción
	$(DC_PROD) logs -f

# ── Base de datos ─────────────────────────────────────────────────────────────
db-backup: ## Hacer backup de la base de datos
	$(DC) exec db pg_dump -U $${POSTGRES_USER} $${POSTGRES_DB} > backup_$(shell date +%Y%m%d_%H%M%S).sql

db-restore: ## Restaurar backup (make db-restore FILE=backup.sql)
	$(DC) exec -T db psql -U $${POSTGRES_USER} $${POSTGRES_DB} < $(FILE)

db-reset: ## Eliminar y recrear la base de datos (¡PELIGROSO!)
	$(DC) exec db psql -U $${POSTGRES_USER} -c "DROP DATABASE IF EXISTS $${POSTGRES_DB};"
	$(DC) exec db psql -U $${POSTGRES_USER} -c "CREATE DATABASE $${POSTGRES_DB};"
	$(MAKE) migrate
