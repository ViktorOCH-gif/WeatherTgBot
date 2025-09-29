import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from api__test2 import get_weather
from api__test2 import save_city_stat, get_statistics

BOT_TOKEN = "7585833404:AAFLKuIiTYjQsgcV2kng94mqBKaOvnLhNGM"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Создаем клавиатуру
keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📊 Статистика")]],
    resize_keyboard=True
)

def init_db():
    conn = sqlite3.connect('weather_stats.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS city_requests (
            city_name TEXT PRIMARY KEY,
            request_count INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()
    print("База данных инициализирована")


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет! Напишите название города для получения погоды.", reply_markup=keyboard)


@dp.message(lambda message: message.text == "📊 Статистика")
async def show_statistics(message: Message):
    stats = get_statistics()

    if stats:
        response = "📊 Статистика запросов городов:\n"
        for i, (city, count) in enumerate(stats, 1):
            response += f"{i}. {city.title()}: {count} запросов\n"
    else:
        response = "Статистика пока пуста"

    await message.answer(response)


@dp.message()
async def handle_city(message: Message):
    city = message.text.strip()

    # Если сообщение не должно быть обработано как город (например, это команда), пропускаем
    if city.startswith('/'):
        return

    print(f"🔍 Обрабатываем город: '{city}'")

    # Сохраняем статистику
    save_city_stat(city)
    print(f"✅ Статистика сохранена для города: '{city}'")

    try:
        weather_info = await get_weather(city)
        await message.answer(f"🌤️ Погода в {city}: {weather_info}", reply_markup=keyboard)
    except Exception as e:
        print(f"❌ Ошибка погоды для {city}: {e}")
        await message.answer(f"❌ Ошибка получения погоды для города {city}", reply_markup=keyboard)


async def main():
    init_db()
    print("🤖 Бот запущен! Используйте кнопку 'Статистика' для просмотра статистики.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())