"""
Serviço de Monitoramento de Sistema
Verifica saúde dos serviços e métricas de performance
"""
import time
import psutil
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy import text
from sqlalchemy.orm import Session
import redis.asyncio as redis
import httpx
from app.core.config import settings


class SistemaService:
    """Serviço para monitorar saúde do sistema"""
    
    # Armazenar métricas de requests em memória (simplificado)
    _request_times: List[float] = []
    _request_errors: List[datetime] = []
    _max_samples = 1000
    
    @classmethod
    def registrar_request(cls, tempo_resposta: float, erro: bool = False):
        """Registra tempo de resposta de uma request"""
        cls._request_times.append(tempo_resposta)
        if len(cls._request_times) > cls._max_samples:
            cls._request_times.pop(0)
        
        if erro:
            cls._request_errors.append(datetime.utcnow())
            # Manter apenas últimos 5 minutos
            cinco_min_atras = datetime.utcnow() - timedelta(minutes=5)
            cls._request_errors = [e for e in cls._request_errors if e > cinco_min_atras]
    
    @staticmethod
    def verificar_postgres(db: Session) -> Dict[str, Any]:
        """Verifica saúde do PostgreSQL"""
        try:
            inicio = time.time()
            # Executar query simples
            db.execute(text("SELECT 1"))
            latencia = (time.time() - inicio) * 1000  # ms
            
            return {
                "status": "conectado",
                "latencia_ms": round(latencia, 2),
                "saudavel": latencia < 100
            }
        except Exception as e:
            return {
                "status": "erro",
                "erro": str(e),
                "saudavel": False
            }
    
    @staticmethod
    async def verificar_redis() -> Dict[str, Any]:
        """Verifica saúde do Redis"""
        try:
            r = redis.from_url(settings.REDIS_URL, decode_responses=True)
            inicio = time.time()
            await r.ping()
            latencia = (time.time() - inicio) * 1000
            
            info = await r.info("memory")
            memoria_usada_mb = info.get("used_memory", 0) / (1024 * 1024)
            
            await r.close()
            
            return {
                "status": "conectado",
                "latencia_ms": round(latencia, 2),
                "memoria_usada_mb": round(memoria_usada_mb, 2),
                "saudavel": latencia < 50
            }
        except Exception as e:
            return {
                "status": "erro",
                "erro": str(e),
                "saudavel": False
            }
    
    @staticmethod
    async def verificar_chromadb() -> Dict[str, Any]:
        """Verifica saúde do ChromaDB"""
        try:
            url = f"http://{settings.CHROMA_HOST}:{settings.CHROMA_PORT}/api/v1/heartbeat"
            async with httpx.AsyncClient(timeout=5.0) as client:
                inicio = time.time()
                response = await client.get(url)
                latencia = (time.time() - inicio) * 1000
                
                if response.status_code == 200:
                    # Tentar contar coleções
                    try:
                        collections_url = f"http://{settings.CHROMA_HOST}:{settings.CHROMA_PORT}/api/v1/collections"
                        coll_response = await client.get(collections_url)
                        colecoes = len(coll_response.json()) if coll_response.status_code == 200 else 0
                    except:
                        colecoes = 0
                    
                    return {
                        "status": "conectado",
                        "latencia_ms": round(latencia, 2),
                        "colecoes": colecoes,
                        "saudavel": True
                    }
                else:
                    return {
                        "status": "erro",
                        "erro": f"Status {response.status_code}",
                        "saudavel": False
                    }
        except Exception as e:
            return {
                "status": "erro",
                "erro": str(e),
                "saudavel": False
            }
    
    @staticmethod
    async def verificar_evolution_api() -> Dict[str, Any]:
        """Verifica saúde da Evolution API"""
        try:
            # Tentar buscar instâncias
            url = f"{settings.EVOLUTION_API_URL}/instance/fetchInstances"
            headers = {"apikey": settings.EVOLUTION_AUTHENTICATION_API_KEY}
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                inicio = time.time()
                response = await client.get(url, headers=headers)
                latencia = (time.time() - inicio) * 1000
                
                if response.status_code == 200:
                    instancias = response.json()
                    total = len(instancias) if isinstance(instancias, list) else 0
                    conectadas = sum(1 for i in instancias if isinstance(i, dict) and i.get("state") == "open") if isinstance(instancias, list) else 0
                    
                    return {
                        "status": "conectado",
                        "latencia_ms": round(latencia, 2),
                        "instancias_total": total,
                        "instancias_conectadas": conectadas,
                        "saudavel": True
                    }
                else:
                    return {
                        "status": "erro",
                        "erro": f"Status {response.status_code}",
                        "saudavel": False
                    }
        except Exception as e:
            return {
                "status": "erro",
                "erro": str(e),
                "saudavel": False
            }
    
    @staticmethod
    async def verificar_openai() -> Dict[str, Any]:
        """Verifica saúde da OpenAI API"""
        try:
            # Fazer uma chamada simples para verificar API key
            url = "https://api.openai.com/v1/models"
            headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                inicio = time.time()
                response = await client.get(url, headers=headers)
                latencia = (time.time() - inicio) * 1000
                
                if response.status_code == 200:
                    return {
                        "status": "conectado",
                        "latencia_ms": round(latencia, 2),
                        "api_key_valida": True,
                        "saudavel": True
                    }
                else:
                    return {
                        "status": "erro",
                        "erro": f"Status {response.status_code}",
                        "api_key_valida": False,
                        "saudavel": False
                    }
        except Exception as e:
            return {
                "status": "erro",
                "erro": str(e),
                "saudavel": False
            }
    
    @classmethod
    async def obter_saude_completa(cls, db: Session) -> Dict[str, Any]:
        """Retorna status de saúde de todos os serviços"""
        postgres = cls.verificar_postgres(db)
        redis_status = await cls.verificar_redis()
        chromadb = await cls.verificar_chromadb()
        evolution = await cls.verificar_evolution_api()
        openai = await cls.verificar_openai()
        
        # Status geral
        todos_saudaveis = all([
            postgres.get("saudavel"),
            redis_status.get("saudavel"),
            chromadb.get("saudavel"),
            evolution.get("saudavel"),
            openai.get("saudavel")
        ])
        
        return {
            "status_geral": "saudavel" if todos_saudaveis else "problemas_detectados",
            "timestamp": datetime.utcnow().isoformat(),
            "servicos": {
                "postgres": postgres,
                "redis": redis_status,
                "chromadb": chromadb,
                "evolution_api": evolution,
                "openai": openai
            }
        }
    
    @classmethod
    def obter_metricas_sistema(cls) -> Dict[str, Any]:
        """Retorna métricas de uso do sistema"""
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memória
        memoria = psutil.virtual_memory()
        memoria_usada_gb = memoria.used / (1024 ** 3)
        memoria_total_gb = memoria.total / (1024 ** 3)
        memoria_percent = memoria.percent
        
        # Disco
        disco = psutil.disk_usage('/')
        disco_usado_gb = disco.used / (1024 ** 3)
        disco_total_gb = disco.total / (1024 ** 3)
        disco_percent = disco.percent
        
        # Métricas de requests
        tempo_resposta_medio = sum(cls._request_times) / len(cls._request_times) if cls._request_times else 0
        requests_por_minuto = len(cls._request_times)  # Aproximado
        
        # Erros por minuto (últimos 5 min)
        erros_por_minuto = len(cls._request_errors) / 5 if cls._request_errors else 0
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu": {
                "uso_percent": round(cpu_percent, 2),
                "alerta": cpu_percent > 80
            },
            "memoria": {
                "usado_gb": round(memoria_usada_gb, 2),
                "total_gb": round(memoria_total_gb, 2),
                "uso_percent": round(memoria_percent, 2),
                "alerta": memoria_percent > 85
            },
            "disco": {
                "usado_gb": round(disco_usado_gb, 2),
                "total_gb": round(disco_total_gb, 2),
                "uso_percent": round(disco_percent, 2),
                "alerta": disco_percent > 90
            },
            "performance": {
                "tempo_resposta_medio_ms": round(tempo_resposta_medio * 1000, 2),
                "requests_por_minuto": requests_por_minuto,
                "erros_por_minuto": round(erros_por_minuto, 2),
                "alerta": tempo_resposta_medio > 1.0 or erros_por_minuto > 10
            }
        }
