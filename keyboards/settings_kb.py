from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.config import LANGUAGES, CURRENCIES

def get_settings_menu(language: str = 'ru') -> InlineKeyboardMarkup:
    """Get settings menu keyboard"""
    kb = InlineKeyboardBuilder()
    
    kb.add(InlineKeyboardButton(text="🌐 Язык" if language == 'ru' else "🌐 Til", callback_data="settings_language"))
    kb.add(InlineKeyboardButton(text="💱 Валюта" if language == 'ru' else "💱 Valyuta", callback_data="settings_currency"))
    kb.add(InlineKeyboardButton(text="🔔 Напоминания" if language == 'ru' else "🔔 Eslatmalar", callback_data="settings_notifications"))
    kb.add(InlineKeyboardButton(text="⬅️ Назад" if language == 'ru' else "⬅️ Orqaga", callback_data="back_to_menu"))
    
    kb.adjust(1)
    return kb.as_markup()

def get_language_settings(current_lang: str) -> InlineKeyboardMarkup:
    """Get language selection keyboard"""
    kb = InlineKeyboardBuilder()
    
    for lang_code, lang_name in LANGUAGES.items():
        text = lang_name
        if lang_code == current_lang:
            text += " ✅"
        kb.add(InlineKeyboardButton(text=text, callback_data=f"lang_{lang_code}"))
    
    kb.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_settings"))
    
    kb.adjust(1)
    return kb.as_markup()

def get_currency_settings(current_currency: str) -> InlineKeyboardMarkup:
    """Get currency selection keyboard"""
    kb = InlineKeyboardBuilder()
    
    for currency_code, currency_symbol in CURRENCIES.items():
        text = f"{currency_symbol} {currency_code}"
        if currency_code == current_currency:
            text += " ✅"
        kb.add(InlineKeyboardButton(text=text, callback_data=f"currency_{currency_code}"))
    
    kb.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_settings"))
    
    kb.adjust(2)
    return kb.as_markup()

def get_notification_settings(current_status: bool) -> InlineKeyboardMarkup:
    """Get notification settings keyboard"""
    kb = InlineKeyboardBuilder()
    
    status_text = "Включены ✅" if current_status else "Выключены ❌"
    kb.add(InlineKeyboardButton(text=f"Текущее состояние: {status_text}", callback_data="notification_status"))
    
    if current_status:
        kb.add(InlineKeyboardButton(text="🔕 Выключить", callback_data="disable_notifications"))
    else:
        kb.add(InlineKeyboardButton(text="🔔 Включить", callback_data="enable_notifications"))
    
    kb.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_settings"))
    
    kb.adjust(1)
    return kb.as_markup()