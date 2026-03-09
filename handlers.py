from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import TEXTS, CURRENCIES, EXPENSE_CATEGORIES, INCOME_CATEGORIES, WALLET_TYPES, ADMIN_ID, get_text, format_amount
from database import db
from keyboards import *

router = Router()

# ========== СОСТОЯНИЯ ==========
class AddOperation(StatesGroup):
    # ✅ ИСПРАВЛЕНО: правильная последовательность
    # 1. select_type (через callback)
    # 2. select_category (через callback)
    # 3. waiting_amount (state)
    # 4. waiting_wallet (state)
    waiting_amount = State()
    waiting_wallet = State()

class CreateWallet(StatesGroup):
    waiting_name = State()

# ========== ХЕЛПЕРЫ ==========
def get_category_name(cat_key: str, t_type: str, lang: str = "ru") -> str:
    if t_type == "expense":
        cat = EXPENSE_CATEGORIES.get(cat_key, {})
    else:
        cat = INCOME_CATEGORIES.get(cat_key, {})
    return cat.get(f"name_{lang}", cat_key)

async def get_user_data(user_id: int) -> tuple:
    user = await db.get_or_create_user(user_id)
    settings = await db.get_user_settings(user_id)
    return user.get("language", "ru"), settings.get("currency", "UZS")

async def check_blocked(user_id: int) -> bool:
    user = await db.get_or_create_user(user_id)
    return user.get("status") == "blocked"

# ✅ ИСПРАВЛЕНО: проверка админа
async def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

# ========== СТАРТ ==========
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = await db.get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name
    )
    
    if user.get("status") == "blocked":
        await message.answer(get_text("user_blocked", user.get("language", "ru")))
        return
    
    if not user.get("language"):
        await message.answer(get_text("welcome", "ru"), reply_markup=get_language_kb())
        return
    
    lang = user["language"]
    await message.answer(get_text("menu", lang), reply_markup=get_main_menu(lang))

@router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery):
    lang = callback.data.replace("lang_", "")
    await db.update_language(callback.from_user.id, lang)
    
    await callback.message.delete()
    await callback.message.answer(get_text("menu", lang), reply_markup=get_main_menu(lang))
    await callback.answer(get_text("language_changed", lang))

# ========== ГЛАВНОЕ МЕНЮ ==========
@router.message(F.text.in_([TEXTS["ru"]["back"], TEXTS["uz"]["back"]]))
async def back_menu(message: Message, state: FSMContext):
    await state.clear()
    lang, _ = await get_user_data(message.from_user.id)
    await message.answer(get_text("menu", lang), reply_markup=get_main_menu(lang))

@router.callback_query(F.data == "back_menu")
async def back_menu_cb(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    lang, _ = await get_user_data(callback.from_user.id)
    await callback.message.delete()
    await callback.message.answer(get_text("menu", lang), reply_markup=get_main_menu(lang))
    await callback.answer()

# ========== БАЛАНС ==========
@router.message(F.text.in_([TEXTS["ru"]["balance"], TEXTS["uz"]["balance"]]))
async def show_balance(message: Message):
    if await check_blocked(message.from_user.id):
        return
    
    lang, currency = await get_user_data(message.from_user.id)
    
    wallets = await db.get_user_wallets(message.from_user.id)
    if not wallets:
        await message.answer(get_text("no_wallets", lang))
        return
    
    text_lines = [get_text("your_balance", lang), ""]
    total = 0.0
    
    for i, w in enumerate(wallets, 1):
        balance = await db.get_wallet_balance(w["id"])
        total += balance
        emoji = "⭐" if w["is_main"] else "💳"
        text_lines.append(f"{i}. {emoji} <b>{w['name']}</b>")
        text_lines.append(f"   💰 {format_amount(balance, currency)}")
        text_lines.append("")
    
    text_lines.append(get_text("total_balance", lang, amount=format_amount(total, currency)))
    
    await message.answer("\n".join(text_lines), reply_markup=get_main_menu(lang))

# ========== ДОБАВЛЕНИЕ ОПЕРАЦИИ ==========
@router.message(F.text.in_([TEXTS["ru"]["add_operation"], TEXTS["uz"]["add_operation"]]))
async def add_operation_start(message: Message, state: FSMContext):
    if await check_blocked(message.from_user.id):
        return
    
    lang, _ = await get_user_data(message.from_user.id)
    # ✅ ИСПРАВЛЕНО: убран set_state, просто показываем выбор типа
    await state.update_data(step="select_type")
    await message.answer(get_text("select_operation_type", lang), reply_markup=get_operation_types_kb(lang))

@router.callback_query(F.data == "op_expense")
async def select_expense_cat(callback: CallbackQuery, state: FSMContext):
    lang, _ = await get_user_data(callback.from_user.id)
    await state.update_data(op_type="expense")
    await callback.message.edit_text(get_text("select_category", lang), reply_markup=get_expense_categories_kb(lang))
    await callback.answer()

@router.callback_query(F.data == "op_income")
async def select_income_cat(callback: CallbackQuery, state: FSMContext):
    lang, _ = await get_user_data(callback.from_user.id)
    await state.update_data(op_type="income")
    await callback.message.edit_text(get_text("select_category", lang), reply_markup=get_income_categories_kb(lang))
    await callback.answer()

@router.callback_query(F.data.startswith("cat_"))
async def select_category(callback: CallbackQuery, state: FSMContext):
    cat_key = callback.data.replace("cat_exp_", "").replace("cat_inc_", "")
    state_data = await state.get_data()
    op_type = state_data.get("op_type")
    
    await state.update_data(category=cat_key)
    await state.set_state(AddOperation.waiting_amount)
    
    lang, _ = await get_user_data(callback.from_user.id)
    await callback.message.delete()
    await callback.message.answer(get_text("enter_amount", lang), reply_markup=get_cancel_kb(lang))
    await callback.answer()

@router.message(AddOperation.waiting_amount)
async def process_amount(message: Message, state: FSMContext):
    lang, _ = await get_user_data(message.from_user.id)
    
    if message.text in [TEXTS["ru"]["cancel"], TEXTS["uz"]["cancel"]]:
        await back_menu(message, state)
        return
    
    try:
        amount = float(message.text.replace(" ", "").replace(",", "."))
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer(get_text("invalid_amount", lang))
        return
    
    await state.update_data(amount=amount)
    await state.set_state(AddOperation.waiting_wallet)
    
    wallets = await db.get_user_wallets(message.from_user.id)
    await message.answer(get_text("select_wallet", lang), reply_markup=get_wallets_kb(wallets, lang, for_selection=True))

@router.callback_query(F.data.startswith("selwallet_"))
async def save_operation(callback: CallbackQuery, state: FSMContext):
    wallet_id = int(callback.data.replace("selwallet_", ""))
    data = await state.get_data()
    
    # ✅ ИСПРАВЛЕНО: получаем date/time из результата add_transaction
    result = await db.add_transaction(
        callback.from_user.id,
        wallet_id,
        data["op_type"],
        data["category"],
        data["amount"]
    )
    
    await state.clear()
    lang, currency = await get_user_data(callback.from_user.id)
    
    wallets = await db.get_user_wallets(callback.from_user.id)
    wallet = next((w for w in wallets if w["id"] == wallet_id), None)
    wallet_name = wallet["name"] if wallet else "?"
    
    cat_name = get_category_name(data["category"], data["op_type"], lang)
    type_name = get_text("expense" if data["op_type"] == "expense" else "income", lang)
    
    # ✅ ИСПРАВЛЕНО: используем date/time из БД
    text = get_text("operation_added", lang,
                   type=type_name,
                   category=cat_name,
                   amount=format_amount(data["amount"], currency),
                   wallet=wallet_name,
                   date=result["date"],
                   time=result["time"])
    
    await callback.message.delete()
    await callback.message.answer(text, reply_markup=get_main_menu(lang))
    await callback.answer()

@router.callback_query(F.data == "cancel_operation")
async def cancel_operation(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    lang, _ = await get_user_data(callback.from_user.id)
    await callback.message.delete()
    await callback.message.answer(get_text("operation_cancelled", lang), reply_markup=get_main_menu(lang))
    await callback.answer()

# ========== ИСТОРИЯ ==========
@router.message(F.text.in_([TEXTS["ru"]["history"], TEXTS["uz"]["history"]]))
async def show_history(message: Message):
    if await check_blocked(message.from_user.id):
        return
    
    lang, currency = await get_user_data(message.from_user.id)
    
    transactions = await db.get_user_transactions(message.from_user.id, 20)
    if not transactions:
        await message.answer(get_text("no_transactions", lang))
        return
    
    text_lines = [get_text("history_title", lang), ""]
    
    for t in transactions:
        emoji = get_text("expense_emoji" if t["type"] == "expense" else "income_emoji", lang)
        cat_name = get_category_name(t["category"], t["type"], lang)
        
        text_lines.append(get_text("transaction_item", lang,
                                  emoji=emoji,
                                  category=cat_name,
                                  amount=format_amount(t["amount"], currency),
                                  wallet=t["wallet_name"],
                                  date=t["date"],
                                  time=t["time"]))
    
    await message.answer("\n".join(text_lines), reply_markup=get_main_menu(lang))

# ========== СТАТИСТИКА ==========
@router.message(F.text.in_([TEXTS["ru"]["statistics"], TEXTS["uz"]["statistics"]]))
async def show_statistics(message: Message):
    if await check_blocked(message.from_user.id):
        return
    
    lang, currency = await get_user_data(message.from_user.id)
    
    stats = await db.get_user_stats(message.from_user.id, 30)
    
    text_lines = [get_text("statistics_title", lang), ""]
    text_lines.append(get_text("stats_income", lang, amount=format_amount(stats["income"], currency)))
    text_lines.append(get_text("stats_expense", lang, amount=format_amount(stats["expense"], currency)))
    text_lines.append(get_text("stats_balance", lang, amount=format_amount(stats["income"] - stats["expense"], currency)))
    
    if stats["categories"]:
        top_cat = max(stats["categories"].items(), key=lambda x: x[1])[0]
        top_name = get_category_name(top_cat, "expense", lang)
        text_lines.append("")
        text_lines.append(get_text("top_category", lang, category=top_name))
    
    await message.answer("\n".join(text_lines), reply_markup=get_main_menu(lang))

# ========== КОШЕЛЬКИ ==========
@router.message(F.text.in_([TEXTS["ru"]["wallets"], TEXTS["uz"]["wallets"]]))
async def show_wallets(message: Message):
    if await check_blocked(message.from_user.id):
        return
    
    lang, currency = await get_user_data(message.from_user.id)
    
    wallets = await db.get_user_wallets(message.from_user.id)
    
    text_lines = [get_text("wallets_title", lang), ""]
    for i, w in enumerate(wallets, 1):
        balance = await db.get_wallet_balance(w["id"])
        emoji = WALLET_TYPES.get(w["type"], {}).get("emoji", "💳")
        text_lines.append(get_text("wallet_item", lang, emoji=emoji, name=w["name"], amount=format_amount(balance, currency)))
    
    await message.answer("\n".join(text_lines), reply_markup=get_wallets_kb(wallets, lang))

@router.callback_query(F.data == "add_wallet")
async def add_wallet_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CreateWallet.waiting_name)
    lang, _ = await get_user_data(callback.from_user.id)
    await callback.message.delete()
    await callback.message.answer(get_text("enter_wallet_name", lang), reply_markup=get_cancel_kb(lang))
    await callback.answer()

@router.message(CreateWallet.waiting_name)
async def create_wallet_finish(message: Message, state: FSMContext):
    lang, _ = await get_user_data(message.from_user.id)
    
    if message.text in [TEXTS["ru"]["cancel"], TEXTS["uz"]["cancel"]]:
        await back_menu(message, state)
        return
    
    name = message.text.strip()
    if len(name) > 50:
        name = name[:50]
    
    # ✅ ИСПРАВЛЕНО: проверка на дубликат
    existing = await db.get_wallet_by_name(message.from_user.id, name)
    if existing:
        await message.answer(get_text("wallet_exists", lang))
        return
    
    # Определяем тип по эмодзи
    wallet_type = "main"
    if "💵" in name:
        wallet_type = "cash"
    elif "🏦" in name:
        wallet_type = "bank"
    elif "💰" in name:
        wallet_type = "savings"
    
    await db.create_wallet(message.from_user.id, name, wallet_type)
    await state.clear()
    
    wallets = await db.get_user_wallets(message.from_user.id)
    type_name = WALLET_TYPES.get(wallet_type, {}).get(f"name_{lang}", wallet_type)
    
    await message.answer(get_text("wallet_created", lang, name=name, type=type_name))
    await message.answer(get_text("wallets_title", lang), reply_markup=get_wallets_kb(wallets, lang))

@router.callback_query(F.data == "back_wallets")
async def back_to_wallets(callback: CallbackQuery):
    lang, currency = await get_user_data(callback.from_user.id)
    wallets = await db.get_user_wallets(callback.from_user.id)
    
    text_lines = [get_text("wallets_title", lang), ""]
    for w in wallets:
        balance = await db.get_wallet_balance(w["id"])
        emoji = WALLET_TYPES.get(w["type"], {}).get("emoji", "💳")
        text_lines.append(get_text("wallet_item", lang, emoji=emoji, name=w["name"], amount=format_amount(balance, currency)))
    
    await callback.message.edit_text("\n".join(text_lines), reply_markup=get_wallets_kb(wallets, lang))
    await callback.answer()

@router.callback_query(F.data.startswith("wallet_"))
async def wallet_details(callback: CallbackQuery):
    wallet_id = int(callback.data.replace("wallet_", ""))
    wallets = await db.get_user_wallets(callback.from_user.id)
    wallet = next((w for w in wallets if w["id"] == wallet_id), None)
    
    if not wallet:
        await callback.answer("Кошелек не найден", show_alert=True)
        return
    
    lang, currency = await get_user_data(callback.from_user.id)
    balance = await db.get_wallet_balance(wallet_id)
    
    text = f"{wallet['name']}\n💰 {format_amount(balance, currency)}"
    if wallet["is_main"]:
        text += "\n⭐ " + ("Основной" if lang == "ru" else "Asosiy")
    
    await callback.message.edit_text(text, reply_markup=get_wallet_actions_kb(wallet_id, wallet["is_main"], lang))
    await callback.answer()

@router.callback_query(F.data.startswith("setmain_"))
async def set_main_wallet(callback: CallbackQuery):
    wallet_id = int(callback.data.replace("setmain_", ""))
    await db.set_main_wallet(wallet_id, callback.from_user.id)
    
    lang, _ = await get_user_data(callback.from_user.id)
    await callback.answer(get_text("main_wallet_set", lang), show_alert=True)
    
    wallets = await db.get_user_wallets(callback.from_user.id)
    await callback.message.edit_text(get_text("wallets_title", lang), reply_markup=get_wallets_kb(wallets, lang))

@router.callback_query(F.data == "del_wallet_menu")
async def delete_wallet_menu(callback: CallbackQuery):
    lang, _ = await get_user_data(callback.from_user.id)
    wallets = await db.get_user_wallets(callback.from_user.id)
    
    if len(wallets) <= 1:
        await callback.answer(get_text("cannot_delete_last", lang), show_alert=True)
        return
    
    await callback.message.edit_text(
        "❌ " + ("Выберите кошелек для удаления:" if lang == "ru" else "O'chirish uchun hamyonni tanlang:"),
        reply_markup=get_delete_wallet_list_kb(wallets, lang)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("conf_del_wallet_"))
async def confirm_delete_wallet(callback: CallbackQuery):
    wallet_id = int(callback.data.replace("conf_del_wallet_", ""))
    wallets = await db.get_user_wallets(callback.from_user.id)
    wallet = next((w for w in wallets if w["id"] == wallet_id), None)
    
    if not wallet:
        await callback.answer("Кошелек не найден", show_alert=True)
        return
    
    lang, _ = await get_user_data(callback.from_user.id)
    await callback.message.edit_text(
        get_text("confirm_delete_wallet", lang, name=wallet["name"]),
        reply_markup=get_delete_wallet_confirmation_kb(wallet_id, lang)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("delwallet_"))
async def delete_wallet(callback: CallbackQuery):
    wallet_id = int(callback.data.replace("delwallet_", ""))
    result = await db.delete_wallet(wallet_id, callback.from_user.id)
    
    lang, _ = await get_user_data(callback.from_user.id)
    
    if not result["success"]:
        error_key = result["error"]  # cannot_delete_main или cannot_delete_last
        await callback.answer(get_text(error_key, lang), show_alert=True)
        return
    
    await callback.answer(get_text("wallet_deleted", lang), show_alert=True)
    
    wallets = await db.get_user_wallets(callback.from_user.id)
    await callback.message.edit_text(get_text("wallets_title", lang), reply_markup=get_wallets_kb(wallets, lang))

# ========== НАСТРОЙКИ ==========
@router.message(F.text.in_([TEXTS["ru"]["settings"], TEXTS["uz"]["settings"]]))
async def show_settings(message: Message):
    if await check_blocked(message.from_user.id):
        return
    
    lang, currency = await get_user_data(message.from_user.id)
    settings = await db.get_user_settings(message.from_user.id)
    
    notif_status = get_text("notifications_on" if settings["notifications"] else "notifications_off", lang)
    text = f"{get_text('settings_title', lang)}\n\n"
    text += get_text("settings_menu", lang, language=LANGUAGES[lang], currency=currency, notifications=notif_status)
    
    await message.answer(text, reply_markup=get_settings_kb(lang))

@router.callback_query(F.data == "set_lang")
async def settings_language(callback: CallbackQuery):
    await callback.message.edit_text(get_text("select_language", "ru"), reply_markup=get_language_kb())
    await callback.answer()

@router.callback_query(F.data == "set_currency")
async def settings_currency(callback: CallbackQuery):
    lang, current = await get_user_data(callback.from_user.id)
    await callback.message.edit_text(get_text("select_currency", lang), reply_markup=get_currency_kb(current, lang))
    await callback.answer()

@router.callback_query(F.data.startswith("cur_"))
async def change_currency(callback: CallbackQuery):
    currency = callback.data.replace("cur_", "")
    await db.update_currency(callback.from_user.id, currency)
    
    lang, _ = await get_user_data(callback.from_user.id)
    await callback.answer(get_text("currency_changed", lang, currency=currency), show_alert=True)
    
    settings = await db.get_user_settings(callback.from_user.id)
    notif_status = get_text("notifications_on" if settings["notifications"] else "notifications_off", lang)
    text = f"{get_text('settings_title', lang)}\n\n"
    text += get_text("settings_menu", lang, language=LANGUAGES[lang], currency=currency, notifications=notif_status)
    
    await callback.message.edit_text(text, reply_markup=get_settings_kb(lang))

@router.callback_query(F.data == "manage_wallets")
async def manage_wallets(callback: CallbackQuery):
    lang, _ = await get_user_data(callback.from_user.id)
    wallets = await db.get_user_wallets(callback.from_user.id)
    
    text_lines = [get_text("wallets_title", lang), ""]
    for w in wallets:
        emoji = "⭐" if w["is_main"] else "💳"
        text_lines.append(f"{emoji} {w['name']}")
    
    await callback.message.edit_text("\n".join(text_lines), reply_markup=get_wallets_kb(wallets, lang))
    await callback.answer()

@router.callback_query(F.data == "back_settings")
async def back_settings(callback: CallbackQuery):
    lang, currency = await get_user_data(callback.from_user.id)
    settings = await db.get_user_settings(callback.from_user.id)
    
    notif_status = get_text("notifications_on" if settings["notifications"] else "notifications_off", lang)
    text = f"{get_text('settings_title', lang)}\n\n"
    text += get_text("settings_menu", lang, language=LANGUAGES[lang], currency=currency, notifications=notif_status)
    
    await callback.message.edit_text(text, reply_markup=get_settings_kb(lang))
    await callback.answer()

# ========== АДМИН ПАНЕЛЬ ==========
@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not await is_admin(message.from_user.id):
        await message.answer(get_text("no_access", "ru"))
        return
    
    total = len(await db.get_all_users())
    active = await db.get_active_users_count(7)
    blocked = await db.get_blocked_users_count()
    
    text = get_text("admin_panel", "ru", total=total, active=active, blocked=blocked)
    await message.answer(text, reply_markup=get_admin_kb())

# ✅ ИСПРАВЛЕНО: добавлена проверка админа во все callback
@router.callback_query(F.data == "admin_panel")
async def admin_panel(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer(get_text("no_access", "ru"), show_alert=True)
        return
    
    total = len(await db.get_all_users())
    active = await db.get_active_users_count(7)
    blocked = await db.get_blocked_users_count()
    
    text = get_text("admin_panel", "ru", total=total, active=active, blocked=blocked)
    await callback.message.edit_text(text, reply_markup=get_admin_kb())
    await callback.answer()

@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer(get_text("no_access", "ru"), show_alert=True)
        return
    
    users = await db.get_all_users()
    await callback.message.edit_text("👥 Пользователи:", reply_markup=get_users_list_kb(users, 0))
    await callback.answer()

@router.callback_query(F.data.startswith("upage_"))
async def users_page(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer(get_text("no_access", "ru"), show_alert=True)
        return
    
    page = int(callback.data.replace("upage_", ""))
    users = await db.get_all_users()
    await callback.message.edit_text("👥 Пользователи:", reply_markup=get_users_list_kb(users, page))
    await callback.answer()

@router.callback_query(F.data.startswith("uinfo_"))
async def user_info(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer(get_text("no_access", "ru"), show_alert=True)
        return
    
    user_id = int(callback.data.replace("uinfo_", ""))
    user = await db.get_or_create_user(user_id)
    
    text = f"👤 {user.get('name', 'No name')}\n"
    text += f"🆔 ID: {user_id}\n"
    text += f"🔗 @{user.get('username', 'нет')}\n"
    text += f"🌐 {user.get('language', 'ru')}\n"
    text += f"📅 {user.get('created_at', '???')[:10]}\n"
    text += f"⚡ {user.get('last_activity', '???')[:10]}\n"
    text += f"📊 {user.get('status', 'active')}"
    
    await callback.message.edit_text(text, reply_markup=get_user_admin_kb(user_id, user.get("status", "active")))
    await callback.answer()

@router.callback_query(F.data.startswith("block_"))
async def block_user(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer(get_text("no_access", "ru"), show_alert=True)
        return
    
    user_id = int(callback.data.replace("block_", ""))
    await db.update_user_status(user_id, "blocked")
    await callback.answer("Заблокировано", show_alert=True)
    await admin_users(callback)

@router.callback_query(F.data.startswith("unblock_"))
async def unblock_user(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer(get_text("no_access", "ru"), show_alert=True)
        return
    
    user_id = int(callback.data.replace("unblock_", ""))
    await db.update_user_status(user_id, "active")
    await callback.answer("Разблокировано", show_alert=True)
    await admin_users(callback)

@router.callback_query(F.data == "admin_blocked")
async def admin_blocked(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer(get_text("no_access", "ru"), show_alert=True)
        return
    
    users = [u for u in await db.get_all_users() if u["status"] == "blocked"]
    if not users:
        await callback.answer("Нет заблокированных", show_alert=True)
        return
    await callback.message.edit_text("🔒 Заблокированные:", reply_markup=get_users_list_kb(users, 0))
    await callback.answer()

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer(get_text("no_access", "ru"), show_alert=True)
        return
    
    users = await db.get_all_users()
    active_7 = await db.get_active_users_count(7)
    active_30 = await db.get_active_users_count(30)
    
    text = "📊 Статистика:\n\n"
    text += f"👥 Всего: {len(users)}\n"
    text += f"⚡ 7 дней: {active_7}\n"
    text += f"⚡ 30 дней: {active_30}\n"
    text += f"🔒 Заблокировано: {await db.get_blocked_users_count()}"
    
    await callback.message.edit_text(text, reply_markup=get_admin_kb())
    await callback.answer()