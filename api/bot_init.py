from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from pydantic_settings import BaseSettings
from typing import Optional
import os
import sys
from aiogram.types import Update
from loguru import logger

# Get the absolute path to the project directories
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
API_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')

logger.info("Project root: {}", PROJECT_ROOT)
logger.info("API directory: {}", API_DIR)
logger.info("SRC directory: {}", SRC_DIR)
logger.info("Current sys.path: {}", sys.path)

# Add directories to Python path in order of preference
paths_to_add = [API_DIR, PROJECT_ROOT, SRC_DIR]
for path in paths_to_add:
    if path not in sys.path:
        sys.path.insert(0, path)

logger.info("Updated sys.path: {}", sys.path)

try:
    # Try importing from api/bot first (where files are copied during build)
    from bot.routers.base import base_router
    from bot.routers.music import music_router
    from bot.routers.inline import inline_router
    from bot.config.config import config as bot_config
    from bot.middlewares.logging import LoggingMiddleware
    logger.info("Successfully imported bot modules from api/bot")
except Exception as e:
    logger.error("Failed to import bot modules from api/bot: {}", str(e))
    try:
        # Try importing from src.bot as fallback
        from src.bot.routers.base import base_router
        from src.bot.routers.music import music_router
        from src.bot.routers.inline import inline_router
        from src.bot.config.config import config as bot_config
        from src.bot.middlewares.logging import LoggingMiddleware
        logger.info("Successfully imported bot modules from src.bot")
    except Exception as e:
        logger.error("Failed to import bot modules from src.bot: {}", str(e))
        raise ImportError("Could not import bot modules from any location") from e

class Settings(BaseSettings):
    bot_token: str = bot_config.bot_token
    bot_env: str = "prod"
    webhook_host: Optional[str] = None
    webhook_secret: Optional[str] = None
    yandex_music_token: str = bot_config.yandex_music_token
    
    @property
    def webhook_url(self) -> Optional[str]:
        if self.webhook_host:
            return f"{self.webhook_host}/api/webhook"
        return None
        
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

def init_bot():
    """Инициализация бота."""
    config = Settings()
    
    # Создаем экземпляр бота
    bot = Bot(token=config.bot_token)
    dp = Dispatcher()
    
    # Добавляем мидлвари
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    dp.inline_query.middleware(LoggingMiddleware())
    
    # Регистрируем существующие роутеры
    logger.debug("Registering routers...")
    dp.include_router(base_router)
    logger.debug("Base router registered")
    dp.include_router(music_router)
    logger.debug("Music router registered")
    dp.include_router(inline_router)
    logger.debug("Inline router registered")
    
    return bot, dp

async def process_update(update_data: dict):
    """Обработка обновления от Telegram."""
    bot, dp = init_bot()
    try:
        # Создаем объект Update из словаря с контекстом бота
        update = Update.model_validate(update_data, context={"bot": bot})
        logger.debug("Update object created: {}", update)
        
        # Передаем update в диспетчер
        result = await dp.feed_update(bot=bot, update=update)
        logger.debug("Update processing result: {}", result)
        
    finally:
        await bot.session.close() 