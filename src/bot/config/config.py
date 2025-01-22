"""
Конфигурация бота.

Этот модуль содержит настройки для работы бота в разных окружениях (dev/prod).
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Настройки бота."""
    # Основные настройки
    bot_token: str
    bot_env: str = "prod"  # dev или prod
    
    # Настройки для разработки
    ngrok_auth_token: Optional[str] = None
    ngrok_tunnel_url: Optional[str] = None
    
    # Настройки для продакшена
    webhook_host: str = "https://aamuzbot.railway.app"
    webhook_path: str = "/webhook"
    webapp_host: str = "0.0.0.0"
    webapp_port: int = int(os.getenv("PORT", "8000"))  # Railway предоставляет порт через переменную окружения PORT
    
    # Настройки Яндекс.Музыки
    yandex_music_token: str
    
    @property
    def is_prod(self) -> bool:
        """Проверяет, запущен ли бот в production режиме."""
        return self.bot_env.lower() == "prod"
        
    @property
    def webhook_url(self) -> str:
        """Возвращает URL для вебхука."""
        return f"{self.webhook_host}{self.webhook_path}"
        
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Создаем экземпляр конфигурации
config = Settings()