from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import aiosqlite

from bot.database import db
from keyboards.wallet_kb import (
    get_user_wallets, get_wallet_types, get_wallet_actions, 
    get_delete_confirmation, get_back_to_admin
)
from utils.texts import get_text

router = Router()

class WalletStates(StatesGroup):
    waiting_for_wallet_name = State()
    waiting_for_wallet_type = State()

@router.callback_query(F.data == "create_wallet")
async def create_wallet_start(callback: CallbackQuery, state: FSMContext):
    """Start wallet creation process"""
    await callback.answer()
    
    user = await db.get_user(callback.from_user.id)
    language = user['language'] if user else 'ru'
    
    text = get_text('select_wallet_type', language)
    keyboard = get_wallet_types()
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.set_state(WalletStates.waiting_for_wallet_type)

@router.callback_query(F.data.startswith("wallet_type_"))
async def select_wallet_type(callback: CallbackQuery, state: FSMContext):
    """Handle wallet type selection"""
    await callback.answer()
    
    wallet_type = callback.data.replace("wallet_type_", "")
    await state.update_data(wallet_type=wallet_type)
    
    user = await db.get_user(callback.from_user.id)
    language = user['language'] if user else 'ru'
    
    text = get_text('enter_wallet_name', language)
    await callback.message.edit_text(text)
    await state.set_state(WalletStates.waiting_for_wallet_name)

@router.message(WalletStates.waiting_for_wallet_name)
async def process_wallet_name(message: Message, state: FSMContext):
    """Process wallet name input"""
    wallet_name = message.text.strip()
    
    if len(wallet_name) > 50:
        user = await db.get_user(message.from_user.id)
        language = user['language'] if user else 'ru'
        await message.answer("❌ Название кошелька слишком длинное. Введите короткое название:")
        return
    
    data = await state.get_data()
    wallet_type = data.get('wallet_type', 'main')
    
    # Create wallet
    wallet_id = await db.create_wallet(message.from_user.id, wallet_name, wallet_type)
    
    user = await db.get_user(message.from_user.id)
    language = user['language'] if user else 'ru'
    
    text = get_text('wallet_created', language, name=wallet_name)
    
    # Return to wallets menu
    wallets = await db.get_user_wallets(message.from_user.id)
    keyboard = get_user_wallets(wallets)
    
    await message.answer(text, reply_markup=keyboard)
    await state.clear()

@router.callback_query(F.data.startswith("wallet_"))
async def show_wallet_details(callback: CallbackQuery):
    """Show wallet details and actions"""
    await callback.answer()
    
    wallet_id = int(callback.data.replace("wallet_", ""))
    
    # Get wallet info
    user_id = callback.from_user.id
    wallets = await db.get_user_wallets(user_id)
    wallet = next((w for w in wallets if w['id'] == wallet_id), None)
    
    if not wallet:
        await callback.message.edit_text("❌ Кошелек не найден.")
        return
    
    user = await db.get_user(user_id)
    language = user['language'] if user else 'ru'
    
    # Get wallet balance
    balance = await db.get_wallet_balance(wallet_id)
    
    # Format wallet info
    wallet_info = f"💳 {wallet['name']}\n"
    wallet_info += f"💰 Баланс: {balance:,} so'm\n"
    if wallet['is_main']:
        wallet_info += "⭐ Основной кошелек\n"
    
    keyboard = get_wallet_actions(wallet_id, wallet['is_main'])
    
    await callback.message.edit_text(wallet_info, reply_markup=keyboard)

@router.callback_query(F.data.startswith("set_main_"))
async def set_main_wallet(callback: CallbackQuery):
    """Set wallet as main"""
    await callback.answer()
    
    wallet_id = int(callback.data.replace("set_main_", ""))
    user_id = callback.from_user.id
    
    # Verify wallet exists and belongs to user
    wallets = await db.get_user_wallets(user_id)
    wallet = next((w for w in wallets if w['id'] == wallet_id), None)
    
    if not wallet:
        await callback.message.edit_text("❌ Кошелек не найден.")
        return
    
    # Check if already main
    if wallet['is_main']:
        await callback.answer("Этот кошелек уже основной.")
        return
    
    # Set wallet as main using database method
    success = await db.set_main_wallet(wallet_id, user_id)
    
    if success:
        await callback.message.edit_text("✅ Кошелек установлен как основной.")
    else:
        await callback.message.edit_text("❌ Не удалось установить кошелек как основной.")

@router.callback_query(F.data.startswith("delete_wallet_"))
async def delete_wallet_confirmation(callback: CallbackQuery):
    """Show wallet deletion confirmation"""
    await callback.answer()
    
    wallet_id = int(callback.data.replace("delete_wallet_", ""))
    
    user = await db.get_user(callback.from_user.id)
    language = user['language'] if user else 'ru'
    
    text = "❓ Вы уверены, что хотите удалить этот кошелек? Все транзакции в этом кошельке также будут удалены."
    keyboard = get_delete_confirmation(wallet_id)
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@router.callback_query(F.data == "cancel_delete")
async def cancel_delete_wallet(callback: CallbackQuery):
    """Cancel wallet deletion"""
    await callback.answer()
    
    # Return to wallets menu
    user_id = callback.from_user.id
    wallets = await db.get_user_wallets(user_id)
    keyboard = get_user_wallets(wallets)
    
    user = await db.get_user(user_id)
    language = user['language'] if user else 'ru'
    text = get_text('your_wallets', language)
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("confirm_delete_"))
async def confirm_delete_wallet(callback: CallbackQuery):
    """Confirm wallet deletion"""
    await callback.answer()
    
    wallet_id = int(callback.data.replace("confirm_delete_", ""))
    user_id = callback.from_user.id
    
    # Delete wallet using database method
    success = await db.delete_wallet(wallet_id, user_id)
    
    user = await db.get_user(user_id)
    language = user['language'] if user else 'ru'
    
    if success:
        await callback.message.edit_text("✅ Кошелек успешно удален.")
    else:
        await callback.message.edit_text("❌ Не удалось удалить кошелек.")

@router.callback_query(F.data == "back_to_wallets")
async def back_to_wallets(callback: CallbackQuery):
    """Return to wallets menu"""
    await callback.answer()
    
    user_id = callback.from_user.id
    wallets = await db.get_user_wallets(user_id)
    keyboard = get_user_wallets(wallets)
    
    user = await db.get_user(user_id)
    language = user['language'] if user else 'ru'
    text = get_text('your_wallets', language)
    
    await callback.message.edit_text(text, reply_markup=keyboard)