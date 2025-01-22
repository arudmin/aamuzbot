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

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/aamuzbot.git
cd aamuzbot
```

2. Установите зависимости с помощью Poetry:
```bash
poetry install
```

3. Создайте файл `.env` на основе `.env.example` и заполните необходимые переменные окружения:
```bash
cp .env.example .env
```

## Запуск

### Режим разработки (dev)

В режиме разработки бот использует ngrok для создания туннеля и получения HTTPS URL:

```bash
BOT_ENV=dev poetry run bot
```

### Деплой на Railway.app

1. Создайте аккаунт на [Railway](https://railway.app)

2. Установите Railway CLI:
```bash
npm i -g @railway/cli
```

3. Авторизуйтесь в Railway:
```bash
railway login
```

4. Создайте новый проект:
```bash
railway init
```

5. Добавьте переменные окружения:
```bash
railway variables set BOT_TOKEN="your_telegram_bot_token"
railway variables set YANDEX_MUSIC_TOKEN="your_yandex_music_token"
railway variables set WEBHOOK_SECRET="your_webhook_secret"
railway variables set BOT_ENV="prod"
```

6. Разверните приложение:
```bash
railway up
```

7. Получите URL приложения:
```bash
railway domain
```

8. Установите вебхук для бота (замените YOUR_APP_URL на полученный URL):
```bash
curl -X POST "https://api.telegram.org/bot$BOT_TOKEN/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://YOUR_APP_URL/webhook", "secret_token": "your_webhook_secret"}'
```

### Деплой на Fly.io

1. Установите Fly CLI:
```bash
# На Linux/WSL
curl -L https://fly.io/install.sh | sh

# На macOS
brew install flyctl
```

2. Авторизуйтесь в Fly.io:
```bash
fly auth login
```

3. Создайте приложение:
```bash
fly apps create aamuzbot
```

4. Настройте секреты:
```bash
fly secrets set BOT_TOKEN="your_telegram_bot_token"
fly secrets set YANDEX_MUSIC_TOKEN="your_yandex_music_token"
fly secrets set WEBHOOK_SECRET="your_webhook_secret"
```

5. Разверните приложение:
```bash
fly deploy
```

6. Получите URL приложения:
```bash
fly apps list
```

7. Установите вебхук для бота (замените YOUR_APP_NAME на имя вашего приложения):
```bash
curl -X POST "https://api.telegram.org/bot$BOT_TOKEN/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://YOUR_APP_NAME.fly.dev/webhook", "secret_token": "your_webhook_secret"}'
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