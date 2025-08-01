import asyncio
import logging
import os
from pathlib import Path
import aiosqlite
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile
)
from aiogram.exceptions import TelegramConflictError

# ========== КОНФИГУРАЦИЯ ==========
API_TOKEN = os.getenv("API_TOKEN")
if not API_TOKEN:
    raise ValueError("Не указан API_TOKEN в переменных окружения")

DB_PATH = "db.sqlite3"
IMAGES_DIR = Path("images")
IMAGES_DIR.mkdir(exist_ok=True)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher()

# ========== ГЛАВНОЕ МЕНЮ ==========
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Зняти з Розшуку"), KeyboardButton(text="Бронювання")],
        [KeyboardButton(text="Виїзд за кордон"), KeyboardButton(text="СЗЧ/Коміс")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Оберіть послугу..."
)

# ========== ТЕКСТЫ УСЛУГ ==========
SERVICE_DATA = {
    "Зняти з Розшуку": {
        "text": """✅ <b>Зняття з РОЗШУКУ на 1 рік</b>
- з повною гарантією недоторканості
- оновленою датою пройденого ВЛК
💰 <i>Вартість:</i> <b>4000 $</b>

✅ <b>БРОНЮВАННЯ і відстрочка на 1 рік</b>
- для тих, хто в РОЗШУКУ
- з виключенням розшуку
- гарантія недоторканості на 1 рік
💰 <i>Вартість:</i> <b>5500 $</b>

📌 <b>Процедура:</b>
1. Перевірка клієнта за паспортними даними та PDF з резерв
2. Часткова оплата 50% + активація послуги
3. Перевірка оновлення в базі (Резерв+, Оберіг/Армор)
4. Оплата другої частини
5. Відправка паперових документів (за бажанням)

⏳ <b>Таймінг:</b>
▪ Миттєва консультація та скрінінг
▪ Зняття з розшуку: 3-10 робочих днів
▪ Бронювання: 3-10 робочих днів
▪ Комплекс: 5-12 робочих днів

💳 <b>Оплата:</b>
USDT | BTC | XMR | Карта України

🔒 <b>Гарантії:</b>
Всі підтвердження, відгуки та гарантії надаються після перевірки клієнта у приватному порядку!

🛡 <b>ГАРАНТОВАНИЙ РЕЗУЛЬТАТ ТА ПОВНА БЕЗПЕКА!</b>

👉 @victor_reserv001 - оператор
👉 /start - головне меню
👉 /military - зняття СЗЧ""",
        "image": "rozshuk.jpg"
    },
    "Бронювання": {
        "text": """✅ <b>БРОНЮВАННЯ і відстрочка на 1 рік</b>
- для тих, хто на обліку
💰 <i>Вартість:</i> <b>3000 $</b>

✅ <b>БРОНЮВАННЯ і відстрочка на 1 рік</b>
- для тих, хто в РОЗШУКУ
- з виключенням розшуку
💰 <i>Вартість:</i> <b>5500 $</b>

📌 <b>Процедура:</b>
1. Перевірка клієнта за паспортними даними та PDF з резерв
2. Часткова оплата 50% + активація послуги
3. Перевірка оновлення в базі (Резерв+, Оберіг/Армор)
4. Оплата другої частини
5. Відправка документів кур'єром/поштою

⏳ <b>Таймінг:</b>
▪ Миттєва консультація та скрінінг
▪ Бронювання: 3-10 робочих днів
▪ Комплекс: 5-12 робочих днів

💳 <b>Оплата:</b>
USDT | BTC | XMR | Карта України

🔒 <b>Гарантії:</b>
Всі підтвердження, відгуки та гарантії надаються після перевірки клієнта у приватному порядку!

🛡 <b>ГАРАНТОВАНИЙ РЕЗУЛЬТАТ ТА ПОВНА БЕЗПЕКА!</b>

👉 @victor_reserv001 - оператор
👉 /start - головне меню
👉 /rozshuk - зняття з розшуку""",
        "image": "bron.jpg"
    },
    "Виїзд за кордон": {
        "text": """✅ <b>Виїзд за кордон</b>
- Виключення з обліку на 5 років
- Можливість перетину кордону ("Білий квиток")
💰 <i>Вартість:</i> <b>від 8000 $</b>

📌 <b>Процедура:</b>
1. Перевірка клієнта за паспортними даними та PDF з резерв
2. Часткова оплата 50% + активація послуги
3. Перевірка документів, підтвердження по базам
4. Оплата другої частини
5. Відправка документів кур'єром/поштою

⏳ <b>Таймінг:</b>
▪ Миттєва консультація та скрінінг
▪ Підготовка: 2-5 робочих днів
▪ Документація: 10-20 робочих днів

💳 <b>Оплата:</b>
USDT | BTC | XMR | Карта України

🔒 <b>Гарантії:</b>
Всі підтвердження, відгуки та гарантії надаються після перевірки клієнта у приватному порядку!

🛡 <b>ГАРАНТОВАНИЙ РЕЗУЛЬТАТ ТА ПОВНА БЕЗПЕКА!</b>

👉 @victor_reserv001 - оператор
👉 /start - головне меню
👉 /military - виведення з ЗС""",
        "image": "vyezd.jpg"
    },
    "СЗЧ/Коміс": {
        "text": """✅ <b>Зняття СЗЧ</b>
- на гарантований 1 рік
💰 <i>Вартість:</i> <b>5000 $</b>

✅ <b>Звільнення зі служби</b>
- за станом здоров'я
💰 <i>Вартість:</i> <b>від 8000 $</b>

📌 <b>Процедура:</b>
1. Перевірка клієнта за паспортними даними та PDF з резерв
2. Часткова оплата 50% + активація послуги
3. Перевірка документів, підтвердження по базам
4. Оплата другої частини
5. Відправка документів кур'єром/поштою

⏳ <b>Таймінг:</b>
▪ Миттєва консультація та скрінінг
▪ Підготовка: 2-5 робочих днів
▪ Документація: 10-20 робочих днів

💳 <b>Оплата:</b>
USDT | BTC | XMR | Карта України

🔒 <b>Гарантії:</b>
Всі підтвердження, відгуки та гарантії надаються після перевірки клієнта у приватному порядку!

🛡 <b>ГАРАНТОВАНИЙ РЕЗУЛЬТАТ ТА ПОВНА БЕЗПЕКА!</b>

👉 @victor_reserv001 - оператор
👉 /start - головне меню
👉 /rozshuk - зняття з розшуку""",
        "image": "szch.jpg"
    }
}

# ========== ОБРАБОТЧИКИ ==========
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привіт! Щоб продовжити, напиши результат: 5 + 3 = ?")

@dp.message(F.text == "8")
async def after_captcha(message: types.Message):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, interactions INT)"
            )
            await db.execute(
                "INSERT OR IGNORE INTO users (id, username, interactions) VALUES (?, ?, 0)",
                (message.from_user.id, message.from_user.username),
            )
            await db.commit()
        await message.answer("Чудово, ви пройшли перевірку! Оберіть послугу:", reply_markup=main_menu)
    except Exception as e:
        logger.error(f"Database error: {e}")
        await message.answer("Сталася помилка. Спробуйте ще раз /start")

@dp.message(F.text == "Зняти з Розшуку")
async def handle_rozshuk(message: types.Message):
    await handle_service(message, "Зняти з Розшуку")

@dp.message(F.text == "Бронювання")
async def handle_bron(message: types.Message):
    await handle_service(message, "Бронювання")

@dp.message(F.text == "Виїзд за кордон")
async def handle_vyezd(message: types.Message):
    await handle_service(message, "Виїзд за кордон")

@dp.message(F.text == "СЗЧ/Коміс")
async def handle_szch(message: types.Message):
    await handle_service(message, "СЗЧ/Коміс")

async def handle_service(message: types.Message, service_name: str):
    service = SERVICE_DATA.get(service_name)
    if not service:
        return await message.answer("Ця послуга тимчасово недоступна")
    
    try:
        # Отправка текста
        await message.answer(
            service["text"],
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        
        # Отправка фото
        photo_path = IMAGES_DIR / service["image"]
        if photo_path.exists():
            await message.answer_photo(
                FSInputFile(photo_path),
                caption="🔍 Детальна інформація вище 👆"
            )
        
        # Кнопка консультации
        consultation_btn = InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(
                    text="🔷 ОТРИМАТИ КОНСУЛЬТАЦІЮ 🔷", 
                    url="https://t.me/victor_reserv001"
                )
            ]]
        )
        await message.answer(
            "Натисніть кнопку нижче для зв'язку з фахівцем:",
            reply_markup=consultation_btn
        )
        
    except Exception as e:
        logger.error(f"Error processing {service_name}: {e}")
        await message.answer("⚠️ Сталася помилка. Спробуйте пізніше.")

# ========== БАЗА ДАННЫХ ==========
async def init_db():
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, interactions INT)"
            )
            await db.commit()
    except Exception as e:
        logger.error(f"Database init error: {e}")

# ========== ЗАПУСК БОТА ==========
async def main():
    await init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    
    while True:
        try:
            logger.info("Starting bot polling...")
            await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        except TelegramConflictError:
            logger.warning("Conflict detected, restarting in 5 sec...")
            await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"Fatal error: {e}, restarting in 10 sec...")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
