from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.database import db
from bot.config import ADMIN_ID
from keyboards.admin_kb import (
    get_admin_menu, get_users_list, get_user_actions, get_back_to_admin
)
from utils.texts import get_text
from utils.helpers import format_datetime, get_user_status_text, validate_username

router = Router()

class AdminStates:
    waiting_for_user_id = State()

@router.callback_query(F.data == "admin_panel")
async def admin_panel(callback: CallbackQuery):
    """Return to admin panel"""
    await callback.answer()
    
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Доступ запрещен.")
        return
    
    # Get admin statistics
    all_users = await db.get_all_users()
    all_transactions = await db.get_all_transactions(limit=1000)
    
    admin_text = get_text('admin_panel', 'ru') + "\n\n"
    admin_text += get_text('total_users', 'ru', count=len(all_users)) + "\n"
    admin_text += get_text('total_transactions', 'ru', count=len(all_transactions))
    
    keyboard = get_admin_menu()
    
    await callback.message.edit_text(admin_text, reply_markup=keyboard)

@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):
    """Show all users"""
    await callback.answer()
    
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Доступ запрещен.")
        return
    
    all_users = await db.get_all_users()
    
    if not all_users:
        await callback.message.edit_text("❌ Пользователи не найдены.")
        return
    
    text = "👥 Все пользователи:"
    keyboard = get_users_list(all_users)
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("users_page_"))
async def admin_users_pagination(callback: CallbackQuery):
    """Handle users pagination"""
    await callback.answer()
    
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Доступ запрещен.")
        return
    
    page = int(callback.data.replace("users_page_", ""))
    all_users = await db.get_all_users()
    
    text = "👥 Все пользователи:"
    keyboard = get_users_list(all_users, page)
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("user_"))
async def admin_user_details(callback: CallbackQuery):
    """Show user details"""
    await callback.answer()
    
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Доступ запрещен.")
        return
    
    user_id = int(callback.data.replace("user_", ""))
    user = await db.get_user(user_id)
    
    if not user:
        await callback.message.edit_text("❌ Пользователь не найден.")
        return
    
    # Format user info
    language_name = get_language_name(user['language'])
    status_text = get_user_status_text(user['status'], 'ru')
    username = validate_username(user['username'])
    
    user_info = get_text('user_info', 'ru',
                        id=user['telegram_id'],
                        name=user['name'],
                        username=username,
                        language=language_name,
                        registration=format_datetime(datetime.fromisoformat(user['registration_date'])),
                        activity=format_datetime(datetime.fromisoformat(user['last_activity'])),
                        status=status_text)
    
    keyboard = get_user_actions(user_id, user['status'])
    
    await callback.message.edit_text(user_info, reply_markup=keyboard)

def get_language_name(lang_code: str) -> str:
    """Get language display name"""
    from utils.texts import get_language_name as get_lang_name
    return get_lang_name(lang_code)

@router.callback_query(F.data.startswith("block_user_"))
async def block_user(callback: CallbackQuery):
    """Block user"""
    await callback.answer()
    
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Доступ запрещен.")
        return
    
    user_id = int(callback.data.replace("block_user_", ""))
    
    if user_id == ADMIN_ID:
        await callback.answer("❌ Нельзя заблокировать администратора.")
        return
    
    await db.update_user_status(user_id, 'blocked')
    
    # Show updated user details
    user = await db.get_user(user_id)
    if user:
        language_name = get_language_name(user['language'])
        status_text = get_user_status_text('blocked', 'ru')
        username = validate_username(user['username'])
        
        user_info = get_text('user_info', 'ru',
                            id=user['telegram_id'],
                            name=user['name'],
                            username=username,
                            language=language_name,
                            registration=format_datetime(datetime.fromisoformat(user['registration_date'])),
                            activity=format_datetime(datetime.fromisoformat(user['last_activity'])),
                            status=status_text)
        
        keyboard = get_user_actions(user_id, 'blocked')
        
        await callback.message.edit_text(user_info, reply_markup=keyboard)

@router.callback_query(F.data.startswith("unblock_user_"))
async def unblock_user(callback: CallbackQuery):
    """Unblock user"""
    await callback.answer()
    
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Доступ запрещен.")
        return
    
    user_id = int(callback.data.replace("unblock_user_", ""))
    
    await db.update_user_status(user_id, 'active')
    
    # Show updated user details
    user = await db.get_user(user_id)
    if user:
        language_name = get_language_name(user['language'])
        status_text = get_user_status_text('active', 'ru')
        username = validate_username(user['username'])
        
        user_info = get_text('user_info', 'ru',
                            id=user['telegram_id'],
                            name=user['name'],
                            username=username,
                            language=language_name,
                            registration=format_datetime(datetime.fromisoformat(user['registration_date'])),
                            activity=format_datetime(datetime.fromisoformat(user['last_activity'])),
                            status=status_text)
        
        keyboard = get_user_actions(user_id, 'active')
        
        await callback.message.edit_text(user_info, reply_markup=keyboard)

@router.callback_query(F.data == "admin_transactions")
async def admin_transactions(callback: CallbackQuery):
    """Show recent transactions"""
    await callback.answer()
    
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Доступ запрещен.")
        return
    
    transactions = await db.get_all_transactions(limit=20)
    
    if not transactions:
        await callback.message.edit_text("❌ Транзакции не найдены.")
        return
    
    text = "📊 Последние транзакции:\n\n"
    
    for transaction in transactions:
        user = await db.get_user(transaction['user_id'])
        user_name = user['name'] if user else f"ID:{transaction['user_id']}"
        
        type_emoji = "💰" if transaction['type'] == 'income' else "💸"
        category_name = get_category_name(transaction['category'], 'ru')
        
        text += f"{type_emoji} {user_name}\n"
        text += f"   {category_name} — {transaction['amount']:,} so'm\n"
        text += f"   {transaction['wallet_name']}\n"
        text += f"   {format_datetime(datetime.fromisoformat(transaction['created_at']))}\n\n"
    
    keyboard = get_back_to_admin()
    
    await callback.message.edit_text(text, reply_markup=keyboard)

def get_category_name(category: str, language: str) -> str:
    """Get category display name"""
    from utils.texts import get_category_name as get_cat_name
    return get_cat_name(category, language)

# Import datetime for admin handler
from datetime import datetime
from aiogram.fsm.state import State