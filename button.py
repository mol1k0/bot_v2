from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import sqlite3

# Токен вашего бота
TOKEN = "8029566728:AAGpHq9J07Fn6r0GNcNy6tQ-11JsPWe9lvI"

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
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
    await message.reply(f"Добро пожаловать в игру, {username}! У вас есть 100 монет.")

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
    # Удаление вебхука и запуск бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

# Запуск асинхронного цикла
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        asyncio.run(on_shutdown())