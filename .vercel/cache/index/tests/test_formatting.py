"""
Тесты для модуля форматирования сообщений.

Этот модуль тестирует функции форматирования сообщений,
включая форматирование длительности, сообщений о треках
и результатов поиска.
"""

import pytest
from bot.utils.formatting import format_duration, format_track_message, format_search_results


def test_format_duration():
    """Тест форматирования длительности."""
    # Тест обычных значений
    assert format_duration(180000) == "3:00"
    assert format_duration(195000) == "3:15"
    
    # Тест граничных значений
    assert format_duration(0) == "0:00"
    assert format_duration(59999) == "0:59"
    assert format_duration(60000) == "1:00"
    
    # Тест больших значений
    assert format_duration(3600000) == "60:00"
    assert format_duration(3661000) == "61:01"


def test_format_track_message():
    """Тест форматирования сообщения о треке."""
    # Подготовка тестовых данных
    track = {
        'title': 'Test Track',
        'artists': ['Test Artist'],
        'duration_ms': 180000,
        'id': '123',
        'track_link': 'https://music.yandex.ru/track/123'
    }
    
    # Тест без имени бота (без ссылки на скачивание)
    message = format_track_message(track)
    assert "Test Track" in message
    assert "Test Artist" in message
    assert "3:00" in message
    assert "Слушать на Яндекс.Музыке" in message
    assert "Скачать MP3" not in message
    
    # Тест с именем бота (со ссылкой на скачивание)
    message = format_track_message(track, "testbot")
    assert "Скачать MP3" in message
    assert "https://t.me/testbot?start=download_123" in message
    
    # Тест с экранированием специальных символов
    track_with_special_chars = {
        'title': 'Test & Track <script>',
        'artists': ['Test & Artist'],
        'duration_ms': 180000,
        'id': '123',
        'track_link': 'https://music.yandex.ru/track/123'
    }
    message = format_track_message(track_with_special_chars)
    assert "<script>" not in message
    assert "&lt;script&gt;" in message
    assert "Test &amp; Track" in message
    assert "Test &amp; Artist" in message


def test_format_search_results():
    """Тест форматирования результатов поиска."""
    # Тест пустого списка
    assert format_search_results([]) == "❌ Ничего не найдено"
    
    # Тест одного трека
    tracks = [{
        'title': 'Test Track',
        'artists': ['Test Artist'],
        'duration_ms': 180000,
        'id': '123',
        'track_link': 'https://music.yandex.ru/track/123'
    }]
    results = format_search_results(tracks, "testbot")
    assert "1." in results
    assert "Test Track" in results
    assert "Test Artist" in results
    assert "3:00" in results
    
    # Тест нескольких треков
    tracks.append({
        'title': 'Another Track',
        'artists': ['Another Artist'],
        'duration_ms': 240000,
        'id': '456',
        'track_link': 'https://music.yandex.ru/track/456'
    })
    results = format_search_results(tracks, "testbot")
    assert "1." in results
    assert "2." in results
    assert "Test Track" in results
    assert "Another Track" in results
    assert "4:00" in results
    
    # Тест без имени бота
    results = format_search_results(tracks)
    assert "Скачать MP3" not in results 