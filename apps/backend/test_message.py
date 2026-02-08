"""
Script para testar envio de mensagem simulada
"""
import asyncio
import sys
sys.path.insert(0, '/app/apps/backend')

from app.services.conversations.message_buffer import buffer_message

async def test():
    # Simular mensagem de um cliente
    chat_id = "5511999999999@s.whatsapp.net"  # Número de teste
    mensagem = "Olá, qual o valor da pizza marguerita?"
    cliente_id = 1
    
    print(f"📤 Enviando mensagem de teste...")
    print(f"   Chat: {chat_id}")
    print(f"   Mensagem: {mensagem}")
    print(f"   Cliente: {cliente_id}")
    
    await buffer_message(chat_id, mensagem, cliente_id)
    
    print(f"✅ Mensagem enviada para processamento!")
    print(f"⏳ Aguardando 15 segundos para processar...")
    
    await asyncio.sleep(15)
    
    print(f"✅ Teste concluído!")

if __name__ == "__main__":
    asyncio.run(test())
