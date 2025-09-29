import requests
API_TOKEN = 'af7e3e046c4aa9bff6277b08d5b7a0c7'
import requests
import asyncio
from aiogram.types import Message
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
import asyncio
from aiogram.types import Message


async def create_requests_chart():
    """Создает круговую диаграмму статистики"""
    try:
        # Получаем статистику
        stats = get_statistics(limit=15)  # Берем топ-15 городов

        if not stats:
            return None, "📊 Нет данных для статистики"

        # Создаем DataFrame
        df = pd.DataFrame(stats, columns=['city_name', 'request_count'])

        # Создаем диаграмму
        plt.figure(figsize=(12, 8))
        plt.pie(df['request_count'], labels=df['city_name'], autopct='%1.1f%%')
        plt.title('📊 Топ городов по запросам погоды', fontsize=14, pad=20)

        # Сохраняем файл
        plt.savefig('weather_stats.png', dpi=300, bbox_inches='tight')
        plt.close()

        # Формируем текст статистики
        total_requests = df['request_count'].sum()
        stats_text = f"📊 Статистика запросов:\nВсего запросов: {total_requests}\n"
        stats_text += f"Уникальных городов: {len(df)}\n\n"
        stats_text += "Топ-5 городов:\n"

        for i, (city, count) in enumerate(stats[:5], 1):
            stats_text += f"{i}. {city.title()}: {count} запросов\n"

        return 'weather_stats.png', stats_text

    except Exception as e:
        print(f"❌ Ошибка создания диаграммы: {e}")
        return None, f"❌ Ошибка при создании статистики: {e}"


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


import sqlite3


def save_city_stat(city_name):
    """Сохраняет статистику по городу"""
    if not city_name or not city_name.strip():
        return

    city_lower = city_name.lower().strip()
    print(f"💾 Сохраняем город: '{city_lower}'")

    conn = sqlite3.connect('weather_stats.db')
    cursor = conn.cursor()

    try:
        # Проверяем, есть ли город в базе
        cursor.execute("SELECT request_count FROM city_requests WHERE city_name = ?", (city_lower,))
        result = cursor.fetchone()

        if result:
            # Если город есть - увеличиваем счетчик
            new_count = result[0] + 1
            cursor.execute("UPDATE city_requests SET request_count = ? WHERE city_name = ?", (new_count, city_lower))
            print(f"✅ Обновлен город {city_lower}: {result[0]} → {new_count}")
        else:
            # Если города нет - добавляем с счетчиком 1
            cursor.execute("INSERT INTO city_requests (city_name, request_count) VALUES (?, 1)", (city_lower,))
            print(f"✅ Добавлен новый город: {city_lower}")

        conn.commit()
    except Exception as e:
        print(f"❌ Ошибка при сохранении статистики: {e}")
    finally:
        conn.close()


def get_statistics(limit=10):
    """Получает статистику из базы данных"""
    conn = sqlite3.connect('weather_stats.db')
    cursor = conn.cursor()
    cursor.execute("SELECT city_name, request_count FROM city_requests ORDER BY request_count DESC LIMIT ?", (limit,))
    stats = cursor.fetchall()
    conn.close()
    return stats