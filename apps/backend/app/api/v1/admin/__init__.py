# Admin API endpoints
from fastapi import APIRouter
from .auth import router as auth_router
from .dashboard import router as dashboard_router
from .clientes import router as clientes_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Admin Auth"])
router.include_router(dashboard_router, prefix="/dashboard", tags=["Admin Dashboard"])
router.include_router(clientes_router, tags=["Admin Clientes"])
