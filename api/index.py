from fastapi import FastAPI, Request, HTTPException
from loguru import logger
from api.bot_init import process_update, Settings
import sys

# Настраиваем логирование
logger.remove()  # Удаляем стандартный обработчик
logger.add(sys.stderr, level="DEBUG")  # Добавляем вывод в stderr для Vercel
logger.add("/tmp/bot.log", rotation="1 MB")

# Инициализируем FastAPI и конфигурацию
app = FastAPI()
config = Settings()

logger.info("Starting bot with config: BOT_ENV={}, WEBHOOK_HOST={}", config.bot_env, config.webhook_host)

@app.get("/api/webhook")
async def health_check():
    """
    Проверка работоспособности сервиса.
    """
    logger.debug("Health check endpoint called")
    return {"status": "ok"}

@app.post("/api/webhook")
async def webhook_handler(request: Request):
    """
    Обработчик вебхуков от Telegram.
    """
    try:
        # Логируем заголовки запроса
        headers = dict(request.headers)
        logger.debug("Received webhook request with headers: {}", headers)
        
        # Проверяем секретный токен
        secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if not secret_token:
            logger.warning("No secret token provided")
            raise HTTPException(status_code=401, detail="No secret token")
            
        if secret_token != config.webhook_secret:
            logger.warning("Invalid secret token provided: {}", secret_token)
            raise HTTPException(status_code=401, detail="Invalid secret token")
        
        # Получаем данные запроса
        update_data = await request.json()
        logger.info("Received update: {}", update_data)
        
        # Обрабатываем update от Telegram
        await process_update(update_data)
        logger.debug("Update processed successfully")
        
        return {"status": "ok"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error processing webhook: {}", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 