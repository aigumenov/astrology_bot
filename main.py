"""
Главный файл запуска бота
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import register_onboarding_handlers

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """
    Основная функция запуска бота.
    """
    # Инициализация бота
    # Замените YOUR_BOT_TOKEN на реальный токен
    bot = Bot(token="YOUR_BOT_TOKEN")
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрация хендлеров
    register_onboarding_handlers(dp)
    
    logger.info("Бот запущен и готов к работе!")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())