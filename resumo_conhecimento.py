from app.db.session import SessionLocal
from app.db.models.conhecimento import Conhecimento

db = SessionLocal()
conhecimento = db.query(Conhecimento).filter(Conhecimento.cliente_id == 1).first()

if conhecimento and conhecimento.conteudo_estruturado:
    servicos = conhecimento.conteudo_estruturado.get('servicos', [])
    
    print('📊 RESUMO DO CONHECIMENTO SALVO')
    print('=' * 80)
    print(f'Empresa: {conhecimento.conteudo_estruturado.get("nome_empresa")}')
    print(f'Tipo: {conhecimento.conteudo_estruturado.get("tipo_negocio")}')
    print(f'Total de serviços: {len(servicos)}')
    print(f'Tamanho do texto: {len(conhecimento.conteudo_texto)} caracteres')
    
    print('\n📦 SERVIÇOS POR CATEGORIA:')
    print('-' * 80)
    
    # Agrupar por categoria
    categorias = {}
    for s in servicos:
        cat = s.get('categoria', 'Sem categoria')
        if cat not in categorias:
            categorias[cat] = []
        categorias[cat].append(s)
    
    for cat, servs in sorted(categorias.items()):
        print(f'\n{cat.upper()}:')
        for s in servs:
            preco = f'R$ {s["preco"]:.2f}' if s.get('preco') else 'Consultar'
            print(f'  - {s.get("nome")}: {preco}')
    
    # Outras informações
    print('\n📍 OUTRAS INFORMAÇÕES:')
    print('-' * 80)
    
    if conhecimento.conteudo_estruturado.get('horario_funcionamento'):
        h = conhecimento.conteudo_estruturado['horario_funcionamento']
        print(f'Horário: {h.get("dias")} - {h.get("horario")}')
    
    if conhecimento.conteudo_estruturado.get('entrega_busca', {}).get('disponivel'):
        eb = conhecimento.conteudo_estruturado['entrega_busca']
        print(f'Busca/Entrega: Sim (raio {eb.get("raio_km")}km)')
    
    if conhecimento.conteudo_estruturado.get('pagamento'):
        p = conhecimento.conteudo_estruturado['pagamento']
        formas = ', '.join(p.get('formas', []))
        print(f'Pagamento: {formas}')
    
    if conhecimento.conteudo_estruturado.get('links', {}).get('youtube'):
        print(f'YouTube: {conhecimento.conteudo_estruturado["links"]["youtube"]}')
    
    politicas = conhecimento.conteudo_estruturado.get('politicas', [])
    if politicas:
        print(f'Políticas: {len(politicas)} regras cadastradas')

db.close()
