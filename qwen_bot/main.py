import asyncio
import logging
from middleware import LoggingMiddleware  # ← добавьте импорт
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from database import init_db
from handlers import main_router  # ← импортируем объединённый роутер

from dotenv import load_dotenv
import os

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Вывод в консоль (systemd/journal)
        logging.FileHandler("bot.log", encoding="utf-8")  # Опционально: файл
    ]
)

logger = logging.getLogger(__name__)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

async def main():
    init_db()
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Подключаем middleware для логирования
    dp.update.middleware(LoggingMiddleware())

    dp.include_router(main_router)
    logger.info("Starting bot...")

    # Указываем, какие обновления нам нужны
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(
        bot,
        allowed_updates=["message", "callback_query"]  # ← только эти типы!
    )

if __name__ == "__main__":
    asyncio.run(main())