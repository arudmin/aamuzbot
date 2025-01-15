from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineQuery
from loguru import logger
import os

# Инициализируем бота и диспетчер
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

@dp.message()
async def handle_message(message: Message):
    """
    Обработчик всех сообщений.
    """
    try:
        logger.info(f"Получено сообщение: {message.text}")
        if message.text == "/start":
            await message.answer("Привет! Я бот для поиска и скачивания музыки. Используй инлайн режим для поиска.")
        
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}", exc_info=True)

@dp.inline_query()
async def handle_inline_query(query: InlineQuery):
    """
    Обработчик инлайн запросов.
    """
    try:
        logger.info(f"Получен инлайн запрос: {query.query}")
        # Заглушка для инлайн режима
        await query.answer(
            results=[],
            switch_pm_text="Поиск музыки",
            switch_pm_parameter="search"
        )
        
    except Exception as e:
        logger.error(f"Ошибка при обработке инлайн запроса: {e}", exc_info=True) 