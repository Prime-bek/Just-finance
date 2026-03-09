from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext

from bot.database import db
from bot.config import ADMIN_ID
from keyboards.main_menu import get_main_menu, get_main_menu_uz
from keyboards.admin_kb import get_admin_menu
from utils.texts import get_text
from utils.helpers import validate_username

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command"""
    await state.clear()
    
    # Add or update user in database
    telegram_id = message.from_user.id
    name = message.from_user.full_name
    username = message.from_user.username
    
    await db.add_user(telegram_id, name, username)
    
    # Get user language (default to Russian)
    user = await db.get_user(telegram_id)
    language = user['language'] if user else 'ru'
    
    # Send welcome message
    welcome_text = get_text('welcome', language)
    
    if telegram_id == ADMIN_ID:
        welcome_text += "\n\n🛡️ Вы администратор бота."
    
    # Get appropriate keyboard based on language
    if language == 'uz':
        keyboard = get_main_menu_uz()
    else:
        keyboard = get_main_menu()
    
    await message.answer(welcome_text, reply_markup=keyboard)

@router.message(F.text == "📊 Баланс")
@router.message(F.text == "📊 Balans")
async def cmd_balance(message: Message):
    """Handle balance command from main menu"""
    from services.balance import balance_service
    from utils.helpers import format_currency
    
    telegram_id = message.from_user.id
    user = await db.get_user(telegram_id)
    language = user['language'] if user else 'ru'
    
    # Get user balance info
    balance_info = await balance_service.get_user_total_balance(telegram_id)
    
    if balance_info['wallet_count'] == 0:
        await message.answer(get_text('no_wallets', language))
        return
    
    # Get user settings for currency
    settings = await db.get_user_settings(telegram_id)
    currency = settings['currency'] if settings else 'RUB'
    
    # Format balance message
    balance_text = get_text('your_balance', language) + "\n\n"
    
    for wallet in balance_info['wallet_balances']:
        formatted_balance = format_currency(wallet['balance'], currency)
        balance_text += get_text('wallet_balance', language, 
                               emoji=get_wallet_emoji(wallet['type']),
                               name=wallet['name'],
                               amount=formatted_balance) + "\n"
    
    await message.answer(balance_text)

def get_wallet_emoji(wallet_type: str) -> str:
    """Get emoji for wallet type"""
    emoji_map = {
        'main': '💳',
        'cash': '💵',
        'bank': '🏦',
        'savings': '💰'
    }
    return emoji_map.get(wallet_type, '💳')

@router.message(F.text == "➕ Добавить операцию")
@router.message(F.text == "➕ Operatsiya qoshish")
async def cmd_add_transaction(message: Message):
    """Handle add transaction command from main menu"""
    from keyboards.categories_kb import get_operation_types
    
    telegram_id = message.from_user.id
    user = await db.get_user(telegram_id)
    language = user['language'] if user else 'ru'
    
    text = get_text('select_operation_type', language)
    keyboard = get_operation_types()
    
    await message.answer(text, reply_markup=keyboard)

@router.message(F.text == "📋 История")
@router.message(F.text == "📋 Tarix")
async def cmd_history(message: Message):
    """Handle history command from main menu"""
    from utils.helpers import format_currency
    
    telegram_id = message.from_user.id
    user = await db.get_user(telegram_id)
    language = user['language'] if user else 'ru'
    
    # Get user settings for currency
    settings = await db.get_user_settings(telegram_id)
    currency = settings['currency'] if settings else 'RUB'
    
    # Get recent transactions
    transactions = await db.get_user_transactions(telegram_id, limit=10)
    
    if not transactions:
        await message.answer(get_text('no_transactions', language))
        return
    
    history_text = get_text('recent_transactions', language) + "\n\n"
    
    for transaction in transactions:
        formatted_amount = format_currency(transaction['amount'], currency)
        category_name = get_category_display_name(transaction['category'], language)
        history_text += get_text('transaction_item', language, 
                               category=category_name,
                               amount=formatted_amount) + "\n"
    
    await message.answer(history_text)

def get_category_display_name(category: str, language: str) -> str:
    """Get category display name in user's language"""
    from utils.texts import get_category_name
    return get_category_name(category, language)

@router.message(F.text == "📈 Статистика")
@router.message(F.text == "📈 Statistika")
async def cmd_statistics(message: Message):
    """Handle statistics command from main menu"""
    from services.statistics import statistics_service
    from utils.helpers import format_currency
    
    telegram_id = message.from_user.id
    user = await db.get_user(telegram_id)
    language = user['language'] if user else 'ru'
    
    # Get user settings for currency
    settings = await db.get_user_settings(telegram_id)
    currency = settings['currency'] if settings else 'RUB'
    
    # Get statistics for current month
    stats = await statistics_service.get_user_statistics(telegram_id, 'month')
    
    # Format statistics message
    period_text = "месяц" if language == 'ru' else "oy"
    stats_text = get_text('statistics', language, period=period_text) + "\n\n"
    
    formatted_income = format_currency(stats['income'], currency)
    formatted_expenses = format_currency(stats['expenses'], currency)
    formatted_balance = format_currency(stats['balance'], currency)
    
    stats_text += get_text('income', language, amount=formatted_income) + "\n"
    stats_text += get_text('expenses', language, amount=formatted_expenses) + "\n"
    stats_text += get_text('balance', language, amount=formatted_balance) + "\n"
    
    if stats['top_expense_category']:
        category_name = get_category_display_name(stats['top_expense_category'], language)
        stats_text += "\n" + get_text('top_category', language, category=category_name)
    
    await message.answer(stats_text)

@router.message(F.text == "💳 Кошельки")
@router.message(F.text == "💳 Hamyonlar")
async def cmd_wallets(message: Message):
    """Handle wallets command from main menu"""
    from keyboards.wallet_kb import get_user_wallets
    
    telegram_id = message.from_user.id
    user = await db.get_user(telegram_id)
    language = user['language'] if user else 'ru'
    
    # Get user wallets
    wallets = await db.get_user_wallets(telegram_id)
    
    if not wallets:
        await message.answer(get_text('no_wallets', language))
        return
    
    text = get_text('your_wallets', language)
    keyboard = get_user_wallets(wallets)
    
    await message.answer(text, reply_markup=keyboard)

@router.message(F.text == "⚙️ Настройки")
@router.message(F.text == "⚙️ Sozlamalar")
async def cmd_settings(message: Message):
    """Handle settings command from main menu"""
    from keyboards.settings_kb import get_settings_menu
    
    telegram_id = message.from_user.id
    user = await db.get_user(telegram_id)
    language = user['language'] if user else 'ru'
    
    settings = await db.get_user_settings(telegram_id)
    if not settings:
        settings = {'language': 'ru', 'currency': 'RUB', 'notifications': True}
    
    # Format settings text
    settings_text = get_text('settings_menu', language) + "\n\n"
    settings_text += get_text('language', language, language=get_language_name(settings['language'])) + "\n"
    settings_text += get_text('currency', language, currency=settings['currency']) + "\n"
    
    notifications_status = "Включены" if settings['notifications'] else "Выключены"
    if language == 'uz':
        notifications_status = "Yoqilgan" if settings['notifications'] else "O'chirilgan"
    
    settings_text += get_text('notifications', language, status=notifications_status)
    
    keyboard = get_settings_menu(language)
    
    await message.answer(settings_text, reply_markup=keyboard)

def get_language_name(lang_code: str) -> str:
    """Get language display name"""
    from utils.texts import get_language_name as get_lang_name
    return get_lang_name(lang_code)

# Admin command
@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Handle admin command"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа к админ панели.")
        return
    
    user = await db.get_user(ADMIN_ID)
    language = user['language'] if user else 'ru'
    
    # Get admin statistics
    all_users = await db.get_all_users()
    all_transactions = await db.get_all_transactions(limit=1000)
    
    admin_text = get_text('admin_panel', language) + "\n\n"
    admin_text += get_text('total_users', language, count=len(all_users)) + "\n"
    admin_text += get_text('total_transactions', language, count=len(all_transactions))
    
    keyboard = get_admin_menu()
    
    await message.answer(admin_text, reply_markup=keyboard)