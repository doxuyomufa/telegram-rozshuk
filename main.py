import logging
import sqlite3
import os
from aiogram import Bot, Dispatcher, Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

API_TOKEN = os.getenv("BOT_TOKEN", "7922526391:AAF6f9uxMOc2CDvaHBU5NrX7DI9ET-d-ysE")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://your-app.onrender.com/webhook")
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", 8080))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# --- База данных ---
conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, interactions INT)")
conn.commit()

# --- Кнопки ---
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(KeyboardButton("Хочу консультацию"), KeyboardButton("Просто узнать"))

# --- Хэндлеры ---
@router.message(commands=["start"])
async def start(message: types.Message):
    await message.answer("Привет! Чтобы продолжить, напиши число 5 + 3 = ?")

@router.message(lambda msg: msg.text.strip() == "8")
async def after_captcha(message: types.Message):
    cursor.execute(
        "INSERT OR IGNORE INTO users (id, username, interactions) VALUES (?, ?, 0)", 
        (message.from_user.id, message.from_user.username)
    )
    conn.commit()
    await message.answer("Отлично, вы прошли проверку! Что вас интересует?", reply_markup=main_menu)

@router.message(lambda msg: msg.text in ["Хочу консультацию", "Просто узнать"])
async def ask_interest(message: types.Message):
    cursor.execute("UPDATE users SET interactions = interactions + 1 WHERE id = ?", (message.from_user.id,))
    conn.commit()
    await message.answer("Спасибо! Свяжитесь с нашим менеджером:",
        reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton(text="Написать менеджеру", url="https://t.me/ManagerUsername")
        )
    )

@router.message(commands=["stats"])
async def stats(message: types.Message):
    cursor.execute("SELECT COUNT(*), SUM(interactions) FROM users")
    users, interactions = cursor.fetchone()
    await message.answer(f"Пользователей: {users}\nВсего взаимодействий: {interactions or 0}")

# --- Webhook server ---
async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(app):
    await bot.delete_webhook()
    await bot.session.close()

def main():
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
    setup_application(app, dp, bot=bot)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)

if __name__ == "__main__":
    main()
