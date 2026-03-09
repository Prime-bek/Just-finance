from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.database import db
from keyboards.settings_kb import (
    get_settings_menu, get_language_settings, 
    get_currency_settings, get_notification_settings
)
from utils.texts import get_text

router = Router()

@router.callback_query(F.data == "back_to_settings")
async def back_to_settings(callback: CallbackQuery):
    """Return to settings menu"""
    await callback.answer()
    
    user = await db.get_user(callback.from_user.id)
    language = user['language'] if user else 'ru'
    
    settings = await db.get_user_settings(callback.from_user.id)
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
    
    await callback.message.edit_text(settings_text, reply_markup=keyboard)

def get_language_name(lang_code: str) -> str:
    """Get language display name"""
    from utils.texts import get_language_name as get_lang_name
    return get_lang_name(lang_code)

@router.callback_query(F.data == "settings_language")
async def settings_language(callback: CallbackQuery):
    """Show language settings"""
    await callback.answer()
    
    user = await db.get_user(callback.from_user.id)
    language = user['language'] if user else 'ru'
    
    settings = await db.get_user_settings(callback.from_user.id)
    current_lang = settings['language'] if settings else 'ru'
    
    text = get_text('select_language', language)
    keyboard = get_language_settings(current_lang)
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("lang_"))
async def change_language(callback: CallbackQuery):
    """Change user language"""
    await callback.answer()
    
    new_lang = callback.data.replace("lang_", "")
    user_id = callback.from_user.id
    
    # Update user language in database
    await db.update_user_settings(user_id, language=new_lang)
    
    # Update user record
    await db.update_user_language(user_id, new_lang)
    
    text = get_text('settings_updated', new_lang)
    keyboard = get_settings_menu(new_lang)
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@router.callback_query(F.data == "settings_currency")
async def settings_currency(callback: CallbackQuery):
    """Show currency settings"""
    await callback.answer()
    
    user = await db.get_user(callback.from_user.id)
    language = user['language'] if user else 'ru'
    
    settings = await db.get_user_settings(callback.from_user.id)
    current_currency = settings['currency'] if settings else 'RUB'
    
    text = get_text('select_currency', language)
    keyboard = get_currency_settings(current_currency)
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("currency_"))
async def change_currency(callback: CallbackQuery):
    """Change user currency"""
    await callback.answer()
    
    new_currency = callback.data.replace("currency_", "")
    user_id = callback.from_user.id
    
    # Update user currency in database
    await db.update_user_settings(user_id, currency=new_currency)
    
    user = await db.get_user(user_id)
    language = user['language'] if user else 'ru'
    
    text = get_text('settings_updated', language)
    keyboard = get_settings_menu(language)
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@router.callback_query(F.data == "settings_notifications")
async def settings_notifications(callback: CallbackQuery):
    """Show notification settings"""
    await callback.answer()
    
    user = await db.get_user(callback.from_user.id)
    language = user['language'] if user else 'ru'
    
    settings = await db.get_user_settings(callback.from_user.id)
    current_status = settings['notifications'] if settings else True
    
    text = "🔔 Настройки напоминаний"
    keyboard = get_notification_settings(current_status)
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@router.callback_query(F.data == "enable_notifications")
async def enable_notifications(callback: CallbackQuery):
    """Enable notifications"""
    await callback.answer()
    
    user_id = callback.from_user.id
    await db.update_user_settings(user_id, notifications=True)
    
    user = await db.get_user(user_id)
    language = user['language'] if user else 'ru'
    
    text = get_text('settings_updated', language)
    keyboard = get_settings_menu(language)
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@router.callback_query(F.data == "disable_notifications")
async def disable_notifications(callback: CallbackQuery):
    """Disable notifications"""
    await callback.answer()
    
    user_id = callback.from_user.id
    await db.update_user_settings(user_id, notifications=False)
    
    user = await db.get_user(user_id)
    language = user['language'] if user else 'ru'
    
    text = get_text('settings_updated', language)
    keyboard = get_settings_menu(language)
    
    await callback.message.edit_text(text, reply_markup=keyboard)