"""
Конфигурация бота.

Этот модуль содержит настройки для работы бота в разных окружениях (dev/prod).
"""

import os
from pydantic import BaseModel
from pyngrok import ngrok
from loguru import logger


class Settings(BaseModel):
    """Настройки бота."""
    # Основные настройки
    bot_token: str
    webhook_host: str = ""
    webhook_path: str = "/webhook"
    webapp_host: str = "0.0.0.0"
    webapp_port: int = 8000
    
    # Настройки Яндекс.Музыки
    yandex_music_token: str
    
    # Настройки окружения
    environment: str = "dev"  # dev или prod
    
    # Настройки ngrok (только для dev)
    ngrok_auth_token: str = ""
    _ngrok_tunnel: object = None
    
    @property
    def is_dev(self) -> bool:
        """Проверяет, запущен ли бот в dev режиме."""
        return self.environment.lower() == "dev"
    
    @property
    def webhook_url(self) -> str:
        """Возвращает полный URL для вебхука."""
        return f"{self.webhook_host}{self.webhook_path}"
    
    def setup_ngrok(self) -> None:
        """
        Настраивает ngrok туннель для локальной разработки.
        Вызывается только в dev режиме.
        """
        if not self.is_dev:
            return
            
        if self.ngrok_auth_token:
            ngrok.set_auth_token(self.ngrok_auth_token)
        
        # Создаем туннель
        self._ngrok_tunnel = ngrok.connect(self.webapp_port)
        tunnel_url = self._ngrok_tunnel.public_url
        
        if tunnel_url.startswith("http://"):
            tunnel_url = tunnel_url.replace("http://", "https://")
            
        self.webhook_host = tunnel_url
        logger.info(f"Ngrok tunnel established: {self.webhook_host}")
    
    def cleanup(self) -> None:
        """Очищает ресурсы при завершении работы."""
        if self.is_dev and self._ngrok_tunnel:
            ngrok.disconnect(self._ngrok_tunnel.public_url)
            ngrok.kill()


# Загружаем настройки из переменных окружения
config = Settings(
    bot_token=os.getenv("BOT_TOKEN", ""),
    yandex_music_token=os.getenv("YANDEX_MUSIC_TOKEN", ""),
    environment=os.getenv("BOT_ENV", "dev"),
    ngrok_auth_token=os.getenv("NGROK_AUTH_TOKEN", ""),
    webhook_host=os.getenv("WEBHOOK_HOST", ""),  # Используется только в prod
)