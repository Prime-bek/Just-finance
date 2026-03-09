from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_main_menu() -> ReplyKeyboardMarkup:
    """Get main menu keyboard"""
    kb = ReplyKeyboardBuilder()
    
    # First row
    kb.row(
        KeyboardButton(text="📊 Баланс"),
        KeyboardButton(text="➕ Добавить операцию")
    )
    
    # Second row
    kb.row(
        KeyboardButton(text="📋 История"),
        KeyboardButton(text="📈 Статистика")
    )
    
    # Third row
    kb.row(
        KeyboardButton(text="💳 Кошельки"),
        KeyboardButton(text="⚙️ Настройки")
    )
    
    return kb.as_markup(resize_keyboard=True)

def get_main_menu_uz() -> ReplyKeyboardMarkup:
    """Get main menu keyboard in Uzbek"""
    kb = ReplyKeyboardBuilder()
    
    # First row
    kb.row(
        KeyboardButton(text="📊 Balans"),
        KeyboardButton(text="➕ Operatsiya qoshish")
    )
    
    # Second row
    kb.row(
        KeyboardButton(text="📋 Tarix"),
        KeyboardButton(text="📈 Statistika")
    )
    
    # Third row
    kb.row(
        KeyboardButton(text="💳 Hamyonlar"),
        KeyboardButton(text="⚙️ Sozlamalar")
    )
    
    return kb.as_markup(resize_keyboard=True)

def get_back_button() -> ReplyKeyboardMarkup:
    """Get back button keyboard"""
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text="⬅️ Назад"))
    return kb.as_markup(resize_keyboard=True)

def get_back_button_uz() -> ReplyKeyboardMarkup:
    """Get back button keyboard in Uzbek"""
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text="⬅️ Orqaga"))
    return kb.as_markup(resize_keyboard=True)

def get_cancel_button() -> ReplyKeyboardMarkup:
    """Get cancel button keyboard"""
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text="❌ Отмена"))
    return kb.as_markup(resize_keyboard=True)

def get_cancel_button_uz() -> ReplyKeyboardMarkup:
    """Get cancel button keyboard in Uzbek"""
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text="❌ Bekor qilish"))
    return kb.as_markup(resize_keyboard=True)