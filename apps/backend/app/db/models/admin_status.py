"""
Model para status online/offline do admin
"""
from sqlalchemy import Column, Integer, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class AdminStatus(Base):
    __tablename__ = "admin_status"
    
    id = Column(Integer, primary_key=True, index=True)
    ultimo_acesso = Column(DateTime(timezone=True), server_default=func.now())
    online = Column(Boolean, default=False)
