from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, or_, and_, func

from app.db.models.ticket import Ticket, TicketCategoria, TicketMensagem
from app.db.models.cliente import Cliente
from app.services.ai.ai_service import AIService
from app.services.conhecimento.embeddings_service import EmbeddingsService


class TicketService:
    """Serviço para gerenciar tickets de suporte"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()
        self.embeddings_service = EmbeddingsService()
    
    # ==================== CATEGORIAS ====================
    
    def listar_categorias(self) -> List[TicketCategoria]:
        """Lista todas as categorias ativas"""
        return self.db.query(TicketCategoria).filter(
            TicketCategoria.ativo == True
        ).all()
    
    # ==================== TICKETS - CLIENTE ====================
    
    def criar_ticket(
        self,
        cliente_id: int,
        assunto: str,
        mensagem: str,
        categoria_id: Optional[int] = None,
        anexos: Optional[List[Dict]] = None
    ) -> Ticket:
        """Cria um novo ticket e tenta responder com IA"""
        
        # Criar ticket
        ticket = Ticket(
            cliente_id=cliente_id,
            categoria_id=categoria_id,
            assunto=assunto,
            status="aberto",
            prioridade="normal"
        )
        self.db.add(ticket)
        self.db.flush()
        
        # Adicionar primeira mensagem do cliente
        mensagem_obj = TicketMensagem(
            ticket_id=ticket.id,
            remetente_tipo="cliente",
            remetente_id=cliente_id,
            mensagem=mensagem,
            anexos=anexos
        )
        self.db.add(mensagem_obj)
        self.db.commit()
        self.db.refresh(ticket)
        
        # Tentar responder com IA
        self._tentar_resposta_ia(ticket, mensagem)
        
        # Notificar admin sobre novo ticket
        from app.services.notificacoes.notificacao_service import NotificacaoService
        from app.db.models.admin import Admin
        from app.db.models.cliente import Cliente
        
        admin = self.db.query(Admin).first()
        cliente = self.db.query(Cliente).filter(Cliente.id == cliente_id).first()
        
        if admin and cliente:
            NotificacaoService.notificar_novo_ticket(
                db=self.db,
                admin_id=admin.id,
                ticket_id=ticket.id,
                cliente_email=cliente.email,
                assunto=assunto
            )
        
        return ticket
    
    def criar_ticket_com_anexos(
        self,
        cliente_id: int,
        assunto: str,
        mensagem: str,
        categoria_id: Optional[int] = None,
        anexos: Optional[List[str]] = None  # Lista de URLs de anexos (até 10)
    ) -> Ticket:
        """
        Cria ticket com suporte a até 10 anexos
        Task 11.4
        """
        # Validar número de anexos
        if anexos and len(anexos) > 10:
            raise ValueError("Máximo de 10 anexos permitidos")
        
        # Converter lista de URLs para formato Dict esperado
        anexos_dict = None
        if anexos:
            anexos_dict = [{"url": url, "tipo": "imagem"} for url in anexos]
        
        return self.criar_ticket(
            cliente_id=cliente_id,
            assunto=assunto,
            mensagem=mensagem,
            categoria_id=categoria_id,
            anexos=anexos_dict
        )
    
    def _tentar_resposta_ia(self, ticket: Ticket, pergunta: str):
        """Tenta responder o ticket com IA baseado em conhecimento admin"""
        try:
            # Buscar contexto relevante (aqui você pode ter uma base de conhecimento admin)
            # Por enquanto, vamos usar um conhecimento básico
            contexto = self._buscar_conhecimento_suporte(pergunta)
            
            # Montar prompt
            prompt = f"""Você é um assistente de suporte técnico. Responda a seguinte pergunta do cliente de forma clara e profissional.

Contexto disponível:
{contexto}

Pergunta do cliente:
{pergunta}

Se você não tiver informações suficientes para responder com confiança, diga: "PRECISO_HUMANO"

Resposta:"""
            
            # Chamar IA
            resposta = self.ai_service.gerar_resposta(
                prompt=prompt,
                max_tokens=500,
                temperature=0.3
            )
            
            # Calcular confiança (simplificado)
            confianca = self._calcular_confianca(resposta, contexto)
            
            # Atualizar ticket
            ticket.ia_respondeu = True
            ticket.confianca_ia = confianca
            
            if confianca >= 0.7 and "PRECISO_HUMANO" not in resposta:
                # IA respondeu com confiança
                mensagem_ia = TicketMensagem(
                    ticket_id=ticket.id,
                    remetente_tipo="ia",
                    remetente_id=None,
                    mensagem=resposta,
                    lida=False
                )
                self.db.add(mensagem_ia)
                ticket.status = "aguardando_cliente"
            else:
                # IA não tem confiança, marcar para admin
                ticket.status = "aberto"
            
            self.db.commit()
            
        except Exception as e:
            print(f"Erro ao tentar resposta IA: {e}")
            ticket.status = "aberto"
            self.db.commit()
    
    def responder_ticket_ia(self, ticket_id: int, pergunta: str) -> Dict[str, Any]:
        """
        Responde ticket usando IA (chamada explícita)
        Task 11.4
        
        Returns:
            Dict com resposta, confiança e se deve escalar para humano
        """
        ticket = self.obter_ticket_admin(ticket_id)
        if not ticket:
            return {
                "sucesso": False,
                "erro": "Ticket não encontrado"
            }
        
        try:
            contexto = self._buscar_conhecimento_suporte(pergunta)
            
            prompt = f"""Você é um assistente de suporte técnico. Responda a seguinte pergunta do cliente de forma clara e profissional.

Contexto disponível:
{contexto}

Pergunta do cliente:
{pergunta}

Se você não tiver informações suficientes para responder com confiança, diga: "PRECISO_HUMANO"

Resposta:"""
            
            resposta = self.ai_service.gerar_resposta(
                prompt=prompt,
                max_tokens=500,
                temperature=0.3
            )
            
            confianca = self._calcular_confianca(resposta, contexto)
            
            # Salvar resposta da IA
            if confianca >= 0.7 and "PRECISO_HUMANO" not in resposta:
                mensagem_ia = TicketMensagem(
                    ticket_id=ticket.id,
                    remetente_tipo="ia",
                    remetente_id=None,
                    mensagem=resposta,
                    lida=False
                )
                self.db.add(mensagem_ia)
                ticket.ia_respondeu = True
                ticket.confianca_ia = confianca
                ticket.status = "aguardando_cliente"
                self.db.commit()
                
                return {
                    "sucesso": True,
                    "resposta": resposta,
                    "confianca": confianca,
                    "escalar_humano": False
                }
            else:
                return {
                    "sucesso": True,
                    "resposta": resposta,
                    "confianca": confianca,
                    "escalar_humano": True,
                    "motivo": "Confiança baixa ou IA solicitou humano"
                }
        
        except Exception as e:
            return {
                "sucesso": False,
                "erro": str(e)
            }
    
    def _buscar_conhecimento_suporte(self, pergunta: str) -> str:
        """Busca conhecimento relevante para suporte (placeholder)"""
        # TODO: Implementar busca em base de conhecimento admin
        return """
        - Para problemas de conexão WhatsApp, verifique se o QR code foi escaneado corretamente
        - Para problemas de pagamento, verifique o status da assinatura no Stripe
        - Para problemas com IA, verifique se a base de conhecimento foi configurada
        - Para resetar senha, use a opção "Esqueci minha senha" na tela de login
        """
    
    def _calcular_confianca(self, resposta: str, contexto: str) -> float:
        """Calcula confiança da resposta (simplificado)"""
        if "PRECISO_HUMANO" in resposta:
            return 0.0
        if "não sei" in resposta.lower() or "não tenho" in resposta.lower():
            return 0.3
        if len(resposta) < 50:
            return 0.4
        return 0.8  # Simplificado
    
    def listar_tickets_cliente(
        self,
        cliente_id: int,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[List[Ticket], int]:
        """Lista tickets de um cliente"""
        query = self.db.query(Ticket).filter(Ticket.cliente_id == cliente_id)
        
        if status:
            query = query.filter(Ticket.status == status)
        
        total = query.count()
        tickets = query.options(
            joinedload(Ticket.categoria),
            joinedload(Ticket.mensagens)
        ).order_by(desc(Ticket.updated_at)).limit(limit).offset(offset).all()
        
        return tickets, total
    
    def obter_ticket_cliente(self, ticket_id: int, cliente_id: int) -> Optional[Ticket]:
        """Obtém um ticket específico do cliente"""
        return self.db.query(Ticket).options(
            joinedload(Ticket.categoria),
            joinedload(Ticket.mensagens),
            joinedload(Ticket.atribuido_admin)
        ).filter(
            Ticket.id == ticket_id,
            Ticket.cliente_id == cliente_id
        ).first()
    
    def adicionar_mensagem_cliente(
        self,
        ticket_id: int,
        cliente_id: int,
        mensagem: str,
        anexos: Optional[List[Dict]] = None
    ) -> Optional[TicketMensagem]:
        """Cliente adiciona mensagem ao ticket"""
        ticket = self.obter_ticket_cliente(ticket_id, cliente_id)
        if not ticket:
            return None
        
        mensagem_obj = TicketMensagem(
            ticket_id=ticket_id,
            remetente_tipo="cliente",
            remetente_id=cliente_id,
            mensagem=mensagem,
            anexos=anexos
        )
        self.db.add(mensagem_obj)
        
        # Atualizar status do ticket
        if ticket.status in ["resolvido", "fechado"]:
            ticket.status = "aberto"
        elif ticket.status == "aguardando_cliente":
            ticket.status = "em_andamento"
        
        ticket.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(mensagem_obj)
        
        return mensagem_obj
    
    # ==================== TICKETS - ADMIN ====================
    
    def listar_tickets_admin(
        self,
        status: Optional[str] = None,
        categoria_id: Optional[int] = None,
        prioridade: Optional[str] = None,
        busca: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[List[Ticket], int]:
        """Lista todos os tickets (admin)"""
        query = self.db.query(Ticket)
        
        if status:
            query = query.filter(Ticket.status == status)
        if categoria_id:
            query = query.filter(Ticket.categoria_id == categoria_id)
        if prioridade:
            query = query.filter(Ticket.prioridade == prioridade)
        if busca:
            query = query.filter(
                or_(
                    Ticket.assunto.ilike(f"%{busca}%"),
                    Cliente.nome.ilike(f"%{busca}%"),
                    Cliente.email.ilike(f"%{busca}%")
                )
            ).join(Cliente)
        
        total = query.count()
        tickets = query.options(
            joinedload(Ticket.cliente),
            joinedload(Ticket.categoria),
            joinedload(Ticket.atribuido_admin)
        ).order_by(desc(Ticket.updated_at)).limit(limit).offset(offset).all()
        
        return tickets, total
    
    def obter_ticket_admin(self, ticket_id: int) -> Optional[Ticket]:
        """Obtém um ticket (admin)"""
        return self.db.query(Ticket).options(
            joinedload(Ticket.cliente),
            joinedload(Ticket.categoria),
            joinedload(Ticket.mensagens),
            joinedload(Ticket.atribuido_admin)
        ).filter(Ticket.id == ticket_id).first()
    
    def adicionar_mensagem_admin(
        self,
        ticket_id: int,
        admin_id: int,
        mensagem: str,
        anexos: Optional[List[Dict]] = None
    ) -> Optional[TicketMensagem]:
        """Admin adiciona mensagem ao ticket"""
        ticket = self.obter_ticket_admin(ticket_id)
        if not ticket:
            return None
        
        mensagem_obj = TicketMensagem(
            ticket_id=ticket_id,
            remetente_tipo="admin",
            remetente_id=admin_id,
            mensagem=mensagem,
            anexos=anexos
        )
        self.db.add(mensagem_obj)
        
        # Atualizar status do ticket
        if ticket.status == "aberto":
            ticket.status = "em_andamento"
        elif ticket.status == "em_andamento":
            ticket.status = "aguardando_cliente"
        
        ticket.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(mensagem_obj)
        
        return mensagem_obj
    
    def atualizar_status_ticket(
        self,
        ticket_id: int,
        status: str,
        admin_id: Optional[int] = None
    ) -> Optional[Ticket]:
        """Atualiza status do ticket"""
        ticket = self.obter_ticket_admin(ticket_id)
        if not ticket:
            return None
        
        ticket.status = status
        ticket.updated_at = datetime.utcnow()
        
        if status == "resolvido":
            ticket.resolvido_em = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(ticket)
        
        return ticket
    
    def atribuir_ticket(
        self,
        ticket_id: int,
        admin_id: int
    ) -> Optional[Ticket]:
        """Atribui ticket a um admin"""
        ticket = self.obter_ticket_admin(ticket_id)
        if not ticket:
            return None
        
        ticket.atribuido_admin_id = admin_id
        ticket.updated_at = datetime.utcnow()
        
        if ticket.status == "aberto":
            ticket.status = "em_andamento"
        
        self.db.commit()
        self.db.refresh(ticket)
        
        return ticket
    
    def marcar_mensagens_lidas(self, ticket_id: int, remetente_tipo: str):
        """Marca mensagens como lidas"""
        self.db.query(TicketMensagem).filter(
            TicketMensagem.ticket_id == ticket_id,
            TicketMensagem.remetente_tipo != remetente_tipo,
            TicketMensagem.lida == False
        ).update({"lida": True})
        self.db.commit()
    
    # ==================== ESTATÍSTICAS ====================
    
    def obter_estatisticas_admin(self) -> Dict[str, Any]:
        """Obtém estatísticas de tickets para admin"""
        total = self.db.query(Ticket).count()
        abertos = self.db.query(Ticket).filter(Ticket.status == "aberto").count()
        em_andamento = self.db.query(Ticket).filter(Ticket.status == "em_andamento").count()
        aguardando = self.db.query(Ticket).filter(Ticket.status == "aguardando_cliente").count()
        resolvidos = self.db.query(Ticket).filter(Ticket.status == "resolvido").count()
        
        # Tickets não lidos (com mensagens não lidas de clientes)
        nao_lidos = self.db.query(Ticket).join(TicketMensagem).filter(
            TicketMensagem.remetente_tipo == "cliente",
            TicketMensagem.lida == False
        ).distinct().count()
        
        return {
            "total": total,
            "abertos": abertos,
            "em_andamento": em_andamento,
            "aguardando_cliente": aguardando,
            "resolvidos": resolvidos,
            "nao_lidos": nao_lidos
        }
