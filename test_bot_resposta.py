from app.services.ai import AIService

# Simular perguntas do usuário
perguntas = [
    "quanto custa lavar um carro pequeno?",
    "qual o horário de funcionamento?",
    "vocês fazem polimento?",
    "qual a chave pix?"
]

print('🤖 TESTANDO BOT COM EMBEDDINGS ESTRUTURADOS\n')
print('=' * 70)

for i, pergunta in enumerate(perguntas, 1):
    print(f'\n📝 Pergunta {i}: "{pergunta}"')
    print('-' * 70)
    
    try:
        resultado = AIService.processar_mensagem(
            cliente_id=1,
            chat_id=f'test_session_{i}',
            mensagem=pergunta,
            tom='casual',
            nome_empresa='Lava Jato Auto Limpo',
            primeira_mensagem=(i == 1)
        )
        
        print(f'✅ Resposta: {resultado["resposta"]}')
        print(f'📊 Confiança: {resultado["confianca"]:.2f}')
        print(f'📦 Documentos usados: {resultado["contexto_usado"]}')
        
    except Exception as e:
        print(f'❌ Erro: {e}')
        import traceback
        traceback.print_exc()

print('\n' + '=' * 70)
print('✅ TESTE CONCLUÍDO!')
