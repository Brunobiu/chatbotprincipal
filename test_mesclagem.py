from app.db.session import SessionLocal
from app.services.conhecimento import ConhecimentoService

db = SessionLocal()
try:
    # Buscar conhecimento atual
    conhecimento = ConhecimentoService.buscar_ou_criar(db, 1)
    
    print('📊 CONHECIMENTO ATUAL:')
    print(f'  - Total de serviços: {len(conhecimento.conteudo_estruturado.get("servicos", []))}')
    print(f'  - Nome empresa: {conhecimento.conteudo_estruturado.get("nome_empresa")}')
    
    # Novo texto para mesclar (adicionar novo serviço)
    novo_texto = """
    NOVO SERVIÇO - POLIMENTO AUTOMOTIVO
    
    Polimento Simples
    Preço: R$ 150,00
    Descrição: Polimento básico da pintura, remove pequenos riscos e manchas superficiais.
    Tempo estimado: 2 horas
    Disponível para: carros pequenos, médios e grandes
    
    Polimento Completo
    Preço: R$ 300,00
    Descrição: Polimento profissional em 3 etapas, remove riscos profundos, restaura brilho original.
    Tempo estimado: 4 horas
    Disponível para: carros pequenos, médios e grandes
    """
    
    print('\n🔄 MESCLANDO NOVO SERVIÇO...')
    print(f'  Novo texto: {len(novo_texto)} chars')
    
    # Atualizar com modo MESCLAR
    conhecimento_atualizado = ConhecimentoService.atualizar(
        db=db,
        cliente_id=1,
        conteudo=novo_texto,
        modo="mesclar"
    )
    
    print('\n✅ CONHECIMENTO MESCLADO:')
    print(f'  - Total de serviços: {len(conhecimento_atualizado.conteudo_estruturado.get("servicos", []))}')
    print(f'  - Nome empresa: {conhecimento_atualizado.conteudo_estruturado.get("nome_empresa")}')
    
    # Verificar se novos serviços foram adicionados
    servicos = conhecimento_atualizado.conteudo_estruturado.get("servicos", [])
    polimentos = [s for s in servicos if "polimento" in s.get("nome", "").lower()]
    
    print(f'\n🎨 SERVIÇOS DE POLIMENTO ENCONTRADOS: {len(polimentos)}')
    for pol in polimentos:
        print(f'  - {pol.get("nome")}: R$ {pol.get("preco"):.2f}')
    
finally:
    db.close()
