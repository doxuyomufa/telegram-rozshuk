import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, Text
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

API_TOKEN = "7922526391:AAF6f9uxMOc2CDvaHBU5NrX7DI9ET-d-ysE"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- База данных ---
conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    interactions INTEGER DEFAULT 0
)
""")
conn.commit()

# --- Кнопки ---
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Хочу консультацию"), KeyboardButton(text="Просто узнать")]
    ],
    resize_keyboard=True
)

# --- Хендлеры ---

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Привет! Чтобы продолжить, напиши число 5 + 3 = ?")

@dp.message(Text(text="8"))
async def after_captcha_handler(message: types.Message):
    cursor.execute(
        "INSERT OR IGNORE INTO users (id, username, interactions) VALUES (?, ?, 0)",
        (message.from_user.id, message.from_user.username)
    )
    conn.commit()
    await message.answer("Отлично, вы прошли проверку! Что вас интересует?", reply_markup=main_menu)

@dp.message(Text(text=["Хочу консультацию", "Просто узнать"]))
async def ask_interest_handler(message: types.Message):
    cursor.execute("UPDATE users SET interactions = interactions + 1 WHERE id = ?", (message.from_user.id,))
    conn.commit()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Написать менеджеру", url="https://t.me/ManagerUsername")]
    ])

    await message.answer("Спасибо! Свяжитесь с нашим менеджером:", reply_markup=keyboard)

@dp.message(Command("stats"))
async def stats_handler(message: types.Message):
    cursor.execute("SELECT COUNT(*), SUM(interactions) FROM users")
    users, interactions = cursor.fetchone()
    await message.answer(f"Пользователей: {users}\nВсего взаимодействий: {interactions or 0}")

# --- Запуск бота ---
async def main():
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        conn.close()

if __name__ == "__main__":
    asyncio.run(main())
