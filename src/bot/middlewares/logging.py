from typing import Any, Awaitable, Callable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from loguru import logger


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        # Log incoming update
        logger.info(f"Incoming update: {event}")
        
        try:
            return await handler(event, data)
        except Exception as e:
            logger.error(f"Error processing update: {e}")
            raise 