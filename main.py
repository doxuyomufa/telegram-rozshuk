import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.filters.text import Text
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import F
import asyncio

API_TOKEN = "7922526391:AAF6f9uxMOc2CDvaHBU5NrX7DI9ET-d-ysE"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- База данных ---
conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, interactions INT)")
conn.commit()

# --- Кнопки ---
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(KeyboardButton("Хочу консультацию"), KeyboardButton("Просто узнать"))

# --- Старт ---
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Чтобы продолжить, напиши число 5 + 3 = ?")

@dp.message(F.text == "8")
async def after_captcha(message: types.Message):
    cursor.execute("INSERT OR IGNORE INTO users (id, username, interactions) VALUES (?, ?, 0)", 
                   (message.from_user.id, message.from_user.username))
    conn.commit()
    await message.answer("Отлично, вы прошли проверку! Что вас интересует?", reply_markup=main_menu)

@dp.message(Text(equals=["Хочу консультацию", "Просто узнать"]))
async def ask_interest(message: types.Message):
    cursor.execute("UPDATE users SET interactions = interactions + 1 WHERE id = ?", (message.from_user.id,))
    conn.commit()
    markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton(text="Написать менеджеру", url="https://t.me/ManagerUsername")
    )
    await message.answer("Спасибо! Свяжитесь с нашим менеджером:", reply_markup=markup)

@dp.message(Command("stats"))
async def stats(message: types.Message):
    cursor.execute("SELECT COUNT(*), SUM(interactions) FROM users")
    users, interactions = cursor.fetchone()
    await message.answer(f"Пользователей: {users}\nВсего взаимодействий: {interactions or 0}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
