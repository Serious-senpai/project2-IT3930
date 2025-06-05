from .detected import router as detected_router
from .refutations import router as refutations_router
from .transactions import router as transactions_router
from .users import router as users_router
from .vehicles import router as vehicles_router
from .violations import router as violations_router


__all__ = ("routers",)
routers = (
    detected_router,
    refutations_router,
    transactions_router,
    users_router,
    vehicles_router,
    violations_router,
)
