"""
Тесты для модуля загрузки треков.

Этот модуль тестирует функциональность загрузки и отправки
музыкальных треков пользователям.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, ANY
from aiogram.types import Message, User, Chat, FSInputFile
from bot.utils.downloader import download_and_send_track


@pytest.fixture
def mock_message():
    """Фикстура для создания мок-объекта сообщения."""
    message = Mock(spec=Message)
    message.answer = AsyncMock()
    message.answer_audio = AsyncMock()
    message.from_user = Mock(spec=User, id=12345, username="testuser")
    message.chat = Mock(spec=Chat, id=12345)
    return message


@pytest.fixture
def mock_status_message():
    """Фикстура для создания мок-объекта статусного сообщения."""
    message = Mock(spec=Message)
    message.edit_text = AsyncMock()
    message.delete = AsyncMock()
    return message


@pytest.fixture
def mock_music_service():
    """Фикстура для создания мок-объекта музыкального сервиса."""
    service = Mock()
    service.get_track_full_info = AsyncMock()
    service.get_track_download_info = AsyncMock()
    return service


@pytest.mark.asyncio
async def test_download_and_send_track_success(mock_message, mock_status_message, mock_music_service):
    """
    Тест успешной загрузки и отправки трека.

    Проверяет, что функция корректно загружает и отправляет трек
    пользователю при успешном выполнении всех операций.
    """
    # Подготовка тестовых данных
    track_info = {
        'id': '123',
        'title': 'Test Track',
        'artists': ['Test Artist'],
        'duration_ms': 180000,
        'track_link': 'https://music.yandex.ru/track/123',
        'download_link': 'https://test.com/track.mp3'
    }
    mock_music_service.get_track_full_info.return_value = track_info

    # Мокаем aiohttp.ClientSession
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.read = AsyncMock(return_value=b'fake_mp3_data')
    mock_session = AsyncMock()
    mock_session.get = AsyncMock(return_value=mock_response)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock()

    # Мокаем mutagen.File
    mock_audio = Mock()
    mock_audio.__setitem__ = Mock()
    mock_audio.save = Mock()

    with patch('bot.utils.downloader.music_service', mock_music_service), \
         patch('aiohttp.ClientSession', return_value=mock_session), \
         patch('mutagen.File', return_value=mock_audio), \
         patch('tempfile.gettempdir', return_value='/tmp'), \
         patch('os.path.exists', return_value=True), \
         patch('os.unlink'):

        result = await download_and_send_track(mock_message, '123', mock_status_message)

        # Проверяем результат
        assert result is True

        # Проверяем вызовы методов
        mock_music_service.get_track_full_info.assert_called_once_with('123')
        mock_status_message.edit_text.assert_any_call("⬇️ Скачиваем трек...")
        mock_status_message.edit_text.assert_any_call("📝 Устанавливаем метаданные...")
        mock_status_message.edit_text.assert_any_call("📤 Отправляем файл...")
        
        # Проверяем вызов answer_audio с правильными параметрами
        mock_message.answer_audio.assert_called_once()
        call_args = mock_message.answer_audio.call_args
        assert isinstance(call_args[0][0], FSInputFile)
        assert call_args[1]['title'] == 'Test Track'
        assert call_args[1]['performer'] == 'Test Artist'
        assert call_args[1]['duration'] == 180
        
        mock_status_message.delete.assert_called_once()


@pytest.mark.asyncio
async def test_download_and_send_track_not_found(mock_message, mock_status_message, mock_music_service):
    """
    Тест случая, когда трек не найден.

    Проверяет, что функция корректно обрабатывает ситуацию,
    когда запрошенный трек не найден.
    """
    mock_music_service.get_track_full_info.return_value = None

    with patch('bot.utils.downloader.music_service', mock_music_service):
        result = await download_and_send_track(mock_message, '123', mock_status_message)

        assert result is False
        mock_status_message.edit_text.assert_called_once_with("❌ Трек не найден")


@pytest.mark.asyncio
async def test_download_and_send_track_download_error(mock_message, mock_status_message, mock_music_service):
    """
    Тест ошибки при скачивании.

    Проверяет, что функция корректно обрабатывает ошибки,
    возникающие при попытке скачать трек.
    """
    track_info = {
        'id': '123',
        'title': 'Test Track',
        'artists': ['Test Artist'],
        'duration_ms': 180000,
        'track_link': 'https://music.yandex.ru/track/123'
    }
    mock_music_service.get_track_full_info.return_value = track_info

    with patch('bot.utils.downloader.music_service', mock_music_service):
        result = await download_and_send_track(mock_message, '123', mock_status_message)

        assert result is False
        mock_status_message.edit_text.assert_called_with("❌ Не удалось получить ссылку на скачивание")


@pytest.mark.asyncio
async def test_download_and_send_track_http_error(mock_message, mock_status_message, mock_music_service):
    """
    Тест ошибки HTTP при скачивании.

    Проверяет, что функция корректно обрабатывает ошибки HTTP,
    возникающие при скачивании трека.
    """
    track_info = {
        'id': '123',
        'title': 'Test Track',
        'artists': ['Test Artist'],
        'duration_ms': 180000,
        'track_link': 'https://music.yandex.ru/track/123',
        'download_link': 'https://test.com/track.mp3'
    }
    mock_music_service.get_track_full_info.return_value = track_info

    # Мокаем aiohttp.ClientSession с ошибкой
    mock_response = AsyncMock()
    mock_response.status = 404
    mock_session = AsyncMock()
    mock_session.get = AsyncMock(return_value=mock_response)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock()

    with patch('bot.utils.downloader.music_service', mock_music_service), \
         patch('aiohttp.ClientSession', return_value=mock_session):

        result = await download_and_send_track(mock_message, '123', mock_status_message)

        assert result is False
        mock_status_message.edit_text.assert_called_with("❌ Ошибка при скачивании трека") 