"""
Модуль конфигурации бота.

Этот модуль содержит настройки и конфигурацию бота, включая:
- Параметры подключения к Telegram API
- Настройки веб-сервера
- Конфигурацию ngrok для туннелирования
- Токены доступа к внешним сервисам

Использование:
    from bot.config.config import config
    
    webhook_url = config.webhook_url
    bot_token = config.bot_token
"""

from os import getenv
from pydantic_settings import BaseSettings
from pydantic import SecretStr
from loguru import logger
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """
    Класс настроек приложения.
    
    Attributes:
        bot_token (SecretStr): Токен Telegram бота
        webhook_host (str): Домен для вебхука
        webhook_path (str): Путь для вебхука
        webapp_host (str): Хост веб-приложения
        webapp_port (int): Порт веб-приложения
        ngrok_auth_token (str): Токен авторизации ngrok
        yandex_music_token (str): Токен Яндекс.Музыки
        _ngrok_tunnel_url (Optional[str]): URL туннеля ngrok
    """
    
    bot_token: SecretStr
    webhook_host: str
    webhook_path: str
    webapp_host: str
    webapp_port: int
    ngrok_auth_token: str
    yandex_music_token: str
    _ngrok_tunnel_url: Optional[str] = None

    @property
    def ngrok_tunnel_url(self) -> str:
        """URL туннеля ngrok."""
        return self._ngrok_tunnel_url or ""

    @ngrok_tunnel_url.setter
    def ngrok_tunnel_url(self, value: str):
        """Установка URL туннеля ngrok."""
        self._ngrok_tunnel_url = value

    @property
    def webhook_url(self) -> str:
        """Полный URL для вебхука."""
        return f"{self.ngrok_tunnel_url}/webhook"

    class Config:
        """Конфигурация для pydantic."""
        env_file = ".env"
        env_file_encoding = "utf-8"


def setup_ngrok() -> Settings:
    """
    Настройка и запуск туннеля ngrok.
    
    Returns:
        Settings: Объект настроек с установленным URL туннеля
        
    Raises:
        ValueError: Если не установлен токен ngrok
    """
    try:
        from pyngrok import ngrok
        from pyngrok.conf import PyngrokConfig

        settings = Settings()

        # Проверяем наличие токена
        if not settings.ngrok_auth_token:
            raise ValueError("NGROK_AUTH_TOKEN not set in .env")

        # Настраиваем ngrok
        pyngrok_config = PyngrokConfig(auth_token=settings.ngrok_auth_token)
        ngrok.set_auth_token(settings.ngrok_auth_token)

        # Убиваем существующие процессы
        ngrok.kill()

        # Запускаем новый туннель
        http_tunnel = ngrok.connect(settings.webapp_port, bind_tls=True)
        settings.webhook_host = http_tunnel.public_url
        settings.ngrok_tunnel_url = http_tunnel.public_url
        logger.info(f"Ngrok tunnel established: {settings.ngrok_tunnel_url}")
        return settings

    except Exception as e:
        logger.error(f"Failed to setup ngrok: {e}")
        # Возвращаем настройки без ngrok
        return Settings()


# Создаем экземпляр конфигурации с настройкой ngrok
config = setup_ngrok()