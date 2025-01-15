from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.types import Update, Message, InlineQuery
from aiogram.client.session.aiohttp import AiohttpSession
import os
import asyncio
from contextlib import asynccontextmanager

# Настраиваем логирование
logger.add("/tmp/bot.log", rotation="1 MB")

# Создаем сессию для бота
session = AiohttpSession()

# Инициализируем бота и диспетчер
bot = Bot(token=os.getenv("BOT_TOKEN"), session=session)
dp = Dispatcher()

# Регистрируем хендлеры
@dp.message()
async def handle_message(message: Message):
    try:
        logger.info(f"Получено сообщение: {message.text}")
        if message.text == "/start":
            await message.answer("Привет! Я бот для поиска и скачивания музыки. Используй инлайн режим для поиска.")
        
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}", exc_info=True)

@dp.inline_query()
async def handle_inline_query(query: InlineQuery):
    try:
        logger.info(f"Получен инлайн запрос: {query.query}")
        await query.answer(
            results=[],
            switch_pm_text="Поиск музыки",
            switch_pm_parameter="search"
        )
        
    except Exception as e:
        logger.error(f"Ошибка при обработке инлайн запроса: {e}", exc_info=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения
    """
    # Настраиваем вебхук при запуске
    logger.info("Инициализация бота...")
    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url:
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_webhook(url=webhook_url)
        logger.info(f"Установлен webhook: {webhook_url}")
    
    yield
    
    # Очистка при завершении
    logger.info("Завершение работы бота...")
    await session.close()

# Инициализируем FastAPI с менеджером жизненного цикла
app = FastAPI(lifespan=lifespan)

# Настраиваем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        
        # Обрабатываем update от Telegram
        await dp.feed_update(bot=bot, update=update)
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Ошибка при обработке вебхука: {e}", exc_info=True)
        return {"status": "error", "message": str(e)} 