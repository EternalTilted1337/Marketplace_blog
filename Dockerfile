FROM python:3.11-slim

#Установка пакетов
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
#Указание на рабочую директорию
workdir /app

#Установка poetry
RUN pip install --no-cache-dir poetry

#Копируем код
COPY pyproject.toml poetry.lock ./

#Установка зависимостей
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main --no-root

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]