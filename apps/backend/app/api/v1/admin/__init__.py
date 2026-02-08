# Admin API endpoints
from fastapi import APIRouter
from .auth import router as auth_router
from .dashboard import router as dashboard_router
from .clientes import router as clientes_router
from .uso import router as uso_router
from .tickets import router as tickets_router
from .tutoriais import router as tutoriais_router
from .avisos import router as avisos_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Admin Auth"])
router.include_router(dashboard_router, prefix="/dashboard", tags=["Admin Dashboard"])
router.include_router(clientes_router, tags=["Admin Clientes"])
router.include_router(uso_router, tags=["Admin Uso OpenAI"])
router.include_router(tickets_router, prefix="/tickets", tags=["Admin Tickets"])
router.include_router(tutoriais_router, prefix="/tutoriais", tags=["Admin Tutoriais"])
router.include_router(avisos_router, prefix="/avisos", tags=["Admin Avisos"])
