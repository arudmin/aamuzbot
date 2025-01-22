FROM python:3.10-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

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

# Установка порта для FastAPI
ENV PORT=8000

# Запуск приложения
CMD uvicorn src.bot.app:app --host 0.0.0.0 --port $PORT 