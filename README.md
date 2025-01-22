# AamuzBot - Telegram бот для скачивания музыки

Telegram бот для поиска и скачивания музыки из Яндекс.Музыки.

Полностью.
Сгенерирован.
Нейросетью.

Я не написал ни строчки кода.

## Возможности

- 🔍 Поиск треков по названию или исполнителю
- 📥 Скачивание треков в MP3 формате
- 📱 Поддержка inline-режима для поиска в других чатах
- 🎵 Сохранение метаданных (название, исполнитель) в MP3 файлах

## Установка

### Локальный запуск

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/aamuzbot.git
cd aamuzbot
```

2. Создайте файл `.env` на основе `.env.example` и заполните необходимые переменные окружения:
```bash
cp .env.example .env
```

3. Запустите через Docker:
```bash
docker build -t aamuzbot .
docker run -p 8000:8000 --env-file .env aamuzbot
```

### GitHub Deployment

1. Форкните репозиторий на GitHub

2. В настройках репозитория:
   - Перейдите в Settings -> Secrets and variables -> Actions
   - Добавьте следующие секреты:
     - `BOT_TOKEN`: Ваш токен Telegram бота
     - `YANDEX_MUSIC_TOKEN`: Ваш токен Яндекс.Музыки
     - `WEBHOOK_SECRET`: Секретный токен для вебхука

3. Включите GitHub Packages:
   - Перейдите в Settings -> Packages
   - Убедитесь, что GitHub Packages включены для репозитория

4. Push изменения в ветку main для автоматической сборки и публикации Docker образа:
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

5. После успешной сборки, Docker образ будет доступен в GitHub Container Registry:
```bash
docker pull ghcr.io/yourusername/aamuzbot:main
```

## Структура проекта

```
src/bot/
├── config/         # Конфигурация бота
├── handlers/       # Обработчики команд
├── middlewares/    # Промежуточные обработчики
├── services/       # Сервисы (Яндекс.Музыка)
└── utils/          # Вспомогательные функции
```

## Версии

- 0.2b - Стабильная версия с улучшенной обработкой ошибок, асинхронной загрузкой и обработкой файлов
- 0.1b - Первая бета-версия с базовым функционалом

## Лицензия

MIT 