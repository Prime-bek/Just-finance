import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import BOT_TOKEN
from bot.database import db
from services.reminders import reminder_service
from handlers import (
    start_router as start,
    wallets_router as wallets,
    transactions_router as transactions,
    stats_router as stats,
    history_router as history,
    settings_router as settings,
    admin_router as admin
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    # Initialize database
    await db.create_tables()
    logger.info("Database initialized")
    
    # Initialize reminder service
    await reminder_service.start()
    await reminder_service.schedule_all_user_reminders()
    logger.info("Reminder service started")
    
    # Initialize bot
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    
    # Register routers
    dp.include_router(start.router)
    dp.include_router(wallets.router)
    dp.include_router(transactions.router)
    dp.include_router(stats.router)
    dp.include_router(history.router)
    dp.include_router(settings.router)
    dp.include_router(admin.router)
    
    logger.info("Bot started")
    
    try:
        # Start polling
        await dp.start_polling(bot)
    finally:
        # Cleanup
        await reminder_service.stop()
        logger.info("Reminder service stopped")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot stopped with error: {e}")