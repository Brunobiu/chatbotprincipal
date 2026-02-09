"""
Serviço para gerenciamento de conversas
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.db.models.conversa import Conversa
from app.db.models.mensagem import Mensagem
from app.db.models.cliente import Cliente


class ConversaService:
    """Serviço para operações com conversas"""
    
    @staticmethod
    def listar_conversas(
        db: Session,
        cliente_id: int,
        filtro_data_inicio: Optional[datetime] = None,
        filtro_data_fim: Optional[datetime] = None,
        filtro_status: Optional[str] = None,
        pagina: int = 1,
        itens_por_pagina: int = 20
    ) -> Dict[str, Any]:
        """
        Lista conversas do cliente com filtros e paginação.
        
        Args:
            db: Sessão do banco de dados
            cliente_id: ID do cliente
            filtro_data_inicio: Data inicial para filtro (opcional)
            filtro_data_fim: Data final para filtro (opcional)
            filtro_status: Status da conversa para filtro (opcional)
            pagina: Número da página (começa em 1)
            itens_por_pagina: Quantidade de itens por página (padrão 20)
        
        Returns:
            {
                "conversas": [...],
                "total": int,
                "pagina": int,
                "total_paginas": int
            }
        """
        # Query base - SEMPRE filtrar por cliente_id (isolamento)
        query = db.query(Conversa).filter(Conversa.cliente_id == cliente_id)
        
        # Aplicar filtros opcionais
        if filtro_data_inicio:
            query = query.filter(Conversa.created_at >= filtro_data_inicio)
        
        if filtro_data_fim:
            query = query.filter(Conversa.created_at <= filtro_data_fim)
        
        if filtro_status:
            query = query.filter(Conversa.status == filtro_status)
        
        # Contar total de conversas (antes da paginação)
        total = query.count()
        
        # Calcular total de páginas
        total_paginas = (total + itens_por_pagina - 1) // itens_por_pagina
        
        # Aplicar paginação
        offset = (pagina - 1) * itens_por_pagina
        conversas = query.order_by(Conversa.created_at.desc()).offset(offset).limit(itens_por_pagina).all()
        
        # Buscar última mensagem de cada conversa
        conversas_data = []
        for conversa in conversas:
            ultima_msg = db.query(Mensagem).filter(
                Mensagem.conversa_id == conversa.id
            ).order_by(Mensagem.created_at.desc()).first()
            
            conversas_data.append({
                "id": conversa.id,
                "numero_whatsapp": conversa.numero_whatsapp,
                "status": conversa.status,
                "motivo_fallback": conversa.motivo_fallback,
                "created_at": conversa.created_at.isoformat() if conversa.created_at else None,
                "updated_at": conversa.updated_at.isoformat() if conversa.updated_at else None,
                "ultima_mensagem": {
                    "conteudo": ultima_msg.conteudo if ultima_msg else None,
                    "remetente": ultima_msg.remetente if ultima_msg else None,
                    "created_at": ultima_msg.created_at.isoformat() if ultima_msg else None
                } if ultima_msg else None
            })
        
        return {
            "conversas": conversas_data,
            "total": total,
            "pagina": pagina,
            "total_paginas": total_paginas
        }
    
    @staticmethod
    def obter_historico_conversa(
        db: Session,
        conversa_id: int,
        cliente_id: int
    ) -> List[Dict[str, Any]]:
        """
        Retorna todas as mensagens de uma conversa.
        
        Args:
            db: Sessão do banco de dados
            conversa_id: ID da conversa
            cliente_id: ID do cliente (para validação)
        
        Returns:
            Lista de mensagens ordenadas cronologicamente
        """
        # Validar que conversa pertence ao cliente (isolamento)
        conversa = db.query(Conversa).filter(
            and_(
                Conversa.id == conversa_id,
                Conversa.cliente_id == cliente_id
            )
        ).first()
        
        if not conversa:
            return []
        
        # Buscar todas as mensagens ordenadas cronologicamente
        mensagens = db.query(Mensagem).filter(
            Mensagem.conversa_id == conversa_id
        ).order_by(Mensagem.created_at.asc()).all()
        
        return [
            {
                "id": msg.id,
                "remetente": msg.remetente,
                "conteudo": msg.conteudo,
                "tipo": msg.tipo,
                "confidence_score": msg.confidence_score,
                "fallback_triggered": msg.fallback_triggered,
                "created_at": msg.created_at.isoformat() if msg.created_at else None
            }
            for msg in mensagens
        ]
