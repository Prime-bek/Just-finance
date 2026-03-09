from .start import router as start_router
from .wallets import router as wallets_router
from .transactions import router as transactions_router
from .stats import router as stats_router
from .history import router as history_router
from .settings import router as settings_router
from .admin import router as admin_router

# Export all routers
__all__ = [
    'start_router',
    'wallets_router', 
    'transactions_router',
    'stats_router',
    'history_router',
    'settings_router',
    'admin_router'
]