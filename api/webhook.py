from http.server import HTTPServer
from bot.web.app import init_app
from bot.config.config import config

# Инициализируем приложение
app = init_app()

# Обработчик для Vercel
async def handler(request):
    if request.method == 'POST':
        # Получаем данные запроса
        body = await request.json()
        
        # Обрабатываем update от Telegram
        await app['bot'].process_update(body)
        
        return {'statusCode': 200, 'body': 'OK'}
        
    return {'statusCode': 405, 'body': 'Method not allowed'} 