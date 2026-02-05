"""
Service para gerenciar conhecimento do bot
"""
from sqlalchemy.orm import Session
from typing import List, Dict
import logging

from app.db.models.conhecimento import Conhecimento


logger = logging.getLogger(__name__)


class ConhecimentoService:
    """Service para CRUD de conhecimento + chunking"""
    
    # Constantes
    MAX_CHARS = 50000
    CHUNK_SIZE = 800  # ~800 caracteres por chunk
    OVERLAP_PERCENT = 0.20  # 20% de overlap
    
    @staticmethod
    def buscar_ou_criar(db: Session, cliente_id: int) -> Conhecimento:
        """
        Busca conhecimento do cliente ou cria um novo vazio
        """
        conhecimento = db.query(Conhecimento).filter(
            Conhecimento.cliente_id == cliente_id
        ).first()
        
        if not conhecimento:
            conhecimento = Conhecimento(
                cliente_id=cliente_id,
                conteudo_texto=""
            )
            db.add(conhecimento)
            db.commit()
            db.refresh(conhecimento)
        
        return conhecimento
    
    @staticmethod
    def atualizar(db: Session, cliente_id: int, conteudo: str) -> Conhecimento:
        """
        Atualiza conhecimento do cliente
        Valida limite de 50.000 caracteres
        Gera embeddings e salva no ChromaDB
        """
        # Validar tamanho
        if len(conteudo) > ConhecimentoService.MAX_CHARS:
            raise ValueError(f"Conteúdo excede o limite de {ConhecimentoService.MAX_CHARS} caracteres")
        
        conhecimento = ConhecimentoService.buscar_ou_criar(db, cliente_id)
        conhecimento.conteudo_texto = conteudo
        
        db.commit()
        db.refresh(conhecimento)
        
        logger.info(f"Conhecimento atualizado para cliente {cliente_id}: {len(conteudo)} chars")
        
        # Gerar chunks e embeddings
        if conteudo and len(conteudo.strip()) > 0:
            try:
                from app.services.rag.vectorstore import criar_vectorstore_de_chunks
                
                chunks = ConhecimentoService.gerar_chunks(conteudo)
                logger.info(f"Gerando embeddings para {len(chunks)} chunks do cliente {cliente_id}")
                
                criar_vectorstore_de_chunks(cliente_id, chunks)
                logger.info(f"Embeddings gerados com sucesso para cliente {cliente_id}")
                
            except Exception as e:
                logger.error(f"Erro ao gerar embeddings para cliente {cliente_id}: {e}")
                # Não falhar a operação se embeddings falharem
        else:
            # Se conteúdo vazio, deletar vectorstore
            try:
                from app.services.rag.vectorstore import deletar_vectorstore_cliente
                deletar_vectorstore_cliente(cliente_id)
                logger.info(f"Vectorstore deletado para cliente {cliente_id} (conteúdo vazio)")
            except Exception as e:
                logger.warning(f"Erro ao deletar vectorstore: {e}")
        
        return conhecimento
    
    @staticmethod
    def gerar_chunks(texto: str) -> List[Dict[str, any]]:
        """
        Divide o texto em chunks com overlap
        
        Retorna lista de dicts com:
        - text: texto do chunk
        - start: posição inicial no texto original
        - end: posição final no texto original
        - index: índice do chunk
        """
        if not texto or len(texto.strip()) == 0:
            return []
        
        chunks = []
        chunk_size = ConhecimentoService.CHUNK_SIZE
        overlap_size = int(chunk_size * ConhecimentoService.OVERLAP_PERCENT)
        
        start = 0
        index = 0
        
        while start < len(texto):
            # Calcular fim do chunk
            end = start + chunk_size
            
            # Se não é o último chunk, tentar quebrar em espaço/pontuação
            if end < len(texto):
                # Procurar último espaço ou pontuação nos últimos 100 chars
                search_start = max(end - 100, start)
                last_break = max(
                    texto.rfind(' ', search_start, end),
                    texto.rfind('\n', search_start, end),
                    texto.rfind('.', search_start, end),
                    texto.rfind('!', search_start, end),
                    texto.rfind('?', search_start, end),
                )
                
                if last_break > start:
                    end = last_break + 1
            else:
                end = len(texto)
            
            # Extrair chunk
            chunk_text = texto[start:end].strip()
            
            if chunk_text:  # Só adicionar se não for vazio
                chunks.append({
                    'text': chunk_text,
                    'start': start,
                    'end': end,
                    'index': index
                })
                index += 1
            
            # Próximo chunk começa com overlap
            start = end - overlap_size
            
            # Evitar loop infinito
            if start >= len(texto):
                break
        
        logger.info(f"Gerados {len(chunks)} chunks de ~{chunk_size} chars com {overlap_size} chars de overlap")
        
        return chunks
