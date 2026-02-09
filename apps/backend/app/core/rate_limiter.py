"""
Rate Limiter para proteção contra força bruta (FASE 1)
"""
from datetime import datetime, timedelta
from typing import Dict, Tuple
from collections import defaultdict
import threading


class RateLimiter:
    """
    Rate limiter simples em memória
    Para produção, considere usar Redis
    """
    
    def __init__(self):
        self._requests: Dict[str, list] = defaultdict(list)
        self._lock = threading.Lock()
    
    def is_allowed(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> Tuple[bool, int]:
        """
        Verifica se a requisição é permitida
        
        Args:
            key: Chave única (ex: IP, email)
            max_requests: Número máximo de requisições
            window_seconds: Janela de tempo em segundos
            
        Returns:
            Tupla (permitido, tentativas_restantes)
        """
        with self._lock:
            now = datetime.utcnow()
            cutoff = now - timedelta(seconds=window_seconds)
            
            # Remover requisições antigas
            self._requests[key] = [
                req_time for req_time in self._requests[key]
                if req_time > cutoff
            ]
            
            # Verificar se atingiu o limite
            if len(self._requests[key]) >= max_requests:
                return False, 0
            
            # Adicionar nova requisição
            self._requests[key].append(now)
            
            remaining = max_requests - len(self._requests[key])
            return True, remaining
    
    def reset(self, key: str):
        """
        Reseta o contador para uma chave
        
        Args:
            key: Chave a resetar
        """
        with self._lock:
            if key in self._requests:
                del self._requests[key]
    
    def cleanup_old_entries(self, max_age_seconds: int = 3600):
        """
        Remove entradas antigas para liberar memória
        
        Args:
            max_age_seconds: Idade máxima em segundos
        """
        with self._lock:
            now = datetime.utcnow()
            cutoff = now - timedelta(seconds=max_age_seconds)
            
            keys_to_delete = []
            for key, requests in self._requests.items():
                # Filtrar requisições antigas
                self._requests[key] = [
                    req_time for req_time in requests
                    if req_time > cutoff
                ]
                
                # Marcar para deletar se vazio
                if not self._requests[key]:
                    keys_to_delete.append(key)
            
            # Deletar chaves vazias
            for key in keys_to_delete:
                del self._requests[key]


# Instância global do rate limiter
rate_limiter = RateLimiter()
