from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from config import TEXTS, LANGUAGES, CURRENCIES, EXPENSE_CATEGORIES, INCOME_CATEGORIES, WALLET_TYPES

def get_language_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for code, name in LANGUAGES.items():
        kb.add(InlineKeyboardButton(text=name, callback_data=f"lang_{code}"))
    return kb.adjust(1).as_markup()

def get_main_menu(lang: str = "ru") -> ReplyKeyboardMarkup:
    t = TEXTS[lang]
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text=t["balance"]), KeyboardButton(text=t["add_operation"]))
    kb.row(KeyboardButton(text=t["history"]), KeyboardButton(text=t["statistics"]))
    kb.row(KeyboardButton(text=t["wallets"]), KeyboardButton(text=t["settings"]))
    return kb.as_markup(resize_keyboard=True)

def get_operation_types_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    t = TEXTS[lang]
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text=f"💸 {t['expense']}", callback_data="op_expense"))
    kb.add(InlineKeyboardButton(text=f"💰 {t['income']}", callback_data="op_income"))
    kb.add(InlineKeyboardButton(text=t["cancel"], callback_data="cancel_operation"))
    return kb.adjust(2, 1).as_markup()

def get_expense_categories_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for key, cat in EXPENSE_CATEGORIES.items():
        text = f"{cat['emoji']} {cat['name_ru'] if lang == 'ru' else cat['name_uz']}"
        kb.add(InlineKeyboardButton(text=text, callback_data=f"cat_exp_{key}"))
    kb.add(InlineKeyboardButton(text=TEXTS[lang]["cancel"], callback_data="cancel_operation"))
    return kb.adjust(2).as_markup()

def get_income_categories_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for key, cat in INCOME_CATEGORIES.items():
        text = f"{cat['emoji']} {cat['name_ru'] if lang == 'ru' else cat['name_uz']}"
        kb.add(InlineKeyboardButton(text=text, callback_data=f"cat_inc_{key}"))
    kb.add(InlineKeyboardButton(text=TEXTS[lang]["cancel"], callback_data="cancel_operation"))
    return kb.adjust(2).as_markup()

def get_wallets_kb(wallets: list, lang: str = "ru", for_selection: bool = False) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for i, w in enumerate(wallets, 1):
        emoji = "⭐" if w["is_main"] else "💳"
        text = f"{emoji} {w['name']}"
        callback = f"selwallet_{w['id']}" if for_selection else f"wallet_{w['id']}"
        kb.add(InlineKeyboardButton(text=text, callback_data=callback))
    
    if not for_selection:
        kb.add(InlineKeyboardButton(text=TEXTS[lang]["add_wallet"], callback_data="add_wallet"))
        kb.add(InlineKeyboardButton(text=TEXTS[lang]["delete_wallet"], callback_data="del_wallet_menu"))
        kb.add(InlineKeyboardButton(text=TEXTS[lang]["back"], callback_data="back_menu"))
    
    return kb.adjust(1).as_markup()

def get_wallet_actions_kb(wallet_id: int, is_main: bool, lang: str = "ru") -> InlineKeyboardMarkup:
    t = TEXTS[lang]
    kb = InlineKeyboardBuilder()
    if not is_main:
        kb.add(InlineKeyboardButton(text=t["set_main"], callback_data=f"setmain_{wallet_id}"))
    kb.add(InlineKeyboardButton(text=t["delete"], callback_data=f"conf_del_wallet_{wallet_id}"))
    kb.add(InlineKeyboardButton(text=t["back"], callback_data="back_wallets"))
    return kb.adjust(1).as_markup()

def get_delete_wallet_confirmation_kb(wallet_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    t = TEXTS[lang]
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text=t["yes"], callback_data=f"delwallet_{wallet_id}"))
    kb.add(InlineKeyboardButton(text=t["no"], callback_data=f"wallet_{wallet_id}"))
    return kb.adjust(2).as_markup()

def get_delete_wallet_list_kb(wallets: list, lang: str = "ru") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for w in wallets:
        kb.add(InlineKeyboardButton(text=f"🗑 {w['name']}", callback_data=f"conf_del_wallet_{w['id']}"))
    kb.add(InlineKeyboardButton(text=TEXTS[lang]["cancel"], callback_data="back_wallets"))
    return kb.adjust(1).as_markup()

def get_settings_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    t = TEXTS[lang]
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text=f"🌐 {t['select_language']}", callback_data="set_lang"))
    kb.add(InlineKeyboardButton(text=f"💱 {t['select_currency']}", callback_data="set_currency"))
    kb.add(InlineKeyboardButton(text=f"💳 {t['manage_wallets']}", callback_data="manage_wallets"))
    kb.add(InlineKeyboardButton(text=t["back"], callback_data="back_menu"))
    return kb.adjust(1).as_markup()

def get_currency_kb(current: str = "UZS", lang: str = "ru") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for code, data in CURRENCIES.items():
        text = f"{data['flag']} {code}"
        if code == current:
            text += " ✅"
        kb.add(InlineKeyboardButton(text=text, callback_data=f"cur_{code}"))
    kb.add(InlineKeyboardButton(text=TEXTS[lang]["back"], callback_data="back_settings"))
    return kb.adjust(2, 2, 2).as_markup()

def get_cancel_kb(lang: str = "ru") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=TEXTS[lang]["cancel"])]],
        resize_keyboard=True
    )

def get_admin_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users"))
    kb.add(InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"))
    kb.add(InlineKeyboardButton(text="🔒 Заблокированные", callback_data="admin_blocked"))
    return kb.adjust(1).as_markup()

def get_users_list_kb(users: list, page: int = 0) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    start, end = page * 5, (page + 1) * 5
    
    for u in users[start:end]:
        status = "🔴" if u["status"] == "blocked" else "🟢"
        name = u["username"] or u["name"] or f"ID:{u['user_id']}"
        kb.add(InlineKeyboardButton(text=f"{status} {name}", callback_data=f"uinfo_{u['user_id']}"))
    
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"upage_{page-1}"))
    if end < len(users):
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"upage_{page+1}"))
    if nav:
        kb.row(*nav)
    
    kb.add(InlineKeyboardButton(text="◀️ Назад", callback_data="admin_panel"))
    return kb.adjust(1).as_markup()

def get_user_admin_kb(user_id: int, status: str, lang: str = "ru") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if status == "active":
        kb.add(InlineKeyboardButton(text="🔒 Заблокировать", callback_data=f"block_{user_id}"))
    else:
        kb.add(InlineKeyboardButton(text="🔓 Разблокировать", callback_data=f"unblock_{user_id}"))
    kb.add(InlineKeyboardButton(text="◀️ Назад", callback_data="admin_users"))
    return kb.adjust(1).as_markup()