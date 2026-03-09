from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.database import db
from keyboards.categories_kb import (
    get_operation_types, get_expense_categories, get_income_categories,
    get_wallet_selection, get_transaction_confirmation
)
from utils.texts import get_text, get_category_name
from utils.helpers import parse_amount, format_currency

router = Router()

class TransactionStates(StatesGroup):
    waiting_for_amount = State()
    waiting_for_confirmation = State()

# Store temporary transaction data
transaction_data = {}

@router.callback_query(F.data == "back_to_operations")
async def back_to_operations(callback: CallbackQuery):
    """Return to operation type selection"""
    await callback.answer()
    
    user = await db.get_user(callback.from_user.id)
    language = user['language'] if user else 'ru'
    
    text = get_text('select_operation_type', language)
    keyboard = get_operation_types()
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@router.callback_query(F.data == "operation_expense")
async def select_expense_category(callback: CallbackQuery, state: FSMContext):
    """Show expense categories"""
    await callback.answer()
    
    user = await db.get_user(callback.from_user.id)
    language = user['language'] if user else 'ru'
    
    await state.update_data(transaction_type='expense')
    
    text = get_text('select_category', language)
    keyboard = get_expense_categories()
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@router.callback_query(F.data == "operation_income")
async def select_income_category(callback: CallbackQuery, state: FSMContext):
    """Show income categories"""
    await callback.answer()
    
    user = await db.get_user(callback.from_user.id)
    language = user['language'] if user else 'ru'
    
    await state.update_data(transaction_type='income')
    
    text = get_text('select_category', language)
    keyboard = get_income_categories()
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("expense_"))
async def select_expense_amount(callback: CallbackQuery, state: FSMContext):
    """Handle expense category selection"""
    await callback.answer()
    
    category = callback.data.replace("expense_", "")
    user = await db.get_user(callback.from_user.id)
    language = user['language'] if user else 'ru'
    
    await state.update_data(category=category)
    
    text = get_text('enter_amount', language)
    await callback.message.edit_text(text)
    await state.set_state(TransactionStates.waiting_for_amount)

@router.callback_query(F.data.startswith("income_"))
async def select_income_amount(callback: CallbackQuery, state: FSMContext):
    """Handle income category selection"""
    await callback.answer()
    
    category = callback.data.replace("income_", "")
    user = await db.get_user(callback.from_user.id)
    language = user['language'] if user else 'ru'
    
    await state.update_data(category=category)
    
    text = get_text('enter_amount', language)
    await callback.message.edit_text(text)
    await state.set_state(TransactionStates.waiting_for_amount)

@router.message(TransactionStates.waiting_for_amount)
async def process_amount(message: Message, state: FSMContext):
    """Process amount input"""
    amount = parse_amount(message.text)
    
    if amount is None:
        user = await db.get_user(message.from_user.id)
        language = user['language'] if user else 'ru'
        await message.answer(get_text('invalid_amount', language))
        return
    
    data = await state.get_data()
    transaction_type = data.get('transaction_type')
    category = data.get('category')
    
    # Store transaction data
    user_id = message.from_user.id
    transaction_data[user_id] = {
        'type': transaction_type,
        'category': category,
        'amount': amount
    }
    
    # Show wallet selection
    user = await db.get_user(user_id)
    language = user['language'] if user else 'ru'
    
    wallets = await db.get_user_wallets(user_id)
    if not wallets:
        await message.answer("❌ У вас нет кошельков. Создайте кошелек сначала.")
        await state.clear()
        return
    
    text = "Выберите кошелек для операции:"
    keyboard = get_wallet_selection(wallets)
    
    await message.answer(text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("trans_wallet_"))
async def select_transaction_wallet(callback: CallbackQuery, state: FSMContext):
    """Handle wallet selection for transaction"""
    await callback.answer()
    
    wallet_id = int(callback.data.replace("trans_wallet_", ""))
    user_id = callback.from_user.id
    
    # Get transaction data
    if user_id not in transaction_data:
        await callback.message.edit_text("❌ Данные транзакции утеряны. Начните сначала.")
        await state.clear()
        return
    
    # Store wallet ID
    transaction_data[user_id]['wallet_id'] = wallet_id
    
    # Get wallet info for confirmation
    wallets = await db.get_user_wallets(user_id)
    wallet = next((w for w in wallets if w['id'] == wallet_id), None)
    
    if not wallet:
        await callback.message.edit_text("❌ Кошелек не найден или не принадлежит вам.")
        await state.clear()
        return
    
    user = await db.get_user(user_id)
    language = user['language'] if user else 'ru'
    settings = await db.get_user_settings(user_id)
    currency = settings['currency'] if settings else 'RUB'
    
    # Format confirmation message
    transaction_type = transaction_data[user_id]['type']
    category = transaction_data[user_id]['category']
    amount = transaction_data[user_id]['amount']
    
    formatted_amount = format_currency(amount, currency)
    category_name = get_category_name(category, language)
    
    confirmation_text = get_text('transaction_added', language,
                                 type="расход" if transaction_type == 'expense' else "доход",
                                 category=category_name,
                                 amount=formatted_amount,
                                 wallet=wallet['name'])
    
    keyboard = get_transaction_confirmation()
    
    await callback.message.edit_text(confirmation_text, reply_markup=keyboard)
    await state.set_state(TransactionStates.waiting_for_confirmation)

@router.callback_query(F.data == "confirm_transaction")
async def confirm_transaction(callback: CallbackQuery, state: FSMContext):
    """Confirm and save transaction"""
    await callback.answer()
    
    user_id = callback.from_user.id
    
    # Get transaction data
    if user_id not in transaction_data:
        await callback.message.edit_text("❌ Данные транзакции утеряны. Начните сначала.")
        await state.clear()
        return
    
    data = transaction_data[user_id]
    
    # Save transaction to database
    transaction_id = await db.add_transaction(
        user_id=user_id,
        wallet_id=data['wallet_id'],
        transaction_type=data['type'],
        category=data['category'],
        amount=data['amount']
    )
    
    # Clean up
    del transaction_data[user_id]
    
    user = await db.get_user(user_id)
    language = user['language'] if user else 'ru'
    
    await callback.message.edit_text("✅ Операция успешно добавлена!")
    await state.clear()

@router.callback_query(F.data == "cancel_transaction")
async def cancel_transaction(callback: CallbackQuery, state: FSMContext):
    """Cancel transaction"""
    await callback.answer()
    
    user_id = callback.from_user.id
    
    # Clean up transaction data
    if user_id in transaction_data:
        del transaction_data[user_id]
    
    user = await db.get_user(user_id)
    language = user['language'] if user else 'ru'
    
    await callback.message.edit_text(get_text('operation_cancelled', language))
    await state.clear()