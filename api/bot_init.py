from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    bot_token: str
    bot_env: str = "prod"
    webhook_host: Optional[str] = None
    webhook_secret: Optional[str] = None
    yandex_music_token: str
    
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
    
    return bot, dp

async def process_update(update_data: dict):
    """Обработка обновления от Telegram."""
    bot, dp = init_bot()
    try:
        await dp.feed_update(bot, update_data)
    finally:
        await bot.session.close() 