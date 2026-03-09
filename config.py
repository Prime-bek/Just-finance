import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1265652628"))

if not BOT_TOKEN:
    raise ValueError("❌ Установи BOT_TOKEN в переменных окружения!")

# База данных
DB_PATH = os.getenv("DB_PATH", "finance_bot.db")

# Настройки
LANGUAGES = {"ru": "Русский", "uz": "O'zbekcha"}
CURRENCIES = {"RUB": "₽", "UZS": "so'm", "USD": "$", "EUR": "€"}

# Категории
EXPENSE_CATEGORIES = {
    "food": "🍔 Еда",
    "transport": "🚕 Транспорт",
    "entertainment": "🎮 Развлечения",
    "shopping": "🛍 Покупки",
    "health": "💊 Здоровье",
    "subscriptions": "📱 Подписки",
    "education": "📚 Образование",
    "utilities": "🏠 Коммунальные",
    "other": "📦 Другое"
}

INCOME_CATEGORIES = {
    "salary": "💼 Зарплата",
    "freelance": "💻 Фриланс",
    "gift": "🎁 Подарок",
    "investments": "📈 Инвестиции",
    "other": "📦 Другое"
}

WALLET_TYPES = {
    "main": "💳 Основной",
    "cash": "💵 Наличные",
    "bank": "🏦 Банк",
    "savings": "💰 Сбережения"
}

# Тексты
TEXTS = {
    "ru": {
        "welcome": "👋 Добро пожаловать в Finance Tracker!\n\nЯ помогу учитывать доходы и расходы.",
        "menu": "📋 Главное меню:",
        "balance": "📊 Баланс",
        "add_operation": "➕ Добавить операцию",
        "history": "📋 История",
        "stats": "📈 Статистика",
        "wallets": "💳 Кошельки",
        "settings": "⚙️ Настройки",
        "select_type": "Выберите тип операции:",
        "expense": "💸 Расход",
        "income": "💰 Доход",
        "select_category": "Выберите категорию:",
        "enter_amount": "Введите сумму:",
        "invalid_amount": "❌ Неверная сумма. Попробуйте ещё раз:",
        "operation_added": "✅ Операция добавлена!",
        "no_wallets": "У вас пока нет кошельков.",
        "your_wallets": "💳 Ваши кошельки:",
        "create_wallet": "➕ Создать кошелек",
        "select_wallet_type": "Выберите тип кошелька:",
        "enter_wallet_name": "Введите название кошелька:",
        "wallet_created": "✅ Кошелек '{name}' создан!",
        "no_transactions": "У вас пока нет операций.",
        "recent_transactions": "📋 Последние операции:",
        "statistics": "📊 Статистика за {period}:",
        "income_stat": "💰 Доход: {amount}",
        "expense_stat": "💸 Расход: {amount}",
        "balance_stat": "💼 Баланс: {amount}",
        "settings_menu": "⚙️ Настройки\n\nЯзык: {lang}\nВалюта: {currency}",
        "select_language": "Выберите язык:",
        "select_currency": "Выберите валюту:",
        "settings_updated": "✅ Настройки обновлены!",
        "back": "◀️ Назад",
        "cancel": "❌ Отмена",
        "admin_panel": "🔐 Админ-панель\n\nВсего пользователей: {total}\nАктивных (7дн): {active}\nЗаблокировано: {blocked}",
        "user_blocked": "❌ Вы заблокированы!",
        "error": "❌ Произошла ошибка.",
    },
    "uz": {
        "welcome": "👋 Finance Tracker'ga xush kelibsiz!\n\nDaromadlar va xarajatlarni hisoblashda yordam beraman.",
        "menu": "📋 Asosiy menyu:",
        "balance": "📊 Balans",
        "add_operation": "➕ Operatsiya qo'shish",
        "history": "📋 Tarix",
        "stats": "📈 Statistika",
        "wallets": "💳 Hamyonlar",
        "settings": "⚙️ Sozlamalar",
        "select_type": "Operatsiya turini tanlang:",
        "expense": "💸 Xarajat",
        "income": "💰 Daromad",
        "select_category": "Kategoriyani tanlang:",
        "enter_amount": "Miqdorni kiriting:",
        "invalid_amount": "❌ Noto'g'ri miqdor. Yana urinib ko'ring:",
        "operation_added": "✅ Operatsiya qo'shildi!",
        "no_wallets": "Sizda hali hamyonlar yo'q.",
        "your_wallets": "💳 Sizning hamyonlaringiz:",
        "create_wallet": "➕ Hamyon yaratish",
        "select_wallet_type": "Hamyon turini tanlang:",
        "enter_wallet_name": "Hamyon nomini kiriting:",
        "wallet_created": "✅ '{name}' hamyoni yaratildi!",
        "no_transactions": "Sizda hali operatsiyalar yo'q.",
        "recent_transactions": "📋 Oxirgi operatsiyalar:",
        "statistics": "📊 {period} uchun statistika:",
        "income_stat": "💰 Daromad: {amount}",
        "expense_stat": "💸 Xarajat: {amount}",
        "balance_stat": "💼 Balans: {amount}",
        "settings_menu": "⚙️ Sozlamalar\n\nTil: {lang}\nValyuta: {currency}",
        "select_language": "Tilni tanlang:",
        "select_currency": "Valyutani tanlang:",
        "settings_updated": "✅ Sozlamalar yangilandi!",
        "back": "◀️ Orqaga",
        "cancel": "❌ Bekor qilish",
        "admin_panel": "🔐 Admin panel\n\nJami foydalanuvchilar: {total}\nFaol (7kun): {active}\nBloklangan: {blocked}",
        "user_blocked": "❌ Siz bloklangansiz!",
        "error": "❌ Xatolik yuz berdi.",
    }
}