import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1265652628"))

# Validate BOT_TOKEN only when running the bot directly
# This allows Railway to handle missing tokens gracefully
if __name__ == "__main__" and not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set")

# Database configuration
DATABASE_NAME = "finance_bot.db"

# Railway provides a persistent volume at /app/data
# Use this path for Railway deployment, fallback to local for development
import os
if os.path.exists("/app/data"):
    DATABASE_PATH = f"/app/data/{DATABASE_NAME}"
else:
    DATABASE_PATH = DATABASE_NAME

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