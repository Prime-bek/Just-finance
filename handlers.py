from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import TEXTS, CURRENCIES, ADMIN_ID
from database import db
from keyboards import *

router = Router()

# ========== СОСТОЯНИЯ ==========
class AddOperation(StatesGroup):
    waiting_amount = State()
    waiting_wallet = State()

class CreateWallet(StatesGroup):
    waiting_type = State()
    waiting_name = State()

# ========== ХЕЛПЕРЫ ==========
def get_text(key: str, lang: str = "ru", **kwargs) -> str:
    text = TEXTS.get(lang, TEXTS["ru"]).get(key, key)
    return text.format(**kwargs) if kwargs else text

def format_amount(amount: float, currency: str) -> str:
    symbol = CURRENCIES.get(currency, currency)
    return f"{amount:,.0f} {symbol}".replace(",", " ")

async def check_blocked(user_id: int) -> bool:
    user = await db.get_or_create_user(user_id)
    return user["status"] == "blocked"

# ========== СТАРТ ==========
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = await db.get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name
    )
    
    if user["status"] == "blocked":
        await message.answer(get_text("user_blocked", user["language"]))
        return
    
    if not user.get("language"):
        await message.answer(get_text("welcome", "ru"), reply_markup=get_language_kb())
        return
    
    lang = user["language"]
    await message.answer(get_text("menu", lang), reply_markup=get_main_menu(lang))

@router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery):
    lang = callback.data.replace("lang_", "")
    await db.update_user_language(callback.from_user.id, lang)
    await callback.message.delete()
    await callback.message.answer(get_text("menu", lang), reply_markup=get_main_menu(lang))
    await callback.answer()

# ========== ГЛАВНОЕ МЕНЮ ==========
@router.message(F.text.in_([get_text("back", "ru"), get_text("back", "uz")]))
async def back_menu(message: Message, state: FSMContext):
    await state.clear()
    user = await db.get_or_create_user(message.from_user.id)
    lang = user["language"]
    await message.answer(get_text("menu", lang), reply_markup=get_main_menu(lang))

@router.callback_query(F.data == "back_menu")
async def back_menu_cb(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user = await db.get_or_create_user(callback.from_user.id)
    lang = user["language"]
    await callback.message.delete()
    await callback.message.answer(get_text("menu", lang), reply_markup=get_main_menu(lang))
    await callback.answer()

# ========== БАЛАНС ==========
@router.message(F.text.in_([get_text("balance", "ru"), get_text("balance", "uz")]))
async def show_balance(message: Message):
    if await check_blocked(message.from_user.id):
        return
    
    user = await db.get_or_create_user(message.from_user.id)
    lang, currency = user["language"], user["currency"]
    
    wallets = await db.get_user_wallets(message.from_user.id)
    if not wallets:
        await message.answer(get_text("no_wallets", lang))
        return
    
    text = "💰 Ваши кошельки:\n\n" if lang == "ru" else "💰 Sizning hamyonlaringiz:\n\n"
    total = 0.0
    
    for w in wallets:
        balance = await db.get_wallet_balance(w["id"])
        total += balance
        emoji = "⭐" if w["is_main"] else "💳"
        text += f"{emoji} {w['name']}: {format_amount(balance, currency)}\n"
    
    text += f"\n📊 Общий баланс: {format_amount(total, currency)}"
    await message.answer(text, reply_markup=get_main_menu(lang))

# ========== ДОБАВЛЕНИЕ ОПЕРАЦИИ ==========
@router.message(F.text.in_([get_text("add_operation", "ru"), get_text("add_operation", "uz")]))
async def add_operation_start(message: Message, state: FSMContext):
    if await check_blocked(message.from_user.id):
        return
    
    user = await db.get_or_create_user(message.from_user.id)
    lang = user["language"]
    
    await message.answer(get_text("select_type", lang), reply_markup=get_operation_types_kb(lang))

@router.callback_query(F.data == "op_expense")
async def select_expense_cat(callback: CallbackQuery):
    user = await db.get_or_create_user(callback.from_user.id)
    lang = user["language"]
    await callback.message.edit_text(get_text("select_category", lang), reply_markup=get_expense_categories_kb(lang))
    await callback.answer()

@router.callback_query(F.data == "op_income")
async def select_income_cat(callback: CallbackQuery):
    user = await db.get_or_create_user(callback.from_user.id)
    lang = user["language"]
    await callback.message.edit_text(get_text("select_category", lang), reply_markup=get_income_categories_kb(lang))
    await callback.answer()

@router.callback_query(F.data == "back_type")
async def back_to_types(callback: CallbackQuery):
    user = await db.get_or_create_user(callback.from_user.id)
    lang = user["language"]
    await callback.message.edit_text(get_text("select_type", lang), reply_markup=get_operation_types_kb(lang))
    await callback.answer()

@router.callback_query(F.data.startswith("cat_"))
async def select_category(callback: CallbackQuery, state: FSMContext):
    data = callback.data
    op_type = "expense" if "exp_" in data else "income"
    category = data.replace("cat_exp_", "").replace("cat_inc_", "")
    
    await state.update_data(op_type=op_type, category=category)
    await state.set_state(AddOperation.waiting_amount)
    
    user = await db.get_or_create_user(callback.from_user.id)
    lang = user["language"]
    
    await callback.message.delete()
    await callback.message.answer(get_text("enter_amount", lang), reply_markup=get_cancel_kb(lang))
    await callback.answer()

@router.message(AddOperation.waiting_amount)
async def process_amount(message: Message, state: FSMContext):
    if message.text in [get_text("cancel", "ru"), get_text("cancel", "uz")]:
        await back_menu(message, state)
        return
    
    try:
        amount = float(message.text.replace(" ", "").replace(",", "."))
        if amount <= 0:
            raise ValueError
    except ValueError:
        user = await db.get_or_create_user(message.from_user.id)
        await message.answer(get_text("invalid_amount", user["language"]))
        return
    
    await state.update_data(amount=amount)
    await state.set_state(AddOperation.waiting_wallet)
    
    user = await db.get_or_create_user(message.from_user.id)
    lang = user["language"]
    wallets = await db.get_user_wallets(message.from_user.id)
    
    # Показываем кошельки для выбора
    kb = InlineKeyboardBuilder()
    for w in wallets:
        name = w["name"] + (" ⭐" if w["is_main"] else "")
        kb.add(InlineKeyboardButton(text=name, callback_data=f"opwallet_{w['id']}"))
    
    await message.answer("Выберите кошелек:" if lang == "ru" else "Hamyonni tanlang:", reply_markup=kb.adjust(1).as_markup())

@router.callback_query(F.data.startswith("opwallet_"))
async def save_operation(callback: CallbackQuery, state: FSMContext):
    wallet_id = int(callback.data.replace("opwallet_", ""))
    data = await state.get_data()
    
    await db.add_operation(
        callback.from_user.id,
        wallet_id,
        data["op_type"],
        data["category"],
        data["amount"]
    )
    
    await state.clear()
    user = await db.get_or_create_user(callback.from_user.id)
    lang = user["language"]
    
    await callback.message.delete()
    await callback.message.answer(get_text("operation_added", lang), reply_markup=get_main_menu(lang))
    await callback.answer()

# ========== ИСТОРИЯ ==========
@router.message(F.text.in_([get_text("history", "ru"), get_text("history", "uz")]))
async def show_history(message: Message):
    if await check_blocked(message.from_user.id):
        return
    
    user = await db.get_or_create_user(message.from_user.id)
    lang, currency = user["language"], user["currency"]
    
    operations = await db.get_user_operations(message.from_user.id, 10)
    if not operations:
        await message.answer(get_text("no_transactions", lang))
        return
    
    text = get_text("recent_transactions", lang) + "\n\n"
    
    for op in operations:
        emoji = "💰" if op["type"] == "income" else "💸"
        cat_name = (INCOME_CATEGORIES if op["type"] == "income" else EXPENSE_CATEGORIES).get(op["category"], op["category"])
        text += f"{emoji} {cat_name}: {format_amount(op['amount'], currency)}\n"
        text += f"   📅 {op['created_at'][:10]} | {op['wallet_name']}\n\n"
    
    await message.answer(text, reply_markup=get_main_menu(lang))

# ========== СТАТИСТИКА ==========
@router.message(F.text.in_([get_text("stats", "ru"), get_text("stats", "uz")]))
async def show_stats(message: Message):
    if await check_blocked(message.from_user.id):
        return
    
    user = await db.get_or_create_user(message.from_user.id)
    lang, currency = user["language"], user["currency"]
    
    stats = await db.get_user_stats(message.from_user.id, 30)
    
    text = get_text("statistics", lang, period="30 дней" if lang == "ru" else "30 kun") + "\n\n"
    text += get_text("income_stat", lang, amount=format_amount(stats["income"], currency)) + "\n"
    text += get_text("expense_stat", lang, amount=format_amount(stats["expense"], currency)) + "\n"
    text += get_text("balance_stat", lang, amount=format_amount(stats["income"] - stats["expense"], currency))
    
    await message.answer(text, reply_markup=get_main_menu(lang))

# ========== КОШЕЛЬКИ ==========
@router.message(F.text.in_([get_text("wallets", "ru"), get_text("wallets", "uz")]))
async def show_wallets(message: Message):
    if await check_blocked(message.from_user.id):
        return
    
    user = await db.get_or_create_user(message.from_user.id)
    lang = user["language"]
    
    wallets = await db.get_user_wallets(message.from_user.id)
    await message.answer(get_text("your_wallets", lang), reply_markup=get_wallets_kb(wallets, lang))

@router.callback_query(F.data == "create_wallet")
async def create_wallet_start(callback: CallbackQuery, state: FSMContext):
    user = await db.get_or_create_user(callback.from_user.id)
    lang = user["language"]
    
    await state.set_state(CreateWallet.waiting_type)
    await callback.message.edit_text(get_text("select_wallet_type", lang), reply_markup=get_wallet_types_kb(lang))
    await callback.answer()

@router.callback_query(F.data.startswith("wtype_"))
async def select_wallet_type(callback: CallbackQuery, state: FSMContext):
    wallet_type = callback.data.replace("wtype_", "")
    await state.update_data(wallet_type=wallet_type)
    await state.set_state(CreateWallet.waiting_name)
    
    user = await db.get_or_create_user(callback.from_user.id)
    lang = user["language"]
    
    await callback.message.delete()
    await callback.message.answer(get_text("enter_wallet_name", lang), reply_markup=get_cancel_kb(lang))
    await callback.answer()

@router.message(CreateWallet.waiting_name)
async def create_wallet_finish(message: Message, state: FSMContext):
    if message.text in [get_text("cancel", "ru"), get_text("cancel", "uz")]:
        await back_menu(message, state)
        return
    
    data = await state.get_data()
    await db.create_wallet(message.from_user.id, message.text, data["wallet_type"])
    
    await state.clear()
    user = await db.get_or_create_user(message.from_user.id)
    lang = user["language"]
    
    wallets = await db.get_user_wallets(message.from_user.id)
    await message.answer(get_text("wallet_created", lang, name=message.text), reply_markup=get_wallets_kb(wallets, lang))

@router.callback_query(F.data == "back_wallets")
async def back_to_wallets(callback: CallbackQuery):
    user = await db.get_or_create_user(callback.from_user.id)
    lang = user["language"]
    wallets = await db.get_user_wallets(callback.from_user.id)
    await callback.message.edit_text(get_text("your_wallets", lang), reply_markup=get_wallets_kb(wallets, lang))
    await callback.answer()

@router.callback_query(F.data.startswith("wallet_"))
async def wallet_details(callback: CallbackQuery):
    wallet_id = int(callback.data.replace("wallet_", ""))
    wallets = await db.get_user_wallets(callback.from_user.id)
    wallet = next((w for w in wallets if w["id"] == wallet_id), None)
    
    if not wallet:
        await callback.answer("Кошелек не найден!")
        return
    
    user = await db.get_or_create_user(callback.from_user.id)
    lang, currency = user["language"], user["currency"]
    balance = await db.get_wallet_balance(wallet_id)
    
    text = f"💳 {wallet['name']}\n💰 Баланс: {format_amount(balance, currency)}"
    if wallet["is_main"]:
        text += "\n⭐ Основной кошелек"
    
    await callback.message.edit_text(text, reply_markup=get_wallet_actions_kb(wallet_id, wallet["is_main"], lang))
    await callback.answer()

@router.callback_query(F.data.startswith("setmain_"))
async def set_main_wallet(callback: CallbackQuery):
    wallet_id = int(callback.data.replace("setmain_", ""))
    await db.set_main_wallet(wallet_id, callback.from_user.id)
    
    user = await db.get_or_create_user(callback.from_user.id)
    lang = user["language"]
    wallets = await db.get_user_wallets(callback.from_user.id)
    
    await callback.message.edit_text(get_text("your_wallets", lang), reply_markup=get_wallets_kb(wallets, lang))
    await callback.answer("Основной кошелек изменен!")

@router.callback_query(F.data.startswith("delwallet_"))
async def delete_wallet(callback: CallbackQuery):
    wallet_id = int(callback.data.replace("delwallet_", ""))
    await db.delete_wallet(wallet_id, callback.from_user.id)
    
    user = await db.get_or_create_user(callback.from_user.id)
    lang = user["language"]
    wallets = await db.get_user_wallets(callback.from_user.id)
    
    await callback.message.edit_text(get_text("your_wallets", lang), reply_markup=get_wallets_kb(wallets, lang))
    await callback.answer("Кошелек удален!")

# ========== НАСТРОЙКИ ==========
@router.message(F.text.in_([get_text("settings", "ru"), get_text("settings", "uz")]))
async def show_settings(message: Message):
    if await check_blocked(message.from_user.id):
        return
    
    user = await db.get_or_create_user(message.from_user.id)
    lang, currency = user["language"], user["currency"]
    
    text = get_text("settings_menu", lang, lang=LANGUAGES[lang], currency=currency)
    await message.answer(text, reply_markup=get_settings_kb(lang))

@router.callback_query(F.data == "set_lang")
async def settings_language(callback: CallbackQuery):
    await callback.message.edit_text("Выберите язык:", reply_markup=get_language_kb())
    await callback.answer()

@router.callback_query(F.data == "set_currency")
async def settings_currency(callback: CallbackQuery):
    user = await db.get_or_create_user(callback.from_user.id)
    await callback.message.edit_text(get_text("select_currency", user["language"]), 
                                     reply_markup=get_currency_kb(user["currency"]))
    await callback.answer()

@router.callback_query(F.data.startswith("cur_"))
async def change_currency(callback: CallbackQuery):
    currency = callback.data.replace("cur_", "")
    await db.update_user_currency(callback.from_user.id, currency)
    
    user = await db.get_or_create_user(callback.from_user.id)
    lang = user["language"]
    text = get_text("settings_menu", lang, lang=LANGUAGES[lang], currency=currency)
    
    await callback.message.edit_text(text, reply_markup=get_settings_kb(lang))
    await callback.answer(get_text("settings_updated", lang))

@router.callback_query(F.data == "back_settings")
async def back_settings(callback: CallbackQuery):
    user = await db.get_or_create_user(callback.from_user.id)
    lang, currency = user["language"], user["currency"]
    text = get_text("settings_menu", lang, lang=LANGUAGES[lang], currency=currency)
    await callback.message.edit_text(text, reply_markup=get_settings_kb(lang))
    await callback.answer()

# ========== АДМИН ПАНЕЛЬ ==========
@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Нет доступа!")
        return
    
    total = len(await db.get_all_users())
    active = await db.get_active_users_count(7)
    blocked = await db.get_blocked_users_count()
    
    text = get_text("admin_panel", "ru", total=total, active=active, blocked=blocked)
    await message.answer(text, reply_markup=get_admin_kb())

@router.callback_query(F.data == "admin_panel")
async def admin_panel(callback: CallbackQuery):
    total = len(await db.get_all_users())
    active = await db.get_active_users_count(7)
    blocked = await db.get_blocked_users_count()
    
    text = get_text("admin_panel", "ru", total=total, active=active, blocked=blocked)
    await callback.message.edit_text(text, reply_markup=get_admin_kb())
    await callback.answer()

@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):
    users = await db.get_all_users()
    await callback.message.edit_text("👥 Пользователи:", reply_markup=get_users_list_kb(users, 0))
    await callback.answer()

@router.callback_query(F.data.startswith("upage_"))
async def users_page(callback: CallbackQuery):
    page = int(callback.data.replace("upage_", ""))
    users = await db.get_all_users()
    await callback.message.edit_text("👥 Пользователи:", reply_markup=get_users_list_kb(users, page))
    await callback.answer()

@router.callback_query(F.data.startswith("uinfo_"))
async def user_info(callback: CallbackQuery):
    user_id = int(callback.data.replace("uinfo_", ""))
    user = await db.get_or_create_user(user_id)
    
    text = f"👤 {user['name'] or 'No name'}\n"
    text += f"🆔 ID: {user_id}\n"
    text += f"🔗 @{user['username'] or 'нет'}\n"
    text += f"🌐 {user['language']}\n"
    text += f"📅 {user['created_at'][:10]}\n"
    text += f"⚡ {user['last_activity'][:10]}\n"
    text += f"📊 Статус: {user['status']}"
    
    await callback.message.edit_text(text, reply_markup=get_user_admin_kb(user_id, user["status"]))
    await callback.answer()

@router.callback_query(F.data.startswith("block_"))
async def block_user(callback: CallbackQuery):
    user_id = int(callback.data.replace("block_", ""))
    await db.update_user_status(user_id, "blocked")
    await callback.answer("Пользователь заблокирован!")
    await admin_users(callback)

@router.callback_query(F.data.startswith("unblock_"))
async def unblock_user(callback: CallbackQuery):
    user_id = int(callback.data.replace("unblock_", ""))
    await db.update_user_status(user_id, "active")
    await callback.answer("Пользователь разблокирован!")
    await admin_users(callback)

@router.callback_query(F.data == "admin_blocked")
async def admin_blocked(callback: CallbackQuery):
    users = [u for u in await db.get_all_users() if u["status"] == "blocked"]
    if not users:
        await callback.answer("Нет заблокированных!")
        return
    
    await callback.message.edit_text("🔒 Заблокированные:", reply_markup=get_users_list_kb(users, 0))
    await callback.answer()

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    users = await db.get_all_users()
    active_7d = await db.get_active_users_count(7)
    active_30d = await db.get_active_users_count(30)
    
    text = "📊 Статистика:\n\n"
    text += f"👥 Всего: {len(users)}\n"
    text += f"⚡ Активны 7дн: {active_7d}\n"
    text += f"⚡ Активны 30дн: {active_30d}\n"
    text += f"🔒 Заблокировано: {await db.get_blocked_users_count()}"
    
    await callback.message.edit_text(text, reply_markup=get_admin_kb())
    await callback.answer()