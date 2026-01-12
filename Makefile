# Используем python из venv, чтобы Makefile был кросс-платформенным (Windows/Linux/macOS)
# Предполагается, что виртуальное окружение активировано, либо мы можем указать путь к нему.
# Для простоты будем полагаться на то, что venv активно, или будем вызывать python/pip через `python -m`.
PYTHON = .venv/bin/python
ifeq ($(OS),Windows_NT)
	PYTHON = .venv\Scripts\python
endif

# Цели в .PHONY должны разделяться пробелами
.PHONY: help build run-docker up down migrate create lint format run-local

IMAGE_NAME = marketplace-app

# --- Docker команды ---
build:
	docker build -t $(IMAGE_NAME) .

run-docker:
	docker run --rm -p 8000:8000 $(IMAGE_NAME)

help:
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  up                - Запустить все сервисы в Docker Compose в фоновом режиме."
	@echo "  down              - Остановить и удалить все сервисы Docker Compose."
	@echo "  run-local         - Запустить приложение локально (требует `make up` для зависимостей, например, БД)."
	@echo ""
	@echo "  build             - Собрать Docker-образ приложения."
	@echo "  run-docker        - Запустить приложение в Docker-контейнере (без docker-compose)."
	@echo ""
	@echo "  migrate           - Применить миграции Alembic к базе данных."
	@echo "  create msg=\"...\"  - Создать новую миграцию Alembic с сообщением."
	@echo ""
	@echo "  lint              - Проверить код на соответствие стандартам с помощью Ruff."
	@echo "  format            - Отформатировать код с помощью Ruff."

# --- Docker Compose ---
up:
	docker-compose up -d

down:
	docker-compose down

# --- Локальный запуск ---
# Эта команда запускает приложение на хост-машине, но зависит от сервисов (например, БД) из docker-compose
run-local: up
	$(PYTHON) -m uvicorn app.main:app --reload

# --- Alembic миграции ---
migrate:
	$(PYTHON) -m alembic upgrade head

# Добавлено значение по умолчанию для `msg`, чтобы избежать ошибок
msg ?= "New migration"
create:
	$(PYTHON) -m alembic revision --autogenerate -m "$(msg)"

# --- Ruff линтер и форматтер ---
lint:
	$(PYTHON) -m ruff check app

format:
	$(PYTHON) -m ruff format app