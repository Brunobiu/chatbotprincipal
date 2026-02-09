"""
Buffer de mensagens com suporte a multi-tenant
"""
import asyncio
import redis.asyncio as redis
import logging
from collections import defaultdict
from typing import Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.whatsapp.evolution_api import send_whatsapp_message
from app.services.ai import AIService
from app.services.confianca import ConfiancaService
from app.services.fallback import FallbackService
from app.db.session import SessionLocal
from app.db.models.mensagem import Mensagem
from app.db.models.conversa import Conversa, StatusConversa, MotivoFallback

logger = logging.getLogger(__name__)

redis_client = redis.Redis.from_url(settings.CACHE_REDIS_URI, decode_responses=True)
debounce_tasks = defaultdict(asyncio.Task)


async def buffer_message(chat_id: str, message: str, cliente_id: Optional[int] = None):
    """
    Adiciona mensagem ao buffer com debounce
    
    Args:
        chat_id: ID do chat (número do WhatsApp)
        message: Mensagem recebida
        cliente_id: ID do cliente (para isolamento multi-tenant)
    """
    buffer_key = f'{chat_id}{settings.BUFFER_KEY_SUFIX}'

    await redis_client.rpush(buffer_key, message)
    await redis_client.expire(buffer_key, int(settings.BUFFER_TTL))

    logger.info(f'[BUFFER] Mensagem adicionada ao buffer de {chat_id}: {message}')

    if debounce_tasks.get(chat_id):
        debounce_tasks[chat_id].cancel()
        logger.info(f'[BUFFER] Debounce resetado para {chat_id}')

    debounce_tasks[chat_id] = asyncio.create_task(
        handle_debounce(chat_id, cliente_id)
    )


async def handle_debounce(chat_id: str, cliente_id: Optional[int] = None):
    """
    Processa mensagens após debounce
    
    Args:
        chat_id: ID do chat
        cliente_id: ID do cliente (para isolamento multi-tenant)
    """
    try:
        logger.info(f'[BUFFER] Iniciando debounce para {chat_id}')
        await asyncio.sleep(float(settings.DEBOUNCE_SECONDS))

        buffer_key = f'{chat_id}{settings.BUFFER_KEY_SUFIX}'
        messages = await redis_client.lrange(buffer_key, 0, -1)

        full_message = ' '.join(messages).strip()
        if full_message:
            logger.info(f'[BUFFER] Processando mensagem para {chat_id}: {full_message}')
            
            if not cliente_id:
                logger.error(f'[BUFFER] Cliente ID não fornecido para {chat_id}')
                return
            
            # Criar session_id único por cliente + chat
            session_id = f'cliente_{cliente_id}_{chat_id}'
            
            # Verificar se é primeira interação
            from app.services.contexto import ContextoUsuarioService
            
            eh_primeira = ContextoUsuarioService.eh_primeira_interacao(db, cliente_id, chat_id)
            nome_usuario = ContextoUsuarioService.obter_nome_usuario(db, cliente_id, chat_id)
            
            # Se é primeira interação, criar contexto e perguntar nome
            if eh_primeira:
                logger.info(f'[CONTEXTO] Primeira interação de {chat_id} - perguntando nome')
                ContextoUsuarioService.criar_contexto(db, cliente_id, chat_id)
                
                send_whatsapp_message(
                    number=chat_id,
                    text="Olá! 👋 Qual é o seu nome?",
                    db=db,
                    cliente_id=cliente_id
                )
                
                # Salvar mensagem do usuário
                conversa = db.query(Conversa).filter(
                    Conversa.cliente_id == cliente_id,
                    Conversa.numero_whatsapp == chat_id
                ).first()
                
                if not conversa:
                    conversa = Conversa(
                        cliente_id=cliente_id,
                        numero_whatsapp=chat_id,
                        status="ativa"
                    )
                    db.add(conversa)
                    db.commit()
                    db.refresh(conversa)
                
                mensagem_user = Mensagem(
                    conversa_id=conversa.id,
                    conteudo=full_message,
                    tipo="usuario",
                    confidence_score=None,
                    fallback_triggered=False
                )
                mensagem_bot = Mensagem(
                    conversa_id=conversa.id,
                    conteudo="Olá! 👋 Qual é o seu nome?",
                    tipo="ia",
                    confidence_score=None,
                    fallback_triggered=False
                )
                db.add(mensagem_user)
                db.add(mensagem_bot)
                db.commit()
                
                await redis_client.delete(buffer_key)
                if chat_id in debounce_tasks:
                    del debounce_tasks[chat_id]
                return
            
            # Se não tem nome ainda, tentar detectar na mensagem
            if not nome_usuario:
                nome_detectado = ContextoUsuarioService.detectar_nome_na_mensagem(full_message)
                if nome_detectado:
                    logger.info(f'[CONTEXTO] Nome detectado: {nome_detectado}')
                    ContextoUsuarioService.salvar_nome_usuario(db, cliente_id, chat_id, nome_detectado)
                    nome_usuario = nome_detectado
                    
                    # Responder com saudação personalizada
                    send_whatsapp_message(
                        number=chat_id,
                        text=f"Prazer em conhecer você, {nome_usuario}! 😊 Como posso ajudar?",
                        db=db,
                        cliente_id=cliente_id
                    )
                    
                    # Salvar mensagens
                    conversa = db.query(Conversa).filter(
                        Conversa.cliente_id == cliente_id,
                        Conversa.numero_whatsapp == chat_id
                    ).first()
                    
                    if conversa:
                        mensagem_user = Mensagem(
                            conversa_id=conversa.id,
                            conteudo=full_message,
                            tipo="usuario",
                            confidence_score=None,
                            fallback_triggered=False
                        )
                        mensagem_bot = Mensagem(
                            conversa_id=conversa.id,
                            conteudo=f"Prazer em conhecer você, {nome_usuario}! 😊 Como posso ajudar?",
                            tipo="ia",
                            confidence_score=None,
                            fallback_triggered=False
                        )
                        db.add(mensagem_user)
                        db.add(mensagem_bot)
                        db.commit()
                    
                    await redis_client.delete(buffer_key)
                    if chat_id in debounce_tasks:
                        del debounce_tasks[chat_id]
                    return
            
            # Atualizar última interação
            ContextoUsuarioService.atualizar_ultima_interacao(db, cliente_id, chat_id)
            
            # Buscar configurações do cliente
            db = SessionLocal()
            try:
                from app.services.configuracoes import ConfiguracaoService
                config = ConfiguracaoService.buscar_ou_criar(db, cliente_id)
                tom = config.tom.value
                threshold_confianca = config.threshold_confianca
                
                logger.info(f'[BUFFER] Usando tom: {tom}, threshold: {threshold_confianca}')
                
                # TASK 10.6: Detectar pedidos de agendamento
                from app.services.agendamentos import AgendamentoService
                from app.services.agendamentos.agendamento_ai_parser import AgendamentoAIParser
                
                parser = AgendamentoAIParser()
                
                # Verificar se mensagem contém intenção de agendamento
                if parser.detectar_intencao_agendamento(full_message):
                    logger.info(f'[AGENDAMENTO] Intenção de agendamento detectada: {chat_id}')
                    
                    # Buscar configuração de horários do cliente
                    config_horarios = AgendamentoService.obter_configuracao(db, cliente_id)
                    tipos_servico = config_horarios.tipos_servico if config_horarios else None
                    
                    # Extrair informações do agendamento
                    info_agendamento = parser.extrair_informacoes_agendamento(full_message, tipos_servico)
                    
                    if info_agendamento:
                        logger.info(f'[AGENDAMENTO] Informações extraídas: {info_agendamento}')
                        
                        # Criar agendamento
                        agendamento = AgendamentoService.criar_agendamento(
                            db=db,
                            cliente_id=cliente_id,
                            numero_usuario=chat_id,
                            nome_usuario=nome_usuario,
                            data_hora=info_agendamento['data_hora'],
                            tipo_servico=info_agendamento.get('tipo_servico'),
                            observacoes=info_agendamento.get('observacoes'),
                            mensagem_original=full_message
                        )
                        
                        # Gerar mensagem de confirmação
                        mensagem_confirmacao = parser.gerar_mensagem_confirmacao(
                            data_hora=agendamento.data_hora,
                            tipo_servico=agendamento.tipo_servico,
                            nome_usuario=nome_usuario
                        )
                        
                        # Enviar mensagem de confirmação
                        send_whatsapp_message(
                            number=chat_id,
                            text=mensagem_confirmacao,
                            db=db,
                            cliente_id=cliente_id
                        )
                        
                        logger.info(f'[AGENDAMENTO] Agendamento criado: ID={agendamento.id}')
                        
                        # Salvar mensagens
                        conversa = db.query(Conversa).filter(
                            Conversa.cliente_id == cliente_id,
                            Conversa.numero_whatsapp == chat_id
                        ).first()
                        
                        if not conversa:
                            conversa = Conversa(
                                cliente_id=cliente_id,
                                numero_whatsapp=chat_id,
                                status="ativa"
                            )
                            db.add(conversa)
                            db.commit()
                            db.refresh(conversa)
                        
                        mensagem_user = Mensagem(
                            conversa_id=conversa.id,
                            conteudo=full_message,
                            tipo="usuario",
                            confidence_score=None,
                            fallback_triggered=False
                        )
                        mensagem_bot = Mensagem(
                            conversa_id=conversa.id,
                            conteudo=mensagem_confirmacao,
                            tipo="ia",
                            confidence_score=None,
                            fallback_triggered=False
                        )
                        db.add(mensagem_user)
                        db.add(mensagem_bot)
                        db.commit()
                        
                        await redis_client.delete(buffer_key)
                        if chat_id in debounce_tasks:
                            del debounce_tasks[chat_id]
                        return
                
                # Verificar se cliente solicitou humano explicitamente
                solicitou_humano = ConfiancaService.detectar_solicitacao_humano(full_message)
                
                if solicitou_humano:
                    logger.info(f'[CONFIANÇA] Cliente solicitou atendimento humano: {chat_id}')
                    
                    # Acionar fallback
                    FallbackService.acionar_fallback(
                        db=db,
                        numero_whatsapp=chat_id,
                        cliente_id=cliente_id,
                        motivo=MotivoFallback.SOLICITACAO_MANUAL.value,
                        ultima_mensagem=full_message
                    )
                    
                    # Salvar mensagem do usuário
                    conversa = db.query(Conversa).filter(
                        Conversa.cliente_id == cliente_id,
                        Conversa.numero_whatsapp == chat_id
                    ).order_by(Conversa.created_at.desc()).first()
                    
                    if conversa:
                        mensagem_user = Mensagem(
                            conversa_id=conversa.id,
                            conteudo=full_message,
                            tipo="usuario",
                            confidence_score=None,
                            fallback_triggered=True
                        )
                        db.add(mensagem_user)
                        db.commit()
                    
                    await redis_client.delete(buffer_key)
                    if chat_id in debounce_tasks:
                        del debounce_tasks[chat_id]
                    return
                
                # Verificar se é primeira mensagem (não tem conversa ativa)
                conversa_existente = db.query(Conversa).filter(
                    Conversa.cliente_id == cliente_id,
                    Conversa.numero_whatsapp == chat_id
                ).first()
                primeira_mensagem = conversa_existente is None
                
                # Buscar nome da empresa do cliente
                from app.db.models.cliente import Cliente
                cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
                nome_empresa = cliente.nome_empresa if cliente else None
                
                # Processar com IA
                resultado = AIService.processar_mensagem(
                    cliente_id=cliente_id,
                    chat_id=session_id,
                    mensagem=full_message,
                    tom=tom,
                    nome_empresa=nome_empresa,
                    primeira_mensagem=primeira_mensagem,
                    nome_usuario=nome_usuario
                )
                
                resposta = resultado['resposta']
                confianca_basica = resultado['confianca']
                documentos = resultado.get('documentos', [])
                
                # Calcular confiança avançada usando ConfiancaService
                confianca = ConfiancaService.calcular_confianca(
                    query=full_message,
                    documentos=documentos,
                    resposta=resposta
                )
                
                logger.info(f'[CONFIANÇA] Score calculado: {confianca:.2f} (threshold: {threshold_confianca})')
                
                # Verificar se deve acionar fallback
                deve_fallback = ConfiancaService.deve_acionar_fallback(confianca, threshold_confianca)
                
                if deve_fallback:
                    logger.warning(f'[CONFIANÇA] Baixa confiança ({confianca:.2f}) - acionando fallback')
                    
                    # Acionar fallback
                    FallbackService.acionar_fallback(
                        db=db,
                        numero_whatsapp=chat_id,
                        cliente_id=cliente_id,
                        motivo=MotivoFallback.BAIXA_CONFIANCA.value,
                        ultima_mensagem=full_message
                    )
                    
                    # Salvar mensagem do usuário com fallback
                    conversa = db.query(Conversa).filter(
                        Conversa.cliente_id == cliente_id,
                        Conversa.numero_whatsapp == chat_id
                    ).order_by(Conversa.created_at.desc()).first()
                    
                    if conversa:
                        mensagem_user = Mensagem(
                            conversa_id=conversa.id,
                            conteudo=full_message,
                            tipo="usuario",
                            confidence_score=confianca,
                            fallback_triggered=True
                        )
                        db.add(mensagem_user)
                        db.commit()
                else:
                    # Confiança OK - enviar resposta normalmente
                    logger.info(f'[CONFIANÇA] Confiança OK ({confianca:.2f}) - enviando resposta')
                    
                    send_whatsapp_message(
                        number=chat_id,
                        text=resposta,
                        db=db,
                        cliente_id=cliente_id
                    )
                    
                    logger.info(f'[BUFFER] Resposta enviada para {chat_id}')
                    
                    # Buscar ou criar conversa
                    conversa = db.query(Conversa).filter(
                        Conversa.cliente_id == cliente_id,
                        Conversa.numero_whatsapp == chat_id,
                        Conversa.status == "ativa"
                    ).first()
                    
                    if not conversa:
                        conversa = Conversa(
                            cliente_id=cliente_id,
                            numero_whatsapp=chat_id,
                            status="ativa"
                        )
                        db.add(conversa)
                        db.commit()
                        db.refresh(conversa)
                    
                    # Salvar mensagens
                    mensagem_user = Mensagem(
                        conversa_id=conversa.id,
                        conteudo=full_message,
                        tipo="usuario",
                        confidence_score=confianca,
                        fallback_triggered=False
                    )
                    mensagem_bot = Mensagem(
                        conversa_id=conversa.id,
                        conteudo=resposta,
                        tipo="ia",
                        confidence_score=confianca,
                        fallback_triggered=False
                    )
                    db.add(mensagem_user)
                    db.add(mensagem_bot)
                    db.commit()
                
            finally:
                db.close()
            
        await redis_client.delete(buffer_key)
        
        # Limpar task do dict
        if chat_id in debounce_tasks:
            del debounce_tasks[chat_id]

    except asyncio.CancelledError:
        logger.info(f'[BUFFER] Debounce cancelado para {chat_id}')
    except Exception as e:
        logger.error(f'[BUFFER] Erro ao processar mensagem: {str(e)}', exc_info=True)
