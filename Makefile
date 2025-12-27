run:
	poetry run uvicorn app.main:app --reload

IMAGE_NAME = marketplace-app

build:
	docker build -t $(IMAGE_NAME) .
run-docker:
	docker run --rm -p 8000:8000 $(IMAGE_NAME)