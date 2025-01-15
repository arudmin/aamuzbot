FROM python:3.10-slim

WORKDIR /app

# Установка poetry
RUN pip install poetry

# Копирование файлов проекта
COPY pyproject.toml poetry.lock ./
COPY src ./src
COPY .env.example ./.env

# Установка зависимостей
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Запуск бота
CMD ["poetry", "run", "bot"] 