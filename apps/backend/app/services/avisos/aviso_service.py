from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.db.models.aviso import Aviso


class AvisoService:
    """Serviço para gerenciar avisos do sistema"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== ADMIN ====================
    
    def criar_aviso(
        self,
        tipo: str,
        titulo: str,
        mensagem: str,
        dismissivel: bool = True,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None
    ) -> Aviso:
        """Cria um novo aviso"""
        aviso = Aviso(
            tipo=tipo,
            titulo=titulo,
            mensagem=mensagem,
            dismissivel=dismissivel,
            data_inicio=data_inicio,
            data_fim=data_fim,
            ativo=True
        )
        self.db.add(aviso)
        self.db.commit()
        self.db.refresh(aviso)
        
        return aviso
    
    def atualizar_aviso(
        self,
        aviso_id: int,
        tipo: Optional[str] = None,
        titulo: Optional[str] = None,
        mensagem: Optional[str] = None,
        dismissivel: Optional[bool] = None,
        ativo: Optional[bool] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None
    ) -> Optional[Aviso]:
        """Atualiza um aviso"""
        aviso = self.db.query(Aviso).filter(Aviso.id == aviso_id).first()
        if not aviso:
            return None
        
        if tipo is not None:
            aviso.tipo = tipo
        if titulo is not None:
            aviso.titulo = titulo
        if mensagem is not None:
            aviso.mensagem = mensagem
        if dismissivel is not None:
            aviso.dismissivel = dismissivel
        if ativo is not None:
            aviso.ativo = ativo
        if data_inicio is not None:
            aviso.data_inicio = data_inicio
        if data_fim is not None:
            aviso.data_fim = data_fim
        
        self.db.commit()
        self.db.refresh(aviso)
        
        return aviso
    
    def deletar_aviso(self, aviso_id: int) -> bool:
        """Deleta um aviso"""
        aviso = self.db.query(Aviso).filter(Aviso.id == aviso_id).first()
        if not aviso:
            return False
        
        self.db.delete(aviso)
        self.db.commit()
        
        return True
    
    def listar_avisos_admin(self) -> List[Aviso]:
        """Lista todos os avisos (admin)"""
        return self.db.query(Aviso).order_by(Aviso.created_at.desc()).all()
    
    def obter_aviso_admin(self, aviso_id: int) -> Optional[Aviso]:
        """Obtém um aviso (admin)"""
        return self.db.query(Aviso).filter(Aviso.id == aviso_id).first()
    
    # ==================== CLIENTE ====================
    
    def listar_avisos_ativos(self) -> List[Aviso]:
        """Lista avisos ativos para clientes"""
        agora = datetime.utcnow()
        
        return self.db.query(Aviso).filter(
            Aviso.ativo == True,
            or_(
                Aviso.data_inicio == None,
                Aviso.data_inicio <= agora
            ),
            or_(
                Aviso.data_fim == None,
                Aviso.data_fim >= agora
            )
        ).order_by(Aviso.created_at.desc()).all()
