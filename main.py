import asyncio
import logging
import sqlite3
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = "8415722752:AAG223wC-0PAlDd0Ax-jYKpIOVgC7g1M_QU"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- База данных ---
conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()
cursor.execute(
    "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, interactions INT)"
)
conn.commit()

# --- Кнопки ---
interest_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Зняти з Розшуку"),
            KeyboardButton(text="Бронювання"),
        ],
        [
            KeyboardButton(text="Виїзд за кордон"),
            KeyboardButton(text="СЗЧ/Коміс"),
        ]
    ],
    resize_keyboard=True,
)

consultation_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Консультація", url="https://t.me/robic33ai")]
    ]
)

# --- Тексти ---
texts = {
    "Зняти з Розшуку": """✅ Зняття з РОЗШУКУ на 1 рік...
на головну - /start
зняття СЗЧ - /military""",
    "Бронювання": """✅ БРОНЮВАННЯ і відстрочка на 1 рік...
на головну - /start
зняття з РОЗШУКУ - /rozshuk""",
    "Виїзд за кордон": """✅ Виключення з обліку на 5 років...
на головну - /start
виведення з ЗС - /military""",
    "СЗЧ/Коміс": """✅ Зняття СЗЧ на гарантований 1 рік...
на головну - /start
виведення з ЗС - /rozshuk""",
}

images = {
    "Зняти з Розшуку": "images/rozshuk.jpg",
    "Бронювання": "images/bron.jpg",
    "Виїзд за кордон": "images/vyezd.jpg",
    "СЗЧ/Коміс": "images/szch.jpg",
}

# --- Хендлери ---
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привіт! Аби продовжити напиши число 5 + 3 = ?")

@dp.message(F.text == "8")
async def after_captcha(message: types.Message):
    cursor.execute(
        "INSERT OR IGNORE INTO users (id, username, interactions) VALUES (?, ?, 0)",
        (message.from_user.id, message.from_user.username),
    )
    conn.commit()
    await message.answer("Чудово, Ви пройшли перевірку! Що Вас цікавить?", reply_markup=interest_menu)

@dp.message(F.text.in_(["Зняти з Розшуку", "Бронювання", "Виїзд за кордон", "СЗЧ/Коміс"]))
async def send_info(message: types.Message):
    choice = message.text
    photo_path = images[choice]

    with open(photo_path, "rb") as photo:
        sent_photo = await message.answer_photo(photo, caption=texts[choice], reply_markup=consultation_button)

    await asyncio.sleep(5)
    await sent_photo.delete()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
