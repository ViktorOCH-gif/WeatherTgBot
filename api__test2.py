import requests
from apitest import API_TOKEN
import requests
import asyncio
from aiogram.types import Message

async def get_weather(city: str) -> float:
    """Асинхронная функция для получения погоды"""
    params = {
        'q': city,
        'appid': API_TOKEN,
        'units': 'metric',
        'lang': 'ru'
    }

    # Делаем запрос в отдельном потоке чтобы не блокировать бота
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: requests.get("https://api.openweathermap.org/data/2.5/weather", params=params, timeout=10)
    )

    if response.status_code == 200:
        data = response.json()
        temperature = data['main']['temp']
        return round(temperature, 1)
    else:
        raise Exception(f"Город {city} не найден или ошибка API")