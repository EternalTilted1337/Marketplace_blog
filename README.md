# Marketplace Blog API

Асинхронное API для блога маркетплейса, построенное на **FastAPI** и **PostgreSQL**. Проект полностью контейнеризирован с помощью Docker и поддерживает автоматизированное тестирование.

## 🚀 Технологии
* **Backend:** FastAPI (Python 3.11)
* **Database:** PostgreSQL + SQLAlchemy (Async)
* **Migrations:** Alembic
* **Containerization:** Docker & Docker Compose
* **Testing:** Pytest (Asyncio)

## 🛠 Установка и запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com/EternalTilted1337/Marketplace_blog.git
cd Marketplace_blog
```

### 2. Настройка окружения
Создайте файл .env в корне проекта на основе примера:

Фрагмент кода
```
DB_USER=postgres
DB_PASS=postgres
DB_NAME=marketplace_db
DB_HOST=db
DB_PORT=5432
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/marketplace_db
SECRET_KEY=your_secret_key_here
```
### 3. Запуск через Docker Compose
Проект запустится вместе с базой данных и применит необходимые настройки:

```
docker-compose up -d --build

```
API будет доступно по адресу: http://localhost:8000

Интерактивная документация (Swagger): http://localhost:8000/docs

🧪 Тестирование
Для запуска тестов внутри контейнера используйте команду:
```
Bash
docker-compose exec app python -m pytest
```

### 📂 Структура проекта
app/ — основной код приложения (роутеры, модели, схемы).

tests/ — интеграционные и юнит-тесты.

alembic/ — миграции базы данных.

docker-compose.yml — конфигурация сервисов приложения и БД.