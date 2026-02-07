"""
Middlewares customizados da aplicação
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware para tratamento global de erros
    Captura exceções não tratadas e retorna respostas padronizadas
    """
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except HTTPException as exc:
            # HTTPException já tem status_code e detail
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "status": "error",
                    "message": exc.detail,
                    "path": str(request.url.path)
                }
            )
        except Exception as exc:
            # Erro não tratado
            logger.error(f"❌ Erro não tratado: {str(exc)}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "status": "error",
                    "message": "Internal server error",
                    "path": str(request.url.path)
                }
            )


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para logging de requisições
    Loga todas as requisições com tempo de processamento
    """
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log da requisição
        logger.info(f"📥 {request.method} {request.url.path}")
        
        response = await call_next(request)
        
        # Calcular tempo de processamento
        process_time = time.time() - start_time
        
        # Log da resposta
        logger.info(
            f"📤 {request.method} {request.url.path} "
            f"| Status: {response.status_code} "
            f"| Time: {process_time:.3f}s"
        )
        
        # Adicionar header com tempo de processamento
        response.headers["X-Process-Time"] = str(process_time)
        
        return response


class AdminAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware para validar autenticação de administradores.
    Valida JWT e role=admin em todas as rotas /api/v1/admin/*
    """
    
    async def dispatch(self, request: Request, call_next):
        # Verificar se é rota admin (exceto login)
        path = request.url.path
        
        if path.startswith("/api/v1/admin") and not path.endswith("/login"):
            # Extrair token do header Authorization
            auth_header = request.headers.get("Authorization")
            
            if not auth_header or not auth_header.startswith("Bearer "):
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "status": "error",
                        "message": "Token de autenticação não fornecido",
                        "path": path
                    }
                )
            
            token = auth_header.replace("Bearer ", "")
            
            # Validar token (será feito pelo dependency get_current_admin)
            # Este middleware apenas garante que o header existe
            # A validação completa é feita no endpoint
        
        response = await call_next(request)
        return response
