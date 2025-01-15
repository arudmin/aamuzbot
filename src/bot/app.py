"""
Основной модуль приложения.

Этот модуль инициализирует бота и веб-сервер, настраивает роутинг
и запускает приложение.
"""

from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from bot.config.config import config
from bot.handlers import register_handlers
from bot.web.routes import routes as download_routes
from loguru import logger


async def on_startup(bot: Bot) -> None:
    """
    Действия при запуске бота.
    
    Устанавливает вебхук для получения обновлений от Telegram.
    
    Аргументы:
        bot (Bot): Экземпляр бота
    """
    await bot.set_webhook(
        url=f"{config.webhook_url}/webhook",
        drop_pending_updates=True
    )
    logger.info(f"Установлен вебхук: {config.webhook_url}/webhook")


async def on_shutdown(bot: Bot) -> None:
    """
    Действия при остановке бота.
    
    Удаляет вебхук и закрывает все соединения.
    
    Аргументы:
        bot (Bot): Экземпляр бота
    """
    await bot.delete_webhook()
    logger.info("Вебхук удален")


def init_app() -> web.Application:
    """
    Инициализация приложения.
    
    Создает и настраивает экземпляры бота, диспетчера и веб-приложения.
    Регистрирует все обработчики и роуты.
    
    Возвращает:
        web.Application: Настроенное веб-приложение
    """
    # Инициализация бота и диспетчера
    bot = Bot(token=config.bot_token)
    dp = Dispatcher()
    
    # Регистрация обработчиков
    register_handlers(dp)
    
    # Создание веб-приложения
    app = web.Application()
    
    # Настройка вебхука
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot
    )
    webhook_requests_handler.register(app, path="/webhook")
    
    # Регистрация обработчиков событий
    app.on_startup.append(lambda x: on_startup(bot))
    app.on_shutdown.append(lambda x: on_shutdown(bot))
    
    # Регистрация роутов для скачивания
    app.add_routes(download_routes)
    
    # Настройка Middleware
    setup_application(app, dp, bot=bot)
    
    return app 