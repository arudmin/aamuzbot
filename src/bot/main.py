"""
Основной модуль приложения.

Этот модуль инициализирует бота и веб-сервер, настраивает роутинг
и запускает приложение.
"""

from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
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


def init_app() -> web.Application:
    """
    Инициализация приложения.
    
    Returns:
        Инициализированное веб-приложение
    """
    # Инициализируем бота и диспетчер
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher()
    
    # Регистрируем обработчики
    dp.include_router(base_router)
    dp.include_router(music_router)
    dp.include_router(inline_router)
    
    # Создаем веб-приложение
    app = web.Application()
    
    # Настраиваем вебхук
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot
    )
    webhook_requests_handler.register(app, path="/webhook")
    
    # Добавляем маршруты для скачивания
    setup_routes(app)
    
    # Настраиваем запуск и остановку
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Добавляем мидлвари
    dp.message.middleware(LoggingMiddleware())
    dp.inline_query.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    
    # Настраиваем интеграцию с aiohttp
    setup_application(app, dp, bot=bot)
    
    return app


def main():
    """
    Точка входа в приложение.
    """
    # Запускаем приложение
    web.run_app(
        init_app(),
        host=config.webapp_host,
        port=config.webapp_port
    )


if __name__ == "__main__":
    main() 