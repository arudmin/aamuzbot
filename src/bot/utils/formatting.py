"""
Утилиты для форматирования сообщений.

Этот модуль содержит функции для форматирования различных типов сообщений,
включая результаты поиска, информацию о треках и справочные сообщения.
"""

from loguru import logger
from typing import List, Dict


def format_duration(duration_ms: int) -> str:
    """
    Форматирует длительность из миллисекунд в формат MM:SS.
    
    Args:
        duration_ms: Длительность в миллисекундах
        
    Returns:
        Отформатированная строка в формате MM:SS
    """
    duration_min = duration_ms // 60000
    duration_sec = (duration_ms // 1000) % 60
    return f"{duration_min:02d}:{duration_sec:02d}"


def format_track_message(track: Dict, bot_username: str) -> str:
    """
    Форматирует сообщение с информацией о треке.
    
    Args:
        track: Словарь с информацией о треке
        bot_username: Имя бота для формирования ссылки на скачивание
        
    Returns:
        Отформатированное сообщение с информацией о треке
    """
    title = track['title']
    artists = ", ".join(track['artists'])
    duration = format_duration(track['duration_ms'])
    
    # Формируем ссылку на скачивание
    download_link = f"https://t.me/{bot_username}?start=download_{track['id']}"
    logger.debug(f"Формирую ссылку на скачивание: {download_link}")
    
    return (
        f"🎵 <b>{title}</b>\n"
        f"👤 {artists}\n"
        f"⏱ {duration}\n"
        f"<a href='{track['track_link']}'>Открыть в Яндекс.Музыке</a> | "
        f"<a href='{download_link}'>Скачать MP3</a>"
    )


def format_search_results(tracks: List[Dict], bot_username: str) -> str:
    """
    Форматирует результаты поиска треков.
    
    Args:
        tracks: Список словарей с информацией о треках
        bot_username: Имя бота для формирования ссылок на скачивание
        
    Returns:
        Отформатированное сообщение со списком найденных треков
    """
    if not tracks:
        return "❌ Ничего не найдено"
    
    result = "🔍 Результаты поиска:\n\n"
    for track in tracks:
        result += format_track_message(track, bot_username) + "\n\n"
    
    return result


def format_help_message() -> str:
    """
    Форматирует справочное сообщение со списком команд.
    
    Returns:
        Отформатированное справочное сообщение
    """
    return (
        "<b>📖 Доступные команды</b>\n\n"
        "• /start - начало работы с ботом\n"
        "• /help - эта справка\n\n"
        "Для поиска музыки просто отправьте название трека или исполнителя.\n"
        "Также вы можете использовать инлайн режим в других чатах: @aamuzbot название"
    ) 