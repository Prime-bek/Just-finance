import time
from typing import Dict, Callable, Awaitable, Any
from collections import defaultdict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
import logging

logger = logging.getLogger(__name__)

class ThrottlingMiddleware(BaseMiddleware):
    """Rate limiting middleware to prevent spam"""
    
    def __init__(self, rate_limit: float = 0.5):
        self.rate_limit = rate_limit  # Minimum time between messages (seconds)
        self.user_last_message: Dict[int, float] = defaultdict(float)
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user_id = None
        
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        
        if not user_id:
            return await handler(event, data)
        
        current_time = time.time()
        last_message_time = self.user_last_message[user_id]
        
        # Check if enough time has passed
        if current_time - last_message_time < self.rate_limit:
            # Too fast - ignore this message
            logger.warning(f"Rate limit exceeded for user {user_id}")
            
            if isinstance(event, Message):
                await event.answer("⏳ Пожалуйста, не спамьте. Подождите немного.")
            elif isinstance(event, CallbackQuery):
                await event.answer("⏳ Слишком быстро! Подождите немного.", show_alert=True)
            
            return  # Don't process the event
        
        # Update last message time
        self.user_last_message[user_id] = current_time
        
        # Continue with the handler
        return await handler(event, data)