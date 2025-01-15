"""
Базовые обработчики команд бота.

Этот модуль содержит обработчики основных команд бота,
таких как /start и /help.
"""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from loguru import logger
from bot.utils.downloader import download_and_send_track
from bot.utils.formatting import format_help_message


router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, command: CommandObject):
    """
    Обработчик команды /start.
    
    Если команда содержит параметр download_{track_id}, начинает скачивание трека.
    В противном случае отправляет приветственное сообщение.
    """
    logger.info("=== Начало обработки команды /start ===")
    logger.info(f"Полный текст команды: {message.text}")
    logger.info(f"ID чата: {message.chat.id}")
    logger.info(f"Пользователь: {message.from_user.username}")

    # Получаем аргументы после команды
    args = command.args
    logger.info(f"Аргументы после /start: {args}")

    if args and args.startswith("download_"):
        # Извлекаем ID трека
        track_id = args.replace("download_", "")
        logger.info(f"Найден ID трека для скачивания: {track_id}")

        # Создаем статусное сообщение
        status_message = await message.answer("⏳ Начинаем скачивание...")

        # Удаляем сообщение с командой
        await message.delete()
        logger.info("Сообщение с командой /start удалено")

        logger.info(f"Начинаем скачивание трека {track_id}")
        success = await download_and_send_track(message, track_id, status_message)
        logger.info(f"Скачивание трека {track_id} завершено {'успешно' if success else 'с ошибкой'}")

    else:
        # Формируем полное имя пользователя
        full_name = message.from_user.full_name
        
        # Отправляем приветственное сообщение
        await message.answer(
            f"Привет, {full_name} 👋\n\n"
            "Я помогу тебе найти музыку из Яндекс.Музыки. Вот что я умею:\n\n"
            "🔍 Поиск треков:\n"
            "Просто напиши мне название трека или исполнителя, и я найду его для тебя.\n\n"
            "📱 Inline-режим:\n"
            "Ты можешь искать музыку прямо в любом чате! Просто набери @aamuzbot и текст для поиска.\n\n"
            "❓ Помощь:\n"
            "Используй команду /help, чтобы увидеть список всех команд."
        )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help."""
    await message.answer(format_help_message()) 