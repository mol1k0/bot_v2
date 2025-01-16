from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
import asyncio
import sqlite3
from config import TELEGRAM_BOT_TOKEN  # Убедитесь, что токен указан в config.py

# Инициализация бота и диспетчера
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# Подключение к базе данных
conn = sqlite3.connect("game.db", check_same_thread=False)
cursor = conn.cursor()

# Создание таблицы игроков
cursor.execute('''CREATE TABLE IF NOT EXISTS players (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    balance INTEGER DEFAULT 100
)''')
conn.commit()

# Хэндлер для команды /start
@dp.message(Command("start"))
async def start_game(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Безымянный"
    cursor.execute("INSERT OR IGNORE INTO players (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()

    # Создаем кнопку с мини-приложением
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Открыть мини-приложение",
            web_app=WebAppInfo(url="https://mol1k0.github.io/bot_v2/")  # URL вашего мини-приложения
        )]
    ])
    await message.reply(f"Добро пожаловать в игру, {username}! У вас есть 100 монет. Нажмите кнопку, чтобы открыть мини-приложение.", reply_markup=keyboard)

# Хэндлер для команды /work
@dp.message(Command("work"))
async def work(message: types.Message):
    user_id = message.from_user.id
    earnings = 10  # Деньги за "работу"
    cursor.execute("UPDATE players SET balance = balance + ? WHERE user_id = ?", (earnings, user_id))
    conn.commit()
    await message.reply(f"Вы поработали и заработали {earnings} монет!")

# Хэндлер для команды /balance
@dp.message(Command("balance"))
async def balance(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("SELECT balance FROM players WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    if result:
        await message.reply(f"Ваш баланс: {result[0]} монет.")
    else:
        await message.reply("Вы ещё не зарегистрированы. Используйте /start.")

# Закрытие соединения с базой данных при завершении работы бота
async def on_shutdown():
    cursor.close()
    conn.close()

# Основная функция
async def main():
    try:
        # Удаление вебхука и запуск бота
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        await on_shutdown()

# Запуск асинхронного цикла
if __name__ == "__main__":
    asyncio.run(main())