"""
Serviço de Histórico Completo do Cliente
Agrega todos os dados de um cliente em um único endpoint
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func
import stripe

from app.core.config import settings
from app.db.models.cliente import Cliente
from app.db.models.conversa import Conversa
from app.db.models.mensagem import Mensagem
from app.db.models.ticket import Ticket, TicketMensagem
from app.db.models.uso_openai import UsoOpenAI
from app.db.models.admin import AuditLog

# Configurar Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class HistoricoService:
    """Serviço para obter histórico completo do cliente"""
    
    @staticmethod
    def obter_historico_completo(
        db: Session,
        cliente_id: int
    ) -> Dict[str, Any]:
        """
        Obtém histórico completo do cliente incluindo:
        - Dados cadastrais
        - Histórico de pagamentos (Stripe)
        - Conversas WhatsApp (últimas 100)
        - Tickets abertos/resolvidos
        - Uso OpenAI (últimos 30 dias)
        - Logins (últimos 30 dias via logs)
        - Timeline de eventos
        """
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        
        if not cliente:
            return {"erro": "Cliente não encontrado"}
        
        # 1. Dados Cadastrais
        dados_cadastrais = {
            "id": cliente.id,
            "nome": cliente.nome,
            "nome_empresa": cliente.nome_empresa,
            "email": cliente.email,
            "telefone": cliente.telefone,
            "status": cliente.status.value,
            "ultimo_login": cliente.ultimo_login.isoformat() if cliente.ultimo_login else None,
            "ip_ultimo_login": cliente.ip_ultimo_login,
            "total_mensagens_enviadas": cliente.total_mensagens_enviadas,
            "created_at": cliente.created_at.isoformat(),
            "updated_at": cliente.updated_at.isoformat()
        }
        
        # 2. Histórico de Pagamentos (Stripe)
        pagamentos = HistoricoService._obter_pagamentos_stripe(cliente)
        
        # 3. Conversas WhatsApp (últimas 100 mensagens)
        conversas = HistoricoService._obter_conversas(db, cliente_id)
        
        # 4. Tickets
        tickets = HistoricoService._obter_tickets(db, cliente_id)
        
        # 5. Uso OpenAI (últimos 30 dias)
        uso_openai = HistoricoService._obter_uso_openai(db, cliente_id)
        
        # 6. Logins (últimos 30 dias)
        logins = HistoricoService._obter_logins(db, cliente_id)
        
        # 7. Timeline de Eventos
        timeline = HistoricoService._gerar_timeline(
            cliente, pagamentos, conversas, tickets, logins
        )
        
        return {
            "dados_cadastrais": dados_cadastrais,
            "pagamentos": pagamentos,
            "conversas": conversas,
            "tickets": tickets,
            "uso_openai": uso_openai,
            "logins": logins,
            "timeline": timeline
        }
    
    @staticmethod
    def _obter_pagamentos_stripe(cliente: Cliente) -> Dict[str, Any]:
        """Obtém histórico de pagamentos do Stripe"""
        if not cliente.stripe_customer_id:
            return {
                "transacoes": [],
                "assinaturas": [],
                "total_gasto": 0,
                "total_transacoes": 0
            }
        
        try:
            # Buscar charges
            charges = stripe.Charge.list(
                customer=cliente.stripe_customer_id,
                limit=100
            )
            
            transacoes = []
            total_gasto = 0
            
            for charge in charges.data:
                valor = charge.amount / 100
                if charge.status == "succeeded":
                    total_gasto += valor
                
                transacoes.append({
                    "id": charge.id,
                    "valor": valor,
                    "moeda": charge.currency.upper(),
                    "status": charge.status,
                    "descricao": charge.description or "Assinatura",
                    "data": datetime.fromtimestamp(charge.created).isoformat(),
                    "reembolsado": charge.refunded,
                    "valor_reembolsado": charge.amount_refunded / 100 if charge.amount_refunded else 0
                })
            
            # Buscar assinaturas
            subscriptions = stripe.Subscription.list(
                customer=cliente.stripe_customer_id,
                limit=10
            )
            
            assinaturas = []
            for sub in subscriptions.data:
                valor = 0
                if sub.items and sub.items.data:
                    valor = sub.items.data[0].price.unit_amount / 100
                
                assinaturas.append({
                    "id": sub.id,
                    "status": sub.status,
                    "valor": valor,
                    "moeda": sub.currency.upper() if sub.currency else "BRL",
                    "intervalo": sub.items.data[0].price.recurring.interval if sub.items.data else "month",
                    "data_inicio": datetime.fromtimestamp(sub.start_date).isoformat(),
                    "proxima_cobranca": datetime.fromtimestamp(sub.current_period_end).isoformat() if sub.current_period_end else None,
                    "cancelar_no_fim": sub.cancel_at_period_end
                })
            
            return {
                "transacoes": transacoes,
                "assinaturas": assinaturas,
                "total_gasto": round(total_gasto, 2),
                "total_transacoes": len(transacoes)
            }
            
        except stripe.error.StripeError as e:
            return {
                "erro": str(e),
                "transacoes": [],
                "assinaturas": [],
                "total_gasto": 0,
                "total_transacoes": 0
            }
    
    @staticmethod
    def _obter_conversas(db: Session, cliente_id: int) -> Dict[str, Any]:
        """Obtém conversas WhatsApp (últimas 100 mensagens)"""
        # Buscar conversas do cliente
        conversas = db.query(Conversa).filter(
            Conversa.cliente_id == cliente_id
        ).order_by(desc(Conversa.ultima_mensagem_em)).limit(20).all()
        
        conversas_data = []
        total_mensagens = 0
        
        for conversa in conversas:
            # Buscar últimas mensagens da conversa
            mensagens = db.query(Mensagem).filter(
                Mensagem.conversa_id == conversa.id
            ).order_by(desc(Mensagem.created_at)).limit(10).all()
            
            mensagens_data = []
            for msg in mensagens:
                mensagens_data.append({
                    "id": msg.id,
                    "tipo": msg.tipo,
                    "conteudo": msg.conteudo[:200] + "..." if len(msg.conteudo) > 200 else msg.conteudo,
                    "confidence_score": msg.confidence_score,
                    "fallback_triggered": msg.fallback_triggered,
                    "created_at": msg.created_at.isoformat()
                })
            
            total_mensagens += len(mensagens)
            
            conversas_data.append({
                "id": conversa.id,
                "numero_whatsapp": conversa.numero_whatsapp,
                "status": conversa.status,
                "motivo_fallback": conversa.motivo_fallback,
                "ultima_mensagem_em": conversa.ultima_mensagem_em.isoformat(),
                "assumida_por": conversa.assumida_por,
                "assumida_em": conversa.assumida_em.isoformat() if conversa.assumida_em else None,
                "mensagens": mensagens_data,
                "total_mensagens": len(mensagens)
            })
        
        return {
            "conversas": conversas_data,
            "total_conversas": len(conversas_data),
            "total_mensagens": total_mensagens
        }
    
    @staticmethod
    def _obter_tickets(db: Session, cliente_id: int) -> Dict[str, Any]:
        """Obtém tickets do cliente"""
        tickets = db.query(Ticket).filter(
            Ticket.cliente_id == cliente_id
        ).order_by(desc(Ticket.created_at)).all()
        
        tickets_data = []
        tickets_abertos = 0
        tickets_resolvidos = 0
        
        for ticket in tickets:
            # Contar mensagens
            total_mensagens = db.query(func.count(TicketMensagem.id)).filter(
                TicketMensagem.ticket_id == ticket.id
            ).scalar()
            
            if ticket.status == "aberto":
                tickets_abertos += 1
            elif ticket.status == "resolvido":
                tickets_resolvidos += 1
            
            tickets_data.append({
                "id": ticket.id,
                "assunto": ticket.assunto,
                "status": ticket.status,
                "prioridade": ticket.prioridade,
                "ia_respondeu": ticket.ia_respondeu,
                "confianca_ia": ticket.confianca_ia,
                "total_mensagens": total_mensagens,
                "created_at": ticket.created_at.isoformat(),
                "resolvido_em": ticket.resolvido_em.isoformat() if ticket.resolvido_em else None
            })
        
        return {
            "tickets": tickets_data,
            "total_tickets": len(tickets_data),
            "tickets_abertos": tickets_abertos,
            "tickets_resolvidos": tickets_resolvidos
        }
    
    @staticmethod
    def _obter_uso_openai(db: Session, cliente_id: int) -> Dict[str, Any]:
        """Obtém uso OpenAI dos últimos 30 dias"""
        data_inicio = datetime.utcnow().date() - timedelta(days=30)
        
        uso = db.query(UsoOpenAI).filter(
            and_(
                UsoOpenAI.cliente_id == cliente_id,
                UsoOpenAI.data >= data_inicio
            )
        ).order_by(desc(UsoOpenAI.data)).all()
        
        uso_data = []
        total_tokens = 0
        total_custo = 0
        total_mensagens = 0
        
        for u in uso:
            total_tokens += u.tokens_total
            total_custo += u.custo_estimado
            total_mensagens += u.mensagens_processadas
            
            uso_data.append({
                "data": u.data.isoformat(),
                "tokens_prompt": u.tokens_prompt,
                "tokens_completion": u.tokens_completion,
                "tokens_total": u.tokens_total,
                "custo_estimado": round(u.custo_estimado, 4),
                "mensagens_processadas": u.mensagens_processadas,
                "modelo": u.modelo
            })
        
        return {
            "uso_diario": uso_data,
            "total_tokens": total_tokens,
            "total_custo": round(total_custo, 2),
            "total_mensagens": total_mensagens,
            "periodo_dias": 30
        }
    
    @staticmethod
    def _obter_logins(db: Session, cliente_id: int) -> Dict[str, Any]:
        """Obtém logins dos últimos 30 dias via logs de ação"""
        data_inicio = datetime.utcnow() - timedelta(days=30)
        
        # Buscar logs de login (ação = "login")
        logs = db.query(AuditLog).filter(
            and_(
                AuditLog.entity_type == "cliente",
                AuditLog.entity_id == cliente_id,
                AuditLog.action == "login",
                AuditLog.created_at >= data_inicio
            )
        ).order_by(desc(AuditLog.created_at)).all()
        
        logins_data = []
        for log in logs:
            logins_data.append({
                "data": log.created_at.isoformat(),
                "ip": log.ip,
                "user_agent": log.new_data.get("user_agent") if log.new_data else None
            })
        
        return {
            "logins": logins_data,
            "total_logins": len(logins_data),
            "periodo_dias": 30
        }
    
    @staticmethod
    def _gerar_timeline(
        cliente: Cliente,
        pagamentos: Dict[str, Any],
        conversas: Dict[str, Any],
        tickets: Dict[str, Any],
        logins: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Gera timeline unificada de eventos"""
        eventos = []
        
        # Evento: Cadastro
        eventos.append({
            "tipo": "cadastro",
            "titulo": "Cliente cadastrado",
            "descricao": f"Cliente {cliente.nome} criou conta",
            "data": cliente.created_at.isoformat(),
            "icone": "user-plus"
        })
        
        # Eventos: Pagamentos
        for transacao in pagamentos.get("transacoes", []):
            eventos.append({
                "tipo": "pagamento",
                "titulo": f"Pagamento {transacao['status']}",
                "descricao": f"R$ {transacao['valor']:.2f} - {transacao['descricao']}",
                "data": transacao["data"],
                "icone": "dollar-sign"
            })
        
        # Eventos: Tickets
        for ticket in tickets.get("tickets", []):
            eventos.append({
                "tipo": "ticket",
                "titulo": f"Ticket {ticket['status']}",
                "descricao": ticket["assunto"],
                "data": ticket["created_at"],
                "icone": "message-circle"
            })
        
        # Eventos: Logins
        for login in logins.get("logins", [])[:10]:  # Últimos 10 logins
            eventos.append({
                "tipo": "login",
                "titulo": "Login realizado",
                "descricao": f"IP: {login['ip']}",
                "data": login["data"],
                "icone": "log-in"
            })
        
        # Ordenar por data (mais recente primeiro)
        eventos.sort(key=lambda x: x["data"], reverse=True)
        
        return eventos[:50]  # Retornar últimos 50 eventos
