from typing import Dict, List, Any
from datetime import datetime, timedelta
from bot.database import db

class StatisticsService:
    
    @staticmethod
    async def get_user_statistics(user_id: int, period: str = 'month') -> Dict[str, Any]:
        """Get comprehensive user statistics for a given period"""
        stats = await db.get_user_stats(user_id, period)
        
        # Get wallet balances
        wallets = await db.get_user_wallets(user_id)
        wallet_balances = []
        total_balance = 0
        
        for wallet in wallets:
            balance = await db.get_wallet_balance(wallet['id'])
            wallet_balances.append({
                'name': wallet['name'],
                'balance': balance,
                'type': wallet['type'],
                'is_main': wallet['is_main']
            })
            total_balance += balance
        
        # Get recent transactions
        recent_transactions = await db.get_user_transactions(user_id, limit=5)
        
        # Calculate daily averages
        days_in_period = 30 if period == 'month' else 7
        avg_daily_income = stats['income'] / days_in_period if days_in_period > 0 else 0
        avg_daily_expenses = stats['expenses'] / days_in_period if days_in_period > 0 else 0
        
        return {
            'period': period,
            'income': stats['income'],
            'expenses': stats['expenses'],
            'balance': stats['balance'],
            'total_balance': total_balance,
            'wallet_balances': wallet_balances,
            'top_expense_category': stats['top_expense_category'],
            'category_stats': stats['category_stats'],
            'recent_transactions': recent_transactions,
            'avg_daily_income': avg_daily_income,
            'avg_daily_expenses': avg_daily_expenses
        }
    
    @staticmethod
    async def get_category_breakdown(user_id: int, period: str = 'month') -> Dict[str, Any]:
        """Get detailed category breakdown"""
        stats = await db.get_user_stats(user_id, period)
        
        # Calculate percentages
        category_percentages = {}
        total_expenses = stats['expenses']
        
        if total_expenses > 0:
            for category, amount in stats['category_stats'].items():
                percentage = (amount / total_expenses) * 100
                category_percentages[category] = {
                    'amount': amount,
                    'percentage': percentage
                }
        
        return {
            'total_expenses': total_expenses,
            'category_breakdown': category_percentages,
            'period': period
        }
    
    @staticmethod
    async def get_trends(user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get spending and income trends over time"""
        # This would require more complex queries to get daily aggregations
        # For now, we'll return basic trend data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get daily transaction summaries
        daily_data = await StatisticsService._get_daily_summaries(user_id, start_date, end_date)
        
        # Calculate trend indicators
        if len(daily_data) >= 2:
            recent_avg = sum(day['expenses'] for day in daily_data[-7:]) / 7
            previous_avg = sum(day['expenses'] for day in daily_data[-14:-7]) / 7
            
            if previous_avg > 0:
                trend_percentage = ((recent_avg - previous_avg) / previous_avg) * 100
            else:
                trend_percentage = 0
            
            trend_direction = 'increasing' if trend_percentage > 5 else 'decreasing' if trend_percentage < -5 else 'stable'
        else:
            trend_percentage = 0
            trend_direction = 'stable'
        
        return {
            'daily_data': daily_data,
            'trend_percentage': trend_percentage,
            'trend_direction': trend_direction,
            'period_days': days
        }
    
    @staticmethod
    async def _get_daily_summaries(user_id: int, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get daily transaction summaries (simplified implementation)"""
        # This is a simplified version - in a real implementation,
        # you'd want to query the database for daily aggregations
        stats = await db.get_user_stats(user_id, 'month')
        
        # Create mock daily data for demonstration
        daily_data = []
        current_date = start_date
        
        while current_date <= end_date:
            # Simple mock data - in reality, this would come from database queries
            daily_income = stats['income'] / 30  # Rough daily average
            daily_expenses = stats['expenses'] / 30  # Rough daily average
            
            daily_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'income': daily_income,
                'expenses': daily_expenses,
                'balance': daily_income - daily_expenses
            })
            
            current_date += timedelta(days=1)
        
        return daily_data

# Global statistics service instance
statistics_service = StatisticsService()