"""
Тесты для базовых обработчиков команд бота.

Этот модуль тестирует базовые обработчики команд,
такие как /start и /help.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from aiogram.types import Message, User, Chat
from bot.handlers.base import cmd_start, cmd_help


@pytest.fixture
def mock_message():
    """Фикстура для создания мок-объекта сообщения."""
    message = Mock(spec=Message)
    message.answer = AsyncMock()
    message.delete = AsyncMock()
    message.from_user = Mock(spec=User, id=12345, username="testuser")
    message.chat = Mock(spec=Chat, id=12345)
    return message


@pytest.mark.asyncio
async def test_cmd_start_without_args(mock_message):
    """Тест команды /start без аргументов."""
    mock_message.text = "/start"
    
    await cmd_start(mock_message)
    
    # Проверяем, что было отправлено приветственное сообщение
    mock_message.answer.assert_called_once()
    args, kwargs = mock_message.answer.call_args
    welcome_text = args[0]
    assert "👋 Привет!" in welcome_text
    assert "parse_mode" in kwargs
    assert kwargs["parse_mode"] == "HTML"


@pytest.mark.asyncio
async def test_cmd_start_with_download(mock_message):
    """Тест команды /start с параметром скачивания."""
    mock_message.text = "/start download_123"
    
    # Мокаем функцию скачивания
    with patch('bot.handlers.base.download_and_send_track', AsyncMock()) as mock_download:
        await cmd_start(mock_message)
        
        # Проверяем, что была вызвана функция скачивания
        mock_download.assert_called_once_with(mock_message, "123")
        # Проверяем, что сообщение было удалено
        mock_message.delete.assert_called_once()


@pytest.mark.asyncio
async def test_cmd_start_with_invalid_download(mock_message):
    """Тест команды /start с некорректным параметром скачивания."""
    mock_message.text = "/start download_invalid"
    
    # Мокаем функцию скачивания с ошибкой
    with patch('bot.handlers.base.download_and_send_track', AsyncMock(side_effect=Exception("Test error"))):
        await cmd_start(mock_message)
        
        # Проверяем, что было отправлено сообщение об ошибке
        mock_message.answer.assert_called_with("❌ Произошла ошибка при скачивании трека")


@pytest.mark.asyncio
async def test_cmd_help(mock_message):
    """Тест команды /help."""
    await cmd_help(mock_message)
    
    # Проверяем, что была отправлена справка
    mock_message.answer.assert_called_once()
    args, kwargs = mock_message.answer.call_args
    help_text = args[0]
    assert "📖 Доступные команды" in help_text
    assert "parse_mode" in kwargs
    assert kwargs["parse_mode"] == "HTML"
    
    # Проверяем наличие всех команд в справке
    assert "/start" in help_text
    assert "/help" in help_text
    assert "/music" in help_text
    assert "/search" in help_text 