"""
Тесты для модуля конфигурации.

Этот модуль тестирует функциональность конфигурации бота,
включая загрузку настроек и работу с ngrok.
"""

import pytest
from unittest.mock import Mock, patch
from bot.config.config import Settings, setup_ngrok


@pytest.fixture
def mock_env(monkeypatch):
    """Фикстура для мока переменных окружения."""
    env_vars = {
        'BOT_TOKEN': 'test_token',
        'WEBHOOK_HOST': 'test.domain',
        'WEBHOOK_PATH': '/webhook',
        'WEBAPP_HOST': '0.0.0.0',
        'WEBAPP_PORT': '8000',
        'NGROK_AUTH_TOKEN': 'test_ngrok_token',
        'YANDEX_MUSIC_TOKEN': 'test_yandex_token'
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars


def test_settings_load(mock_env):
    """Тест загрузки настроек из переменных окружения."""
    settings = Settings()
    
    assert settings.bot_token.get_secret_value() == 'test_token'
    assert settings.webhook_host == 'test.domain'
    assert settings.webhook_path == '/webhook'
    assert settings.webapp_host == '0.0.0.0'
    assert settings.webapp_port == 8000
    assert settings.ngrok_auth_token == 'test_ngrok_token'
    assert settings.yandex_music_token == 'test_yandex_token'


def test_settings_webhook_url():
    """Тест формирования URL для вебхука."""
    settings = Settings()
    settings.ngrok_tunnel_url = 'https://test.ngrok.io'
    
    assert settings.webhook_url == 'https://test.ngrok.io/webhook'


def test_setup_ngrok_success():
    """Тест успешной настройки ngrok."""
    # Мокаем ngrok
    mock_tunnel = Mock()
    mock_tunnel.public_url = 'https://test.ngrok.io'
    
    mock_ngrok = Mock()
    mock_ngrok.connect = Mock(return_value=mock_tunnel)
    mock_ngrok.set_auth_token = Mock()
    mock_ngrok.kill = Mock()
    
    with patch('bot.config.config.Settings') as mock_settings, \
         patch.dict('sys.modules', {'pyngrok': Mock(ngrok=mock_ngrok)}):
        
        # Настраиваем мок Settings
        settings_instance = Settings()
        settings_instance.ngrok_auth_token = 'test_token'
        settings_instance.webapp_port = 8000
        mock_settings.return_value = settings_instance
        
        # Вызываем тестируемую функцию
        result = setup_ngrok()
        
        # Проверяем результат
        assert result.webhook_host == 'https://test.ngrok.io'
        assert result.ngrok_tunnel_url == 'https://test.ngrok.io'
        
        # Проверяем вызовы методов
        mock_ngrok.set_auth_token.assert_called_once_with('test_token')
        mock_ngrok.kill.assert_called_once()
        mock_ngrok.connect.assert_called_once_with(8000, bind_tls=True)


def test_setup_ngrok_no_token():
    """Тест настройки ngrok без токена."""
    with patch('bot.config.config.Settings') as mock_settings:
        # Настраиваем мок Settings без токена
        settings_instance = Settings()
        settings_instance.ngrok_auth_token = ''
        mock_settings.return_value = settings_instance
        
        # Вызываем тестируемую функцию
        result = setup_ngrok()
        
        # Проверяем, что вернулись настройки без ngrok
        assert result.ngrok_tunnel_url == ""


def test_setup_ngrok_error():
    """Тест обработки ошибок при настройке ngrok."""
    # Мокаем ngrok с ошибкой
    mock_ngrok = Mock()
    mock_ngrok.connect = Mock(side_effect=Exception("Test error"))
    
    with patch('bot.config.config.Settings') as mock_settings, \
         patch.dict('sys.modules', {'pyngrok': Mock(ngrok=mock_ngrok)}):
        
        # Настраиваем мок Settings
        settings_instance = Settings()
        settings_instance.ngrok_auth_token = 'test_token'
        mock_settings.return_value = settings_instance
        
        # Вызываем тестируемую функцию
        result = setup_ngrok()
        
        # Проверяем, что вернулись настройки без ngrok
        assert result.ngrok_tunnel_url == "" 