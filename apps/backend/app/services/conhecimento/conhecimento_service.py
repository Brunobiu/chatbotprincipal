"""
Service para gerenciar conhecimento do bot
"""
from sqlalchemy.orm import Session
from typing import List, Dict
import logging

from app.db.models.conhecimento import Conhecimento
from app.services.conhecimento.estruturador_service import EstruturadorService


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
    def _limpar_texto_ia(texto: str) -> str:
        """
        Remove introduções/comentários da IA que podem estar no texto
        
        Exemplos de padrões removidos:
        - "Com certeza! Para alimentar uma base de conhecimento..."
        - "Aqui está o conhecimento estruturado..."
        - Qualquer parágrafo que mencione "IA", "base de conhecimento", "estrutura"
        
        Returns:
            Texto limpo sem introduções da IA
        """
        import re
        
        linhas = texto.split('\n')
        linhas_limpas = []
        
        # Padrões que indicam introdução da IA (case insensitive)
        padroes_ia = [
            r'com certeza',
            r'para alimentar',
            r'base de conhecimento',
            r'estrutura.*clara',
            r'criei.*clínica',
            r'criei.*empresa',
            r'o texto abaixo',
            r'sua ia',
            r'inteligência artificial',
            r'aqui está',
            r'segue.*conhecimento'
        ]
        
        pular_linha = False
        
        for linha in linhas:
            linha_lower = linha.lower().strip()
            
            # Se linha vazia, manter
            if not linha_lower:
                linhas_limpas.append(linha)
                continue
            
            # Verificar se linha contém padrões de IA
            eh_introducao_ia = False
            for padrao in padroes_ia:
                if re.search(padrao, linha_lower):
                    eh_introducao_ia = True
                    logger.info(f"🧹 Removendo introdução da IA: {linha[:80]}...")
                    break
            
            # Se não é introdução, manter
            if not eh_introducao_ia:
                linhas_limpas.append(linha)
        
        texto_limpo = '\n'.join(linhas_limpas).strip()
        
        # Se removeu muita coisa, logar
        if len(texto_limpo) < len(texto) * 0.8:
            logger.info(f"🧹 Texto limpo: {len(texto)} → {len(texto_limpo)} caracteres")
        
        return texto_limpo
    
    @staticmethod
    def atualizar(db: Session, cliente_id: int, conteudo: str, modo: str = "substituir") -> Conhecimento:
        """
        Atualiza conhecimento do cliente
        Valida limite de 50.000 caracteres
        Estrutura automaticamente em JSON usando IA
        Gera embeddings estruturados
        
        Args:
            db: Sessão do banco
            cliente_id: ID do cliente
            conteudo: Novo conteúdo (texto livre)
            modo: "substituir" (padrão - sobrescreve), "mesclar" (incremental)
            
        Returns:
            Conhecimento atualizado
        """
        # Validar tamanho
        if len(conteudo) > ConhecimentoService.MAX_CHARS:
            raise ValueError(f"Conteúdo excede o limite de {ConhecimentoService.MAX_CHARS} caracteres")
        
        conhecimento = ConhecimentoService.buscar_ou_criar(db, cliente_id)
        
        # Modo padrão é sempre SUBSTITUIR (para testes)
        logger.info(f"💾 Modo: {modo.upper()}")
        
        # 🧹 LIMPAR TEXTO: Remover introduções da IA se houver
        conteudo_limpo = ConhecimentoService._limpar_texto_ia(conteudo)
        
        # Atualizar texto
        conhecimento.conteudo_texto = conteudo_limpo
        
        # 🚀 ESTRUTURAR OU MESCLAR CONHECIMENTO COM IA
        try:
            if modo == "mesclar" and conhecimento.conteudo_estruturado:
                logger.info(f"🔄 Mesclando conhecimento existente com novo texto...")
                conhecimento_estruturado = EstruturadorService.mesclar_conhecimento(
                    existente=conhecimento.conteudo_estruturado,
                    novo_texto=conteudo_limpo
                )
            else:
                logger.info(f"📊 Estruturando conhecimento do zero...")
                conhecimento_estruturado = EstruturadorService.estruturar_conhecimento(conteudo_limpo)
            
            conhecimento.conteudo_estruturado = conhecimento_estruturado
            logger.info(f"✅ Conhecimento estruturado com sucesso!")
            
            # Salvar no banco antes de gerar embeddings
            db.commit()
            db.refresh(conhecimento)
            
            # 🔢 GERAR EMBEDDINGS ESTRUTURADOS
            logger.info(f"🔢 Gerando embeddings estruturados...")
            from app.services.conhecimento.embeddings_service import EmbeddingsService
            
            sucesso = EmbeddingsService.gerar_embeddings_estruturados(
                cliente_id=cliente_id,
                conhecimento_json=conhecimento_estruturado
            )
            
            if sucesso:
                logger.info(f"✅ Embeddings gerados com sucesso!")
            else:
                logger.warning(f"⚠️ Falha ao gerar embeddings - bot usará texto direto")
                
        except Exception as e:
            logger.error(f"❌ Erro ao estruturar/gerar embeddings: {e}", exc_info=True)
            # Continuar mesmo se estruturação falhar
            conhecimento.conteudo_estruturado = None
        
        db.commit()
        db.refresh(conhecimento)
        
        logger.info(f"Conhecimento atualizado para cliente {cliente_id}: {len(conteudo)} chars")
        
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
