"""
Основной модуль приложения.

Этот модуль инициализирует бота и веб-сервер, настраивает роутинг
и запускает приложение.
"""

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.exceptions import TelegramRetryAfter
from aiohttp import web
from bot.config.config import config
from bot.handlers.base import router as base_router
from bot.handlers.music import router as music_router
from bot.handlers.inline import router as inline_router
from bot.routers.web import setup_routes
from bot.middlewares.logging import LoggingMiddleware
from loguru import logger


async def on_startup(bot: Bot) -> None:
    """
    Действия при запуске бота.
    
    Args:
        bot: Экземпляр бота
    """
    # Устанавливаем вебхук
    await bot.set_webhook(
        url=config.webhook_url,
        drop_pending_updates=False,
        allowed_updates=["message", "inline_query", "callback_query"]
    )
    logger.info(f"Webhook set to {config.webhook_url}")


async def on_shutdown(bot: Bot) -> None:
    """
    Действия при остановке бота.
    
    Args:
        bot: Экземпляр бота
    """
    # Удаляем вебхук
    await bot.delete_webhook()
    
    # Закрываем сессии
    await bot.session.close()


async def process_update(request: web.Request) -> web.Response:
    """
    Обрабатывает входящие обновления от Telegram.
    
    Args:
        request: Входящий HTTP запрос
        
    Returns:
        HTTP ответ
    """
    bot = request.app["bot"]
    dp = request.app["dp"]
    update = Update(**(await request.json()))
    await dp.feed_update(bot=bot, update=update)
    return web.Response()


# Инициализируем бота и диспетчер на уровне модуля
bot = Bot(token=config.bot_token)
dp = Dispatcher()

# Регистрируем обработчики
dp.include_router(base_router)
dp.include_router(music_router)
dp.include_router(inline_router)

# Добавляем мидлвари
dp.message.middleware(LoggingMiddleware())
dp.inline_query.middleware(LoggingMiddleware())
dp.callback_query.middleware(LoggingMiddleware())

# Создаем приложение
app = web.Application()
app["bot"] = bot
app["dp"] = dp

# Настраиваем маршруты
app.router.add_post(config.webhook_path, process_update)

# Настраиваем запуск и остановку
dp.startup.register(on_startup)
dp.shutdown.register(on_shutdown)

# Для uvicorn
app = init_app() 