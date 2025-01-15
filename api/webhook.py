from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.types import Update, Message, InlineQuery
import os
import sys

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    level="DEBUG",
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# Initialize FastAPI
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize bot and dispatcher
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message()
async def handle_message(message: Message):
    try:
        if message.text == "/start":
            await message.answer("Привет! Я бот для поиска и скачивания музыки. Используй инлайн режим для поиска.")
    except Exception as e:
        logger.exception(f"Error in message handler: {e}")
        await message.answer("Произошла ошибка при обработке сообщения. Попробуйте позже.")

@dp.inline_query()
async def handle_inline_query(query: InlineQuery):
    try:
        await query.answer(
            results=[],
            switch_pm_text="Поиск музыки",
            switch_pm_parameter="search"
        )
    except Exception as e:
        logger.exception(f"Error in inline query handler: {e}")

@app.on_event("startup")
async def on_startup():
    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url:
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_webhook(url=webhook_url)
        logger.info(f"Webhook set to {webhook_url}")

@app.on_event("shutdown")
async def on_shutdown():
    await bot.session.close()
    logger.info("Bot session closed")

@app.get("/api/webhook")
async def health_check():
    return {"status": "ok"}

@app.post("/api/webhook")
async def webhook_handler(request: Request):
    """Process Telegram update"""
    try:
        update_data = await request.json()
        update = Update(**update_data)
        await dp.feed_update(bot=bot, update=update)
        return {"status": "ok"}
    except Exception as e:
        logger.exception(f"Error processing update: {e}")
        return {"status": "error", "message": str(e)} 