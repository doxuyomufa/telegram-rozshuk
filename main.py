import logging
import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

API_TOKEN = "7922526391:AAF6f9uxMOc2CDvaHBU5NrX7DI9ET-d-ysE"

logging.basicConfig(level=logging.INFO)

# --- База данных ---
conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()
cursor.execute(
    "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, interactions INT)"
)
conn.commit()

# --- Кнопки ---
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Хочу консультацию"), KeyboardButton(text="Просто узнать")]
    ],
    resize_keyboard=True,
)

# --- Инициализация бота и диспетчера ---
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


# --- Старт ---
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Чтобы продолжить, напиши число 5 + 3 = ?")


@dp.message(lambda message: message.text.strip() == "8")
async def after_captcha(message: types.Message):
    cursor.execute(
        "INSERT OR IGNORE INTO users (id, username, interactions) VALUES (?, ?, 0)",
        (message.from_user.id, message.from_user.username),
    )
    conn.commit()
    await message.answer("Отлично, вы прошли проверку! Что вас интересует?", reply_markup=main_menu)


@dp.message(lambda message: message.text in ["Хочу консультацию", "Просто узнать"])
async def ask_interest(message: types.Message):
    cursor.execute("UPDATE users SET interactions = interactions + 1 WHERE id = ?", (message.from_user.id,))
    conn.commit()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Написать менеджеру", url="https://t.me/ManagerUsername")]
    ])
    await message.answer("Спасибо! Свяжитесь с нашим менеджером:", reply_markup=kb)


@dp.message(Command("stats"))
async def stats(message: types.Message):
    cursor.execute("SELECT COUNT(*), SUM(interactions) FROM users")
    users, interactions = cursor.fetchone()
    await message.answer(f"Пользователей: {users}\nВсего взаимодействий: {interactions or 0}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
