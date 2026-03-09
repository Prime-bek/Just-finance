from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_admin_menu() -> InlineKeyboardMarkup:
    """Get admin menu keyboard"""
    kb = InlineKeyboardBuilder()
    
    kb.add(InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users"))
    kb.add(InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"))
    kb.add(InlineKeyboardButton(text="💰 Транзакции", callback_data="admin_transactions"))
    kb.add(InlineKeyboardButton(text="🔍 Найти пользователя", callback_data="admin_find_user"))
    kb.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu"))
    
    kb.adjust(2, 2, 1)
    return kb.as_markup()

def get_users_list(users: list, page: int = 0) -> InlineKeyboardMarkup:
    """Get users list keyboard with pagination"""
    kb = InlineKeyboardBuilder()
    
    # Show 5 users per page
    start_idx = page * 5
    end_idx = min(start_idx + 5, len(users))
    
    for i in range(start_idx, end_idx):
        user = users[i]
        user_text = f"{user['name']} ({user['telegram_id']})"
        kb.add(InlineKeyboardButton(text=user_text, callback_data=f"user_{user['telegram_id']}"))
    
    # Pagination buttons
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="⬅️ Предыдущая", callback_data=f"users_page_{page-1}"))
    if end_idx < len(users):
        nav_row.append(InlineKeyboardButton(text="Следующая ➡️", callback_data=f"users_page_{page+1}"))
    
    if nav_row:
        kb.row(*nav_row)
    
    kb.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_panel"))
    
    kb.adjust(1)
    return kb.as_markup()

def get_user_actions(user_id: int, status: str) -> InlineKeyboardMarkup:
    """Get user actions keyboard"""
    kb = InlineKeyboardBuilder()
    
    if status == 'active':
        kb.add(InlineKeyboardButton(text="🔒 Заблокировать", callback_data=f"block_user_{user_id}"))
    else:
        kb.add(InlineKeyboardButton(text="🔓 Разблокировать", callback_data=f"unblock_user_{user_id}"))
    
    kb.add(InlineKeyboardButton(text="👤 Профиль", callback_data=f"user_profile_{user_id}"))
    kb.add(InlineKeyboardButton(text="💰 Транзакции", callback_data=f"user_transactions_{user_id}"))
    kb.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_users"))
    
    kb.adjust(1)
    return kb.as_markup()

def get_back_to_admin() -> InlineKeyboardMarkup:
    """Get back to admin panel button"""
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_panel"))
    return kb.as_markup()