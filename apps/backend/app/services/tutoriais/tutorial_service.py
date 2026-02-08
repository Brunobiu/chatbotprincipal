from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func

from app.db.models.tutorial import Tutorial, TutorialVisualizacao, TutorialComentario


class TutorialService:
    """Serviço para gerenciar tutoriais"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== ADMIN ====================
    
    def criar_tutorial(
        self,
        titulo: str,
        descricao: Optional[str],
        video_url: str,
        thumbnail_url: Optional[str] = None
    ) -> Tutorial:
        """Cria um novo tutorial"""
        # Pegar próxima ordem
        max_ordem = self.db.query(func.max(Tutorial.ordem)).scalar() or 0
        
        tutorial = Tutorial(
            titulo=titulo,
            descricao=descricao,
            video_url=video_url,
            thumbnail_url=thumbnail_url,
            ordem=max_ordem + 1,
            ativo=True
        )
        self.db.add(tutorial)
        self.db.commit()
        self.db.refresh(tutorial)
        
        return tutorial
    
    def atualizar_tutorial(
        self,
        tutorial_id: int,
        titulo: Optional[str] = None,
        descricao: Optional[str] = None,
        video_url: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
        ativo: Optional[bool] = None
    ) -> Optional[Tutorial]:
        """Atualiza um tutorial"""
        tutorial = self.db.query(Tutorial).filter(Tutorial.id == tutorial_id).first()
        if not tutorial:
            return None
        
        if titulo is not None:
            tutorial.titulo = titulo
        if descricao is not None:
            tutorial.descricao = descricao
        if video_url is not None:
            tutorial.video_url = video_url
        if thumbnail_url is not None:
            tutorial.thumbnail_url = thumbnail_url
        if ativo is not None:
            tutorial.ativo = ativo
        
        self.db.commit()
        self.db.refresh(tutorial)
        
        return tutorial
    
    def deletar_tutorial(self, tutorial_id: int) -> bool:
        """Deleta um tutorial"""
        tutorial = self.db.query(Tutorial).filter(Tutorial.id == tutorial_id).first()
        if not tutorial:
            return False
        
        self.db.delete(tutorial)
        self.db.commit()
        
        return True
    
    def reordenar_tutoriais(self, ordem: List[int]) -> bool:
        """Reordena tutoriais"""
        try:
            for idx, tutorial_id in enumerate(ordem):
                self.db.query(Tutorial).filter(Tutorial.id == tutorial_id).update(
                    {"ordem": idx}
                )
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False
    
    def listar_tutoriais_admin(self) -> List[Tutorial]:
        """Lista todos os tutoriais (admin)"""
        return self.db.query(Tutorial).order_by(Tutorial.ordem).all()
    
    def obter_tutorial_admin(self, tutorial_id: int) -> Optional[Tutorial]:
        """Obtém um tutorial com estatísticas (admin)"""
        return self.db.query(Tutorial).options(
            joinedload(Tutorial.visualizacoes),
            joinedload(Tutorial.comentarios)
        ).filter(Tutorial.id == tutorial_id).first()
    
    def obter_estatisticas_tutorial(self, tutorial_id: int) -> Dict[str, Any]:
        """Obtém estatísticas de um tutorial"""
        total_visualizacoes = self.db.query(TutorialVisualizacao).filter(
            TutorialVisualizacao.tutorial_id == tutorial_id
        ).count()
        
        total_comentarios = self.db.query(TutorialComentario).filter(
            TutorialComentario.tutorial_id == tutorial_id
        ).count()
        
        return {
            "total_visualizacoes": total_visualizacoes,
            "total_comentarios": total_comentarios
        }
    
    # ==================== CLIENTE ====================
    
    def listar_tutoriais_cliente(self, cliente_id: int) -> List[Dict[str, Any]]:
        """Lista tutoriais ativos para cliente com status de visualização"""
        tutoriais = self.db.query(Tutorial).filter(
            Tutorial.ativo == True
        ).order_by(Tutorial.ordem).all()
        
        # Verificar quais foram visualizados
        visualizados_ids = set(
            v.tutorial_id for v in self.db.query(TutorialVisualizacao.tutorial_id).filter(
                TutorialVisualizacao.cliente_id == cliente_id
            ).all()
        )
        
        resultado = []
        for tutorial in tutoriais:
            resultado.append({
                "id": tutorial.id,
                "titulo": tutorial.titulo,
                "descricao": tutorial.descricao,
                "video_url": tutorial.video_url,
                "thumbnail_url": tutorial.thumbnail_url,
                "visualizado": tutorial.id in visualizados_ids,
                "created_at": tutorial.created_at.isoformat()
            })
        
        return resultado
    
    def obter_tutorial_cliente(self, tutorial_id: int, cliente_id: int) -> Optional[Dict[str, Any]]:
        """Obtém um tutorial para cliente"""
        tutorial = self.db.query(Tutorial).filter(
            Tutorial.id == tutorial_id,
            Tutorial.ativo == True
        ).first()
        
        if not tutorial:
            return None
        
        # Verificar se foi visualizado
        visualizado = self.db.query(TutorialVisualizacao).filter(
            TutorialVisualizacao.tutorial_id == tutorial_id,
            TutorialVisualizacao.cliente_id == cliente_id
        ).first() is not None
        
        # Buscar comentários
        comentarios = self.db.query(TutorialComentario).options(
            joinedload(TutorialComentario.cliente)
        ).filter(
            TutorialComentario.tutorial_id == tutorial_id
        ).order_by(desc(TutorialComentario.created_at)).all()
        
        return {
            "id": tutorial.id,
            "titulo": tutorial.titulo,
            "descricao": tutorial.descricao,
            "video_url": tutorial.video_url,
            "thumbnail_url": tutorial.thumbnail_url,
            "visualizado": visualizado,
            "created_at": tutorial.created_at.isoformat(),
            "comentarios": [
                {
                    "id": c.id,
                    "cliente_nome": c.cliente.nome,
                    "comentario": c.comentario,
                    "created_at": c.created_at.isoformat()
                } for c in comentarios
            ]
        }
    
    def marcar_visualizado(self, tutorial_id: int, cliente_id: int) -> bool:
        """Marca tutorial como visualizado"""
        # Verificar se já existe
        existe = self.db.query(TutorialVisualizacao).filter(
            TutorialVisualizacao.tutorial_id == tutorial_id,
            TutorialVisualizacao.cliente_id == cliente_id
        ).first()
        
        if existe:
            return True
        
        visualizacao = TutorialVisualizacao(
            tutorial_id=tutorial_id,
            cliente_id=cliente_id
        )
        self.db.add(visualizacao)
        self.db.commit()
        
        return True
    
    def adicionar_comentario(
        self,
        tutorial_id: int,
        cliente_id: int,
        comentario: str
    ) -> Optional[TutorialComentario]:
        """Adiciona comentário a um tutorial"""
        # Verificar se tutorial existe e está ativo
        tutorial = self.db.query(Tutorial).filter(
            Tutorial.id == tutorial_id,
            Tutorial.ativo == True
        ).first()
        
        if not tutorial:
            return None
        
        comentario_obj = TutorialComentario(
            tutorial_id=tutorial_id,
            cliente_id=cliente_id,
            comentario=comentario
        )
        self.db.add(comentario_obj)
        self.db.commit()
        self.db.refresh(comentario_obj)
        
        return comentario_obj
    
    def listar_comentarios(self, tutorial_id: int) -> List[Dict[str, Any]]:
        """Lista comentários de um tutorial"""
        comentarios = self.db.query(TutorialComentario).options(
            joinedload(TutorialComentario.cliente)
        ).filter(
            TutorialComentario.tutorial_id == tutorial_id
        ).order_by(desc(TutorialComentario.created_at)).all()
        
        return [
            {
                "id": c.id,
                "cliente_nome": c.cliente.nome,
                "comentario": c.comentario,
                "created_at": c.created_at.isoformat()
            } for c in comentarios
        ]
