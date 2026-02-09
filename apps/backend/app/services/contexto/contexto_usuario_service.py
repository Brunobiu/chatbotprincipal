"""
Service para gerenciar contexto de usuários do WhatsApp
"""
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from typing import Optional

from app.db.models.contexto_usuario import ContextoUsuarioWhatsApp

logger = logging.getLogger(__name__)


class ContextoUsuarioService:
    """Service para gerenciar contexto de usuários"""
    
    @staticmethod
    def eh_primeira_interacao(db: Session, cliente_id: int, numero_usuario: str) -> bool:
        """
        Verifica se é a primeira interação do usuário
        
        Args:
            db: Sessão do banco
            cliente_id: ID do cliente
            numero_usuario: Número do WhatsApp do usuário
            
        Returns:
            bool: True se é primeira interação
        """
        contexto = db.query(ContextoUsuarioWhatsApp).filter(
            ContextoUsuarioWhatsApp.cliente_id == cliente_id,
            ContextoUsuarioWhatsApp.numero_usuario == numero_usuario
        ).first()
        
        return contexto is None
    
    @staticmethod
    def criar_contexto(db: Session, cliente_id: int, numero_usuario: str) -> ContextoUsuarioWhatsApp:
        """
        Cria contexto para novo usuário
        
        Args:
            db: Sessão do banco
            cliente_id: ID do cliente
            numero_usuario: Número do WhatsApp do usuário
            
        Returns:
            ContextoUsuarioWhatsApp: Contexto criado
        """
        contexto = ContextoUsuarioWhatsApp(
            cliente_id=cliente_id,
            numero_usuario=numero_usuario
        )
        db.add(contexto)
        db.commit()
        db.refresh(contexto)
        
        logger.info(f"Contexto criado para usuário {numero_usuario} do cliente {cliente_id}")
        
        return contexto
    
    @staticmethod
    def salvar_nome_usuario(db: Session, cliente_id: int, numero_usuario: str, nome: str) -> bool:
        """
        Salva nome do usuário no contexto
        
        Args:
            db: Sessão do banco
            cliente_id: ID do cliente
            numero_usuario: Número do WhatsApp do usuário
            nome: Nome do usuário
            
        Returns:
            bool: True se salvou com sucesso
        """
        try:
            contexto = db.query(ContextoUsuarioWhatsApp).filter(
                ContextoUsuarioWhatsApp.cliente_id == cliente_id,
                ContextoUsuarioWhatsApp.numero_usuario == numero_usuario
            ).first()
            
            if not contexto:
                # Criar contexto se não existir
                contexto = ContextoUsuarioService.criar_contexto(db, cliente_id, numero_usuario)
            
            contexto.nome = nome
            contexto.ultima_interacao = datetime.utcnow()
            db.commit()
            
            logger.info(f"Nome '{nome}' salvo para usuário {numero_usuario}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar nome: {e}")
            db.rollback()
            return False
    
    @staticmethod
    def obter_nome_usuario(db: Session, cliente_id: int, numero_usuario: str) -> Optional[str]:
        """
        Obtém nome do usuário do contexto
        
        Args:
            db: Sessão do banco
            cliente_id: ID do cliente
            numero_usuario: Número do WhatsApp do usuário
            
        Returns:
            str: Nome do usuário ou None
        """
        contexto = db.query(ContextoUsuarioWhatsApp).filter(
            ContextoUsuarioWhatsApp.cliente_id == cliente_id,
            ContextoUsuarioWhatsApp.numero_usuario == numero_usuario
        ).first()
        
        return contexto.nome if contexto else None
    
    @staticmethod
    def atualizar_ultima_interacao(db: Session, cliente_id: int, numero_usuario: str):
        """
        Atualiza timestamp da última interação
        
        Args:
            db: Sessão do banco
            cliente_id: ID do cliente
            numero_usuario: Número do WhatsApp do usuário
        """
        try:
            contexto = db.query(ContextoUsuarioWhatsApp).filter(
                ContextoUsuarioWhatsApp.cliente_id == cliente_id,
                ContextoUsuarioWhatsApp.numero_usuario == numero_usuario
            ).first()
            
            if contexto:
                contexto.ultima_interacao = datetime.utcnow()
                db.commit()
                
        except Exception as e:
            logger.error(f"Erro ao atualizar última interação: {e}")
            db.rollback()
    
    @staticmethod
    def detectar_nome_na_mensagem(mensagem: str) -> Optional[str]:
        """
        Tenta detectar nome na mensagem do usuário
        
        Args:
            mensagem: Mensagem do usuário
            
        Returns:
            str: Nome detectado ou None
        """
        # Remover pontuação e normalizar
        mensagem_limpa = mensagem.strip().replace('.', '').replace(',', '').replace('!', '')
        
        # Padrões comuns de resposta
        padroes = [
            "meu nome é ",
            "me chamo ",
            "sou ",
            "eu sou ",
            "pode me chamar de ",
            "meu nome eh ",
            "me chamo de "
        ]
        
        mensagem_lower = mensagem_limpa.lower()
        
        for padrao in padroes:
            if padrao in mensagem_lower:
                # Extrair nome após o padrão
                idx = mensagem_lower.index(padrao)
                nome = mensagem_limpa[idx + len(padrao):].strip()
                
                # Pegar apenas a primeira palavra (nome)
                nome = nome.split()[0] if nome else None
                
                if nome and len(nome) > 1:
                    # Capitalizar primeira letra
                    return nome.capitalize()
        
        # Se não encontrou padrão, assumir que a mensagem inteira é o nome
        # (apenas se for curta e não tiver muitas palavras)
        palavras = mensagem_limpa.split()
        if len(palavras) <= 3 and len(mensagem_limpa) <= 50:
            # Pegar primeiro nome
            nome = palavras[0]
            if len(nome) > 1:
                return nome.capitalize()
        
        return None
