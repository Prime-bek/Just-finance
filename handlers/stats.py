from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.database import db
from services.statistics import statistics_service
from utils.texts import get_text
from utils.helpers import format_currency

router = Router()

@router.message(F.text == "📊 Детальная статистика")
async def cmd_detailed_stats(message: Message):
    """Show detailed statistics"""
    telegram_id = message.from_user.id
    user = await db.get_user(telegram_id)
    language = user['language'] if user else 'ru'
    
    # Get user settings for currency
    settings = await db.get_user_settings(telegram_id)
    currency = settings['currency'] if settings else 'RUB'
    
    # Get comprehensive statistics
    monthly_stats = await statistics_service.get_user_statistics(telegram_id, 'month')
    weekly_stats = await statistics_service.get_user_statistics(telegram_id, 'week')
    
    # Format detailed statistics message
    text = "📊 Детальная статистика\n\n"
    
    # Monthly statistics
    text += "📅 За месяц:\n"
    formatted_income = format_currency(monthly_stats['income'], currency)
    formatted_expenses = format_currency(monthly_stats['expenses'], currency)
    formatted_balance = format_currency(monthly_stats['balance'], currency)
    
    text += f"💰 Доход: {formatted_income}\n"
    text += f"💸 Расход: {formatted_expenses}\n"
    text += f"💼 Баланс: {formatted_balance}\n"
    
    if monthly_stats['top_expense_category']:
        category_name = get_category_display_name(monthly_stats['top_expense_category'], language)
        text += f"🏆 Топ категория: {category_name}\n"
    
    text += f"📊 Средний доход в день: {format_currency(monthly_stats['avg_daily_income'], currency)}\n"
    text += f"📊 Средний расход в день: {format_currency(monthly_stats['avg_daily_expenses'], currency)}\n\n"
    
    # Weekly statistics
    text += "📅 За неделю:\n"
    formatted_weekly_income = format_currency(weekly_stats['income'], currency)
    formatted_weekly_expenses = format_currency(weekly_stats['expenses'], currency)
    formatted_weekly_balance = format_currency(weekly_stats['balance'], currency)
    
    text += f"💰 Доход: {formatted_weekly_income}\n"
    text += f"💸 Расход: {formatted_weekly_expenses}\n"
    text += f"💼 Баланс: {formatted_weekly_balance}\n\n"
    
    # Category breakdown
    text += "📊 Расходы по категориям:\n"
    category_breakdown = await statistics_service.get_category_breakdown(telegram_id, 'month')
    
    if category_breakdown['category_breakdown']:
        for category, data in category_breakdown['category_breakdown'].items():
            category_name = get_category_display_name(category, language)
            percentage = data['percentage']
            amount = format_currency(data['amount'], currency)
            text += f"• {category_name}: {amount} ({percentage:.1f}%)\n"
    else:
        text += "Нет расходов в этом месяце.\n"
    
    await message.answer(text)

def get_category_display_name(category: str, language: str) -> str:
    """Get category display name in user's language"""
    from utils.texts import get_category_name
    return get_category_name(category, language)

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    """Show admin statistics"""
    from bot.config import ADMIN_ID
    
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Доступ запрещен.")
        return
    
    await callback.answer()
    
    # Get all users and transactions
    all_users = await db.get_all_users()
    all_transactions = await db.get_all_transactions(limit=1000)
    
    # Calculate admin statistics
    total_users = len(all_users)
    total_transactions = len(all_transactions)
    
    # Calculate total amounts
    total_income = sum(t['amount'] for t in all_transactions if t['type'] == 'income')
    total_expenses = sum(t['amount'] for t in all_transactions if t['type'] == 'expense')
    
    # Count users by status
    active_users = len([u for u in all_users if u['status'] == 'active'])
    blocked_users = len([u for u in all_users if u['status'] == 'blocked'])
    
    # Recent registrations (last 7 days)
    from datetime import datetime, timedelta
    week_ago = datetime.now() - timedelta(days=7)
    recent_users = len([u for u in all_users if datetime.fromisoformat(u['registration_date']) > week_ago])
    
    # Format admin statistics
    text = "🛡️ Админ статистика\n\n"
    text += f"👥 Всего пользователей: {total_users}\n"
    text += f"✅ Активных: {active_users}\n"
    text += f"🔒 Заблокировано: {blocked_users}\n"
    text += f"🆕 Новых за неделю: {recent_users}\n\n"
    
    text += "💰 Финансовая статистика:\n"
    text += f"📊 Всего транзакций: {total_transactions}\n"
    text += f"💰 Общий доход: {format_currency(total_income, 'RUB')}\n"
    text += f"💸 Общий расход: {format_currency(total_expenses, 'RUB')}\n"
    text += f"💼 Общий баланс: {format_currency(total_income - total_expenses, 'RUB')}\n\n"
    
    # Top users by transaction count
    user_transaction_counts = {}
    for transaction in all_transactions:
        user_id = transaction['user_id']
        user_transaction_counts[user_id] = user_transaction_counts.get(user_id, 0) + 1
    
    if user_transaction_counts:
        top_users = sorted(user_transaction_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        text += "🏆 Топ пользователей по транзакциям:\n"
        for user_id, count in top_users:
            user = next((u for u in all_users if u['telegram_id'] == user_id), None)
            if user:
                text += f"• {user['name']} ({count} транзакций)\n"
    
    await callback.message.edit_text(text)