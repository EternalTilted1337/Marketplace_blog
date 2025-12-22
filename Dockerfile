FROM python:3.11-slim


#Устанавливаем poetry
RUN pip install --no-cache-dir poetry

#Копируем файлы зависимостей
COPY pyproject.toml poetry.lock ./

#Установка зависимостей
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main --no-root

#Копия кода
COPY . .

#Открытие порта
EXPOSE 8000

#Запуск FastAPI

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]