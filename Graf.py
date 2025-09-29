import matplotlib.pyplot as plt
import pandas as pd
import aiosqlite
import asyncio


async def create_requests_chart():
    # Асинхронное подключение
    async with aiosqlite.connect('weather_stats.db') as db:
        # Асинхронный запрос
        async with db.execute("SELECT city_name, request_count FROM city_requests") as cursor:
            rows = await cursor.fetchall()

    # Создаем DataFrame из результатов
    df = pd.DataFrame(rows, columns=['city_name', 'request_count'])

    # Создание диаграммы
    plt.pie(df['request_count'], labels=df['city_name'], autopct='%1.1f%%')
    plt.title('Количество запросов по городам')
    plt.savefig('chart.png')
    plt.show()

    return f"Диаграмма создана! Обработано {len(df)} городов"


# Запуск
async def main():
    result = await create_requests_chart()
    print(result)


if __name__ == "__main__":
    asyncio.run(main())