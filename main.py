import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

API_TOKEN = os.getenv("API_TOKEN")  # Токен бота
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")  # Например https://telegram-bot-7pjk.onrender.com
WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "super_secret_key")
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}" if WEBHOOK_HOST else None

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Клавиатура
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
    "Зняти з Розшуку": "Текст для Зняття з Розшуку",
    "Бронювання": "Текст для Бронювання",
    "Виїзд за кордон": "Текст для Виїзду за кордон",
    "СЗЧ/Коміс": "Текст для СЗЧ/Коміс",
}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привіт! Введіть число 5 + 3 = ?")

@dp.message(F.text == "8")
async def captcha_passed(message: types.Message):
    await message.answer("Чудово, Ви пройшли перевірку! Що Вас цікавить?", reply_markup=interest_menu)

@dp.message(F.text.in_(list(texts.keys())))
async def send_info(message: types.Message):
    choice = message.text
    await message.answer(texts[choice], reply_markup=consultation_button)

# Установка webhook при старте приложения (если WEBHOOK_HOST задан)
async def on_startup(app):
    if WEBHOOK_URL:
        logging.info(f"Setting webhook: {WEBHOOK_URL}")
        await bot.set_webhook(WEBHOOK_URL, secret_token=WEBHOOK_SECRET)

async def on_shutdown(app):
    logging.info("Deleting webhook")
    await bot.delete_webhook()

# Обработка обновлений от Telegram (Webhook)
async def handle_webhook(request):
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
        return web.Response(status=403)
    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(bot, update)
    return web.Response()

# Роут для ручной установки webhook с любого URL (в том числе после деплоя)
async def set_webhook_handler(request):
    url = request.query.get("url")
    if not url:
        return web.Response(text="Missing 'url' parameter", status=400)
    await bot.set_webhook(url, secret_token=WEBHOOK_SECRET)
    return web.Response(text=f"Webhook set to {url}")

def main():
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle_webhook)
    app.router.add_get("/set_webhook", set_webhook_handler)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    port = int(os.getenv("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
