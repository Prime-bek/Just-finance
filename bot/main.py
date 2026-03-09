import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import BOT_TOKEN
from bot.database import db
from services.reminders import reminder_service
from middleware.user_check import UserCheckMiddleware
from middleware.throttling import ThrottlingMiddleware
from handlers import (
    start_router as start,
    wallets_router as wallets,
    transactions_router as transactions,
    stats_router as stats,
    history_router as history,
    settings_router as settings,
    admin_router as admin
)

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def main():
    # Validate BOT_TOKEN before proceeding
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN environment variable is not set. Please set it in your environment variables.")
        logger.info("You can get a bot token from @BotFather on Telegram")
        return
    
    # Initialize database
    try:
        await db.create_tables()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return
    
    # Initialize reminder service
    try:
        await reminder_service.start()
        await reminder_service.schedule_all_user_reminders()
        logger.info("Reminder service started")
    except Exception as e:
        logger.error(f"Failed to start reminder service: {e}")
        # Continue without reminders rather than crashing
    
    # Initialize bot
    try:
        bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        dp = Dispatcher()
    except Exception as e:
        logger.error(f"Failed to initialize bot: {e}")
        return
    
    # Register middleware
    dp.message.middleware(UserCheckMiddleware())
    dp.callback_query.middleware(UserCheckMiddleware())
    dp.message.middleware(ThrottlingMiddleware(rate_limit=0.5))  # 0.5 second rate limit
    dp.callback_query.middleware(ThrottlingMiddleware(rate_limit=0.3))  # 0.3 second rate limit for callbacks
    
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
        try:
            await reminder_service.stop()
            logger.info("Reminder service stopped")
        except:
            pass

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot stopped with error: {e}")