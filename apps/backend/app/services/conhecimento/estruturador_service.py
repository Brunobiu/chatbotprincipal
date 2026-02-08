"""
Service para estruturar conhecimento em JSON usando IA
"""
import logging
import json
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.core.config import settings

logger = logging.getLogger(__name__)


class EstruturadorService:
    """Service para estruturar texto de conhecimento em JSON"""
    
    @staticmethod
    def estruturar_conhecimento(texto: str) -> Dict[str, Any]:
        """
        Usa IA para estruturar texto livre em JSON organizado
        
        Args:
            texto: Texto livre do conhecimento
            
        Returns:
            Dict com conhecimento estruturado em JSON
        """
        logger.info(f"Estruturando conhecimento: {len(texto)} caracteres")
        
        system_prompt = """Você é um especialista em estruturar informações de negócios em JSON.

Sua tarefa é analisar o texto fornecido e extrair TODAS as informações relevantes, organizando-as em um JSON estruturado.

ESTRUTURA DO JSON (adapte conforme o conteúdo):

{
  "nome_empresa": "string ou null",
  "tipo_negocio": "string (ex: lava-jato, restaurante, clínica, etc)",
  "horario_funcionamento": {
    "dias": "string",
    "horario": "string",
    "observacoes": "string ou null"
  },
  "servicos": [
    {
      "categoria": "string",
      "nome": "string",
      "preco": number ou null,
      "descricao": "string",
      "tempo_estimado": "string ou null",
      "observacoes": "string ou null"
    }
  ],
  "produtos": [
    {
      "nome": "string",
      "preco": number ou null,
      "descricao": "string"
    }
  ],
  "entrega_busca": {
    "disponivel": boolean,
    "raio_km": number ou null,
    "custo": "string ou object",
    "observacoes": "string ou null"
  },
  "pagamento": {
    "formas": ["array de strings"],
    "chave_pix": "string ou null",
    "observacoes": "string ou null"
  },
  "contato": {
    "telefone": "string ou null",
    "email": "string ou null",
    "whatsapp": "string ou null",
    "endereco": "string ou null"
  },
  "capacidade": {
    "descricao": "string ou null",
    "limites": {}
  },
  "links": {
    "site": "string ou null",
    "instagram": "string ou null",
    "facebook": "string ou null",
    "youtube": "string ou null"
  },
  "politicas": [
    "array de strings com regras, políticas, observações importantes"
  ],
  "perguntas_frequentes": [
    {
      "pergunta": "string",
      "resposta": "string"
    }
  ],
  "informacoes_adicionais": "string ou null"
}

REGRAS IMPORTANTES:
1. Extraia TODAS as informações do texto
2. Se uma seção não tiver informação, use null ou array vazio []
3. Mantenha preços como números (ex: 50.00, não "R$ 50,00")
4. Seja preciso e não invente informações
5. Organize de forma lógica e fácil de buscar
6. Retorne APENAS o JSON, sem texto adicional
7. Use UTF-8 para caracteres especiais

Analise o texto e retorne o JSON estruturado:"""

        try:
            llm = ChatOpenAI(
                model=settings.OPENAI_MODEL_NAME,
                temperature=0  # Temperatura 0 para ser mais preciso
            )
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=texto)
            ]
            
            response = llm.invoke(messages)
            json_text = response.content.strip()
            
            # Remover markdown se houver
            if json_text.startswith("```json"):
                json_text = json_text[7:]
            if json_text.startswith("```"):
                json_text = json_text[3:]
            if json_text.endswith("```"):
                json_text = json_text[:-3]
            
            json_text = json_text.strip()
            
            # Parse JSON
            conhecimento_estruturado = json.loads(json_text)
            
            logger.info(f"✅ Conhecimento estruturado com sucesso")
            logger.debug(f"JSON gerado: {json.dumps(conhecimento_estruturado, indent=2, ensure_ascii=False)}")
            
            return conhecimento_estruturado
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erro ao parsear JSON: {e}")
            logger.error(f"Resposta da IA: {json_text}")
            # Retornar estrutura mínima em caso de erro
            return {
                "tipo_negocio": "desconhecido",
                "informacoes_adicionais": texto,
                "erro_estruturacao": str(e)
            }
        except Exception as e:
            logger.error(f"❌ Erro ao estruturar conhecimento: {e}", exc_info=True)
            return {
                "tipo_negocio": "desconhecido",
                "informacoes_adicionais": texto,
                "erro_estruturacao": str(e)
            }
    
    @staticmethod
    def mesclar_conhecimento(existente: Dict[str, Any], novo_texto: str) -> Dict[str, Any]:
        """
        Mescla conhecimento existente com novo texto usando IA
        A IA decide o que manter, atualizar ou adicionar
        
        Args:
            existente: JSON estruturado existente
            novo_texto: Novo texto a ser adicionado/atualizado
            
        Returns:
            Dict com conhecimento mesclado
        """
        logger.info("🔄 Mesclando conhecimento existente com novo texto usando IA")
        
        # Converter JSON existente para texto legível
        existente_texto = json.dumps(existente, indent=2, ensure_ascii=False)
        
        system_prompt = """Você é um especialista em mesclar e atualizar bases de conhecimento em JSON.

Sua tarefa é receber:
1. Um JSON estruturado EXISTENTE (conhecimento atual)
2. Um NOVO TEXTO com informações adicionais ou atualizações

E retornar um JSON MESCLADO que:
- MANTÉM todas as informações existentes que não foram alteradas
- ATUALIZA informações que mudaram (ex: novos preços, horários)
- ADICIONA novas informações (ex: novos serviços, produtos)
- REMOVE informações explicitamente marcadas como removidas no novo texto

REGRAS IMPORTANTES:
1. NÃO delete informações a menos que o novo texto diga explicitamente para remover
2. Se houver conflito (ex: preço diferente), use a informação do NOVO TEXTO
3. Mantenha a mesma estrutura JSON do conhecimento existente
4. Adicione novos serviços/produtos à lista existente
5. Se o novo texto for vazio ou só tiver "nenhuma alteração", retorne o JSON existente sem mudanças
6. Retorne APENAS o JSON mesclado, sem texto adicional
7. Use UTF-8 para caracteres especiais

CONHECIMENTO EXISTENTE (JSON):
{existente_json}

NOVO TEXTO COM ATUALIZAÇÕES:
{novo_texto}

Analise e retorne o JSON mesclado:"""

        try:
            llm = ChatOpenAI(
                model=settings.OPENAI_MODEL_NAME,
                temperature=0
            )
            
            prompt = system_prompt.format(
                existente_json=existente_texto,
                novo_texto=novo_texto
            )
            
            messages = [
                SystemMessage(content=prompt)
            ]
            
            response = llm.invoke(messages)
            json_text = response.content.strip()
            
            # Remover markdown se houver
            if json_text.startswith("```json"):
                json_text = json_text[7:]
            if json_text.startswith("```"):
                json_text = json_text[3:]
            if json_text.endswith("```"):
                json_text = json_text[:-3]
            
            json_text = json_text.strip()
            
            # Parse JSON
            conhecimento_mesclado = json.loads(json_text)
            
            logger.info(f"✅ Conhecimento mesclado com sucesso!")
            logger.debug(f"JSON mesclado: {json.dumps(conhecimento_mesclado, indent=2, ensure_ascii=False)[:500]}...")
            
            return conhecimento_mesclado
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erro ao parsear JSON mesclado: {e}")
            logger.error(f"Resposta da IA: {json_text[:500]}")
            # Em caso de erro, estruturar do zero
            logger.warning("⚠️ Fallback: estruturando do zero")
            return EstruturadorService.estruturar_conhecimento(novo_texto)
            
        except Exception as e:
            logger.error(f"❌ Erro ao mesclar conhecimento: {e}", exc_info=True)
            # Em caso de erro, estruturar do zero
            logger.warning("⚠️ Fallback: estruturando do zero")
            return EstruturadorService.estruturar_conhecimento(novo_texto)
    
    @staticmethod
    def json_para_texto_busca(conhecimento_json: Dict[str, Any]) -> str:
        """
        Converte JSON estruturado em texto otimizado para busca/RAG
        
        Args:
            conhecimento_json: JSON estruturado
            
        Returns:
            String formatada para busca
        """
        partes = []
        
        # Nome da empresa
        if conhecimento_json.get("nome_empresa"):
            partes.append(f"Empresa: {conhecimento_json['nome_empresa']}")
        
        # Horário
        if conhecimento_json.get("horario_funcionamento"):
            h = conhecimento_json["horario_funcionamento"]
            partes.append(f"Horário: {h.get('dias', '')} {h.get('horario', '')}")
        
        # Serviços
        if conhecimento_json.get("servicos"):
            partes.append("\nServiços:")
            for s in conhecimento_json["servicos"]:
                preco = f"R$ {s['preco']:.2f}" if s.get('preco') else "Consultar"
                partes.append(f"- {s.get('categoria', '')} {s.get('nome', '')}: {preco} - {s.get('descricao', '')}")
        
        # Pagamento
        if conhecimento_json.get("pagamento"):
            p = conhecimento_json["pagamento"]
            formas = ", ".join(p.get("formas", []))
            partes.append(f"\nFormas de pagamento: {formas}")
            if p.get("chave_pix"):
                partes.append(f"Chave Pix: {p['chave_pix']}")
        
        # Links
        if conhecimento_json.get("links"):
            links = conhecimento_json["links"]
            for tipo, url in links.items():
                if url:
                    partes.append(f"{tipo.capitalize()}: {url}")
        
        # Políticas
        if conhecimento_json.get("politicas"):
            partes.append("\nPolíticas:")
            for pol in conhecimento_json["politicas"]:
                partes.append(f"- {pol}")
        
        return "\n".join(partes)
