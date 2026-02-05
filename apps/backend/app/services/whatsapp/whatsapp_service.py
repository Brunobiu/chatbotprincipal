"""
Service para gerenciar instâncias do WhatsApp via Evolution API
"""
import requests
import logging
from sqlalchemy.orm import Session
from typing import Optional, Dict

from app.core.config import settings
from app.db.models.instancia_whatsapp import InstanciaWhatsApp, InstanciaStatus

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Service para integração com Evolution API"""
    
    @staticmethod
    def criar_instancia(db: Session, cliente_id: int) -> InstanciaWhatsApp:
        """
        Cria uma nova instância do WhatsApp para o cliente
        """
        # Verificar se já existe instância para este cliente
        instancia_existente = db.query(InstanciaWhatsApp).filter(
            InstanciaWhatsApp.cliente_id == cliente_id
        ).first()
        
        if instancia_existente:
            logger.info(f"Cliente {cliente_id} já possui instância: {instancia_existente.instance_id}")
            return instancia_existente
        
        # Gerar instance_id único
        instance_id = f"cliente_{cliente_id}"
        
        # Criar instância na Evolution API
        try:
            url = f"{settings.EVOLUTION_API_URL}/instance/create"
            headers = {
                "apikey": settings.AUTHENTICATION_API_KEY,
                "Content-Type": "application/json"
            }
            payload = {
                "instanceName": instance_id,
                "qrcode": True,
                "integration": "WHATSAPP-BAILEYS"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Instância criada na Evolution API: {instance_id}")
            
        except Exception as e:
            logger.error(f"Erro ao criar instância na Evolution API: {e}")
            raise Exception(f"Erro ao criar instância do WhatsApp: {str(e)}")
        
        # Salvar no banco
        instancia = InstanciaWhatsApp(
            cliente_id=cliente_id,
            instance_id=instance_id,
            status=InstanciaStatus.PENDENTE
        )
        db.add(instancia)
        db.commit()
        db.refresh(instancia)
        
        logger.info(f"Instância salva no banco: {instance_id}")
        return instancia
    
    @staticmethod
    def buscar_instancia(db: Session, cliente_id: int) -> Optional[InstanciaWhatsApp]:
        """
        Busca instância do cliente
        """
        return db.query(InstanciaWhatsApp).filter(
            InstanciaWhatsApp.cliente_id == cliente_id
        ).first()
    
    @staticmethod
    def obter_qrcode(instance_id: str) -> Optional[Dict]:
        """
        Obtém QR Code da instância
        """
        try:
            url = f"{settings.EVOLUTION_API_URL}/instance/connect/{instance_id}"
            headers = {
                "apikey": settings.AUTHENTICATION_API_KEY
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if "qrcode" in data or "base64" in data:
                return {
                    "qrcode": data.get("qrcode", {}).get("base64") or data.get("base64"),
                    "code": data.get("qrcode", {}).get("code") or data.get("code")
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter QR code: {e}")
            return None
    
    @staticmethod
    def obter_status(instance_id: str) -> Dict:
        """
        Obtém status da conexão da instância
        """
        try:
            url = f"{settings.EVOLUTION_API_URL}/instance/connectionState/{instance_id}"
            headers = {
                "apikey": settings.AUTHENTICATION_API_KEY
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            state = data.get("state", "close")
            
            # Mapear estado da Evolution para nosso enum
            if state == "open":
                status = InstanciaStatus.CONECTADA
            elif state == "close":
                status = InstanciaStatus.DESCONECTADA
            else:
                status = InstanciaStatus.PENDENTE
            
            return {
                "status": status.value,
                "state": state,
                "raw_data": data
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter status: {e}")
            return {
                "status": InstanciaStatus.ERRO.value,
                "state": "error",
                "error": str(e)
            }
    
    @staticmethod
    def atualizar_status(db: Session, instance_id: str, status: InstanciaStatus, numero: Optional[str] = None):
        """
        Atualiza status da instância no banco
        """
        instancia = db.query(InstanciaWhatsApp).filter(
            InstanciaWhatsApp.instance_id == instance_id
        ).first()
        
        if instancia:
            instancia.status = status
            if numero:
                instancia.numero = numero
            db.commit()
            db.refresh(instancia)
            logger.info(f"Status atualizado: {instance_id} -> {status.value}")
            return instancia
        
        return None
    
    @staticmethod
    def desconectar_instancia(instance_id: str) -> bool:
        """
        Desconecta instância do WhatsApp
        """
        try:
            url = f"{settings.EVOLUTION_API_URL}/instance/logout/{instance_id}"
            headers = {
                "apikey": settings.AUTHENTICATION_API_KEY
            }
            
            response = requests.delete(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            logger.info(f"Instância desconectada: {instance_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao desconectar instância: {e}")
            return False
