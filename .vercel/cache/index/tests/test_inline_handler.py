"""
Тесты для inline-обработчика.

Этот модуль тестирует функциональность inline-обработчика,
включая поиск треков и форматирование результатов.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from aiogram.types import InlineQuery, User, InlineQueryResultArticle, InputTextMessageContent
from aiogram import Bot
from bot.handlers.inline import inline_search
import asyncio


@pytest.fixture
def inline_query():
    """Фикстура для создания мок-объекта inline-запроса."""
    query = Mock(spec=InlineQuery)
    query.query = "test query"
    query.from_user = Mock(spec=User, id=12345, username="testuser")
    query.answer = AsyncMock()
    
    # Создаем мок бота
    bot = Mock(spec=Bot)
    bot.get_me = AsyncMock(return_value=Mock(username="testbot"))
    query.bot = bot
    
    return query


@pytest.fixture
def mock_music_service():
    """Фикстура для создания мок-объекта музыкального сервиса."""
    service = Mock()
    service.search_track = AsyncMock()
    return service


@pytest.mark.asyncio
async def test_inline_search_empty_query(inline_query):
    """
    Тест обработки пустого inline-запроса.

    Проверяет, что обработчик корректно отвечает на пустой запрос
    сообщением-подсказкой.
    """
    inline_query.query = ""
    
    await inline_search(inline_query)
    
    # Проверяем, что был отправлен ответ с подсказкой
    inline_query.answer.assert_called_once()
    args = inline_query.answer.call_args[0][0]
    assert len(args) == 1
    assert isinstance(args[0], InlineQueryResultArticle)
    assert args[0].id == "empty"
    assert "Поиск музыки" in args[0].title


@pytest.mark.asyncio
async def test_inline_search_success(inline_query, mock_music_service):
    """
    Тест успешного поиска через inline-запрос.

    Проверяет, что обработчик корректно обрабатывает результаты поиска
    и форматирует их для отображения.
    """
    # Подготовка тестовых данных
    mock_tracks = [{
        'id': '123',
        'title': 'Test Track',
        'artists': ['Test Artist'],
        'duration_ms': 180000,
        'track_link': 'https://music.yandex.ru/track/123',
        'download_link': 'http://test.com/download'
    }]
    mock_music_service.search_track.return_value = mock_tracks
    
    with patch('bot.handlers.inline.music_service', mock_music_service):
        await inline_search(inline_query)
    
    # Проверяем вызов поиска
    mock_music_service.search_track.assert_called_once_with(
        "test query", limit=10, fetch_download_info=False
    )
    
    # Проверяем ответ
    inline_query.answer.assert_called_once()
    args = inline_query.answer.call_args[0][0]
    assert len(args) == 1
    result = args[0]
    assert isinstance(result, InlineQueryResultArticle)
    assert "Test Track" in result.title
    assert "Test Artist" in result.description


@pytest.mark.asyncio
async def test_inline_search_no_results(inline_query, mock_music_service):
    """
    Тест поиска при отсутствии результатов.

    Проверяет, что обработчик корректно обрабатывает случай,
    когда поиск не возвращает результатов.
    """
    mock_music_service.search_track.return_value = []
    
    with patch('bot.handlers.inline.music_service', mock_music_service):
        await inline_search(inline_query)
    
    # Проверяем ответ
    inline_query.answer.assert_called_once()
    args = inline_query.answer.call_args[0][0]
    assert len(args) == 0


@pytest.mark.asyncio
async def test_inline_search_timeout(inline_query, mock_music_service):
    """
    Тест обработки таймаута при поиске.

    Проверяет, что обработчик корректно обрабатывает ситуацию,
    когда поиск превышает установленный таймаут.
    """
    # Мокаем asyncio.wait_for, чтобы он вызывал TimeoutError
    async def mock_wait_for(*args, **kwargs):
        raise asyncio.TimeoutError()
    
    with patch('bot.handlers.inline.music_service', mock_music_service), \
         patch('asyncio.wait_for', mock_wait_for):
        await inline_search(inline_query)
    
    # Проверяем ответ с сообщением о таймауте
    inline_query.answer.assert_called_once()
    args = inline_query.answer.call_args[0][0]
    assert len(args) == 1
    result = args[0]
    assert isinstance(result, InlineQueryResultArticle)
    assert result.id == "timeout"
    assert "слишком много времени" in result.title


@pytest.mark.asyncio
async def test_inline_search_error(inline_query, mock_music_service):
    """
    Тест обработки ошибок при поиске.

    Проверяет, что обработчик корректно обрабатывает непредвиденные
    ошибки, возникающие в процессе поиска.
    """
    mock_music_service.search_track.side_effect = Exception("Test error")
    
    with patch('bot.handlers.inline.music_service', mock_music_service):
        await inline_search(inline_query)
    
    # Проверяем ответ с сообщением об ошибке
    inline_query.answer.assert_called_once()
    args = inline_query.answer.call_args[0][0]
    assert len(args) == 1
    result = args[0]
    assert isinstance(result, InlineQueryResultArticle)
    assert result.id == "error"
    assert "Произошла ошибка" in result.title 