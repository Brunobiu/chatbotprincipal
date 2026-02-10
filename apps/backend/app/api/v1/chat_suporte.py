"""API de Chat Suporte"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, time
from pydantic import BaseModel
import asyncio
from app.db.session import get_db
from app.db.models.admin_status import AdminStatus
from app.db.models.chat_suporte import ChatSuporteConversa, ChatSuporteMensagem
from app.api.v1.auth import get_current_cliente

router = APIRouter()

class EnviarMensagemRequest(BaseModel):
    mensagem: str

class ResponderMensagemRequest(BaseModel):
    mensagem: str

def esta_em_horario_atendimento() -> bool:
    agora = datetime.utcnow() - timedelta(hours=3)
    dia_semana = agora.weekday()
    if dia_semana >= 5:
        return False
    hora_atual = agora.time()
    return time(8, 0) <= hora_atual < time(18, 0)

@router.post("/admin/heartbeat")
def admin_heartbeat(db: Session = Depends(get_db)):
    status = db.query(AdminStatus).first()
    if not status:
        status = AdminStatus(online=True, ultimo_acesso=datetime.utcnow())
        db.add(status)
    else:
        status.online = True
        status.ultimo_acesso = datetime.utcnow()
    db.commit()
    return {"status": "online"}

@router.get("/admin/status")
def verificar_admin_online(db: Session = Depends(get_db)):
    em_horario = esta_em_horario_atendimento()
    if not em_horario:
        return {"online": False, "ultimo_acesso": None, "mensagem": "Offline - Atendimento: Seg-Sex, 8h-18h", "em_horario_atendimento": False}
    status = db.query(AdminStatus).first()
    if not status:
        return {"online": False, "ultimo_acesso": None, "mensagem": "Offline", "em_horario_atendimento": True}
    dois_minutos_atras = datetime.utcnow() - timedelta(minutes=2)
    online = status.online and status.ultimo_acesso > dois_minutos_atras
    if status.ultimo_acesso:
        tempo_offline = datetime.utcnow() - status.ultimo_acesso
        minutos = int(tempo_offline.total_seconds() / 60)
        if minutos < 1:
            mensagem = "Online agora"
        elif minutos < 60:
            mensagem = f"Última vez há {minutos} minuto{'s' if minutos > 1 else ''}"
        else:
            horas = int(minutos / 60)
            mensagem = f"Última vez há {horas} hora{'s' if horas > 1 else ''}"
    else:
        mensagem = "Offline"
    return {"online": online, "ultimo_acesso": status.ultimo_acesso.isoformat() if status.ultimo_acesso else None, "mensagem": mensagem if not online else "Online - Seg-Sex, 8h-18h", "em_horario_atendimento": True}

@router.post("/mensagem")
async def enviar_mensagem(request: EnviarMensagemRequest, cliente = Depends(get_current_cliente), db: Session = Depends(get_db)):
    conversa = db.query(ChatSuporteConversa).filter(ChatSuporteConversa.cliente_id == cliente.id, ChatSuporteConversa.status.in_(["nao_respondido", "respondido"])).first()
    primeira_mensagem = False
    if not conversa:
        conversa = ChatSuporteConversa(cliente_id=cliente.id, status="nao_respondido", visualizado_admin=False, bot_respondeu_boas_vindas=False, bot_respondeu_aguarde=False)
        db.add(conversa)
        db.commit()
        db.refresh(conversa)
        primeira_mensagem = True
    mensagem = ChatSuporteMensagem(conversa_id=conversa.id, remetente_tipo="cliente", remetente_id=cliente.id, mensagem=request.mensagem)
    db.add(mensagem)
    conversa.ultima_mensagem_em = datetime.utcnow()
    conversa.ultima_mensagem_cliente = datetime.utcnow()
    conversa.visualizado_admin = False
    db.commit()
    db.refresh(mensagem)
    if primeira_mensagem or not conversa.bot_respondeu_boas_vindas:
        await asyncio.sleep(5)
        em_horario = esta_em_horario_atendimento()
        if em_horario:
            mensagem_bot = "Olá! Tudo bem? Logo uma pessoa irá te atender.\nEnquanto isso, pode descrever o seu problema.\nSe precisar enviar alguma imagem, abra um ticket."
        else:
            mensagem_bot = "No momento, estamos offline.\nNosso atendimento é de segunda a sexta, das 8h às 18h.\nPode mandar sua dúvida que assim que estivermos online, vamos atendê-lo."
        mensagem_auto = ChatSuporteMensagem(conversa_id=conversa.id, remetente_tipo="sistema", remetente_id=None, mensagem=mensagem_bot)
        db.add(mensagem_auto)
        conversa.bot_respondeu_boas_vindas = True
        db.commit()
    return {"id": mensagem.id, "mensagem": mensagem.mensagem, "created_at": mensagem.created_at.isoformat()}

@router.get("/historico")
def obter_historico(cliente = Depends(get_current_cliente), db: Session = Depends(get_db)):
    conversa = db.query(ChatSuporteConversa).filter(ChatSuporteConversa.cliente_id == cliente.id).order_by(ChatSuporteConversa.iniciada_em.desc()).first()
    if not conversa:
        return {"mensagens": [], "deve_sugerir_ticket": False}
    if (conversa.ultima_mensagem_cliente and not conversa.bot_respondeu_aguarde and conversa.bot_respondeu_boas_vindas and conversa.status == "nao_respondido"):
        tempo_desde_ultima = datetime.utcnow() - conversa.ultima_mensagem_cliente
        if tempo_desde_ultima > timedelta(minutes=1):
            mensagem_aguarde = ChatSuporteMensagem(conversa_id=conversa.id, remetente_tipo="sistema", remetente_id=None, mensagem="Aguarde, já iremos atender você.")
            db.add(mensagem_aguarde)
            conversa.bot_respondeu_aguarde = True
            db.commit()
    mensagens = db.query(ChatSuporteMensagem).filter(ChatSuporteMensagem.conversa_id == conversa.id).order_by(ChatSuporteMensagem.created_at.asc()).all()
    deve_sugerir_ticket = False
    if conversa.status == "nao_respondido":
        tempo_desde_inicio = datetime.utcnow() - conversa.iniciada_em
        if tempo_desde_inicio > timedelta(hours=1):
            deve_sugerir_ticket = True
    return {"mensagens": [{"id": msg.id, "remetente_tipo": msg.remetente_tipo, "mensagem": msg.mensagem, "created_at": msg.created_at.isoformat()} for msg in mensagens], "deve_sugerir_ticket": deve_sugerir_ticket}

@router.get("/admin/conversas")
def listar_conversas_admin(db: Session = Depends(get_db)):
    from app.db.models.cliente import Cliente
    conversas = db.query(ChatSuporteConversa).filter(ChatSuporteConversa.status.in_(["nao_respondido", "respondido"])).order_by(ChatSuporteConversa.ultima_mensagem_em.desc()).all()
    resultado = []
    for conv in conversas:
        cliente = db.query(Cliente).filter(Cliente.id == conv.cliente_id).first()
        msgs_nao_vistas = db.query(ChatSuporteMensagem).filter(ChatSuporteMensagem.conversa_id == conv.id, ChatSuporteMensagem.remetente_tipo == "cliente", ChatSuporteMensagem.visualizado == False).count()
        ultima_msg = db.query(ChatSuporteMensagem).filter(ChatSuporteMensagem.conversa_id == conv.id).order_by(ChatSuporteMensagem.created_at.desc()).first()
        resultado.append({"id": conv.id, "cliente_id": conv.cliente_id, "cliente_nome": cliente.nome if cliente else "Cliente", "status": conv.status, "mensagens_nao_vistas": msgs_nao_vistas, "ultima_mensagem": ultima_msg.mensagem if ultima_msg else "", "ultima_mensagem_em": conv.ultima_mensagem_em.isoformat() if conv.ultima_mensagem_em else None})
    return resultado

@router.get("/admin/conversas/{conversa_id}/mensagens")
def obter_mensagens_conversa(conversa_id: int, db: Session = Depends(get_db)):
    mensagens = db.query(ChatSuporteMensagem).filter(ChatSuporteMensagem.conversa_id == conversa_id).order_by(ChatSuporteMensagem.created_at.asc()).all()
    db.query(ChatSuporteMensagem).filter(ChatSuporteMensagem.conversa_id == conversa_id, ChatSuporteMensagem.remetente_tipo == "cliente").update({"visualizado": True})
    conversa = db.query(ChatSuporteConversa).filter(ChatSuporteConversa.id == conversa_id).first()
    if conversa:
        conversa.visualizado_admin = True
    db.commit()
    return [{"id": msg.id, "remetente_tipo": msg.remetente_tipo, "mensagem": msg.mensagem, "created_at": msg.created_at.isoformat()} for msg in mensagens]

@router.post("/admin/conversas/{conversa_id}/responder")
def admin_responder(conversa_id: int, request: ResponderMensagemRequest, db: Session = Depends(get_db)):
    conversa = db.query(ChatSuporteConversa).filter(ChatSuporteConversa.id == conversa_id).first()
    if not conversa:
        return {"error": "Conversa não encontrada"}
    mensagem = ChatSuporteMensagem(conversa_id=conversa_id, remetente_tipo="admin", remetente_id=1, mensagem=request.mensagem)
    db.add(mensagem)
    conversa.status = "respondido"
    conversa.ultima_mensagem_admin_em = datetime.utcnow()
    conversa.ultima_mensagem_em = datetime.utcnow()
    db.commit()
    db.refresh(mensagem)
    return {"id": mensagem.id, "mensagem": mensagem.mensagem, "created_at": mensagem.created_at.isoformat()}

@router.get("/admin/conversas/nao-visualizadas/count")
def contar_nao_visualizadas(db: Session = Depends(get_db)):
    count = db.query(ChatSuporteConversa).filter(ChatSuporteConversa.visualizado_admin == False, ChatSuporteConversa.status.in_(["nao_respondido", "respondido"])).count()
    return {"count": count}

@router.post("/admin/conversas/{conversa_id}/encerrar")
def encerrar_conversa(conversa_id: int, db: Session = Depends(get_db)):
    conversa = db.query(ChatSuporteConversa).filter(ChatSuporteConversa.id == conversa_id).first()
    if not conversa:
        return {"error": "Conversa não encontrada"}
    conversa.status = "concluido"
    conversa.encerrada_em = datetime.utcnow()
    conversa.encerrada_por = 1
    db.commit()
    return {"success": True, "message": "Conversa encerrada"}

