"""
Rotas para WhatsApp (Evolution API)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.v1.auth import get_current_cliente
from app.services.whatsapp import WhatsAppService


router = APIRouter()


# Schemas
class InstanciaResponse(BaseModel):
    """Schema para response de instância"""
    instance_id: str
    status: str
    numero: str | None
    qr_code: str | None
    
    class Config:
        from_attributes = True


class StatusResponse(BaseModel):
    """Schema para response de status"""
    status: str
    state: str
    numero: str | None


@router.post("/instance", response_model=InstanciaResponse)
def criar_instancia(
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    """
    Cria instância do WhatsApp para o cliente autenticado
    Se já existir, retorna a existente
    """
    try:
        instancia = WhatsAppService.criar_instancia(db, cliente.id)
        
        return {
            "instance_id": instancia.instance_id,
            "status": instancia.status.value.lower(),  # Retornar em minúsculo
            "numero": instancia.numero,
            "qr_code": instancia.qr_code
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/instance", response_model=InstanciaResponse)
def get_instancia(
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    """
    Retorna instância do cliente autenticado
    """
    instancia = WhatsAppService.buscar_instancia(db, cliente.id)
    
    if not instancia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instância não encontrada. Crie uma primeiro."
        )
    
    return {
        "instance_id": instancia.instance_id,
        "status": instancia.status.value.lower(),  # Retornar em minúsculo
        "numero": instancia.numero,
        "qr_code": instancia.qr_code
    }


@router.get("/qrcode")
def get_qrcode(
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    """
    Obtém QR Code da instância do cliente
    """
    instancia = WhatsAppService.buscar_instancia(db, cliente.id)
    
    if not instancia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instância não encontrada. Crie uma primeiro."
        )
    
    qr_data = WhatsAppService.obter_qrcode(instancia.instance_id)
    
    if not qr_data:
        return {
            "qrcode": None,
            "message": "QR Code não disponível. A instância pode já estar conectada."
        }
    
    # Atualizar QR no banco
    instancia.qr_code = qr_data.get("qrcode")
    db.commit()
    
    return {
        "qrcode": qr_data.get("qrcode"),
        "code": qr_data.get("code")
    }


@router.get("/status", response_model=StatusResponse)
def get_status(
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    """
    Obtém status da conexão do WhatsApp
    """
    instancia = WhatsAppService.buscar_instancia(db, cliente.id)
    
    if not instancia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instância não encontrada. Crie uma primeiro."
        )
    
    status_data = WhatsAppService.obter_status(instancia.instance_id)
    
    # Atualizar status no banco
    from app.db.models.instancia_whatsapp import InstanciaStatus
    novo_status = InstanciaStatus(status_data["status"])
    WhatsAppService.atualizar_status(db, instancia.instance_id, novo_status)
    
    return {
        "status": status_data["status"].lower(),  # Retornar em minúsculo para o frontend
        "state": status_data["state"],
        "numero": instancia.numero
    }


@router.delete("/instance")
def desconectar_instancia(
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    """
    Desconecta instância do WhatsApp
    """
    instancia = WhatsAppService.buscar_instancia(db, cliente.id)
    
    if not instancia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instância não encontrada."
        )
    
    success = WhatsAppService.desconectar_instancia(instancia.instance_id)
    
    if success:
        # Atualizar status no banco
        from app.db.models.instancia_whatsapp import InstanciaStatus
        WhatsAppService.atualizar_status(db, instancia.instance_id, InstanciaStatus.DESCONECTADA)
        
        return {"message": "Instância desconectada com sucesso"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao desconectar instância"
        )
