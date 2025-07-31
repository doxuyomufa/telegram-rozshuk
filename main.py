import asyncio
import logging
import sqlite3
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

API_TOKEN = "8415722752:AAG223wC-0PAlDd0Ax-jYKpIOVgC7g1M_QU"
WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = "super_secret_key"  # можно любой текст
WEBHOOK_URL = "https://telegram-bot-1-fwf1.onrender.com/webhook"

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
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Хочу консультацию"), KeyboardButton(text="Просто узнать")]
    ],
    resize_keyboard=True,
)

# Новое меню после прохождения проверки
interest_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Зняти з Розшуку"),
            KeyboardButton(text="Бронювання"),
            KeyboardButton(text="Виїзд за кордон"),
        ]
    ],
    resize_keyboard=True,
)

consultation_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Консультація", url="https://t.me/robic33ai")]
    ]
)

# --- Хендлеры ---
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

# Новый хендлер для трёх новых кнопок
@dp.message(F.text.in_(["Зняти з Розшуку", "Бронювання", "Виїзд за кордон"]))
async def interest_choice(message: types.Message):
    cursor.execute("UPDATE users SET interactions = interactions + 1 WHERE id = ?", (message.from_user.id,))
    conn.commit()

    if message.text == "Зняти з Розшуку":
        text = (
            "Інформація про зняття з розшуку:\n"
            "Тут опис процедури, необхідні документи та контакти.\n"
        )
    elif message.text == "Бронювання":
        text = (
            "Інформація про бронювання:\n"
            "Як зробити бронювання, терміни та умови.\n"
        )
    elif message.text == "Виїзд за кордон":
        text = (
            "Інформація про виїзд за кордон:\n"
            "Правила, необхідні документи та поради.\n"
        )
    else:
        text = "Інформація відсутня."

    await message.answer(text, reply_markup=consultation_button)

@dp.message(F.text.in_(["Хочу консультацию", "Просто узнать"]))
async def ask_interest(message: types.Message):
    cursor.execute("UPDATE users SET interactions = interactions + 1 WHERE id = ?", (message.from_user.id,))
    conn.commit()
    manager_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Написать менеджеру", url="https://t.me/ManagerUsername")]
        ]
    )
    await message.answer("Спасибо! Свяжитесь с нашим менеджером:", reply_markup=manager_button)

@dp.message(Command("stats"))
async def stats(message: types.Message):
    cursor.execute("SELECT COUNT(*), SUM(interactions) FROM users")
    users, interactions = cursor.fetchone()
    await message.answer(f"Пользователей: {users}\nВсего взаимодействий: {interactions or 0}")

# --- Webhook-сервер ---
async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL, secret_token=WEBHOOK_SECRET)

async def on_shutdown(app):
    await bot.delete_webhook()

async def handle_webhook(request):
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
        return web.Response(status=403)
    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(bot, update)
    return web.Response()

def main():
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle_webhook)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

if __name__ == "__main__":
    main()
