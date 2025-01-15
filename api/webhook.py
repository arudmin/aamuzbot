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

# Configure logging to use stderr with more detailed format
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    level="DEBUG",
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# Initialize bot and dispatcher
logger.info("Initializing bot with token length: {}", len(os.getenv("BOT_TOKEN", "")))
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

# Register handlers
@dp.message()
async def handle_message(message: Message):
    try:
        logger.info("Message handler called with text: {}", message.text)
        logger.debug("Full message object: {}", message)
        
        if message.text == "/start":
            logger.info("Processing /start command from user {}", message.from_user.id)
            await message.answer("Привет! Я бот для поиска и скачивания музыки. Используй инлайн режим для поиска.")
            logger.info("Welcome message sent to user {}", message.from_user.id)
        
    except Exception as e:
        logger.exception("Error in message handler: {}", str(e))
        try:
            await message.answer("Произошла ошибка при обработке сообщения. Попробуйте позже.")
        except:
            logger.exception("Failed to send error message to user")

@dp.inline_query()
async def handle_inline_query(query: InlineQuery):
    try:
        logger.info("Inline query handler called with query: {}", query.query)
        logger.debug("Full inline query object: {}", query)
        
        await query.answer(
            results=[],
            switch_pm_text="Поиск музыки",
            switch_pm_parameter="search"
        )
        logger.info("Inline query response sent to user {}", query.from_user.id)
        
    except Exception as e:
        logger.exception("Error in inline query handler: {}", str(e))

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle management
    """
    try:
        # Configure webhook on startup
        logger.info("Starting application lifecycle...")
        webhook_url = os.getenv("WEBHOOK_URL")
        if webhook_url:
            logger.info("Setting webhook URL: {}", webhook_url)
            await bot.delete_webhook(drop_pending_updates=True)
            await bot.set_webhook(url=webhook_url)
            logger.info("Webhook successfully set")
        else:
            logger.warning("No webhook URL provided")
        
        yield
        
    except Exception as e:
        logger.exception("Error in application lifecycle: {}", str(e))
        raise
    finally:
        logger.info("Cleaning up resources...")
        await bot.session.close()
        logger.info("Cleanup completed")

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
        logger.info("Received webhook update: {}", update_data)
        
        # Create Update object from received data
        logger.debug("Creating Update object from data")
        update = Update(**update_data)
        logger.info("Update object created successfully")
        
        # Process Telegram update
        logger.debug("Starting update processing")
        await dp.feed_update(bot=bot, update=update)
        logger.info("Update processed successfully")
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.exception("Error processing webhook: {}", str(e))
        return {"status": "error", "message": str(e)} 