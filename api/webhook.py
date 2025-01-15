from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import sys

# Добавляем путь к исходникам бота
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bot.main import process_update
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from bot.config.config import config

# Инициализируем бота и диспетчер
bot = Bot(token=config.bot_token)
dp = Dispatcher()

async def handler(request):
    """
    Обработчик вебхуков для Vercel Serverless
    """
    # Проверяем метод
    if request.method == "POST":
        # Получаем данные
        update_data = await request.json()
        
        # Создаем объект Update
        update = Update(**update_data)
        
        # Обрабатываем update
        await dp.feed_update(bot=bot, update=update)
        
        return {"statusCode": 200}
    
    # Для GET запросов возвращаем статус
    return {"statusCode": 200, "body": "Bot webhook is working"} 