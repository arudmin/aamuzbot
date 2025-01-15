"""
Утилиты для скачивания и отправки музыкальных треков.

Этот модуль предоставляет функции для скачивания треков с Яндекс.Музыки
и отправки их пользователям через Telegram Bot API.
"""

import os
import tempfile
import aiohttp
import mutagen
from loguru import logger
from aiogram.types import Message, FSInputFile
from typing import Optional, Union
from bot.services.music import music_service
import re


def sanitize_filename(filename: str) -> str:
    """
    Очищает имя файла от недопустимых символов.
    
    Args:
        filename: Исходное имя файла
        
    Returns:
        Безопасное имя файла
    """
    # Заменяем недопустимые символы на подчеркивание
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Убираем множественные подчеркивания
    filename = re.sub(r'_+', '_', filename)
    # Убираем подчеркивания в начале и конце
    filename = filename.strip('_')
    return filename


async def download_and_send_track(
    message: Message,
    track_id: Union[int, str],
    status_message: Optional[Message] = None
) -> bool:
    """
    Скачивает трек и отправляет его пользователю.

    Args:
        message: Сообщение от пользователя
        track_id: ID трека в Яндекс.Музыке
        status_message: Сообщение со статусом загрузки

    Returns:
        bool: True если трек успешно скачан и отправлен, False в случае ошибки
    """
    try:
        # Создаем статусное сообщение, если оно не передано
        if not status_message:
            status_message = await message.answer("⏳ Получаем информацию о треке...")

        # Получаем информацию о треке
        track_info = await music_service.get_track_full_info(track_id)
        if not track_info:
            await status_message.edit_text("❌ Трек не найден")
            return False

        # Формируем строку с информацией о треке
        track_str = f"{track_info['title']} - {', '.join(track_info['artists'])}"

        # Получаем ссылку на скачивание
        download_link = track_info.get('download_link')
        if not download_link:
            await status_message.edit_text(f"❌ Не удалось получить ссылку на скачивание для трека:\n{track_str}")
            return False

        # Создаем имя файла из названия трека и исполнителей
        filename = f"{track_info['title']} - {', '.join(track_info['artists'])}.mp3"
        # Очищаем имя файла от недопустимых символов
        safe_filename = sanitize_filename(filename)
        
        # Создаем временный файл для скачивания
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, safe_filename)

        try:
            # Скачиваем файл
            await status_message.edit_text(f"⬇️ Скачиваем трек:\n{track_str}")

            async with aiohttp.ClientSession() as session:
                async with session.get(download_link) as response:
                    if response.status != 200:
                        await status_message.edit_text(f"❌ Ошибка при скачивании трека:\n{track_str}")
                        return False

                    content = await response.read()
                    with open(temp_file, 'wb') as f:
                        f.write(content)

            # Устанавливаем метаданные
            await status_message.edit_text(f"📝 Устанавливаем метаданные:\n{track_str}")

            audio = mutagen.File(temp_file)
            if audio:
                audio['title'] = track_info['title']
                audio['artist'] = ", ".join(track_info['artists'])
                audio.save()

            # Отправляем файл
            await status_message.edit_text(f"📤 Отправляем файл:\n{track_str}")

            audio_file = FSInputFile(temp_file, filename=safe_filename)
            await message.answer_audio(
                audio_file,
                title=track_info['title'],
                performer=", ".join(track_info['artists']),
                duration=track_info['duration_ms'] // 1000
            )

            # Удаляем временный файл
            if os.path.exists(temp_file):
                os.unlink(temp_file)
                logger.debug(f"Временный файл {temp_file} удален")

            # Удаляем сообщение о статусе
            await status_message.delete()

            return True

        except Exception as e:
            logger.error(f"Ошибка при скачивании трека {track_str}: {str(e)}", exc_info=True)
            await status_message.edit_text(f"❌ Ошибка при скачивании:\n{track_str}\n\n{str(e)}")
            return False

    except Exception as e:
        logger.error(f"Ошибка при скачивании трека {track_id}: {str(e)}", exc_info=True)
        if status_message:
            await status_message.edit_text(f"❌ Ошибка при скачивании трека {track_id}:\n{str(e)}")
        return False 