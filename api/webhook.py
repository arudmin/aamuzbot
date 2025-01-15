from fastapi import FastAPI, Request
from bot.web.app import init_app
from bot.config.config import config
from loguru import logger

# Инициализируем FastAPI
app = FastAPI()

# Инициализируем бота
bot_app = init_app()

@app.post("/api/webhook")
async def webhook_handler(request: Request):
    """
    Обработчик вебхуков от Telegram.
    """
    try:
        # Получаем данные запроса
        update_data = await request.json()
        logger.info(f"Получен update: {update_data}")
        
        # Обрабатываем update от Telegram
        await bot_app['bot'].process_update(update_data)
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Ошибка при обработке вебхука: {e}", exc_info=True)
        return {"status": "error", "message": str(e)} 