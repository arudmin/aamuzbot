"""
Обработчики inline-запросов для Telegram бота.

Этот модуль содержит обработчики для обработки inline-запросов в Telegram боте.
Он предоставляет функциональность для поиска и обмена музыкальными треками
прямо в любом чате с помощью inline-режима бота.

Примечание:
    Для работы этих обработчиков необходимо включить inline-режим в BotFather.
"""

from aiogram import Router, F
from aiogram.types import (
    InlineQuery, 
    InlineQueryResultArticle, 
    InputTextMessageContent
)
from bot.services.music import music_service
from bot.utils.formatting import format_duration, format_track_message
import hashlib
import asyncio
from loguru import logger


# Инициализация роутера для обработчиков inline-запросов
router = Router()


@router.inline_query()
async def inline_search(query: InlineQuery) -> None:
    """
    Обработка inline-запросов для поиска музыки.
    
    Этот обработчик обрабатывает inline-запросы и возвращает список треков,
    соответствующих поисковому запросу. Каждый результат содержит информацию
    о треке и команду для скачивания.
    
    Аргументы:
        query (InlineQuery): Inline-запрос от Telegram, содержащий текст поиска
    
    Возвращает:
        None: Результаты отправляются обратно в Telegram через query.answer()
    """
    try:
        logger.info(f"Получен inline-запрос: {query.query}")
        
        # Обработка пустого запроса с помощью сообщения-подсказки
        if not query.query:
            empty_result = InlineQueryResultArticle(
                id="empty",
                title="Поиск музыки",
                description="Введите название трека или исполнителя",
                input_message_content=InputTextMessageContent(
                    message_text="Для поиска музыки введите название трека или исполнителя"
                )
            )
            await query.answer([empty_result], cache_time=1)
            logger.info("Отправлен ответ на пустой запрос")
            return

        # Быстрый поиск треков без получения информации о скачивании
        try:
            logger.info("Начинаем поиск треков...")
            tracks = await asyncio.wait_for(
                music_service.search_track(query.query, limit=10, fetch_download_info=False),
                timeout=10.0
            )
            logger.info(f"Найдено треков: {len(tracks)}")
        except asyncio.TimeoutError:
            logger.warning("Превышен таймаут поиска")
            timeout_result = InlineQueryResultArticle(
                id="timeout",
                title="Поиск занял слишком много времени",
                description="Пожалуйста, попробуйте еще раз",
                input_message_content=InputTextMessageContent(
                    message_text="⚠️ Поиск занял слишком много времени. Пожалуйста, попробуйте еще раз."
                )
            )
            await query.answer([timeout_result], cache_time=1)
            return
        
        # Получаем информацию о боте
        bot_info = await query.bot.get_me()
        bot_username = bot_info.username
        
        # Обработка и форматирование результатов поиска
        results = []
        for track in tracks:
            try:
                logger.debug(f"Обработка трека: {track}")
                # Генерация уникального ID результата на основе ID трека
                result_id = hashlib.md5(str(track['id']).encode()).hexdigest()
                logger.debug(f"Сгенерирован ID результата: {result_id}")
                
                # Форматирование информации о треке
                artists = ", ".join(track['artists'])
                duration_str = format_duration(track['duration_ms'])
                message_text = format_track_message(track, bot_username)
                
                # Создание статьи с результатом inline-запроса
                result = InlineQueryResultArticle(
                    id=result_id,
                    title=f"🎵 {track['title']}",
                    description=f"{artists} • {duration_str}",
                    input_message_content=InputTextMessageContent(
                        message_text=message_text,
                        disable_web_page_preview=True,
                        parse_mode="HTML"
                    )
                )
                results.append(result)
                logger.debug("Результат успешно добавлен в список")
            except Exception as e:
                logger.error(f"Ошибка при обработке трека {track.get('id', 'Unknown')}: {e}", exc_info=True)
                continue
        
        # Отправка результатов обратно в Telegram
        logger.info(f"Отправляем {len(results)} результатов")
        await query.answer(results, cache_time=300)
        logger.info("Результаты успешно отправлены")
    except Exception as e:
        logger.error(f"Необработанная ошибка в inline_search: {e}", exc_info=True)
        error_result = InlineQueryResultArticle(
            id="error",
            title="Произошла ошибка",
            description="Пожалуйста, попробуйте еще раз",
            input_message_content=InputTextMessageContent(
                message_text=f"❌ Произошла ошибка при поиске: {str(e)}"
            )
        )
        await query.answer([error_result], cache_time=1) 