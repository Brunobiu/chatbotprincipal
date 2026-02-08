from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.db.models.cliente import Cliente, ClienteStatus
from app.db.models.uso_openai import UsoOpenAI
from app.db.models.ticket import Ticket
from app.db.models.conversa import Conversa
from app.db.models.mensagem import Mensagem


class RelatorioService:
    """Serviço para gerar relatórios"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== RELATÓRIO DE CLIENTES ====================
    
    def relatorio_clientes(
        self,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Gera relatório de clientes"""
        query = self.db.query(Cliente)
        
        if data_inicio:
            query = query.filter(Cliente.created_at >= data_inicio)
        if data_fim:
            query = query.filter(Cliente.created_at <= data_fim)
        if status:
            query = query.filter(Cliente.status == status)
        
        clientes = query.all()
        
        # Estatísticas
        total = len(clientes)
        por_status = {}
        for cliente in clientes:
            status_str = cliente.status.value if hasattr(cliente.status, 'value') else str(cliente.status)
            por_status[status_str] = por_status.get(status_str, 0) + 1
        
        return {
            "total": total,
            "por_status": por_status,
            "clientes": [
                {
                    "id": c.id,
                    "nome": c.nome,
                    "email": c.email,
                    "status": c.status.value if hasattr(c.status, 'value') else str(c.status),
                    "created_at": c.created_at.isoformat(),
                    "ultimo_login": c.ultimo_login.isoformat() if c.ultimo_login else None,
                    "total_mensagens": c.total_mensagens_enviadas
                } for c in clientes
            ]
        }
    
    # ==================== RELATÓRIO DE USO OPENAI ====================
    
    def relatorio_uso_openai(
        self,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        cliente_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Gera relatório de uso OpenAI"""
        query = self.db.query(UsoOpenAI)
        
        if data_inicio:
            query = query.filter(UsoOpenAI.data >= data_inicio)
        if data_fim:
            query = query.filter(UsoOpenAI.data <= data_fim)
        if cliente_id:
            query = query.filter(UsoOpenAI.cliente_id == cliente_id)
        
        registros = query.all()
        
        # Estatísticas
        total_tokens = sum(r.tokens_total for r in registros)
        total_custo = sum(r.custo_estimado for r in registros)
        total_mensagens = sum(r.mensagens_processadas for r in registros)
        
        # Por cliente
        por_cliente = {}
        for r in registros:
            if r.cliente_id not in por_cliente:
                por_cliente[r.cliente_id] = {
                    "tokens": 0,
                    "custo": 0,
                    "mensagens": 0
                }
            por_cliente[r.cliente_id]["tokens"] += r.tokens_total
            por_cliente[r.cliente_id]["custo"] += r.custo_estimado
            por_cliente[r.cliente_id]["mensagens"] += r.mensagens_processadas
        
        return {
            "total_tokens": total_tokens,
            "total_custo": round(total_custo, 2),
            "total_mensagens": total_mensagens,
            "por_cliente": por_cliente,
            "registros": [
                {
                    "cliente_id": r.cliente_id,
                    "data": r.data.isoformat(),
                    "tokens_total": r.tokens_total,
                    "custo_estimado": round(r.custo_estimado, 2),
                    "mensagens_processadas": r.mensagens_processadas,
                    "modelo": r.modelo
                } for r in registros
            ]
        }
    
    # ==================== RELATÓRIO DE TICKETS ====================
    
    def relatorio_tickets(
        self,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Gera relatório de tickets"""
        query = self.db.query(Ticket)
        
        if data_inicio:
            query = query.filter(Ticket.created_at >= data_inicio)
        if data_fim:
            query = query.filter(Ticket.created_at <= data_fim)
        if status:
            query = query.filter(Ticket.status == status)
        
        tickets = query.all()
        
        # Estatísticas
        total = len(tickets)
        por_status = {}
        por_categoria = {}
        ia_respondeu = 0
        
        for ticket in tickets:
            # Por status
            por_status[ticket.status] = por_status.get(ticket.status, 0) + 1
            
            # Por categoria
            if ticket.categoria:
                cat_nome = ticket.categoria.nome
                por_categoria[cat_nome] = por_categoria.get(cat_nome, 0) + 1
            
            # IA respondeu
            if ticket.ia_respondeu:
                ia_respondeu += 1
        
        return {
            "total": total,
            "por_status": por_status,
            "por_categoria": por_categoria,
            "ia_respondeu": ia_respondeu,
            "taxa_ia": round((ia_respondeu / total * 100) if total > 0 else 0, 2),
            "tickets": [
                {
                    "id": t.id,
                    "cliente_id": t.cliente_id,
                    "assunto": t.assunto,
                    "status": t.status,
                    "categoria": t.categoria.nome if t.categoria else None,
                    "ia_respondeu": t.ia_respondeu,
                    "created_at": t.created_at.isoformat(),
                    "resolvido_em": t.resolvido_em.isoformat() if t.resolvido_em else None
                } for t in tickets
            ]
        }
    
    # ==================== RELATÓRIO DE CONVERSAS ====================
    
    def relatorio_conversas(
        self,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        cliente_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Gera relatório de conversas"""
        query = self.db.query(Conversa)
        
        if data_inicio:
            query = query.filter(Conversa.created_at >= data_inicio)
        if data_fim:
            query = query.filter(Conversa.created_at <= data_fim)
        if cliente_id:
            query = query.filter(Conversa.cliente_id == cliente_id)
        
        conversas = query.all()
        
        # Estatísticas
        total = len(conversas)
        por_estado = {}
        
        for conversa in conversas:
            por_estado[conversa.estado] = por_estado.get(conversa.estado, 0) + 1
        
        # Contar mensagens
        mensagens_query = self.db.query(Mensagem)
        if data_inicio:
            mensagens_query = mensagens_query.filter(Mensagem.timestamp >= data_inicio)
        if data_fim:
            mensagens_query = mensagens_query.filter(Mensagem.timestamp <= data_fim)
        
        total_mensagens = mensagens_query.count()
        
        return {
            "total_conversas": total,
            "total_mensagens": total_mensagens,
            "por_estado": por_estado,
            "conversas": [
                {
                    "id": c.id,
                    "cliente_id": c.cliente_id,
                    "numero_usuario": c.numero_usuario,
                    "estado": c.estado,
                    "created_at": c.created_at.isoformat(),
                    "updated_at": c.updated_at.isoformat()
                } for c in conversas
            ]
        }
    
    # ==================== RELATÓRIO GERAL ====================
    
    def relatorio_geral(
        self,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Gera relatório geral do sistema"""
        
        # Clientes
        clientes_query = self.db.query(Cliente)
        if data_inicio:
            clientes_query = clientes_query.filter(Cliente.created_at >= data_inicio)
        if data_fim:
            clientes_query = clientes_query.filter(Cliente.created_at <= data_fim)
        
        total_clientes = clientes_query.count()
        clientes_ativos = clientes_query.filter(Cliente.status == ClienteStatus.ATIVO).count()
        
        # Uso OpenAI
        uso_query = self.db.query(UsoOpenAI)
        if data_inicio:
            uso_query = uso_query.filter(UsoOpenAI.data >= data_inicio)
        if data_fim:
            uso_query = uso_query.filter(UsoOpenAI.data <= data_fim)
        
        total_custo = self.db.query(func.sum(UsoOpenAI.custo_estimado)).filter(
            and_(
                UsoOpenAI.data >= data_inicio if data_inicio else True,
                UsoOpenAI.data <= data_fim if data_fim else True
            )
        ).scalar() or 0
        
        # Tickets
        tickets_query = self.db.query(Ticket)
        if data_inicio:
            tickets_query = tickets_query.filter(Ticket.created_at >= data_inicio)
        if data_fim:
            tickets_query = tickets_query.filter(Ticket.created_at <= data_fim)
        
        total_tickets = tickets_query.count()
        tickets_resolvidos = tickets_query.filter(Ticket.status == 'resolvido').count()
        
        # Conversas
        conversas_query = self.db.query(Conversa)
        if data_inicio:
            conversas_query = conversas_query.filter(Conversa.created_at >= data_inicio)
        if data_fim:
            conversas_query = conversas_query.filter(Conversa.created_at <= data_fim)
        
        total_conversas = conversas_query.count()
        
        return {
            "periodo": {
                "inicio": data_inicio.isoformat() if data_inicio else None,
                "fim": data_fim.isoformat() if data_fim else None
            },
            "clientes": {
                "total": total_clientes,
                "ativos": clientes_ativos
            },
            "uso_openai": {
                "custo_total": round(total_custo, 2)
            },
            "tickets": {
                "total": total_tickets,
                "resolvidos": tickets_resolvidos,
                "taxa_resolucao": round((tickets_resolvidos / total_tickets * 100) if total_tickets > 0 else 0, 2)
            },
            "conversas": {
                "total": total_conversas
            }
        }
