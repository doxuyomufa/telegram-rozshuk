import os
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

# --- Logging ---
logging.basicConfig(level=logging.INFO)

# --- Variables from environment ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")  # https://telegram-bot-2-1aou.onrender.com
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Keyboards ---
interest_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Зняти з Розшуку"), KeyboardButton(text="Бронювання")],
        [KeyboardButton(text="Виїзд за кордон"), KeyboardButton(text="СЗЧ/Коміс")]
    ],
    resize_keyboard=True,
)

consultation_button = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Консультація", url="https://t.me/robic33ai")]]
)

texts = {
    "Зняти з Розшуку": "✅ Зняття з РОЗШУКУ на 1 рік ...\n\nна головну - /start",
    "Бронювання": "✅ БРОНЮВАННЯ і відстрочка на 1 рік ...\n\nна головну - /start",
    "Виїзд за кордон": "✅ Виїзд за кордон ...\n\nна головну - /start",
    "СЗЧ/Коміс": "✅  Зняття СЗЧ ...\n\nна головну - /start",
}

images = {
    "Зняти з Розшуку": "images/rozshuk.jpg",
    "Бронювання": "images/bron.jpg",
    "Виїзд за кордон": "images/vyezd.jpg",
    "СЗЧ/Коміс": "images/szch.jpg",
}

# --- Handlers ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Привіт! Аби продовжити напиши число 5 + 3 = ?")

@dp.message(F.text == "8")
async def after_captcha(message: types.Message):
    await message.answer("Чудово, Ви пройшли перевірку! Що Вас цікавить?", reply_markup=interest_menu)

@dp.message(F.text.in_(texts.keys()))
async def send_info(message: types.Message):
    choice = message.text
    photo_path = images[choice]
    with open(photo_path, "rb") as photo:
        sent_photo = await message.answer_photo(photo, caption=texts[choice], reply_markup=consultation_button)
    await asyncio.sleep(5)
    await sent_photo.delete()

# --- Webhook ---
async def handle_webhook(request):
    data = await request.json()
    update = types.Update(**data)
    await dp._process_update(update, bot)   # Aiogram 3.x internal update processing
    return web.Response()

async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(app):
    await bot.delete_webhook()

def main():
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle_webhook)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

if __name__ == "__main__":
    main()
