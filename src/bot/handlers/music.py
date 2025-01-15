"""
Обработчики команд для работы с музыкой.
"""

import re
from aiogram import Router, F
from aiogram.types import Message
from loguru import logger
from aiogram.filters import Command
from bot.config.config import config
from bot.services.music import music_service
from bot.utils.downloader import download_and_send_track
from bot.utils.formatting import format_search_results

router = Router()

@router.message(Command(commands=["music"]))
async def cmd_music_help(message: Message) -> None:
    """Отправляет справку по музыкальным командам."""
    help_text = (
        "<b>🎵 Музыкальные команды</b>\n\n"
        "• Отправьте название трека или исполнителя для поиска\n"
        "• Используйте инлайн режим для поиска в других чатах: @aamuzbot название\n"
        "• /search название - поиск треков\n"
        "• /music - эта справка"
    )
    await message.answer(help_text, parse_mode="HTML")

@router.message(F.text.regexp(r"^/download_(\d+)$"))
async def cmd_download(message: Message) -> None:
    """Скачивает трек по ID."""
    match = re.match(r"^/download_(\d+)$", message.text)
    if not match:
        await message.answer("❌ Неверный формат команды")
        return
        
    track_id = match.group(1)
    logger.info(f"Получена команда скачивания: {message.text}")
    
    await download_and_send_track(message, track_id)

@router.message(Command(commands=["search"]))
async def cmd_search(message: Message) -> None:
    """Ищет треки по запросу."""
    # Получаем текст после команды
    query = message.text.replace("/search", "").strip()
    if not query:
        await message.answer("Введите название трека или исполнителя для поиска")
        return
        
    try:
        # Отправляем сообщение о поиске
        status = await message.answer("🔍 Ищу трек...")
        
        # Получаем информацию о боте
        bot_info = await message.bot.get_me()
        
        # Ищем треки
        tracks = await music_service.search_track(query, limit=5, fetch_download_info=False)
        if not tracks:
            await status.edit_text("❌ Ничего не найдено")
            return
            
        # Форматируем результаты
        response_text = format_search_results(tracks, bot_info.username)
        await status.edit_text(response_text, parse_mode="HTML", disable_web_page_preview=True)
        
    except Exception as e:
        logger.error(f"Ошибка при поиске треков: {e}", exc_info=True)
        await status.edit_text(f"❌ Ошибка при поиске: {str(e)}")

@router.message(~F.text.startswith('/') & ~F.via_bot)
async def handle_text_search(message: Message) -> None:
    """Обрабатывает текстовые сообщения как поисковые запросы."""
    try:
        # Отправляем сообщение о поиске
        status = await message.answer("🔍 Ищу трек...")
        
        # Получаем информацию о боте
        bot_info = await message.bot.get_me()
        
        # Ищем треки
        tracks = await music_service.search_track(message.text, limit=5, fetch_download_info=False)
        if not tracks:
            await status.edit_text("❌ Ничего не найдено")
            return
            
        # Форматируем результаты
        response_text = format_search_results(tracks, bot_info.username)
        await status.edit_text(response_text, parse_mode="HTML", disable_web_page_preview=True)
        
    except Exception as e:
        logger.error(f"Ошибка при поиске треков: {e}", exc_info=True)
        await status.edit_text(f"❌ Ошибка при поиске: {str(e)}") 