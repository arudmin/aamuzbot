FROM python:3.10-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Установка рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY pyproject.toml poetry.lock ./

# Установка зависимостей
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --no-dev

# Копирование исходного кода
COPY . .

# Установка проекта
RUN poetry install --no-interaction --no-ansi --no-dev

# Порт для FastAPI (по умолчанию для Fly.io)
ENV PORT=8000

# Запуск приложения
CMD poetry run uvicorn api.index:app --host 0.0.0.0 --port $PORT 