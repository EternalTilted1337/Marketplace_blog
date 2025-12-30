PIP = .venv/Scripts/pip
UVICORN = .venv/Scripts/uvicorn
PYTHON = .venv/Scripts/python

.PHONY: run, up, down,migrate,create,lint,format

IMAGE_NAME = marketplace-app

build:
	docker build -t $(IMAGE_NAME) .
run-docker:
	docker run --rm -p 8000:8000 $(IMAGE_NAME)
down-docker:
	docker-compose down 8000:8000 $(IMAGE_NAME)

help:
	@echo ""
	@echo "start"
	@echo "make run - start project with docker-compose up"
	@echo "------------Docker------------"
	@echo "make up - docker-compose up"
	@echo "make down - docker-compose down"
	@echo "------------Alembic-----------"
	@echo "make migration - accept migration"
	@echo "make create - create migration"
	@echo "------------Ruff-----------"
	@echo "make lint - check PEP8"
	@echo "make format - check trash"

#start
run: up
	$(UVICORN) app.main:app --reload

#docker
up:
	docker-compose up -d

down:
	docker-compose down

#migration
migrate:
	$(PYTHON) -m alembic upgrade head

create:
	$(PYTHON) -m alembic revision --autogenerate -m "$(msg)"

#Ruff linter
lint:
	$(PYTHON) -m ruff check app
format:
	$(PYTHON) -m ruff format app
