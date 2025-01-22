FROM python:3.10-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    ffmpeg \
    libavcodec-extra \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade pip

# Копирование исходного кода
COPY . .

# Установка переменных окружения
ENV PORT=8000
ENV PYTHONPATH=/app/src

# Запуск приложения
CMD uvicorn bot.main:app --host 0.0.0.0 --port $PORT --app-dir /app/src 