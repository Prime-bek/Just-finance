from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from bot.database import db
import logging

logger = logging.getLogger(__name__)

class UserCheckMiddleware(BaseMiddleware):
    """Middleware to check user status and block access if needed"""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # Handle both Message and CallbackQuery
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        
        if not user_id:
            return await handler(event, data)
        
        # Get user from database
        user = await db.get_user(user_id)
        
        if not user:
            # New user - let them register
            return await handler(event, data)
        
        # Check if user is blocked
        if user['status'] == 'blocked':
            logger.warning(f"Blocked user {user_id} attempted to use the bot")
            
            if isinstance(event, Message):
                await event.answer("❌ Вы заблокированы и не можете использовать этого бота.")
            elif isinstance(event, CallbackQuery):
                await event.answer("❌ Вы заблокированы.", show_alert=True)
            
            return  # Don't process the event
        
        # Update last activity for active users
        await db.update_user_activity(user_id)
        
        # Continue with the handler
        return await handler(event, data)