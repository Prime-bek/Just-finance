from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, time
import logging

from bot.database import db
from utils.texts import get_text

logger = logging.getLogger(__name__)

class ReminderService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.jobs = {}
    
    async def start(self):
        """Start the scheduler"""
        self.scheduler.start()
        logger.info("Reminder scheduler started")
    
    async def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Reminder scheduler stopped")
    
    async def add_daily_reminder(self, user_id: int, reminder_time: time = time(20, 0)):
        """Add daily reminder for user"""
        job_id = f"reminder_{user_id}"
        
        # Remove existing job if any
        if job_id in self.jobs:
            self.scheduler.remove_job(job_id)
        
        # Add new job
        job = self.scheduler.add_job(
            self.send_daily_reminder,
            CronTrigger(hour=reminder_time.hour, minute=reminder_time.minute),
            id=job_id,
            args=[user_id],
            replace_existing=True
        )
        
        self.jobs[job_id] = job
        logger.info(f"Added daily reminder for user {user_id} at {reminder_time}")
    
    async def remove_reminder(self, user_id: int):
        """Remove reminder for user"""
        job_id = f"reminder_{user_id}"
        
        if job_id in self.jobs:
            self.scheduler.remove_job(job_id)
            del self.jobs[job_id]
            logger.info(f"Removed reminder for user {user_id}")
    
    async def send_daily_reminder(self, user_id: int):
        """Send daily reminder to user"""
        try:
            # Get user info
            user = await db.get_user(user_id)
            if not user or user['status'] != 'active':
                return
            
            # Get user settings
            settings = await db.get_user_settings(user_id)
            if not settings or not settings.get('notifications', True):
                return
            
            language = user['language']
            
            # Get today's statistics
            from services.statistics import statistics_service
            today_stats = await statistics_service.get_user_statistics(user_id, 'today')
            
            # Format reminder message
            reminder_text = self.format_reminder_message(today_stats, language, settings['currency'])
            
            # Send reminder (this would need to be implemented with bot instance)
            # For now, we'll just log it
            logger.info(f"Would send reminder to user {user_id}: {reminder_text}")
            
        except Exception as e:
            logger.error(f"Error sending reminder to user {user_id}: {e}")
    
    def format_reminder_message(self, stats: dict, language: str, currency: str) -> str:
        """Format daily reminder message"""
        from utils.helpers import format_currency
        
        if language == 'uz':
            text = "📊 Кунлик эслатма\n\n"
            text += f"💰 Бугунги даромадингиз: {format_currency(stats['income'], currency)}\n"
            text += f"💸 Бугунги харажатларингиз: {format_currency(stats['expenses'], currency)}\n"
            text += f"💼 Баланс: {format_currency(stats['balance'], currency)}\n\n"
            
            if stats['top_expense_category']:
                category_name = get_category_name(stats['top_expense_category'], language)
                text += f"🏆 Энг ката харажат категорияси: {category_name}\n"
            
            text += "\n💡 Эслатма: Кеча хам кунлик хисоботни куринг!"
        else:
            text = "📊 Ежедневное напоминание\n\n"
            text += f"💰 Ваш доход за сегодня: {format_currency(stats['income'], currency)}\n"
            text += f"💸 Ваши расходы за сегодня: {format_currency(stats['expenses'], currency)}\n"
            text += f"💼 Баланс: {format_currency(stats['balance'], currency)}\n\n"
            
            if stats['top_expense_category']:
                category_name = get_category_name(stats['top_expense_category'], language)
                text += f"🏆 Самая большая категория расходов: {category_name}\n"
            
            text += "\n💡 Напоминание: Не забудьте посмотреть ежедневную статистику!"
        
        return text
    
    async def schedule_all_user_reminders(self):
        """Schedule reminders for all active users"""
        try:
            all_users = await db.get_all_users()
            active_users = [u for u in all_users if u['status'] == 'active']
            
            for user in active_users:
                settings = await db.get_user_settings(user['telegram_id'])
                if settings and settings.get('notifications', True):
                    # Default reminder time: 8 PM
                    await self.add_daily_reminder(user['telegram_id'])
            
            logger.info(f"Scheduled reminders for {len(active_users)} active users")
            
        except Exception as e:
            logger.error(f"Error scheduling user reminders: {e}")

# Global reminder service instance
reminder_service = ReminderService()

def get_category_name(category: str, language: str) -> str:
    """Get category name in specified language"""
    from utils.texts import get_category_name as get_cat_name
    return get_cat_name(category, language)