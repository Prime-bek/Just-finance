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
                    currency TEXT DEFAULT 'RUB',
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Кошельки
            await db.execute('''
                CREATE TABLE IF NOT EXISTS wallets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT,
                    type TEXT,
                    is_main BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            ''')
            
            # Операции
            await db.execute('''
                CREATE TABLE IF NOT EXISTS operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    wallet_id INTEGER,
                    type TEXT,
                    category TEXT,
                    amount REAL,
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
                await db.execute(
                    "INSERT INTO users (user_id, username, name) VALUES (?, ?, ?)",
                    (user_id, username, name)
                )
                await db.commit()
                
                # Создаем основной кошелек
                await db.execute(
                    "INSERT INTO wallets (user_id, name, type, is_main) VALUES (?, ?, ?, ?)",
                    (user_id, "💳 Основной" if True else "💳 Asosiy", "main", True)
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

    async def update_user_language(self, user_id: int, language: str):
        await db.execute("UPDATE users SET language = ? WHERE user_id = ?", (language, user_id))
        await db.commit()

    async def update_user_currency(self, user_id: int, currency: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE users SET currency = ? WHERE user_id = ?", (currency, user_id))
            await db.commit()

    async def update_user_status(self, user_id: int, status: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE users SET status = ? WHERE user_id = ?", (status, user_id))
            await db.commit()

    async def get_user_wallets(self, user_id: int) -> List[Dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM wallets WHERE user_id = ?", (user_id,)) as cur:
                return [dict(row) for row in await cur.fetchall()]

    async def create_wallet(self, user_id: int, name: str, wallet_type: str, is_main: bool = False) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute(
                "INSERT INTO wallets (user_id, name, type, is_main) VALUES (?, ?, ?, ?)",
                (user_id, name, wallet_type, is_main)
            )
            await db.commit()
            return cur.lastrowid

    async def delete_wallet(self, wallet_id: int, user_id: int) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM wallets WHERE id = ? AND user_id = ?", (wallet_id, user_id))
            await db.commit()
            return True

    async def set_main_wallet(self, wallet_id: int, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE wallets SET is_main = FALSE WHERE user_id = ?", (user_id,))
            await db.execute("UPDATE wallets SET is_main = TRUE WHERE id = ? AND user_id = ?", (wallet_id, user_id))
            await db.commit()

    async def add_operation(self, user_id: int, wallet_id: int, op_type: str, category: str, amount: float):
        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute(
                "INSERT INTO operations (user_id, wallet_id, type, category, amount) VALUES (?, ?, ?, ?, ?)",
                (user_id, wallet_id, op_type, category, amount)
            )
            await db.commit()
            return cur.lastrowid

    async def get_wallet_balance(self, wallet_id: int) -> float:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT type, amount FROM operations WHERE wallet_id = ?", (wallet_id,)
            ) as cur:
                balance = 0.0
                async for row in cur:
                    if row[0] == 'income':
                        balance += row[1]
                    else:
                        balance -= row[1]
                return balance

    async def get_user_operations(self, user_id: int, limit: int = 20) -> List[Dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """SELECT o.*, w.name as wallet_name 
                   FROM operations o 
                   JOIN wallets w ON o.wallet_id = w.id 
                   WHERE o.user_id = ? 
                   ORDER BY o.created_at DESC LIMIT ?""",
                (user_id, limit)
            ) as cur:
                return [dict(row) for row in await cur.fetchall()]

    async def get_user_stats(self, user_id: int, days: int = 30) -> Dict:
        async with aiosqlite.connect(self.db_path) as db:
            date_from = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
            
            async with db.execute(
                """SELECT type, SUM(amount) as total 
                   FROM operations 
                   WHERE user_id = ? AND created_at > ? 
                   GROUP BY type""",
                (user_id, date_from)
            ) as cur:
                stats = {'income': 0, 'expense': 0}
                async for row in cur:
                    stats[row[0]] = row[1]
                return stats

    # ========== ADMIN МЕТОДЫ ==========
    
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

db = Database()