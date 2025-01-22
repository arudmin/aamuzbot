from fastapi import FastAPI, Request, HTTPException
from loguru import logger
from api.bot_init import process_update, Settings
import sys

# Настраиваем логирование
logger.remove()  # Удаляем стандартный обработчик
logger.add(sys.stderr, level="DEBUG")  # Добавляем вывод в stderr
logger.add("bot.log", rotation="1 MB")  # Добавляем файловый лог

# Инициализируем FastAPI и конфигурацию
app = FastAPI()
config = Settings()

logger.info(f"Starting bot with config: BOT_ENV={config.bot_env}, WEBHOOK_HOST={config.webhook_host}")

@app.get("/webhook")
async def health_check():
    """
    Проверка работоспособности сервиса.
    """
    logger.debug("Health check endpoint called")
    return {"status": "ok"}

@app.post("/webhook")
async def webhook_handler(request: Request):
    """
    Обработчик вебхуков от Telegram.
    """
    try:
        # Логируем заголовки запроса
        headers = dict(request.headers)
        logger.debug(f"Received webhook request with headers: {headers}")
        
        # Проверяем секретный токен
        secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        logger.debug(f"Received secret token: {secret_token}")
        logger.debug(f"Expected secret token: {config.webhook_secret}")
        
        if config.webhook_secret and (not secret_token or secret_token != config.webhook_secret):
            logger.warning(f"Invalid secret token provided: {secret_token}")
            raise HTTPException(status_code=401, detail="Invalid secret token")
        
        # Получаем данные запроса
        update_data = await request.json()
        logger.info(f"Received update: {update_data}")
        
        # Обрабатываем update от Telegram
        await process_update(update_data)
        logger.debug("Update processed successfully")
        
        return {"status": "ok"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 