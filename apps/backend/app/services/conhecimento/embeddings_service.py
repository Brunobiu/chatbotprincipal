"""
Service para gerar embeddings de conhecimento estruturado
"""
import logging
from typing import Dict, Any, List
import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingsService:
    """Service para gerar e gerenciar embeddings de conhecimento estruturado"""
    
    @staticmethod
    def gerar_embeddings_estruturados(
        cliente_id: int,
        conhecimento_json: Dict[str, Any]
    ) -> bool:
        """
        Gera embeddings separados por seção do JSON estruturado
        
        Args:
            cliente_id: ID do cliente
            conhecimento_json: JSON estruturado do conhecimento
            
        Returns:
            bool: True se sucesso, False se erro
        """
        try:
            logger.info(f"🔄 Gerando embeddings estruturados para cliente {cliente_id}")
            
            # Conectar ao ChromaDB
            chroma_client = chromadb.HttpClient(
                host=settings.CHROMA_HOST,
                port=settings.CHROMA_PORT,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Nome da coleção por cliente
            collection_name = f"cliente_{cliente_id}_conhecimento"
            
            # Deletar coleção existente (para recriar)
            try:
                chroma_client.delete_collection(name=collection_name)
                logger.info(f"🗑️ Coleção antiga deletada: {collection_name}")
            except Exception:
                pass  # Coleção não existe, tudo bem
            
            # Criar nova coleção
            collection = chroma_client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            # Gerar chunks estruturados
            chunks = EmbeddingsService._gerar_chunks_estruturados(conhecimento_json)
            
            if not chunks:
                logger.warning(f"⚠️ Nenhum chunk gerado para cliente {cliente_id}")
                return False
            
            logger.info(f"📦 Gerados {len(chunks)} chunks estruturados")
            
            # Gerar embeddings com OpenAI
            embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")
            
            # Preparar dados para ChromaDB
            texts = [chunk['text'] for chunk in chunks]
            metadatas = [chunk['metadata'] for chunk in chunks]
            ids = [f"chunk_{i}" for i in range(len(chunks))]
            
            # Gerar embeddings
            logger.info(f"🔢 Gerando embeddings com OpenAI...")
            embeddings = embeddings_model.embed_documents(texts)
            
            # Adicionar ao ChromaDB
            collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"✅ {len(chunks)} embeddings salvos no ChromaDB!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar embeddings estruturados: {e}", exc_info=True)
            return False
    
    @staticmethod
    def _gerar_chunks_estruturados(conhecimento_json: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Gera chunks estruturados do JSON
        Cada seção importante vira um chunk separado
        
        Returns:
            Lista de dicts com 'text' e 'metadata'
        """
        chunks = []
        
        # 1. INFORMAÇÕES GERAIS
        info_geral = []
        if conhecimento_json.get("nome_empresa"):
            info_geral.append(f"Empresa: {conhecimento_json['nome_empresa']}")
        if conhecimento_json.get("tipo_negocio"):
            info_geral.append(f"Tipo: {conhecimento_json['tipo_negocio']}")
        
        if info_geral:
            chunks.append({
                'text': "\n".join(info_geral),
                'metadata': {
                    'tipo': 'informacoes_gerais',
                    'categoria': 'empresa'
                }
            })
        
        # 2. HORÁRIO DE FUNCIONAMENTO
        if conhecimento_json.get("horario_funcionamento"):
            h = conhecimento_json["horario_funcionamento"]
            texto_horario = []
            
            if h.get("dias"):
                texto_horario.append(f"Dias: {h['dias']}")
            if h.get("horario"):
                texto_horario.append(f"Horário: {h['horario']}")
            if h.get("observacoes"):
                texto_horario.append(f"Observações: {h['observacoes']}")
            
            if texto_horario:
                chunks.append({
                    'text': "HORÁRIO DE FUNCIONAMENTO\n" + "\n".join(texto_horario),
                    'metadata': {
                        'tipo': 'horario',
                        'categoria': 'operacional'
                    }
                })
        
        # 3. SERVIÇOS (cada serviço = 1 chunk)
        if conhecimento_json.get("servicos"):
            for idx, servico in enumerate(conhecimento_json["servicos"]):
                texto_servico = []
                
                categoria = servico.get("categoria", "Serviço")
                nome = servico.get("nome", "")
                
                texto_servico.append(f"SERVIÇO: {categoria} - {nome}")
                
                if servico.get("preco"):
                    texto_servico.append(f"Preço: R$ {servico['preco']:.2f}")
                
                if servico.get("descricao"):
                    texto_servico.append(f"Descrição: {servico['descricao']}")
                
                if servico.get("tempo_estimado"):
                    texto_servico.append(f"Tempo: {servico['tempo_estimado']}")
                
                if servico.get("observacoes"):
                    texto_servico.append(f"Observações: {servico['observacoes']}")
                
                chunks.append({
                    'text': "\n".join(texto_servico),
                    'metadata': {
                        'tipo': 'servico',
                        'categoria': categoria,
                        'nome': nome,
                        'preco': servico.get("preco")
                    }
                })
        
        # 4. PRODUTOS (cada produto = 1 chunk)
        if conhecimento_json.get("produtos"):
            for produto in conhecimento_json["produtos"]:
                texto_produto = []
                
                nome = produto.get("nome", "")
                texto_produto.append(f"PRODUTO: {nome}")
                
                if produto.get("preco"):
                    texto_produto.append(f"Preço: R$ {produto['preco']:.2f}")
                
                if produto.get("descricao"):
                    texto_produto.append(f"Descrição: {produto['descricao']}")
                
                chunks.append({
                    'text': "\n".join(texto_produto),
                    'metadata': {
                        'tipo': 'produto',
                        'nome': nome,
                        'preco': produto.get("preco")
                    }
                })
        
        # 5. ENTREGA/BUSCA
        if conhecimento_json.get("entrega_busca"):
            eb = conhecimento_json["entrega_busca"]
            texto_entrega = ["ENTREGA E BUSCA"]
            
            if eb.get("disponivel"):
                texto_entrega.append("Disponível: Sim")
                
                if eb.get("raio_km"):
                    texto_entrega.append(f"Raio: {eb['raio_km']} km")
                
                if eb.get("custo"):
                    if isinstance(eb["custo"], dict):
                        texto_entrega.append("Custos:")
                        for tipo, valor in eb["custo"].items():
                            texto_entrega.append(f"  - {tipo}: R$ {valor:.2f}")
                    else:
                        texto_entrega.append(f"Custo: {eb['custo']}")
                
                if eb.get("observacoes"):
                    texto_entrega.append(f"Observações: {eb['observacoes']}")
            else:
                texto_entrega.append("Disponível: Não")
            
            chunks.append({
                'text': "\n".join(texto_entrega),
                'metadata': {
                    'tipo': 'entrega_busca',
                    'categoria': 'logistica'
                }
            })
        
        # 6. PAGAMENTO
        if conhecimento_json.get("pagamento"):
            p = conhecimento_json["pagamento"]
            texto_pagamento = ["FORMAS DE PAGAMENTO"]
            
            if p.get("formas"):
                texto_pagamento.append("Aceitamos: " + ", ".join(p["formas"]))
            
            if p.get("chave_pix"):
                texto_pagamento.append(f"Chave Pix: {p['chave_pix']}")
            
            if p.get("observacoes"):
                texto_pagamento.append(f"Observações: {p['observacoes']}")
            
            chunks.append({
                'text': "\n".join(texto_pagamento),
                'metadata': {
                    'tipo': 'pagamento',
                    'categoria': 'financeiro'
                }
            })
        
        # 7. CONTATO
        if conhecimento_json.get("contato"):
            c = conhecimento_json["contato"]
            texto_contato = ["CONTATO"]
            
            if c.get("telefone"):
                texto_contato.append(f"Telefone: {c['telefone']}")
            if c.get("whatsapp"):
                texto_contato.append(f"WhatsApp: {c['whatsapp']}")
            if c.get("email"):
                texto_contato.append(f"Email: {c['email']}")
            if c.get("endereco"):
                texto_contato.append(f"Endereço: {c['endereco']}")
            
            if len(texto_contato) > 1:  # Tem pelo menos 1 info além do título
                chunks.append({
                    'text': "\n".join(texto_contato),
                    'metadata': {
                        'tipo': 'contato',
                        'categoria': 'informacoes'
                    }
                })
        
        # 8. CAPACIDADE
        if conhecimento_json.get("capacidade"):
            cap = conhecimento_json["capacidade"]
            texto_capacidade = ["CAPACIDADE"]
            
            if cap.get("descricao"):
                texto_capacidade.append(cap["descricao"])
            
            if cap.get("limites"):
                texto_capacidade.append("Limites:")
                for tipo, qtd in cap["limites"].items():
                    texto_capacidade.append(f"  - {tipo}: {qtd}")
            
            if len(texto_capacidade) > 1:
                chunks.append({
                    'text': "\n".join(texto_capacidade),
                    'metadata': {
                        'tipo': 'capacidade',
                        'categoria': 'operacional'
                    }
                })
        
        # 9. LINKS
        if conhecimento_json.get("links"):
            links = conhecimento_json["links"]
            texto_links = ["LINKS E REDES SOCIAIS"]
            
            for tipo, url in links.items():
                if url:
                    texto_links.append(f"{tipo.capitalize()}: {url}")
            
            if len(texto_links) > 1:
                chunks.append({
                    'text': "\n".join(texto_links),
                    'metadata': {
                        'tipo': 'links',
                        'categoria': 'informacoes'
                    }
                })
        
        # 10. POLÍTICAS (cada política = 1 chunk)
        if conhecimento_json.get("politicas"):
            for idx, politica in enumerate(conhecimento_json["politicas"]):
                chunks.append({
                    'text': f"POLÍTICA/REGRA: {politica}",
                    'metadata': {
                        'tipo': 'politica',
                        'categoria': 'regras',
                        'indice': idx
                    }
                })
        
        # 11. PERGUNTAS FREQUENTES
        if conhecimento_json.get("perguntas_frequentes"):
            for idx, faq in enumerate(conhecimento_json["perguntas_frequentes"]):
                texto_faq = [
                    f"PERGUNTA: {faq.get('pergunta', '')}",
                    f"RESPOSTA: {faq.get('resposta', '')}"
                ]
                
                chunks.append({
                    'text': "\n".join(texto_faq),
                    'metadata': {
                        'tipo': 'faq',
                        'categoria': 'ajuda',
                        'indice': idx
                    }
                })
        
        # 12. INFORMAÇÕES ADICIONAIS
        if conhecimento_json.get("informacoes_adicionais"):
            chunks.append({
                'text': f"INFORMAÇÕES ADICIONAIS\n{conhecimento_json['informacoes_adicionais']}",
                'metadata': {
                    'tipo': 'informacoes_adicionais',
                    'categoria': 'geral'
                }
            })
        
        logger.info(f"📦 Gerados {len(chunks)} chunks estruturados")
        return chunks
