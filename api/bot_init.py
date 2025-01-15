from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from pydantic_settings import BaseSettings
from typing import Optional
import os
import sys
from aiogram.types import Update

# Добавляем путь к исходникам бота
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bot.routers.base import base_router
from src.bot.routers.music import music_router
from src.bot.routers.inline import inline_router
from src.bot.config.config import config as bot_config

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
    
    # Регистрируем существующие роутеры
    dp.include_router(base_router)
    dp.include_router(music_router)
    dp.include_router(inline_router)
    
    return bot, dp

async def process_update(update_data: dict):
    """Обработка обновления от Telegram."""
    bot, dp = init_bot()
    try:
        # Создаем объект Update из словаря с контекстом бота
        update = Update.model_validate(update_data, context={"bot": bot})
        # Передаем update в диспетчер
        await dp.feed_update(bot=bot, update=update)
    finally:
        await bot.session.close() 