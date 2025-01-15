from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineQuery
from loguru import logger
import os
import asyncio

# Настраиваем логирование
logger.add("bot_polling.log", rotation="1 MB", enqueue=True)

async def main():
    # Инициализируем бота и диспетчер
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()

    # Регистрируем хендлеры
    @dp.message()
    async def handle_message(message: Message):
        try:
            logger.info(f"Получено сообщение: {message.text}")
            if message.text == "/start":
                logger.info("Отправляем приветственное сообщение...")
                await message.answer("Привет! Я бот для поиска и скачивания музыки. Используй инлайн режим для поиска.")
                logger.info("Приветственное сообщение отправлено")
            
        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения: {e}", exc_info=True)
            try:
                await message.answer("Произошла ошибка при обработке сообщения. Попробуйте позже.")
            except:
                logger.error("Не удалось отправить сообщение об ошибке", exc_info=True)

    @dp.inline_query()
    async def handle_inline_query(query: InlineQuery):
        try:
            logger.info(f"Получен инлайн запрос: {query.query}")
            await query.answer(
                results=[],
                switch_pm_text="Поиск музыки",
                switch_pm_parameter="search"
            )
            logger.info("Ответ на инлайн запрос отправлен")
            
        except Exception as e:
            logger.error(f"Ошибка при обработке инлайн запроса: {e}", exc_info=True)

    try:
        logger.info("Запуск бота в режиме polling...")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        logger.info("Завершение работы бота...")
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main()) 