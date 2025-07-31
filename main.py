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
WEBHOOK_SECRET = "super_secret_key"
WEBHOOK_URL = "https://telegram-bot-o8fs.onrender.com/webhook"

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
    "Зняти з Розшуку": """✅ Зняття з РОЗШУКУ на 1 рік - з повною гарантією недоторканості та оновленою датою пройденого ВЛК - 4000 дол

✅ БРОНЮВАННЯ і відстрочка на 1 рік для тих, хто в РОЗШУКУ з виключенням розшуку і гарантією недоторканості на 1 рік - 5500 дол

Процедура:
1. Перевірка клієнта за паспортними даними та пдф з резерв
2. Часткова оплата в розмірі 50% і активація послуги
3. Перевірка оновлення в базі Резерв+, Оберіг/Армор та оплата другої частини
4. Відправка паперових документів бронювання, якщо була вибрана дана опція

⌛️ Таймінг:
Миттєва консультація та скрінінг клієнта
Зняття з розшуку або бронювання від 3 до 10 робочих днів
Зняття з розшуку та бронювання - від 5 до 12 робочих днів

💲 Оплата:
Крипто USDT, BTC, XMR або карта

💬 ВІДГУКИ ТА ГАРАНТІЇ:
Відгуки, гарантії та підтвердження - інформація конфіденційна, тому видається у приватному спілкуванні після перевірки клієнта та попереднього погодження на замовлення послуги!

ГАРАНТОВАНИЙ РЕЗУЛЬТАТ ТА ВАША БЕЗПЕКА!
ЗВЕРТАЙТЕСЯ!!!

на головну - /start
зняття СЗЧ - /military""",
    "Бронювання": """✅ БРОНЮВАННЯ і відстрочка на 1 рік ...

на головну - /start
зняття з РОЗШУКУ - /rozshuk""",
    "Виїзд за кордон": """✅ Виключення з обліку на 5 років ...

на головну - /start
виведення з ЗС - /military""",
    "СЗЧ/Коміс": """✅  Зняття СЗЧ на гарантований 1 рік ...

на головну - /start
виведення з ЗС - /rozshuk""",
}

# --- Фото ---
images = {
    "Зняти з Розшуку": "images/rozshuk.jpg",
    "Бронювання": "images/bron.jpg",
    "Виїзд за кордон": "images/vyezd.jpg",
    "СЗЧ/Коміс": "images/szch.jpg",
}

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

@dp.message(F.text.in_(["Зняти з Розшуку", "Бронювання", "Виїзд за кордон", "СЗЧ/Коміс"]))
async def send_info(message: types.Message):
    choice = message.text
    photo_path = images[choice]

    # Надсилаємо фото + текст одночасно
    with open(photo_path, "rb") as photo:
        sent_photo = await message.answer_photo(photo, caption=texts[choice], reply_markup=consultation_button)

    # Чекаємо 5 сек і видаляємо фото (текст залишається, бо він у caption)
    await asyncio.sleep(5)
    await sent_photo.delete()

# --- Webhook ---
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
