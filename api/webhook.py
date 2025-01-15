from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.types import Update, Message, InlineQuery
import os
import sys
import asyncio
from contextlib import asynccontextmanager

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Configure logging to use stderr
logger.remove()  # Remove default handler
logger.add(sys.stderr, level="INFO")

# Initialize bot and dispatcher
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

# Register handlers
@dp.message()
async def handle_message(message: Message):
    try:
        logger.info(f"Received message: {message.text}")
        if message.text == "/start":
            logger.info("Sending welcome message...")
            await message.answer("Привет! Я бот для поиска и скачивания музыки. Используй инлайн режим для поиска.")
            logger.info("Welcome message sent")
        
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        try:
            await message.answer("Произошла ошибка при обработке сообщения. Попробуйте позже.")
        except:
            logger.error("Failed to send error message", exc_info=True)

@dp.inline_query()
async def handle_inline_query(query: InlineQuery):
    try:
        logger.info(f"Received inline query: {query.query}")
        await query.answer(
            results=[],
            switch_pm_text="Поиск музыки",
            switch_pm_parameter="search"
        )
        logger.info("Inline query response sent")
        
    except Exception as e:
        logger.error(f"Error processing inline query: {e}", exc_info=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle management
    """
    try:
        # Configure webhook on startup
        logger.info("Initializing bot...")
        webhook_url = os.getenv("WEBHOOK_URL")
        if webhook_url:
            await bot.delete_webhook(drop_pending_updates=True)
            await bot.set_webhook(url=webhook_url)
            logger.info(f"Webhook set: {webhook_url}")
        
        yield
        
    except Exception as e:
        logger.error(f"Error in application lifecycle: {e}", exc_info=True)
        raise
    finally:
        # Cleanup on shutdown
        logger.info("Shutting down bot...")
        await bot.session.close()

# Initialize FastAPI with lifecycle manager
app = FastAPI(lifespan=lifespan)

# Configure CORS
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
    Service health check endpoint.
    """
    return {"status": "ok"}

@app.post("/api/webhook")
async def webhook_handler(request: Request):
    """
    Telegram webhook handler.
    """
    try:
        # Get request data
        update_data = await request.json()
        logger.info(f"Received update: {update_data}")
        
        # Create Update object from received data
        update = Update(**update_data)
        
        # Process Telegram update
        await dp.feed_update(bot=bot, update=update)
        logger.info("Update processed successfully")
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        return {"status": "error", "message": str(e)} 