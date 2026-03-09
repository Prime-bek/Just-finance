from bot.config import LANGUAGES, CURRENCIES, EXPENSE_CATEGORIES, INCOME_CATEGORIES, WALLET_TYPES

TEXTS = {
    'ru': {
        'welcome': '👋 Добро пожаловать в Finance Tracker Bot!\n\nЯ помогу вам учитывать доходы и расходы, управлять кошельками и следить за финансами.',
        'main_menu': '🏠 Главное меню',
        'balance': '📊 Баланс',
        'add_transaction': '➕ Добавить операцию',
        'history': '📋 История',
        'statistics': '📈 Статистика',
        'wallets': '💳 Кошельки',
        'settings': '⚙️ Настройки',
        
        'select_operation_type': 'Выберите тип операции:',
        'expense': '💸 Расход',
        'income': '💰 Доход',
        
        'select_category': 'Выберите категорию:',
        'enter_amount': 'Введите сумму:',
        'invalid_amount': '❌ Неверная сумма. Попробуйте еще раз:',
        'transaction_added': '✅ Операция добавлена.\n\nТип: {type}\nКатегория: {category}\nСумма: {amount}\nКошелек: {wallet}',
        
        'your_balance': '💰 Ваш баланс:',
        'wallet_balance': '{emoji} {name} — {amount} {currency}',
        'no_wallets': 'У вас пока нет кошельков.',
        
        'recent_transactions': '📋 Последние операции:',
        'transaction_item': '{category} — {amount} {currency}',
        'no_transactions': 'У вас пока нет операций.',
        
        'statistics': '📊 Статистика за {period}:',
        'income': '💰 Доход: {amount} {currency}',
        'expenses': '💸 Расход: {amount} {currency}',
        'balance': '💼 Баланс: {amount} {currency}',
        'top_category': '🏆 Самая большая категория: {category}',
        
        'your_wallets': '💳 Ваши кошельки:',
        'create_wallet': '➕ Создать кошелек',
        'select_wallet_type': 'Выберите тип кошелька:',
        'enter_wallet_name': 'Введите название кошелька:',
        'wallet_created': '✅ Кошелек создан: {name}',
        
        'settings_menu': '⚙️ Настройки',
        'language': '🌐 Язык: {language}',
        'currency': '💱 Валюта: {currency}',
        'notifications': '🔔 Напоминания: {status}',
        'select_language': 'Выберите язык:',
        'select_currency': 'Выберите валюту:',
        'settings_updated': '✅ Настройки обновлены!',
        
        'back': '⬅️ Назад',
        'cancel': '❌ Отмена',
        'confirm': '✅ Подтвердить',
        'yes': 'Да',
        'no': 'Нет',
        
        'admin_panel': '🛡️ Админ панель',
        'total_users': '👥 Всего пользователей: {count}',
        'total_transactions': '📊 Всего транзакций: {count}',
        'user_info': '🆔 ID: {id}\n👤 Имя: {name}\n🔗 Username: {username}\n🌐 Язык: {language}\n📅 Регистрация: {registration}\n⚡ Последняя активность: {activity}\n📊 Статус: {status}',
        
        'error_occurred': '❌ Произошла ошибка. Попробуйте еще раз.',
        'operation_cancelled': '❌ Операция отменена.',
    },
    'uz': {
        'welcome': '👋 Finance Tracker Botga xush kelibsiz!\n\nMen sizga daromadlar va xarajatlarni hisoblash, hamyonlarni boshqarish va moliyangizni kuzatishda yordam beraman.',
        'main_menu': '🏠 Bosh menyu',
        'balance': '📊 Balans',
        'add_transaction': '➕ Operatsiya qoshish',
        'history': '📋 Tarix',
        'statistics': '📈 Statistika',
        'wallets': '💳 Hamyonlar',
        'settings': '⚙️ Sozlamalar',
        
        'select_operation_type': 'Operatsiya turini tanlang:',
        'expense': '💸 Xarajat',
        'income': '💰 Daromad',
        
        'select_category': 'Kategoriyani tanlang:',
        'enter_amount': 'Miqdorni kiriting:',
        'invalid_amount': '❌ Notogri miqdor. Yana urinib koring:',
        'transaction_added': '✅ Operatsiya qoshildi.\n\nTuri: {type}\nKategoriya: {category}\nMiqdor: {amount}\nHamyon: {wallet}',
        
        'your_balance': '💰 Sizning balansingiz:',
        'wallet_balance': '{emoji} {name} — {amount} {currency}',
        'no_wallets': 'Sizda hali hamyonlar yo\'q.',
        
        'recent_transactions': '📋 Oxirgi operatsiyalar:',
        'transaction_item': '{category} — {amount} {currency}',
        'no_transactions': 'Sizda hali operatsiyalar yo\'q.',
        
        'statistics': '📊 {period} davomida statistika:',
        'income': '💰 Daromad: {amount} {currency}',
        'expenses': '💸 Xarajat: {amount} {currency}',
        'balance': '💼 Balans: {amount} {currency}',
        'top_category': '🏆 Eng katta kategoriya: {category}',
        
        'your_wallets': '💳 Sizning hamyonlaringiz:',
        'create_wallet': '➕ Hamyon yaratish',
        'select_wallet_type': 'Hamyon turini tanlang:',
        'enter_wallet_name': 'Hamyon nomini kiriting:',
        'wallet_created': '✅ Hamyon yaratildi: {name}',
        
        'settings_menu': '⚙️ Sozlamalar',
        'language': '🌐 Til: {language}',
        'currency': '💱 Valyuta: {currency}',
        'notifications': '🔔 Eslatmalar: {status}',
        'select_language': 'Tilni tanlang:',
        'select_currency': 'Valyutani tanlang:',
        'settings_updated': '✅ Sozlamalar yangilandi!',
        
        'back': '⬅️ Orqaga',
        'cancel': '❌ Bekor qilish',
        'confirm': '✅ Tasdiqlash',
        'yes': 'Ha',
        'no': 'Yo\'q',
        
        'admin_panel': '🛡️ Admin paneli',
        'total_users': '👥 Jami foydalanuvchilar: {count}',
        'total_transactions': '📊 Jami tranzaksiyalar: {count}',
        'user_info': '🆔 ID: {id}\n👤 Ism: {name}\n🔗 Username: {username}\n🌐 Til: {language}\n📅 Ro\'yxatdan o\'tgan: {registration}\n⚡ Oxirgi faollik: {activity}\n📊 Holat: {status}',
        
        'error_occurred': '❌ Xatolik yuz berdi. Yana urinib ko\'ring.',
        'operation_cancelled': '❌ Operatsiya bekor qilindi.',
    }
}

def get_text(key: str, language: str = 'ru', **kwargs) -> str:
    """Get text by key and language with optional formatting"""
    text = TEXTS.get(language, TEXTS['ru']).get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except KeyError:
            return text
    return text

def get_category_name(category_key: str, language: str = 'ru') -> str:
    """Get category name in specified language"""
    if category_key in EXPENSE_CATEGORIES:
        return EXPENSE_CATEGORIES[category_key]
    elif category_key in INCOME_CATEGORIES:
        return INCOME_CATEGORIES[category_key]
    return category_key

def get_wallet_type_name(wallet_type: str, language: str = 'ru') -> str:
    """Get wallet type name in specified language"""
    return WALLET_TYPES.get(wallet_type, wallet_type)

def get_language_name(lang_code: str) -> str:
    """Get language name by code"""
    return LANGUAGES.get(lang_code, lang_code)

def get_currency_symbol(currency_code: str) -> str:
    """Get currency symbol by code"""
    return CURRENCIES.get(currency_code, currency_code)