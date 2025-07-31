import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

API_TOKEN = "7922526391:AAF6f9uxMOc2CDvaHBU5NrX7DI9ET-d-ysE"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- База данных ---
conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, interactions INT)")
conn.commit()

# --- Кнопки ---
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(KeyboardButton("Хочу консультацию"), KeyboardButton("Просто узнать"))

# --- Старт ---
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    # простая "капча"
    await message.answer("Привет! Чтобы продолжить, напиши число 5 + 3 = ?")

@dp.message_handler(lambda message: message.text.strip() == "8")
async def after_captcha(message: types.Message):
    # сохраняем пользователя
    cursor.execute("INSERT OR IGNORE INTO users (id, username, interactions) VALUES (?, ?, 0)", 
                   (message.from_user.id, message.from_user.username))
    conn.commit()
    await message.answer("Отлично, вы прошли проверку! Что вас интересует?", reply_markup=main_menu)

@dp.message_handler(lambda message: message.text in ["Хочу консультацию", "Просто узнать"])
async def ask_interest(message: types.Message):
    # обновляем счетчик
    cursor.execute("UPDATE users SET interactions = interactions + 1 WHERE id = ?", (message.from_user.id,))
    conn.commit()
    await message.answer("Спасибо! Свяжитесь с нашим менеджером:", 
                         reply_markup=types.InlineKeyboardMarkup().add(
                             types.InlineKeyboardButton(text="Написать менеджеру", url="https://t.me/ManagerUsername")
                         ))

@dp.message_handler(commands=["stats"])
async def stats(message: types.Message):
    cursor.execute("SELECT COUNT(*), SUM(interactions) FROM users")
    users, interactions = cursor.fetchone()
    await message.answer(f"Пользователей: {users}\nВсего взаимодействий: {interactions or 0}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
