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
    bot_env: str = "dev"  # dev или prod
    
    # Настройки для разработки
    ngrok_auth_token: Optional[str] = None
    ngrok_tunnel_url: Optional[str] = None
    
    # Настройки для продакшена
    webhook_host: Optional[str] = None  # URL в формате https://your-app.vercel.app
    
    # Настройки Яндекс.Музыки
    yandex_music_token: str
    
    @property
    def is_prod(self) -> bool:
        """Проверяет, запущен ли бот в production режиме."""
        return self.bot_env.lower() == "prod"
        
    @property
    def webhook_url(self) -> Optional[str]:
        """Возвращает URL для вебхука."""
        if self.is_prod and self.webhook_host:
            return f"{self.webhook_host}/api/webhook"
        return self.ngrok_tunnel_url
        
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Создаем экземпляр конфигурации
config = Settings()