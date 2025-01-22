"""
Скрипт для обновления веб-хука бота.
"""

import asyncio
from aiogram import Bot
from bot.config.config import config


async def update_webhook():
    """Обновляет веб-хук бота."""
    bot = Bot(token=config.bot_token)
    
    # Сначала удалим текущий веб-хук
    await bot.delete_webhook()
    
    # Установим новый веб-хук
    webhook_url = f"{config.webhook_url}/webhook"
    result = await bot.set_webhook(
        url=webhook_url,
        drop_pending_updates=True
    )
    
    if result:
        print(f"Веб-хук успешно установлен на {webhook_url}")
    else:
        print("Ошибка при установке веб-хука")
    
    # Проверим информацию о веб-хуке
    webhook_info = await bot.get_webhook_info()
    print(f"\nИнформация о веб-хуке:")
    print(f"URL: {webhook_info.url}")
    print(f"Pending updates: {webhook_info.pending_update_count}")
    print(f"Last error: {webhook_info.last_error_message if webhook_info.last_error_message else 'Нет ошибок'}")
    
    await bot.session.close()


if __name__ == "__main__":
    asyncio.run(update_webhook()) 