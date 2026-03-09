from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.database import db
from utils.texts import get_text, get_category_name
from utils.helpers import format_currency, format_datetime

router = Router()

@router.message(F.text == "📋 Полная история")
async def cmd_full_history(message: Message):
    """Show complete transaction history"""
    telegram_id = message.from_user.id
    user = await db.get_user(telegram_id)
    language = user['language'] if user else 'ru'
    
    # Get user settings for currency
    settings = await db.get_user_settings(telegram_id)
    currency = settings['currency'] if settings else 'RUB'
    
    # Get all transactions (limited to 50 for performance)
    transactions = await db.get_user_transactions(telegram_id, limit=50)
    
    if not transactions:
        await message.answer(get_text('no_transactions', language))
        return
    
    # Group transactions by date
    from collections import defaultdict
    grouped_transactions = defaultdict(list)
    
    for transaction in transactions:
        date_str = format_datetime(datetime.fromisoformat(transaction['created_at'])).split(' ')[0]
        grouped_transactions[date_str].append(transaction)
    
    # Format history message
    text = "📋 Полная история операций:\n\n"
    
    for date, day_transactions in sorted(grouped_transactions.items(), reverse=True):
        text += f"📅 {date}:\n"
        
        daily_income = 0
        daily_expenses = 0
        
        for transaction in day_transactions:
            category_name = get_category_name(transaction['category'], language)
            formatted_amount = format_currency(transaction['amount'], currency)
            transaction_type = "💰" if transaction['type'] == 'income' else "💸"
            
            text += f"  {transaction_type} {category_name} — {formatted_amount}"
            if transaction['wallet_name']:
                text += f" ({transaction['wallet_name']})"
            text += "\n"
            
            if transaction['type'] == 'income':
                daily_income += transaction['amount']
            else:
                daily_expenses += transaction['amount']
        
        # Add daily summary
        daily_balance = daily_income - daily_expenses
        text += f"  💼 Итог: +{format_currency(daily_income, currency)} / -{format_currency(daily_expenses, currency)} = {format_currency(daily_balance, currency)}\n\n"
    
    await message.answer(text)

@router.message(F.text == "📊 Сводка по категориям")
async def cmd_category_summary(message: Message):
    """Show category summary"""
    telegram_id = message.from_user.id
    user = await db.get_user(telegram_id)
    language = user['language'] if user else 'ru'
    
    # Get user settings for currency
    settings = await db.get_user_settings(telegram_id)
    currency = settings['currency'] if settings else 'RUB'
    
    # Get all transactions
    transactions = await db.get_user_transactions(telegram_id, limit=100)
    
    if not transactions:
        await message.answer(get_text('no_transactions', language))
        return
    
    # Group by category and type
    from collections import defaultdict
    category_stats = defaultdict(lambda: {'income': 0, 'expenses': 0, 'count': 0})
    
    for transaction in transactions:
        category = transaction['category']
        category_stats[category]['count'] += 1
        
        if transaction['type'] == 'income':
            category_stats[category]['income'] += transaction['amount']
        else:
            category_stats[category]['expenses'] += transaction['amount']
    
    # Format summary message
    text = "📊 Сводка по категориям:\n\n"
    
    for category, stats in sorted(category_stats.items(), key=lambda x: x[1]['expenses'] + x[1]['income'], reverse=True):
        category_name = get_category_name(category, language)
        text += f"📂 {category_name}:\n"
        
        if stats['income'] > 0:
            text += f"  💰 Доход: {format_currency(stats['income'], currency)} ({stats['count'] if stats['income'] > stats['expenses'] else stats['count'] - (stats['expenses'] > 0 and stats['income'] == 0)} операций)\n"
        
        if stats['expenses'] > 0:
            text += f"  💸 Расход: {format_currency(stats['expenses'], currency)} ({stats['count'] if stats['expenses'] > stats['income'] else stats['count'] - (stats['income'] > 0 and stats['expenses'] == 0)} операций)\n"
        
        text += "\n"
    
    await message.answer(text)

@router.message(F.text == "🔍 Поиск по дате")
async def cmd_search_by_date(message: Message, state: FSMContext):
    """Start date-based search"""
    user = await db.get_user(message.from_user.id)
    language = user['language'] if user else 'ru'
    
    await message.answer("Введите дату в формате ГГГГ-ММ-ДД (например, 2026-03-09):")
    await state.set_state(HistoryStates.waiting_for_date)

class HistoryStates:
    waiting_for_date = State()

@router.message(HistoryStates.waiting_for_date)
async def process_date_search(message: Message, state: FSMContext):
    """Process date-based search"""
    from datetime import datetime
    
    try:
        search_date = datetime.strptime(message.text.strip(), "%Y-%m-%d")
    except ValueError:
        await message.answer("❌ Неверный формат даты. Попробуйте еще раз (ГГГГ-ММ-ДД):")
        return
    
    telegram_id = message.from_user.id
    user = await db.get_user(telegram_id)
    language = user['language'] if user else 'ru'
    
    # Get user settings for currency
    settings = await db.get_user_settings(telegram_id)
    currency = settings['currency'] if settings else 'RUB'
    
    # Get transactions for the specified date
    # This would require a new database method to filter by date
    # For now, we'll show all transactions and filter client-side
    transactions = await db.get_user_transactions(telegram_id, limit=100)
    
    # Filter by date
    filtered_transactions = []
    for transaction in transactions:
        transaction_date = datetime.fromisoformat(transaction['created_at']).date()
        if transaction_date == search_date.date():
            filtered_transactions.append(transaction)
    
    if not filtered_transactions:
        await message.answer(f"❌ Операций за {search_date.strftime('%Y-%m-%d')} не найдено.")
        await state.clear()
        return
    
    # Format results
    text = f"🔍 Операции за {search_date.strftime('%Y-%m-%d')}:\n\n"
    
    daily_income = 0
    daily_expenses = 0
    
    for transaction in filtered_transactions:
        category_name = get_category_name(transaction['category'], language)
        formatted_amount = format_currency(transaction['amount'], currency)
        transaction_type = "💰" if transaction['type'] == 'income' else "💸"
        time_str = datetime.fromisoformat(transaction['created_at']).strftime('%H:%M')
        
        text += f"{transaction_type} {time_str} - {category_name} — {formatted_amount}"
        if transaction['wallet_name']:
            text += f" ({transaction['wallet_name']})"
        text += "\n"
        
        if transaction['type'] == 'income':
            daily_income += transaction['amount']
        else:
            daily_expenses += transaction['amount']
    
    # Add daily summary
    daily_balance = daily_income - daily_expenses
    text += f"\n💼 Итог за день: +{format_currency(daily_income, currency)} / -{format_currency(daily_expenses, currency)} = {format_currency(daily_balance, currency)}"
    
    await message.answer(text)
    await state.clear()

# Import datetime for the history handler
from datetime import datetime