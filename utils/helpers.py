import datetime
from typing import Optional

def format_number(number: float) -> str:
    """Format number with spaces as thousand separators"""
    return f"{number:,.0f}".replace(",", " ")

def format_datetime(dt: datetime.datetime) -> str:
    """Format datetime for display"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def format_currency(amount: float, currency: str = "RUB") -> str:
    """Format amount with currency"""
    from bot.config import CURRENCIES
    symbol = CURRENCIES.get(currency, currency)
    formatted_amount = format_number(abs(amount))
    return f"{formatted_amount} {symbol}"

def parse_amount(text: str) -> Optional[float]:
    """Parse amount from user input"""
    try:
        # Remove spaces and replace comma with dot
        cleaned = text.replace(" ", "").replace(",", ".")
        amount = float(cleaned)
        if amount <= 0:
            return None
        return amount
    except ValueError:
        return None

def get_period_dates(period: str) -> tuple:
    """Get start and end dates for a given period"""
    now = datetime.datetime.now()
    
    if period == 'month':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif period == 'week':
        start_date = now - datetime.timedelta(days=7)
        end_date = now
    elif period == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    else:
        start_date = now - datetime.timedelta(days=30)
        end_date = now
    
    return start_date, end_date

def validate_username(username: Optional[str]) -> str:
    """Validate and format username"""
    if not username:
        return "Не указан"
    return f"@{username}"

def get_user_status_text(status: str, language: str = 'ru') -> str:
    """Get user status text in specified language"""
    status_texts = {
        'ru': {
            'active': 'Активен',
            'blocked': 'Заблокирован',
            'inactive': 'Неактивен'
        },
        'uz': {
            'active': 'Faol',
            'blocked': 'Bloklangan',
            'inactive': 'Faol emas'
        }
    }
    return status_texts.get(language, status_texts['ru']).get(status, status)