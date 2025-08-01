import asyncio
import logging
import os
import aiosqlite
from pathlib import Path

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

# --- Конфигурация ---
API_TOKEN = os.getenv("API_TOKEN", "PUT-YOUR-TOKEN-HERE")
DB_PATH = "db.sqlite3"
IMAGES_DIR = Path("images")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- Меню ---
interest_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Зняти з Розшуку"), KeyboardButton(text="Бронювання")],
        [KeyboardButton(text="Виїзд за кордон"), KeyboardButton(text="СЗЧ/Коміс")],
    ],
    resize_keyboard=True,
)

consultation_button = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Консультація", url="https://t.me/robic33ai")]]
)

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
    "Зняти з Розшуку": IMAGES_DIR / "rozshuk.jpg",
    "Бронювання": IMAGES_DIR / "bron.jpg",
    "Виїзд за кордон": IMAGES_DIR / "vyezd.jpg",
    "СЗЧ/Коміс": IMAGES_DIR / "szch.jpg",
}

# --- Хендлеры ---
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привіт! Аби продовжити напиши число 5 + 3 = ?")


@dp.message(F.text == "8")
async def after_captcha(message: types.Message):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (id, username, interactions) VALUES (?, ?, 0)",
            (message.from_user.id, message.from_user.username),
        )
        await db.commit()
    await message.answer("Чудово, Ви пройшли перевірку! Що Вас цікавить?", reply_markup=interest_menu)


@dp.message(F.text.in_(texts.keys()))
async def send_info(message: types.Message):
    choice = message.text
    photo_path = images.get(choice)

    if photo_path and photo_path.exists():
        with open(photo_path, "rb") as photo:
            sent_photo = await message.answer_photo(photo, caption=texts[choice], reply_markup=consultation_button)
        await asyncio.sleep(5)
        await sent_photo.delete()
    else:
        await message.answer(texts[choice], reply_markup=consultation_button)


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, interactions INT)"
        )
        await db.commit()


async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
