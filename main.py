import logging
import os
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiohttp import web
import asyncio

API_TOKEN = "7922526391:AAF6f9uxMOc2CDvaHBU5NrX7DI9ET-d-ysE"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- База данных ---
conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()
cursor.execute(
    "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, interactions INT)"
)
conn.commit()

# --- Кнопки ---
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(KeyboardButton("Хочу консультацию"), KeyboardButton("Просто узнать"))


# --- Обработчики aiogram ---


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Привет! Чтобы продолжить, напиши число 5 + 3 = ?")


@dp.message_handler(lambda message: message.text.strip() == "8")
async def after_captcha(message: types.Message):
    cursor.execute(
        "INSERT OR IGNORE INTO users (id, username, interactions) VALUES (?, ?, 0)",
        (message.from_user.id, message.from_user.username),
    )
    conn.commit()
    await message.answer("Отлично, вы прошли проверку! Что вас интересует?", reply_markup=main_menu)


@dp.message_handler(lambda message: message.text in ["Хочу консультацию", "Просто узнать"])
async def ask_interest(message: types.Message):
    cursor.execute(
        "UPDATE users SET interactions = interactions + 1 WHERE id = ?", (message.from_user.id,)
    )
    conn.commit()
    await message.answer(
        "Спасибо! Свяжитесь с нашим менеджером:",
        reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton(
                text="Написать менеджеру", url="https://t.me/ManagerUsername"
            )
        ),
    )


@dp.message_handler(commands=["stats"])
async def stats(message: types.Message):
    cursor.execute("SELECT COUNT(*), SUM(interactions) FROM users")
    users, interactions = cursor.fetchone()
    await message.answer(f"Пользователей: {users}\nВсего взаимодействий: {interactions or 0}")


# --- HTTP сервер для пинга (UptimeRobot и т.п.) ---


async def handle_health(request):
    return web.Response(text="OK")


async def start_webserver():
    app = web.Application()
    app.router.add_get("/", handle_health)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()


async def main():
    # Запускаем HTTP сервер
    await start_webserver()

    # Запускаем Telegram-бота
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
