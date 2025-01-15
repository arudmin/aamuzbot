"""
Обработчики веб-запросов для скачивания треков.

Этот модуль содержит обработчики для веб-сервера, который обслуживает
запросы на скачивание треков. Он предоставляет прямые ссылки для скачивания
MP3 файлов, полученных через API Яндекс.Музыки.
"""

from aiohttp import web
from loguru import logger
from bot.services.music import music_service
import aiohttp
import re


routes = web.RouteTableDef()


@routes.get("/track/{track_id}.mp3")
async def download_track(request: web.Request) -> web.StreamResponse:
    """
    Обработчик для скачивания трека.
    URL формат: /track/{track_id}.mp3
    """
    try:
        # Получаем ID трека из URL
        track_id = request.match_info['track_id'].replace('.mp3', '')
        
        # Получаем информацию о треке
        track_info = await music_service.get_track_full_info(track_id)
        if not track_info:
            return web.Response(status=404, text="Track not found")
            
        # Получаем прямую ссылку на скачивание
        download_link = track_info['download_link']
        
        # Создаем асинхронную сессию для скачивания
        async with aiohttp.ClientSession() as session:
            async with session.get(download_link) as response:
                if response.status != 200:
                    return web.Response(status=response.status, text="Failed to download track")
                    
                # Создаем StreamResponse для отправки файла
                stream = web.StreamResponse(
                    status=200,
                    reason='OK',
                    headers={
                        'Content-Type': 'audio/mpeg',
                        'Content-Disposition': f'attachment; filename="{track_info["title"]}.mp3"'
                    }
                )
                
                await stream.prepare(request)
                
                # Читаем и отправляем файл по частям
                async for chunk in response.content.iter_chunked(8192):
                    await stream.write(chunk)
                    
                return stream
                    
    except Exception as e:
        logger.error(f"Ошибка при скачивании трека {track_id}: {e}")
        return web.Response(status=500, text=str(e)) 