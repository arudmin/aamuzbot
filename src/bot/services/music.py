"""
Сервис для работы с API Яндекс.Музыки.

Этот модуль предоставляет интерфейс для взаимодействия с API Яндекс.Музыки,
включая поиск треков и получение информации для скачивания.
"""

from yandex_music import ClientAsync
from loguru import logger
from bot.config.config import config
import asyncio
from typing import List, Dict, Optional, Union


class MusicService:
    def __init__(self, client: Optional[ClientAsync] = None):
        if client is None:
            self.client = ClientAsync(config.yandex_music_token)
        else:
            self.client = client
        self._initialized = False
        logger.info("Клиент Яндекс.Музыки создан")

    async def ensure_initialized(self):
        """Убеждаемся, что клиент инициализирован."""
        if not self._initialized:
            await self.client.init()
            self._initialized = True
            logger.info("Клиент Яндекс.Музыки инициализирован")

    async def search_track(self, query: str, limit: int = 5, fetch_download_info: bool = True) -> List[Dict]:
        try:
            await self.ensure_initialized()
            
            # Выполняем поиск через асинхронный клиент
            search_result = await self.client.search(query)
            if not search_result or not search_result.tracks:
                return []
            
            tracks = search_result.tracks.results[:limit]
            results = []
            
            for track in tracks:
                # Создаем базовую информацию о треке
                track_info = {
                    'title': track.title,
                    'artists': [artist.name for artist in track.artists],
                    'duration_ms': track.duration_ms,
                    'id': track.id,
                    'track_link': f"https://music.yandex.ru/track/{track.id}"
                }
                results.append(track_info)
                
                # Если нужно получить информацию о скачивании
                if fetch_download_info:
                    download_link = await self.get_track_download_info(track.id)
                    if download_link:
                        track_info['download_link'] = download_link
            
            return results
        except Exception as e:
            logger.error(f"Ошибка при поиске треков: {e}")
            return []

    async def get_track_download_info(self, track_id: Union[int, str]) -> Optional[str]:
        try:
            await self.ensure_initialized()
            
            # Получаем информацию о треке через асинхронный клиент
            tracks = await self.client.tracks([track_id])
            if not tracks:
                logger.error(f"Трек {track_id} не найден")
                return None
            
            track = tracks[0]
            # Получаем информацию о скачивании
            info = await track.get_download_info_async()
            if not info:
                logger.error(f"Не удалось получить информацию о скачивании для трека {track_id}")
                return None
            
            best_quality = max(info, key=lambda x: x.bitrate_in_kbps)
            download_link = await best_quality.get_direct_link_async()
            
            logger.info(f"Получена ссылка на скачивание для трека {track_id}")
            return download_link
            
        except Exception as e:
            logger.error(f"Ошибка при получении информации о скачивании трека {track_id}: {e}", exc_info=True)
            return None

    async def get_track_full_info(self, track_id: Union[int, str]) -> Optional[Dict]:
        try:
            await self.ensure_initialized()
            
            # Получаем информацию о треке через асинхронный клиент
            tracks = await self.client.tracks([track_id])
            if not tracks:
                logger.error(f"Трек {track_id} не найден")
                return None
                
            track = tracks[0]
            
            # Получаем ссылку на скачивание
            download_link = await self.get_track_download_info(track_id)
            if not download_link:
                logger.error(f"Не удалось получить информацию о скачивании для трека {track_id}")
                return None
                
            # Формируем результат
            result = {
                'id': track.id,
                'title': track.title,
                'artists': [artist.name for artist in track.artists],
                'duration_ms': track.duration_ms,
                'track_link': f'https://music.yandex.ru/track/{track.id}',
                'download_link': download_link
            }
            
            logger.info(f"Получена полная информация о треке {track_id}")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при получении информации о треке {track_id}: {e}", exc_info=True)
            return None


# Создаем экземпляр-синглтон
music_service = MusicService() 