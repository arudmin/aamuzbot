"""
Утилиты для скачивания музыки.

Этот модуль содержит функции для скачивания треков и отправки их пользователю.
"""

import os
import asyncio
from typing import Optional
from aiogram.types import Message, FSInputFile
from loguru import logger

from bot.services.music import music_service


async def download_and_send_track(message: Message, track_id: str, status_message: Optional[Message] = None) -> bool:
    """
    Скачивает трек и отправляет его пользователю.
    Запускает скачивание в фоновом режиме, чтобы не блокировать обработку других команд.
    
    Args:
        message: Сообщение пользователя
        track_id: ID трека в Яндекс.Музыке
        status_message: Сообщение со статусом загрузки
        
    Returns:
        True если скачивание успешно, False в случае ошибки
    """
    # Создаем задачу для скачивания
    download_task = asyncio.create_task(_download_and_send(message, track_id, status_message))
    
    # Добавляем обработчик ошибок
    download_task.add_done_callback(lambda t: logger.error(f"Ошибка при скачивании: {t.exception()}") if t.exception() else None)
    
    return True


async def _download_and_send(message: Message, track_id: str, status_message: Optional[Message] = None) -> None:
    """
    Внутренняя функция для скачивания и отправки трека.
    
    Args:
        message: Сообщение пользователя
        track_id: ID трека в Яндекс.Музыке
        status_message: Сообщение со статусом загрузки
    """
    try:
        # Получаем информацию о треке
        track_info = await music_service.get_track_full_info(track_id)
        if not track_info:
            await status_message.edit_text("❌ Трек не найден")
            return
        
        # Формируем строку с информацией о треке
        track_str = f"{track_info['title']} - {', '.join(track_info['artists'])}"
        
        # Получаем ссылку на скачивание
        download_url = await music_service.get_track_download_info(track_id)
        if not download_url:
            await status_message.edit_text(f"❌ Не удалось получить ссылку на скачивание для трека {track_str}")
            return
        
        # Обновляем статус
        await status_message.edit_text(f"⬇️ Скачиваю трек {track_str}...")
        
        # Формируем имя файла
        filename = f"{track_str}.mp3"
        filename = sanitize_filename(filename)
        temp_path = f"/tmp/{filename}"
        
        # Скачиваем файл
        await music_service.download_track(download_url, temp_path)
        
        # Обновляем статус
        await status_message.edit_text(f"📝 Устанавливаю метаданные для {track_str}...")
        
        # Устанавливаем метаданные
        await music_service.set_track_metadata(temp_path, track_info)
        
        # Обновляем статус
        await status_message.edit_text(f"📤 Отправляю файл {track_str}...")
        
        # Отправляем файл
        audio = FSInputFile(temp_path)
        await message.answer_audio(
            audio,
            title=track_info['title'],
            performer=", ".join(track_info['artists']),
            duration=track_info['duration_ms'] // 1000
        )
        
        # Удаляем временный файл
        os.remove(temp_path)
        logger.debug(f"Временный файл {temp_path} удален")
        
        # Обновляем статус
        await status_message.edit_text(f"✅ Трек {track_str} успешно загружен!")
        
    except Exception as e:
        error_msg = f"❌ Ошибка при скачивании трека {track_str}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        if status_message:
            await status_message.edit_text(error_msg)


def sanitize_filename(filename: str) -> str:
    """
    Очищает имя файла от недопустимых символов.
    
    Args:
        filename: Исходное имя файла
        
    Returns:
        Очищенное имя файла
    """
    # Заменяем недопустимые символы на _
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename 