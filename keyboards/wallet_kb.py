from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.config import WALLET_TYPES

def get_wallet_types() -> InlineKeyboardMarkup:
    """Get wallet types selection keyboard"""
    kb = InlineKeyboardBuilder()
    
    for wallet_type, name in WALLET_TYPES.items():
        kb.add(InlineKeyboardButton(text=name, callback_data=f"wallet_type_{wallet_type}"))
    
    kb.adjust(2)
    return kb.as_markup()

def get_user_wallets(wallets: list) -> InlineKeyboardMarkup:
    """Get user's wallets keyboard"""
    kb = InlineKeyboardBuilder()
    
    for wallet in wallets:
        wallet_name = wallet['name']
        if wallet['is_main']:
            wallet_name += " ⭐"
        kb.add(InlineKeyboardButton(text=wallet_name, callback_data=f"wallet_{wallet['id']}"))
    
    kb.add(InlineKeyboardButton(text="➕ Создать кошелек", callback_data="create_wallet"))
    kb.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu"))
    
    kb.adjust(1)
    return kb.as_markup()

def get_wallet_actions(wallet_id: int, is_main: bool = False) -> InlineKeyboardMarkup:
    """Get wallet actions keyboard"""
    kb = InlineKeyboardBuilder()
    
    if not is_main:
        kb.add(InlineKeyboardButton(text="⭐ Сделать основным", callback_data=f"set_main_{wallet_id}"))
    
    kb.add(InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_wallet_{wallet_id}"))
    kb.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_wallets"))
    
    kb.adjust(1)
    return kb.as_markup()

def get_delete_confirmation(wallet_id: int) -> InlineKeyboardMarkup:
    """Get delete confirmation keyboard"""
    kb = InlineKeyboardBuilder()
    
    kb.add(InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"confirm_delete_{wallet_id}"))
    kb.add(InlineKeyboardButton(text="❌ Нет, отменить", callback_data="cancel_delete"))
    
    kb.adjust(2)
    return kb.as_markup()