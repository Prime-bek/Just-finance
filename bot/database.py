import aiosqlite
import datetime
from typing import Optional, List, Dict, Any
from bot.config import DATABASE_PATH, ADMIN_ID

class Database:
    def __init__(self):
        self.db_name = DATABASE_PATH

    async def create_tables(self):
        async with aiosqlite.connect(self.db_name) as db:
            # Users table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    username TEXT,
                    language TEXT DEFAULT 'ru',
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active'
                )
            ''')
            
            # Wallets table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS wallets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    is_main BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (telegram_id) ON DELETE CASCADE
                )
            ''')
            
            # Transactions table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    wallet_id INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (telegram_id) ON DELETE CASCADE,
                    FOREIGN KEY (wallet_id) REFERENCES wallets (id) ON DELETE CASCADE
                )
            ''')
            
            # Settings table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    user_id INTEGER PRIMARY KEY,
                    language TEXT DEFAULT 'ru',
                    currency TEXT DEFAULT 'RUB',
                    notifications BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users (telegram_id) ON DELETE CASCADE
                )
            ''')
            
            await db.commit()

    async def add_user(self, telegram_id: int, name: str, username: Optional[str] = None, language: str = 'ru'):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                INSERT OR REPLACE INTO users (telegram_id, name, username, language, last_activity)
                VALUES (?, ?, ?, ?, ?)
            ''', (telegram_id, name, username, language, datetime.datetime.now()))
            
            # Create default settings
            await db.execute('''
                INSERT OR IGNORE INTO settings (user_id, language)
                VALUES (?, ?)
            ''', (telegram_id, language))
            
            # Create default wallet for new user
            await self.create_wallet(telegram_id, "💳 Основной", "main", True)
            
            await db.commit()

    async def get_user(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, row))
                return None

    async def update_user_activity(self, telegram_id: int):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE users SET last_activity = ? WHERE telegram_id = ?', 
                           (datetime.datetime.now(), telegram_id))
            await db.commit()

    async def create_wallet(self, user_id: int, name: str, wallet_type: str, is_main: bool = False) -> int:
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('''
                INSERT INTO wallets (user_id, name, type, is_main)
                VALUES (?, ?, ?, ?)
            ''', (user_id, name, wallet_type, is_main))
            await db.commit()
            return cursor.lastrowid

    async def get_user_wallets(self, user_id: int) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('SELECT * FROM wallets WHERE user_id = ? ORDER BY is_main DESC, name', (user_id,)) as cursor:
                rows = await cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]

    async def get_main_wallet(self, user_id: int) -> Optional[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('SELECT * FROM wallets WHERE user_id = ? AND is_main = TRUE', (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, row))
                return None

    async def add_transaction(self, user_id: int, wallet_id: int, transaction_type: str, 
                            category: str, amount: float, description: Optional[str] = None) -> int:
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('''
                INSERT INTO transactions (user_id, wallet_id, type, category, amount, description)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, wallet_id, transaction_type, category, amount, description))
            await db.commit()
            return cursor.lastrowid

    async def get_wallet_balance(self, wallet_id: int) -> float:
        async with aiosqlite.connect(self.db_name) as db:
            # Get all transactions for this wallet
            async with db.execute('''
                SELECT type, amount FROM transactions WHERE wallet_id = ?
            ''', (wallet_id,)) as cursor:
                transactions = await cursor.fetchall()
                
                balance = 0.0
                for transaction_type, amount in transactions:
                    if transaction_type == 'income':
                        balance += amount
                    else:  # expense
                        balance -= amount
                
                return balance

    async def get_user_transactions(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('''
                SELECT t.*, w.name as wallet_name 
                FROM transactions t
                JOIN wallets w ON t.wallet_id = w.id
                WHERE t.user_id = ?
                ORDER BY t.created_at DESC
                LIMIT ?
            ''', (user_id, limit)) as cursor:
                rows = await cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]

    async def get_user_stats(self, user_id: int, period: str = 'month') -> Dict[str, Any]:
        async with aiosqlite.connect(self.db_name) as db:
            # Calculate date range based on period
            if period == 'month':
                date_from = datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            else:  # week
                date_from = datetime.datetime.now() - datetime.timedelta(days=7)
            
            # Get income and expenses for the period
            async with db.execute('''
                SELECT type, SUM(amount) as total, category
                FROM transactions
                WHERE user_id = ? AND created_at >= ?
                GROUP BY type, category
                ORDER BY total DESC
            ''', (user_id, date_from)) as cursor:
                rows = await cursor.fetchall()
                
                income = 0
                expenses = 0
                category_stats = {}
                
                for transaction_type, total, category in rows:
                    if transaction_type == 'income':
                        income += total
                    else:
                        expenses += total
                        category_stats[category] = total
                
                # Find top expense category
                top_expense_category = max(category_stats.items(), key=lambda x: x[1])[0] if category_stats else None
                
                return {
                    'income': income,
                    'expenses': expenses,
                    'balance': income - expenses,
                    'top_expense_category': top_expense_category,
                    'category_stats': category_stats
                }

    async def get_all_users(self) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('SELECT * FROM users ORDER BY registration_date DESC') as cursor:
                rows = await cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]

    async def get_all_transactions(self, limit: int = 100) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('''
                SELECT t.*, u.name as user_name, u.username as user_username, w.name as wallet_name
                FROM transactions t
                JOIN users u ON t.user_id = u.telegram_id
                JOIN wallets w ON t.wallet_id = w.id
                ORDER BY t.created_at DESC
                LIMIT ?
            ''', (limit,)) as cursor:
                rows = await cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]

    async def update_user_status(self, telegram_id: int, status: str):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE users SET status = ? WHERE telegram_id = ?', (status, telegram_id))
            await db.commit()

    async def update_user_language(self, telegram_id: int, language: str):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE users SET language = ? WHERE telegram_id = ?', (language, telegram_id))
            await db.commit()

    async def delete_wallet(self, wallet_id: int, user_id: int) -> bool:
        """Delete wallet and all its transactions"""
        async with aiosqlite.connect(self.db_name) as db:
            # Check if wallet exists and belongs to user
            async with db.execute('SELECT id FROM wallets WHERE id = ? AND user_id = ?', (wallet_id, user_id)) as cursor:
                if not await cursor.fetchone():
                    return False
            
            # Delete wallet (cascade will delete transactions)
            await db.execute('DELETE FROM wallets WHERE id = ? AND user_id = ?', (wallet_id, user_id))
            await db.commit()
            return True

    async def set_main_wallet(self, wallet_id: int, user_id: int) -> bool:
        """Set wallet as main and reset all others"""
        async with aiosqlite.connect(self.db_name) as db:
            # Check if wallet exists and belongs to user
            async with db.execute('SELECT id FROM wallets WHERE id = ? AND user_id = ?', (wallet_id, user_id)) as cursor:
                if not await cursor.fetchone():
                    return False
            
            # Reset all wallets to non-main
            await db.execute('UPDATE wallets SET is_main = FALSE WHERE user_id = ?', (user_id,))
            # Set selected wallet as main
            await db.execute('UPDATE wallets SET is_main = TRUE WHERE id = ? AND user_id = ?', (wallet_id, user_id))
            await db.commit()
            return True

    async def get_user_settings(self, user_id: int) -> Optional[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('SELECT * FROM settings WHERE user_id = ?', (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, row))
                return None

    async def update_user_settings(self, user_id: int, language: Optional[str] = None, 
                                 currency: Optional[str] = None, notifications: Optional[bool] = None):
        async with aiosqlite.connect(self.db_name) as db:
            if language is not None:
                await db.execute('UPDATE settings SET language = ? WHERE user_id = ?', (language, user_id))
            if currency is not None:
                await db.execute('UPDATE settings SET currency = ? WHERE user_id = ?', (currency, user_id))
            if notifications is not None:
                await db.execute('UPDATE settings SET notifications = ? WHERE user_id = ?', (notifications, user_id))
            
            await db.commit()

# Global database instance
db = Database()