from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.models.admin import NotificacaoAdmin


class NotificacaoService:
    """Serviço para gerenciar notificações do admin"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def criar_notificacao(
        self,
        admin_id: int,
        tipo: str,
        titulo: str,
        mensagem: str,
        prioridade: str = "normal",
        data: Optional[Dict] = None
    ) -> NotificacaoAdmin:
        """
        Cria uma nova notificação para o admin.
        
        Tipos disponíveis:
        - novo_cliente
        - pagamento_recusado
        - plano_expirado
        - novo_ticket
        - alto_uso_openai
        - tentativa_invasao
        
        Prioridades:
        - baixa
        - normal
        - alta
        - urgente
        """
        notificacao = NotificacaoAdmin(
            admin_id=admin_id,
            tipo=tipo,
            titulo=titulo,
            mensagem=mensagem,
            prioridade=prioridade,
            data=data or {}
        )
        
        self.db.add(notificacao)
        self.db.commit()
        self.db.refresh(notificacao)
        
        return notificacao
    
    def listar_notificacoes(
        self,
        admin_id: int,
        limit: int = 50,
        offset: int = 0,
        apenas_nao_lidas: bool = False
    ) -> tuple[List[NotificacaoAdmin], int]:
        """Lista notificações do admin"""
        query = self.db.query(NotificacaoAdmin).filter(
            NotificacaoAdmin.admin_id == admin_id
        )
        
        if apenas_nao_lidas:
            query = query.filter(NotificacaoAdmin.lida == False)
        
        total = query.count()
        notificacoes = query.order_by(
            desc(NotificacaoAdmin.created_at)
        ).limit(limit).offset(offset).all()
        
        return notificacoes, total
    
    def contar_nao_lidas(self, admin_id: int) -> int:
        """Conta notificações não lidas"""
        return self.db.query(NotificacaoAdmin).filter(
            NotificacaoAdmin.admin_id == admin_id,
            NotificacaoAdmin.lida == False
        ).count()
    
    def marcar_como_lida(self, notificacao_id: int, admin_id: int) -> bool:
        """Marca uma notificação como lida"""
        notificacao = self.db.query(NotificacaoAdmin).filter(
            NotificacaoAdmin.id == notificacao_id,
            NotificacaoAdmin.admin_id == admin_id
        ).first()
        
        if not notificacao:
            return False
        
        notificacao.lida = True
        self.db.commit()
        
        return True
    
    def marcar_todas_como_lidas(self, admin_id: int) -> int:
        """Marca todas as notificações como lidas"""
        count = self.db.query(NotificacaoAdmin).filter(
            NotificacaoAdmin.admin_id == admin_id,
            NotificacaoAdmin.lida == False
        ).update({"lida": True})
        
        self.db.commit()
        
        return count
    
    # ==================== HELPERS PARA CRIAR NOTIFICAÇÕES ====================
    
    @staticmethod
    def notificar_novo_cliente(db: Session, admin_id: int, cliente_id: int, cliente_email: str):
        """Cria notificação de novo cliente"""
        service = NotificacaoService(db)
        return service.criar_notificacao(
            admin_id=admin_id,
            tipo="novo_cliente",
            titulo="Novo Cliente Cadastrado",
            mensagem=f"Cliente {cliente_email} acabou de se cadastrar",
            prioridade="normal",
            data={"cliente_id": cliente_id, "email": cliente_email}
        )
    
    @staticmethod
    def notificar_pagamento_recusado(db: Session, admin_id: int, cliente_id: int, cliente_email: str, motivo: str):
        """Cria notificação de pagamento recusado"""
        service = NotificacaoService(db)
        return service.criar_notificacao(
            admin_id=admin_id,
            tipo="pagamento_recusado",
            titulo="Pagamento Recusado",
            mensagem=f"Pagamento do cliente {cliente_email} foi recusado: {motivo}",
            prioridade="alta",
            data={"cliente_id": cliente_id, "email": cliente_email, "motivo": motivo}
        )
    
    @staticmethod
    def notificar_plano_expirado(db: Session, admin_id: int, cliente_id: int, cliente_email: str):
        """Cria notificação de plano expirado"""
        service = NotificacaoService(db)
        return service.criar_notificacao(
            admin_id=admin_id,
            tipo="plano_expirado",
            titulo="Plano Expirado",
            mensagem=f"Plano do cliente {cliente_email} expirou",
            prioridade="alta",
            data={"cliente_id": cliente_id, "email": cliente_email}
        )
    
    @staticmethod
    def notificar_novo_ticket(db: Session, admin_id: int, ticket_id: int, cliente_email: str, assunto: str):
        """Cria notificação de novo ticket"""
        service = NotificacaoService(db)
        return service.criar_notificacao(
            admin_id=admin_id,
            tipo="novo_ticket",
            titulo="Novo Ticket de Suporte",
            mensagem=f"Cliente {cliente_email} abriu ticket: {assunto}",
            prioridade="normal",
            data={"ticket_id": ticket_id, "email": cliente_email, "assunto": assunto}
        )
    
    @staticmethod
    def notificar_alto_uso_openai(db: Session, admin_id: int, cliente_id: int, cliente_email: str, custo_total: float):
        """Cria notificação de alto uso OpenAI"""
        service = NotificacaoService(db)
        return service.criar_notificacao(
            admin_id=admin_id,
            tipo="alto_uso_openai",
            titulo="Alto Uso de Créditos OpenAI",
            mensagem=f"Cliente {cliente_email} gastou ${custo_total:.2f} em créditos OpenAI",
            prioridade="alta",
            data={"cliente_id": cliente_id, "email": cliente_email, "custo_total": custo_total}
        )
    
    @staticmethod
    def notificar_tentativa_invasao(db: Session, admin_id: int, ip: str, tentativas: int):
        """Cria notificação de tentativa de invasão"""
        service = NotificacaoService(db)
        return service.criar_notificacao(
            admin_id=admin_id,
            tipo="tentativa_invasao",
            titulo="Tentativa de Invasão Detectada",
            mensagem=f"IP {ip} teve {tentativas} tentativas de login falhadas",
            prioridade="urgente",
            data={"ip": ip, "tentativas": tentativas}
        )
