from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from api.bot_init import process_update
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

# Инициализируем бота
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

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