"""
Веб-роутер для обработки HTTP запросов.

Этот модуль содержит обработчики для скачивания треков.
"""

import re
from aiohttp import web
from bot.services.music import MusicService
from loguru import logger


async def download_track(request: web.Request) -> web.Response:
    """
    Обработчик для скачивания трека.
    
    Args:
        request: HTTP запрос
        
    Returns:
        HTTP ответ с MP3 файлом или ошибкой
    """
    # Получаем ID трека из URL
    track_id_match = re.match(r"/track/(\d+)\.mp3", request.path)
    if not track_id_match:
        return web.Response(
            text="Invalid track ID",
            status=400
        )
    
    track_id = int(track_id_match.group(1))
    
    try:
        # Получаем информацию о треке
        music_service = MusicService()
        track_info = music_service.get_track_full_info(track_id)
        if not track_info:
            return web.Response(
                text="Track not found",
                status=404
            )
            
        # Получаем ссылку на скачивание
        download_link = music_service.get_track_download_info(track_id)
        if not download_link:
            return web.Response(
                text="Download link not available",
                status=404
            )
            
        # Формируем имя файла
        filename = f"{track_info['title']} - {track_info['artists']}.mp3"
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)  # Убираем недопустимые символы
        
        # Возвращаем редирект на скачивание
        return web.Response(
            status=302,
            headers={
                "Location": download_link,
                "Content-Type": "audio/mpeg",
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
            
    except Exception as e:
        logger.error(f"Error downloading track {track_id}: {e}")
        return web.Response(
            text="Internal server error",
            status=500
        )


def setup_routes(app: web.Application) -> None:
    """
    Настройка маршрутов для веб-приложения.
    
    Args:
        app: Веб-приложение
    """
    app.router.add_get(r"/track/{track_id:\d+}.mp3", download_track) 