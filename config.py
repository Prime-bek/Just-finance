import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1265652628"))

if not BOT_TOKEN:
    raise ValueError("❌ Установи BOT_TOKEN в переменных окружения!")

DB_PATH = os.getenv("DB_PATH", "finance_bot.db")

# Языки
LANGUAGES = {
    "ru": "🇷🇺 Русский",
    "uz": "🇺🇿 O'zbekcha"
}

# Валюты с флагами
CURRENCIES = {
    "UZS": {"symbol": "so'm", "flag": "🇺🇿", "name": "UZS"},
    "RUB": {"symbol": "₽", "flag": "🇷🇺", "name": "RUB"},
    "USD": {"symbol": "$", "flag": "🇺🇸", "name": "USD"},
    "EUR": {"symbol": "€", "flag": "🇪🇺", "name": "EUR"},
    "KZT": {"symbol": "₸", "flag": "🇰🇿", "name": "KZT"},
    "TRY": {"symbol": "₺", "flag": "🇹🇷", "name": "TRY"}
}

# Категории расходов
EXPENSE_CATEGORIES = {
    "food": {"emoji": "🍔", "name_ru": "Еда", "name_uz": "Oziq-ovqat"},
    "transport": {"emoji": "🚕", "name_ru": "Транспорт", "name_uz": "Transport"},
    "entertainment": {"emoji": "🎮", "name_ru": "Развлечения", "name_uz": "Ko'ngil ochar"},
    "shopping": {"emoji": "🛍", "name_ru": "Покупки", "name_uz": "Xaridlar"},
    "health": {"emoji": "💊", "name_ru": "Здоровье", "name_uz": "Salomatlik"},
    "subscriptions": {"emoji": "📱", "name_ru": "Подписки", "name_uz": "Obunalar"},
    "education": {"emoji": "📚", "name_ru": "Образование", "name_uz": "Ta'lim"},
    "utilities": {"emoji": "🏠", "name_ru": "Коммунальные", "name_uz": "Kommunal"},
    "other": {"emoji": "📦", "name_ru": "Другое", "name_uz": "Boshqa"}
}

# Категории доходов
INCOME_CATEGORIES = {
    "salary": {"emoji": "💼", "name_ru": "Зарплата", "name_uz": "Ish haqi"},
    "freelance": {"emoji": "💻", "name_ru": "Фриланс", "name_uz": "Frilans"},
    "gift": {"emoji": "🎁", "name_ru": "Подарок", "name_uz": "Sovg'a"},
    "investments": {"emoji": "📈", "name_ru": "Инвестиции", "name_uz": "Investitsiyalar"},
    "other": {"emoji": "📦", "name_ru": "Другое", "name_uz": "Boshqa"}
}

# Типы кошельков
WALLET_TYPES = {
    "main": {"emoji": "💳", "name_ru": "Основной", "name_uz": "Asosiy"},
    "cash": {"emoji": "💵", "name_ru": "Наличные", "name_uz": "Naqd pul"},
    "bank": {"emoji": "🏦", "name_ru": "Банк", "name_uz": "Bank"},
    "savings": {"emoji": "💰", "name_ru": "Сбережения", "name_uz": "Jamg'arma"}
}

# Тексты переводов
TEXTS = {
    "ru": {
        "welcome": "👋 Добро пожаловать в <b>Finance Tracker</b>!\n\nЯ помогу вам учитывать доходы и расходы, управлять кошельками и следить за финансами.\n\nВыберите язык:",
        "menu": "📋 <b>Главное меню</b>\n\nВыберите действие:",
        
        # Главное меню
        "balance": "📊 Мой баланс",
        "add_operation": "➕ Добавить операцию",
        "history": "📋 История операций",
        "statistics": "📈 Финансовая статистика",
        "wallets": "💳 Кошельки",
        "settings": "⚙️ Настройки",
        
        # Операции
        "select_operation_type": "💰 <b>Выберите тип операции</b>",
        "expense": "💸 Расход",
        "income": "💰 Доход",
        "select_category": "📂 <b>Выберите категорию</b>",
        "enter_amount": "💵 <b>Введите сумму</b>\n\nПример: 15000",
        "invalid_amount": "❌ <b>Неверная сумма</b>\n\nПожалуйста, введите число больше 0",
        "select_wallet": "💳 <b>Выберите кошелек</b>",
        "operation_added": "✅ <b>Операция добавлена!</b>\n\n"
                          "📌 Тип: {type}\n"
                          "📂 Категория: {category}\n"
                          "💵 Сумма: {amount}\n"
                          "💳 Кошелек: {wallet}\n"
                          "📅 Дата: {date}\n"
                          "⏰ Время: {time}",
        "operation_cancelled": "❌ Операция отменена",
        
        # Баланс
        "your_balance": "💰 <b>Ваши кошельки</b>",
        "total_balance": "\n📊 <b>Общий баланс:</b> {amount}",
        "no_wallets": "❌ У вас пока нет кошельков\n\nСоздайте кошелек в разделе «Кошельки»",
        
        # Кошельки
        "wallets_title": "💳 <b>Ваши кошельки</b>\n\nНажмите на кошелек для управления:",
        "wallet_item": "{emoji} <b>{name}</b>\n   💰 Баланс: {amount}\n",
        "add_wallet": "➕ Добавить кошелек",
        "delete_wallet": "❌ Удалить кошелек",
        "enter_wallet_name": "✏️ <b>Введите название кошелька</b>\n\nПримеры:\n• 💳 Основной\n• 💵 Наличные\n• 🏦 Банк\n• 💰 Сбережения",
        "wallet_created": "✅ <b>Кошелек создан!</b>\n\nНазвание: {name}\nТип: {type}",
        "wallet_deleted": "🗑 <b>Кошелек удален</b>",
        "confirm_delete_wallet": "⚠️ <b>Удалить кошелек?</b>\n\n{name}\n\nВсе операции этого кошелька будут удалены!\n\nВы уверены?",
        "yes": "✅ Да",
        "no": "❌ Нет",
        "set_main": "⭐ Сделать основным",
        "main_wallet_set": "✅ Основной кошелек изменен",
        
        # История
        "history_title": "📋 <b>История операций</b>\n\nПоследние 20 операций:",
        "no_transactions": "📭 История пуста\n\nДобавьте первую операцию!",
        "transaction_item": "{emoji} <b>{category}</b> — {amount}\n"
                          "💳 {wallet}\n"
                          "📅 {date}  ⏰ {time}\n",
        "expense_emoji": "💸",
        "income_emoji": "💰",
        
        # Статистика
        "statistics_title": "📈 <b>Финансовая статистика</b>\n\nЗа последние 30 дней:",
        "stats_income": "💰 Доход: {amount}",
        "stats_expense": "💸 Расход: {amount}",
        "stats_balance": "📊 Баланс: {amount}",
        "top_category": "🏆 Топ категория: {category}",
        
        # Настройки
        "settings_title": "⚙️ <b>Настройки</b>",
        "settings_menu": "🌐 Язык: {language}\n💱 Валюта: {currency}\n🔔 Напоминания: {notifications}",
        "select_language": "🌐 <b>Выберите язык</b>",
        "select_currency": "💱 <b>Выберите валюту</b>",
        "language_changed": "✅ Язык изменен",
        "currency_changed": "✅ Валюта изменена на {currency}",
        "notifications_on": "🔔 Включены",
        "notifications_off": "🔕 Выключены",
        "manage_wallets": "💳 Управление кошельками",
        
        # Админ
        "admin_panel": "🔐 <b>Админ-панель</b>\n\n"
                      "👥 Всего пользователей: {total}\n"
                      "⚡ Активные (7дн): {active}\n"
                      "🔒 Заблокировано: {blocked}",
        "admin_users": "👥 Пользователи",
        "admin_stats": "📊 Статистика",
        "admin_blocked": "🔒 Заблокированные",
        "user_blocked": "❌ Вы заблокированы и не можете использовать бота",
        "no_access": "⛔ Нет доступа",
        
        # Общее
        "back": "🔙 Назад",
        "cancel": "❌ Отмена",
        "save": "💾 Сохранить",
        "delete": "🗑 Удалить",
        "error": "❌ Произошла ошибка. Попробуйте еще раз.",
    },
    
    "uz": {
        "welcome": "👋 <b>Finance Tracker</b>ga xush kelibsiz!\n\nMen sizga daromadlar va xarajatlarni hisoblash, hamyonlarni boshqarish va moliyangizni kuzatishda yordam beraman.\n\nTilni tanlang:",
        "menu": "📋 <b>Asosiy menyu</b>\n\nAmalni tanlang:",
        
        # Главное меню
        "balance": "📊 Mening balansim",
        "add_operation": "➕ Operatsiya qo'shish",
        "history": "📋 Operatsiyalar tarixi",
        "statistics": "📈 Moliyaviy statistika",
        "wallets": "💳 Hamyonlar",
        "settings": "⚙️ Sozlamalar",
        
        # Операции
        "select_operation_type": "💰 <b>Operatsiya turini tanlang</b>",
        "expense": "💸 Xarajat",
        "income": "💰 Daromad",
        "select_category": "📂 <b>Kategoriyani tanlang</b>",
        "enter_amount": "💵 <b>Miqdorni kiriting</b>\n\nMisol: 15000",
        "invalid_amount": "❌ <b>Noto'g'ri miqdor</b>\n\nIltimos, 0 dan katta son kiriting",
        "select_wallet": "💳 <b>Hamyonni tanlang</b>",
        "operation_added": "✅ <b>Operatsiya qo'shildi!</b>\n\n"
                          "📌 Tur: {type}\n"
                          "📂 Kategoriya: {category}\n"
                          "💵 Miqdor: {amount}\n"
                          "💳 Hamyon: {wallet}\n"
                          "📅 Sana: {date}\n"
                          "⏰ Vaqt: {time}",
        "operation_cancelled": "❌ Operatsiya bekor qilindi",
        
        # Баланс
        "your_balance": "💰 <b>Sizning hamyonlaringiz</b>",
        "total_balance": "\n📊 <b>Umumiy balans:</b> {amount}",
        "no_wallets": "❌ Sizda hali hamyonlar yo'q\n\n«Hamyonlar» bo'limida hamyon yarating",
        
        # Кошельки
        "wallets_title": "💳 <b>Sizning hamyonlaringiz</b>\n\nBoshqarish uchun hamyonni bosing:",
        "wallet_item": "{emoji} <b>{name}</b>\n   💰 Balans: {amount}\n",
        "add_wallet": "➕ Hamyon qo'shish",
        "delete_wallet": "❌ Hamyonni o'chirish",
        "enter_wallet_name": "✏️ <b>Hamyon nomini kiriting</b>\n\nMisollar:\n• 💳 Asosiy\n• 💵 Naqd pul\n• 🏦 Bank\n• 💰 Jamg'arma",
        "wallet_created": "✅ <b>Hamyon yaratildi!</b>\n\nNomi: {name}\nTuri: {type}",
        "wallet_deleted": "🗑 <b>Hamyon o'chirildi</b>",
        "confirm_delete_wallet": "⚠️ <b>Hamyonni o'chirish?</b>\n\n{name}\n\nBu hamyondagi barcha operatsiyalar o'chiriladi!\n\nIshonchingiz komilmi?",
        "yes": "✅ Ha",
        "no": "❌ Yo'q",
        "set_main": "⭐ Asosiy qilish",
        "main_wallet_set": "✅ Asosiy hamyon o'zgartirildi",
        
        # История
        "history_title": "📋 <b>Operatsiyalar tarixi</b>\n\nOxirgi 20 operatsiya:",
        "no_transactions": "📭 Tarix bo'sh\n\nBirinchi operatsiyani qo'shing!",
        "transaction_item": "{emoji} <b>{category}</b> — {amount}\n"
                          "💳 {wallet}\n"
                          "📅 {date}  ⏰ {time}\n",
        "expense_emoji": "💸",
        "income_emoji": "💰",
        
        # Статистика
        "statistics_title": "📈 <b>Moliyaviy statistika</b>\n\nOxirgi 30 kun uchun:",
        "stats_income": "💰 Daromad: {amount}",
        "stats_expense": "💸 Xarajat: {amount}",
        "stats_balance": "📊 Balans: {amount}",
        "top_category": "🏆 Top kategoriya: {category}",
        
        # Настройки
        "settings_title": "⚙️ <b>Sozlamalar</b>",
        "settings_menu": "🌐 Til: {language}\n💱 Valyuta: {currency}\n🔔 Eslatmalar: {notifications}",
        "select_language": "🌐 <b>Tilni tanlang</b>",
        "select_currency": "💱 <b>Valyutani tanlang</b>",
        "language_changed": "✅ Til o'zgartirildi",
        "currency_changed": "✅ Valyuta {currency} ga o'zgartirildi",
        "notifications_on": "🔔 Yoqilgan",
        "notifications_off": "🔕 O'chirilgan",
        "manage_wallets": "💳 Hamyonlarni boshqarish",
        
        # Админ
        "admin_panel": "🔐 <b>Admin panel</b>\n\n"
                      "👥 Jami foydalanuvchilar: {total}\n"
                      "⚡ Faol (7kun): {active}\n"
                      "🔒 Bloklangan: {blocked}",
        "admin_users": "👥 Foydalanuvchilar",
        "admin_stats": "📊 Statistika",
        "admin_blocked": "🔒 Bloklanganlar",
        "user_blocked": "❌ Siz bloklangansiz va botdan foydalana olmaysiz",
        "no_access": "⛔ Kirish taqiqlangan",
        
        # Общее
        "back": "🔙 Orqaga",
        "cancel": "❌ Bekor qilish",
        "save": "💾 Saqlash",
        "delete": "🗑 O'chirish",
        "error": "❌ Xatolik yuz berdi. Qayta urinib ko'ring.",
    }
}