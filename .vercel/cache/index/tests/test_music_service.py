"""
Тесты для модуля музыкального сервиса.

Этот модуль содержит тесты для проверки функциональности MusicService,
включая поиск треков и получение информации для скачивания.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bot.services.music import MusicService


@pytest.fixture
def mock_track():
    """Фикстура, создающая мок объекта трека."""
    track = MagicMock()
    track.title = "Test Track"
    track.artists = [MagicMock(name="Test Artist")]
    track.duration_ms = 180000
    track.id = "123456"
    
    download_info = MagicMock()
    download_info.bitrate_in_kbps = 320
    download_info.direct_link = "https://test-download-link.com"
    track.get_download_info.return_value = [download_info]
    
    return track


@pytest.fixture
def mock_client():
    """Фикстура, создающая мок клиента Яндекс.Музыки."""
    client = AsyncMock()
    return client


@pytest.fixture
def music_service(mock_client):
    """Фикстура, создающая экземпляр MusicService с мок-клиентом."""
    return MusicService(client=mock_client)


@pytest.mark.asyncio
async def test_search_track_success(music_service, mock_track):
    """Тест успешного поиска треков."""
    # Настраиваем мок для поиска
    search_result = MagicMock()
    search_result.tracks.results = [mock_track]
    music_service.client.search.return_value = search_result
    
    # Настраиваем мок для получения информации о треке
    music_service.client.tracks.return_value = [mock_track]
    
    # Выполняем поиск
    results = await music_service.search_track("test query")
    
    # Проверяем результаты
    assert len(results) == 1
    track = results[0]
    assert track["title"] == "Test Track"
    assert track["artists"] == ["Test Artist"]
    assert track["duration_ms"] == 180000
    assert track["id"] == "123456"
    assert track["track_link"] == "https://music.yandex.ru/track/123456"
    assert track["download_link"] == "https://test-download-link.com"
    
    # Проверяем, что методы клиента были вызваны
    music_service.client.search.assert_called_once_with("test query")
    music_service.client.tracks.assert_called_once_with(["123456"])


@pytest.mark.asyncio
async def test_search_track_no_results(music_service):
    """Тест поиска треков без результатов."""
    # Настраиваем мок для пустого результата поиска
    search_result = MagicMock()
    search_result.tracks.results = []
    music_service.client.search.return_value = search_result
    
    # Выполняем поиск
    results = await music_service.search_track("non existent track")
    
    # Проверяем, что результат пустой
    assert len(results) == 0
    
    # Проверяем, что поиск был выполнен
    music_service.client.search.assert_called_once_with("non existent track")


@pytest.mark.asyncio
async def test_search_track_error(music_service):
    """Тест обработки ошибки при поиске треков."""
    # Настраиваем мок для генерации ошибки
    music_service.client.search.side_effect = Exception("API Error")
    
    # Выполняем поиск
    results = await music_service.search_track("test query")
    
    # Проверяем, что при ошибке возвращается пустой список
    assert len(results) == 0
    
    # Проверяем, что попытка поиска была сделана
    music_service.client.search.assert_called_once_with("test query")


@pytest.mark.asyncio
async def test_get_track_download_info_success(music_service, mock_track):
    """Тест успешного получения информации о скачивании трека."""
    # Настраиваем мок для получения трека
    music_service.client.tracks.return_value = [mock_track]
    
    # Получаем информацию о скачивании
    download_link = await music_service.get_track_download_info("123456")
    
    # Проверяем результат
    assert download_link == "https://test-download-link.com"
    
    # Проверяем, что метод клиента был вызван
    music_service.client.tracks.assert_called_once_with(["123456"])


@pytest.mark.asyncio
async def test_get_track_download_info_no_track(music_service):
    """Тест получения информации о скачивании несуществующего трека."""
    # Настраиваем мок для отсутствующего трека
    music_service.client.tracks.return_value = []
    
    # Получаем информацию о скачивании
    download_link = await music_service.get_track_download_info("123456")
    
    # Проверяем, что результат None
    assert download_link is None
    
    # Проверяем, что метод клиента был вызван
    music_service.client.tracks.assert_called_once_with(["123456"])


@pytest.mark.asyncio
async def test_get_track_download_info_error(music_service):
    """Тест обработки ошибки при получении информации о скачивании."""
    # Настраиваем мок для генерации ошибки
    music_service.client.tracks.side_effect = Exception("API Error")
    
    # Получаем информацию о скачивании
    download_link = await music_service.get_track_download_info("123456")
    
    # Проверяем, что при ошибке возвращается None
    assert download_link is None
    
    # Проверяем, что попытка получения информации была сделана
    music_service.client.tracks.assert_called_once_with(["123456"])


@pytest.mark.asyncio
async def test_get_track_full_info_success(music_service, mock_track):
    """Тест успешного получения полной информации о треке."""
    # Настраиваем мок для получения трека
    music_service.client.tracks.return_value = [mock_track]
    
    # Получаем полную информацию о треке
    track_info = await music_service.get_track_full_info("123456")
    
    # Проверяем результат
    assert track_info is not None
    assert track_info["title"] == "Test Track"
    assert track_info["artists"] == ["Test Artist"]
    assert track_info["duration_ms"] == 180000
    assert track_info["id"] == "123456"
    assert track_info["track_link"] == "https://music.yandex.ru/track/123456"
    assert track_info["download_link"] == "https://test-download-link.com"
    
    # Проверяем, что метод клиента был вызван
    music_service.client.tracks.assert_called_with(["123456"])


@pytest.mark.asyncio
async def test_get_track_full_info_no_track(music_service):
    """Тест получения полной информации о несуществующем треке."""
    # Настраиваем мок для отсутствующего трека
    music_service.client.tracks.return_value = []
    
    # Получаем полную информацию о треке
    track_info = await music_service.get_track_full_info("123456")
    
    # Проверяем, что результат None
    assert track_info is None
    
    # Проверяем, что метод клиента был вызван
    music_service.client.tracks.assert_called_once_with(["123456"])


@pytest.mark.asyncio
async def test_get_track_full_info_error(music_service):
    """Тест обработки ошибки при получении полной информации о треке."""
    # Настраиваем мок для генерации ошибки
    music_service.client.tracks.side_effect = Exception("API Error")
    
    # Получаем полную информацию о треке
    track_info = await music_service.get_track_full_info("123456")
    
    # Проверяем, что при ошибке возвращается None
    assert track_info is None
    
    # Проверяем, что попытка получения информации была сделана
    music_service.client.tracks.assert_called_once_with(["123456"]) 