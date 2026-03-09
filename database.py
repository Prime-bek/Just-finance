import aiosqlite
import datetime
from typing import Optional, List, Dict, Any
from config import DB_PATH, EXPENSE_CATEGORIES, INCOME_CATEGORIES

class Database:
    def __init__(self):
        self.db_path = DB_PATH

    async def init(self):
        """Создание таблиц"""
        async with aiosqlite.connect(self.db_path) as db:
            # Пользователи
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    name TEXT,
                    language TEXT DEFAULT 'ru',
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Настройки
            await db.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    user_id INTEGER PRIMARY KEY,
                    currency TEXT DEFAULT 'UZS',
                    notifications BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            ''')
            
            # Кошельки
            await db.execute('''
                CREATE TABLE IF NOT EXISTS wallets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT,
                    type TEXT DEFAULT 'main',
                    is_main BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            ''')
            
            # Операции с date и time
            await db.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    wallet_id INTEGER,
                    type TEXT,
                    category TEXT,
                    amount REAL,
                    date TEXT,
                    time TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    FOREIGN KEY (wallet_id) REFERENCES wallets(id) ON DELETE CASCADE
                )
            ''')
            
            await db.commit()

    async def get_or_create_user(self, user_id: int, username: str = None, name: str = None) -> Dict:
        """Получить или создать пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cur:
                user = await cur.fetchone()
            
            if not user:
                # Создаем пользователя
                await db.execute(
                    "INSERT INTO users (user_id, username, name) VALUES (?, ?, ?)",
                    (user_id, username, name)
                )
                # Создаем настройки
                await db.execute(
                    "INSERT INTO settings (user_id) VALUES (?)",
                    (user_id,)
                )
                # Создаем основной кошелек
                await db.execute(
                    "INSERT INTO wallets (user_id, name, type, is_main) VALUES (?, ?, ?, ?)",
                    (user_id, "💳 Основной", "main", True)
                )
                await db.commit()
                
                async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cur:
                    user = await cur.fetchone()
            else:
                # Обновляем активность
                await db.execute(
                    "UPDATE users SET last_activity = ? WHERE user_id = ?",
                    (datetime.datetime.now(), user_id)
                )
                await db.commit()
            
            return dict(user)

    async def get_user_settings(self, user_id: int) -> Dict:
        """Получить настройки пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM settings WHERE user_id = ?", (user_id,)) as cur:
                row = await cur.fetchone()
                if row:
                    return dict(row)
                # Создаем настройки если нет
                await db.execute("INSERT INTO settings (user_id) VALUES (?)", (user_id,))
                await db.commit()
                return {"user_id": user_id, "currency": "UZS", "notifications": True}

    async def update_language(self, user_id: int, language: str):
        await db.execute("UPDATE users SET language = ? WHERE user_id = ?", (language, user_id))
        await db.commit()

    async def update_currency(self, user_id: int, currency: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO settings (user_id, currency) VALUES (?, ?) "
                "ON CONFLICT(user_id) DO UPDATE SET currency = ?",
                (user_id, currency, currency)
            )
            await db.commit()

    async def update_notifications(self, user_id: int, status: bool):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO settings (user_id, notifications) VALUES (?, ?) "
                "ON CONFLICT(user_id) DO UPDATE SET notifications = ?",
                (user_id, status, status)
            )
            await db.commit()

    async def get_user_wallets(self, user_id: int) -> List[Dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM wallets WHERE user_id = ? ORDER BY is_main DESC, id", 
                (user_id,)
            ) as cur:
                return [dict(row) for row in await cur.fetchall()]

    async def create_wallet(self, user_id: int, name: str, wallet_type: str = "main", is_main: bool = False) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute(
                "INSERT INTO wallets (user_id, name, type, is_main) VALUES (?, ?, ?, ?)",
                (user_id, name, wallet_type, is_main)
            )
            await db.commit()
            return cur.lastrowid

    async def delete_wallet(self, wallet_id: int, user_id: int) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            # Удаляем операции кошелька
            await db.execute("DELETE FROM transactions WHERE wallet_id = ?", (wallet_id,))
            # Удаляем кошелек
            await db.execute("DELETE FROM wallets WHERE id = ? AND user_id = ?", (wallet_id, user_id))
            await db.commit()
            return True

    async def set_main_wallet(self, wallet_id: int, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE wallets SET is_main = FALSE WHERE user_id = ?", (user_id,))
            await db.execute(
                "UPDATE wallets SET is_main = TRUE WHERE id = ? AND user_id = ?", 
                (wallet_id, user_id)
            )
            await db.commit()

    async def add_transaction(self, user_id: int, wallet_id: int, t_type: str, category: str, amount: float) -> int:
        """Добавить операцию с date и time"""
        now = datetime.datetime.now()
        date_str = now.strftime("%d.%m.%Y")
        time_str = now.strftime("%H:%M")
        
        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute(
                "INSERT INTO transactions (user_id, wallet_id, type, category, amount, date, time) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (user_id, wallet_id, t_type, category, amount, date_str, time_str)
            )
            await db.commit()
            return cur.lastrowid

    async def get_wallet_balance(self, wallet_id: int) -> float:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT type, amount FROM transactions WHERE wallet_id = ?", (wallet_id,)
            ) as cur:
                balance = 0.0
                async for row in cur:
                    if row[0] == 'income':
                        balance += row[1]
                    else:
                        balance -= row[1]
                return balance

    async def get_user_transactions(self, user_id: int, limit: int = 20) -> List[Dict]:
        """Получить операции с date, time и wallet_name"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """SELECT t.*, w.name as wallet_name 
                   FROM transactions t 
                   JOIN wallets w ON t.wallet_id = w.id 
                   WHERE t.user_id = ? 
                   ORDER BY t.created_at DESC 
                   LIMIT ?""",
                (user_id, limit)
            ) as cur:
                return [dict(row) for row in await cur.fetchall()]

    async def get_user_stats(self, user_id: int, days: int = 30) -> Dict:
        async with aiosqlite.connect(self.db_path) as db:
            date_from = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
            
            async with db.execute(
                """SELECT type, SUM(amount) as total, category 
                   FROM transactions 
                   WHERE user_id = ? AND created_at > ? 
                   GROUP BY type, category""",
                (user_id, date_from)
            ) as cur:
                stats = {'income': 0, 'expense': 0, 'categories': {}}
                async for row in cur:
                    t_type, total, cat = row
                    if t_type == 'income':
                        stats['income'] += total
                    else:
                        stats['expense'] += total
                        stats['categories'][cat] = total
                return stats

    # ========== ADMIN ==========
    
    async def get_all_users(self) -> List[Dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM users ORDER BY created_at DESC") as cur:
                return [dict(row) for row in await cur.fetchall()]

    async def get_active_users_count(self, days: int = 7) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            date_limit = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
            async with db.execute(
                "SELECT COUNT(*) FROM users WHERE last_activity > ?", (date_limit,)
            ) as cur:
                return (await cur.fetchone())[0]

    async def get_blocked_users_count(self) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM users WHERE status = 'blocked'") as cur:
                return (await cur.fetchone())[0]

    async def update_user_status(self, user_id: int, status: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE users SET status = ? WHERE user_id = ?", (status, user_id))
            await db.commit()

db = Database()