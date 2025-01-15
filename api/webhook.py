from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.types import Update, Message, InlineQuery
import os
import asyncio

# Настраиваем логирование
logger.add("/tmp/bot.log", rotation="1 MB")

# Инициализируем FastAPI
app = FastAPI()

# Настраиваем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/api/webhook")
async def health_check():
    """
    Проверка работоспособности сервиса.
    """
    return {"status": "ok"}

@app.post("/api/webhook")
async def webhook_handler(request: Request):
    """
    Обработчик вебхуков от Telegram.
    """
    try:
        # Получаем данные запроса
        update_data = await request.json()
        logger.info(f"Получен update: {update_data}")
        
        # Создаем объект Update из полученных данных
        update = Update(**update_data)
        
        # Создаем новый event loop для обработки update
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Обрабатываем update от Telegram
            loop.run_until_complete(dp.feed_update(bot=bot, update=update))
        finally:
            # Закрываем loop после обработки
            loop.close()
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Ошибка при обработке вебхука: {e}", exc_info=True)
        return {"status": "error", "message": str(e)} 