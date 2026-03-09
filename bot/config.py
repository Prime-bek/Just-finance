import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set")

ADMIN_ID = 1265652628

DATABASE_NAME = "finance_bot.db"

LANGUAGES = {
    "ru": "Русский",
    "uz": "O'zbekcha"
}

CURRENCIES = {
    "RUB": "₽",
    "UZS": "so'm",
    "USD": "$",
    "EUR": "€"
}

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