from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.config import EXPENSE_CATEGORIES, INCOME_CATEGORIES

def get_operation_types() -> InlineKeyboardMarkup:
    """Get operation types selection keyboard"""
    kb = InlineKeyboardBuilder()
    
    kb.add(InlineKeyboardButton(text="💸 Расход", callback_data="operation_expense"))
    kb.add(InlineKeyboardButton(text="💰 Доход", callback_data="operation_income"))
    kb.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu"))
    
    kb.adjust(2, 1)
    return kb.as_markup()

def get_expense_categories() -> InlineKeyboardMarkup:
    """Get expense categories keyboard"""
    kb = InlineKeyboardBuilder()
    
    for category_key, category_name in EXPENSE_CATEGORIES.items():
        kb.add(InlineKeyboardButton(text=category_name, callback_data=f"expense_{category_key}"))
    
    kb.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_operations"))
    
    kb.adjust(2, 2, 2, 2, 1)
    return kb.as_markup()

def get_income_categories() -> InlineKeyboardMarkup:
    """Get income categories keyboard"""
    kb = InlineKeyboardBuilder()
    
    for category_key, category_name in INCOME_CATEGORIES.items():
        kb.add(InlineKeyboardButton(text=category_name, callback_data=f"income_{category_key}"))
    
    kb.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_operations"))
    
    kb.adjust(2, 2, 1)
    return kb.as_markup()

def get_wallet_selection(wallets: list) -> InlineKeyboardMarkup:
    """Get wallet selection keyboard for transactions"""
    kb = InlineKeyboardBuilder()
    
    for wallet in wallets:
        wallet_name = wallet['name']
        if wallet['is_main']:
            wallet_name += " ⭐"
        kb.add(InlineKeyboardButton(text=wallet_name, callback_data=f"trans_wallet_{wallet['id']}"))
    
    kb.add(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_transaction"))
    
    kb.adjust(1)
    return kb.as_markup()

def get_transaction_confirmation() -> InlineKeyboardMarkup:
    """Get transaction confirmation keyboard"""
    kb = InlineKeyboardBuilder()
    
    kb.add(InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_transaction"))
    kb.add(InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_transaction"))
    
    kb.adjust(2)
    return kb.as_markup()