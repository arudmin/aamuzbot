from fastapi import FastAPI, Request
from loguru import logger
import sys
import os

# Добавляем путь к корневой директории проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Настраиваем логирование
logger.add("/tmp/bot.log", rotation="1 MB")

# Инициализируем FastAPI
app = FastAPI()

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
        
        # Обрабатываем update от Telegram
        from src.bot.web.app import process_update
        await process_update(update_data)
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Ошибка при обработке вебхука: {e}", exc_info=True)
        return {"status": "error", "message": str(e)} 