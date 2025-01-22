"""
Инициализация обработчиков бота.

Этот модуль экспортирует функцию register_handlers для регистрации всех обработчиков бота.
"""

from aiogram import Dispatcher
from .base import router as base_router
from .music import router as music_router
from .inline import router as inline_router


def register_handlers(dp: Dispatcher) -> None:
    """
    Регистрирует все обработчики бота.
    
    Args:
        dp: Экземпляр диспетчера
    """
    dp.include_router(base_router)
    dp.include_router(music_router)
    dp.include_router(inline_router) 