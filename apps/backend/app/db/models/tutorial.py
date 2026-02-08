from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base


class Tutorial(Base):
    __tablename__ = "tutoriais"
    
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False)
    descricao = Column(Text, nullable=True)
    video_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    ordem = Column(Integer, default=0, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relacionamentos
    visualizacoes = relationship("TutorialVisualizacao", back_populates="tutorial", cascade="all, delete-orphan")
    comentarios = relationship("TutorialComentario", back_populates="tutorial", cascade="all, delete-orphan")


class TutorialVisualizacao(Base):
    __tablename__ = "tutorial_visualizacoes"
    __table_args__ = (
        UniqueConstraint('tutorial_id', 'cliente_id', name='uq_tutorial_cliente'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    tutorial_id = Column(Integer, ForeignKey("tutoriais.id", ondelete="CASCADE"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id", ondelete="CASCADE"), nullable=False)
    visualizado_em = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relacionamentos
    tutorial = relationship("Tutorial", back_populates="visualizacoes")
    cliente = relationship("Cliente")


class TutorialComentario(Base):
    __tablename__ = "tutorial_comentarios"
    
    id = Column(Integer, primary_key=True, index=True)
    tutorial_id = Column(Integer, ForeignKey("tutoriais.id", ondelete="CASCADE"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id", ondelete="CASCADE"), nullable=False)
    comentario = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relacionamentos
    tutorial = relationship("Tutorial", back_populates="comentarios")
    cliente = relationship("Cliente")
