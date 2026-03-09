from typing import Dict, List, Any
from bot.database import db

class BalanceService:
    
    @staticmethod
    async def get_user_total_balance(user_id: int) -> Dict[str, Any]:
        """Get user's total balance across all wallets"""
        wallets = await db.get_user_wallets(user_id)
        
        total_balance = 0
        wallet_balances = []
        
        for wallet in wallets:
            balance = await db.get_wallet_balance(wallet['id'])
            wallet_balances.append({
                'id': wallet['id'],
                'name': wallet['name'],
                'type': wallet['type'],
                'balance': balance,
                'is_main': wallet['is_main']
            })
            total_balance += balance
        
        return {
            'total_balance': total_balance,
            'wallet_count': len(wallets),
            'wallet_balances': wallet_balances
        }
    
    @staticmethod
    async def get_wallet_balance_with_history(wallet_id: int, days: int = 30) -> Dict[str, Any]:
        """Get wallet balance with recent transaction history"""
        current_balance = await db.get_wallet_balance(wallet_id)
        
        # Get recent transactions for this wallet
        # This would require a new method in database.py to get wallet-specific transactions
        # For now, we'll return just the current balance
        
        return {
            'wallet_id': wallet_id,
            'current_balance': current_balance,
            'recent_transactions': []  # Would be populated with actual transaction history
        }
    
    @staticmethod
    async def recalculate_all_balances(user_id: int) -> Dict[str, Any]:
        """Recalculate all wallet balances for a user"""
        wallets = await db.get_user_wallets(user_id)
        results = []
        
        for wallet in wallets:
            balance = await db.get_wallet_balance(wallet['id'])
            results.append({
                'wallet_id': wallet['id'],
                'wallet_name': wallet['name'],
                'balance': balance
            })
        
        return {
            'user_id': user_id,
            'wallets': results,
            'total_balance': sum(r['balance'] for r in results)
        }
    
    @staticmethod
    async def get_balance_alerts(user_id: int) -> List[Dict[str, Any]]:
        """Get balance alerts for low balances or unusual activity"""
        alerts = []
        wallets = await db.get_user_wallets(user_id)
        
        for wallet in wallets:
            balance = await db.get_wallet_balance(wallet['id'])
            
            # Check for low balance (example threshold)
            if balance < 0:
                alerts.append({
                    'type': 'negative_balance',
                    'wallet_id': wallet['id'],
                    'wallet_name': wallet['name'],
                    'balance': balance,
                    'message': f'Отрицательный баланс в кошельке "{wallet["name"]}"'
                })
            elif balance < 1000:  # Example threshold
                alerts.append({
                    'type': 'low_balance',
                    'wallet_id': wallet['id'],
                    'wallet_name': wallet['name'],
                    'balance': balance,
                    'message': f'Низкий баланс в кошельке "{wallet["name"]}"'
                })
        
        return alerts

# Global balance service instance
balance_service = BalanceService()