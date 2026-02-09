"""
AgendamentoAIParser - Parser de IA para detectar pedidos de agendamento
Task 10.3
"""

import re
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from openai import OpenAI

from app.core.config import settings


class AgendamentoAIParser:
    """Parser de IA para identificar e extrair informações de agendamentos"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def detectar_intencao_agendamento(self, mensagem: str) -> bool:
        """
        Detecta se mensagem contém intenção de agendamento
        
        Args:
            mensagem: Mensagem do usuário
        
        Returns:
            True se detectar intenção de agendamento
        """
        # Palavras-chave que indicam agendamento
        palavras_chave = [
            'agendar', 'marcar', 'horário', 'horario', 'consulta',
            'reservar', 'reserva', 'disponível', 'disponivel',
            'quando', 'que dia', 'que hora', 'amanhã', 'amanha',
            'próxima', 'proxima', 'semana', 'mês', 'mes',
            'segunda', 'terça', 'terca', 'quarta', 'quinta', 'sexta', 'sábado', 'sabado', 'domingo'
        ]
        
        mensagem_lower = mensagem.lower()
        
        # Verificar se contém alguma palavra-chave
        for palavra in palavras_chave:
            if palavra in mensagem_lower:
                return True
        
        return False
    
    def extrair_informacoes_agendamento(self, mensagem: str, tipos_servico: Optional[list] = None) -> Optional[Dict[str, Any]]:
        """
        Extrai informações de agendamento da mensagem usando OpenAI
        
        Args:
            mensagem: Mensagem do usuário
            tipos_servico: Lista de tipos de serviço disponíveis (opcional)
        
        Returns:
            Dict com informações extraídas ou None se não for agendamento
            {
                "data_hora": datetime,
                "tipo_servico": str,
                "observacoes": str
            }
        """
        try:
            # Preparar prompt para OpenAI
            tipos_servico_str = ""
            if tipos_servico:
                tipos_servico_str = f"\nTipos de serviço disponíveis: {', '.join(tipos_servico)}"
            
            prompt = f"""Analise a seguinte mensagem e extraia informações de agendamento.
{tipos_servico_str}

Mensagem: "{mensagem}"

Data/hora atual: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Retorne um JSON com:
- "eh_agendamento": true/false (se a mensagem é um pedido de agendamento)
- "data_hora": data e hora no formato ISO 8601 (YYYY-MM-DDTHH:MM:SS)
- "tipo_servico": tipo de serviço mencionado (ou null)
- "observacoes": observações adicionais (ou null)

Regras:
1. Se não mencionar hora específica, use 09:00
2. Se mencionar "amanhã", use a data de amanhã
3. Se mencionar dia da semana, use a próxima ocorrência desse dia
4. Se mencionar apenas "hoje", use hoje às 09:00
5. Interprete datas relativas (ex: "daqui 2 dias", "próxima segunda")

Retorne APENAS o JSON, sem texto adicional."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Você é um assistente especializado em extrair informações de agendamentos de mensagens."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            resultado_texto = response.choices[0].message.content.strip()
            
            # Remover markdown se presente
            if resultado_texto.startswith("```json"):
                resultado_texto = resultado_texto[7:]
            if resultado_texto.startswith("```"):
                resultado_texto = resultado_texto[3:]
            if resultado_texto.endswith("```"):
                resultado_texto = resultado_texto[:-3]
            
            resultado = json.loads(resultado_texto.strip())
            
            # Verificar se é agendamento
            if not resultado.get("eh_agendamento", False):
                return None
            
            # Converter data_hora para datetime
            data_hora_str = resultado.get("data_hora")
            if not data_hora_str:
                return None
            
            try:
                data_hora = datetime.fromisoformat(data_hora_str)
            except:
                # Tentar formato alternativo
                data_hora = datetime.strptime(data_hora_str, "%Y-%m-%d %H:%M:%S")
            
            return {
                "data_hora": data_hora,
                "tipo_servico": resultado.get("tipo_servico"),
                "observacoes": resultado.get("observacoes")
            }
            
        except Exception as e:
            print(f"Erro ao extrair informações de agendamento: {e}")
            return None
    
    def gerar_mensagem_confirmacao(
        self,
        data_hora: datetime,
        tipo_servico: Optional[str] = None,
        nome_usuario: Optional[str] = None
    ) -> str:
        """
        Gera mensagem de confirmação de agendamento
        
        Args:
            data_hora: Data e hora do agendamento
            tipo_servico: Tipo de serviço (opcional)
            nome_usuario: Nome do usuário (opcional)
        
        Returns:
            Mensagem de confirmação
        """
        saudacao = f"Olá{', ' + nome_usuario if nome_usuario else ''}!"
        
        # Formatar data e hora
        data_formatada = data_hora.strftime("%d/%m/%Y")
        hora_formatada = data_hora.strftime("%H:%M")
        dia_semana = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"][data_hora.weekday()]
        
        servico_str = f" para {tipo_servico}" if tipo_servico else ""
        
        mensagem = f"""{saudacao}

✅ Seu agendamento{servico_str} foi registrado!

📅 Data: {dia_semana}, {data_formatada}
🕐 Horário: {hora_formatada}

⏳ Aguardando confirmação...

Você receberá uma notificação assim que seu agendamento for confirmado."""
        
        return mensagem
    
    def gerar_mensagem_aprovacao(
        self,
        data_hora: datetime,
        tipo_servico: Optional[str] = None,
        nome_usuario: Optional[str] = None
    ) -> str:
        """
        Gera mensagem de aprovação de agendamento
        
        Args:
            data_hora: Data e hora do agendamento
            tipo_servico: Tipo de serviço (opcional)
            nome_usuario: Nome do usuário (opcional)
        
        Returns:
            Mensagem de aprovação
        """
        saudacao = f"Olá{', ' + nome_usuario if nome_usuario else ''}!"
        
        data_formatada = data_hora.strftime("%d/%m/%Y")
        hora_formatada = data_hora.strftime("%H:%M")
        dia_semana = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"][data_hora.weekday()]
        
        servico_str = f" de {tipo_servico}" if tipo_servico else ""
        
        mensagem = f"""{saudacao}

✅ Seu agendamento{servico_str} foi CONFIRMADO!

📅 Data: {dia_semana}, {data_formatada}
🕐 Horário: {hora_formatada}

Nos vemos lá! 😊"""
        
        return mensagem
    
    def gerar_mensagem_recusa(
        self,
        data_hora: datetime,
        tipo_servico: Optional[str] = None,
        nome_usuario: Optional[str] = None,
        motivo: Optional[str] = None
    ) -> str:
        """
        Gera mensagem de recusa de agendamento
        
        Args:
            data_hora: Data e hora do agendamento
            tipo_servico: Tipo de serviço (opcional)
            nome_usuario: Nome do usuário (opcional)
            motivo: Motivo da recusa (opcional)
        
        Returns:
            Mensagem de recusa
        """
        saudacao = f"Olá{', ' + nome_usuario if nome_usuario else ''}!"
        
        data_formatada = data_hora.strftime("%d/%m/%Y")
        hora_formatada = data_hora.strftime("%H:%M")
        
        servico_str = f" de {tipo_servico}" if tipo_servico else ""
        motivo_str = f"\n\nMotivo: {motivo}" if motivo else ""
        
        mensagem = f"""{saudacao}

❌ Infelizmente não conseguimos confirmar seu agendamento{servico_str} para {data_formatada} às {hora_formatada}.{motivo_str}

Por favor, entre em contato para reagendar."""
        
        return mensagem
