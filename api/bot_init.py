from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from pydantic_settings import BaseSettings
from typing import Optional
import os
from aiogram.types import Update, Message
from aiogram.filters import Command

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
    
    # Регистрируем обработчики
    @dp.message(Command("start"))
    async def cmd_start(message: Message):
        await message.answer("Привет! Я бот для поиска и скачивания музыки. Используй инлайн режим для поиска.")
    
    return bot, dp

async def process_update(update_data: dict):
    """Обработка обновления от Telegram."""
    bot, dp = init_bot()
    try:
        # Создаем объект Update из словаря
        update = Update.model_validate(update_data)
        # Передаем update в диспетчер
        await dp.feed_update(bot=bot, update=update)
    finally:
        await bot.session.close() 