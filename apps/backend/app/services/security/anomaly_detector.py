"""
Detector de Anomalias (FASE 5)
Detecta comportamento suspeito e bloqueia automaticamente
"""
from datetime import datetime, timedelta
from typing import Tuple, List
import redis
import logging
import json

logger = logging.getLogger("security")


class AnomalyDetector:
    """Detecta padrões suspeitos de comportamento"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def track_request(self, ip: str, endpoint: str, status_code: int = 200):
        """
        Rastreia requisição
        
        Args:
            ip: Endereço IP
            endpoint: Endpoint acessado
            status_code: Código de status HTTP
        """
        key = f"requests:{ip}"
        
        # Adicionar requisição com timestamp
        request_data = json.dumps({
            "endpoint": endpoint,
            "status": status_code,
            "timestamp": datetime.utcnow().timestamp()
        })
        
        self.redis.lpush(key, request_data)
        
        # Manter apenas últimos 100 requests
        self.redis.ltrim(key, 0, 99)
        
        # Expirar em 1 hora
        self.redis.expire(key, 3600)
    
    def get_recent_requests(self, ip: str, minutes: int = 5) -> List[dict]:
        """
        Obtém requisições recentes de um IP
        
        Args:
            ip: Endereço IP
            minutes: Janela de tempo em minutos
            
        Returns:
            Lista de requisições
        """
        key = f"requests:{ip}"
        requests = self.redis.lrange(key, 0, -1)
        
        if not requests:
            return []
        
        cutoff = datetime.utcnow().timestamp() - (minutes * 60)
        recent = []
        
        for req in requests:
            try:
                data = json.loads(req.decode('utf-8'))
                if data['timestamp'] > cutoff:
                    recent.append(data)
            except:
                continue
        
        return recent
    
    def is_suspicious(self, ip: str) -> Tuple[bool, str]:
        """
        Detecta padrões suspeitos
        
        Args:
            ip: Endereço IP
            
        Returns:
            (is_suspicious, reason)
        """
        # Obter requisições dos últimos 5 minutos
        recent = self.get_recent_requests(ip, minutes=5)
        
        if not recent:
            return False, ""
        
        # REGRA 1: Muitas requisições em curto período (DDoS/Brute Force)
        if len(recent) > 100:
            return True, f"Muitas requisições em 5 minutos ({len(recent)} requests)"
        
        # REGRA 2: Muitos endpoints diferentes (Scanning/Reconnaissance)
        unique_endpoints = set([r['endpoint'] for r in recent])
        if len(unique_endpoints) > 30:
            return True, f"Scanning de endpoints ({len(unique_endpoints)} endpoints diferentes)"
        
        # REGRA 3: Muitos erros 404 (Path Traversal/Directory Scanning)
        errors_404 = [r for r in recent if r['status'] == 404]
        if len(errors_404) > 20:
            return True, f"Muitos erros 404 ({len(errors_404)} tentativas)"
        
        # REGRA 4: Muitos erros 401/403 (Brute Force de autenticação)
        auth_errors = [r for r in recent if r['status'] in [401, 403]]
        if len(auth_errors) > 10:
            return True, f"Muitas falhas de autenticação ({len(auth_errors)} tentativas)"
        
        # REGRA 5: Muitos erros 500 (Tentando explorar vulnerabilidades)
        server_errors = [r for r in recent if r['status'] >= 500]
        if len(server_errors) > 15:
            return True, f"Muitos erros de servidor ({len(server_errors)} erros)"
        
        return False, ""
    
    def get_block_duration(self, ip: str) -> int:
        """
        Calcula duração do bloqueio baseado em histórico
        
        Args:
            ip: Endereço IP
            
        Returns:
            Duração em minutos
        """
        # Verificar quantas vezes já foi bloqueado
        block_count_key = f"block_count:{ip}"
        block_count = self.redis.get(block_count_key)
        
        if block_count:
            count = int(block_count)
        else:
            count = 0
        
        # Incrementar contador
        self.redis.incr(block_count_key)
        self.redis.expire(block_count_key, 86400)  # 24 horas
        
        # Bloqueio progressivo
        durations = [15, 30, 60, 120, 240]  # 15min, 30min, 1h, 2h, 4h
        
        if count < len(durations):
            return durations[count]
        else:
            return None  # Permanente após 5 bloqueios
    
    def check_and_block(self, db, ip: str) -> Tuple[bool, str]:
        """
        Verifica anomalia e bloqueia se necessário
        
        Args:
            db: Sessão do banco
            ip: Endereço IP
            
        Returns:
            (was_blocked, reason)
        """
        is_suspicious, reason = self.is_suspicious(ip)
        
        if is_suspicious:
            from app.services.security.ip_blocker import IPBlocker
            
            # Calcular duração do bloqueio
            duration = self.get_block_duration(ip)
            
            # Bloquear IP
            IPBlocker.block_ip(
                db=db,
                ip=ip,
                reason=reason,
                duration_minutes=duration,
                details={"detected_by": "anomaly_detector", "timestamp": datetime.utcnow().isoformat()}
            )
            
            return True, reason
        
        return False, ""
    
    def clear_tracking(self, ip: str):
        """
        Limpa rastreamento de um IP
        
        Args:
            ip: Endereço IP
        """
        key = f"requests:{ip}"
        self.redis.delete(key)
        
        block_count_key = f"block_count:{ip}"
        self.redis.delete(block_count_key)
