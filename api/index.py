from fastapi import FastAPI, Request, HTTPException
from loguru import logger
from api.bot_init import process_update, Settings

# Настраиваем логирование
logger.add("/tmp/bot.log", rotation="1 MB")

# Инициализируем FastAPI и конфигурацию
app = FastAPI()
config = Settings()

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
        # Проверяем секретный токен
        secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if not secret_token or secret_token != config.webhook_secret:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        # Получаем данные запроса
        update_data = await request.json()
        logger.info(f"Получен update: {update_data}")
        
        # Обрабатываем update от Telegram
        await process_update(update_data)
        
        return {"status": "ok"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при обработке вебхука: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 