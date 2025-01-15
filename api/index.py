from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.types import Update, Message, InlineQuery
import os

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

@app.on_event("startup")
async def startup():
    """
    Инициализация бота при запуске приложения.
    """
    logger.info("Инициализация бота...")
    await bot.delete_webhook(drop_pending_updates=True)
    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url:
        await bot.set_webhook(url=webhook_url)
        logger.info(f"Установлен webhook: {webhook_url}")

@app.on_event("shutdown")
async def shutdown():
    """
    Корректное завершение работы бота.
    """
    logger.info("Завершение работы бота...")
    await bot.session.close()

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
        
        # Обрабатываем update от Telegram
        await dp.feed_update(bot=bot, update=update)
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Ошибка при обработке вебхука: {e}", exc_info=True)
        return {"status": "error", "message": str(e)} 