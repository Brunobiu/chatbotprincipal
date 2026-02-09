# FASE B - IA Assistente - INSTRUÇÕES DE USO

## ✅ Backend Completo

### Rotas Disponíveis:
- `GET /api/v1/admin/ia/resumo-atual` - Resumo atual da IA
- `POST /api/v1/admin/ia/gerar-resumo` - Força geração de novo resumo
- `GET /api/v1/admin/ia/historico` - Histórico de mensagens
- `GET /api/v1/admin/ia/objetivos` - Objetivos do admin
- `PUT /api/v1/admin/ia/objetivos` - Atualizar objetivos

### Modelos Criados:
- `IAMensagem` - Armazena mensagens da IA
- `AdminObjetivos` - Armazena objetivos/metas do admin

### Serviço:
- `IAAssistenteService` - Gera resumos e análises

---

## 🎨 Frontend - Como Usar

### 1. Adicionar Widget no Dashboard Admin

No arquivo do dashboard admin (ex: `apps/frontend/app/admin/page.tsx`):

```tsx
import IAWidget from '@/components/admin/IAWidget';

export default function AdminDashboard() {
  return (
    <div>
      {/* Adicionar logo no topo, antes das estatísticas */}
      <IAWidget />
      
      {/* Resto do dashboard */}
      <div className="grid grid-cols-4 gap-6">
        {/* Cards de estatísticas */}
      </div>
    </div>
  );
}
```

### 2. Página de Histórico de Mensagens

Criar `apps/frontend/app/admin/ia-mensagens/page.tsx`:

```tsx
'use client';

import { useEffect, useState } from 'react';

export default function IAMensagensPage() {
  const [mensagens, setMensagens] = useState([]);

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/admin/ia/historico')
      .then(res => res.json())
      .then(data => setMensagens(data.mensagens));
  }, []);

  return (
    <div>
      <h1>Histórico de Mensagens da IA</h1>
      {mensagens.map(msg => (
        <div key={msg.id} className="bg-white p-4 rounded mb-4">
          <p>{msg.conteudo}</p>
          <small>{new Date(msg.created_at).toLocaleString()}</small>
        </div>
      ))}
    </div>
  );
}
```

### 3. Página de Objetivos

Criar `apps/frontend/app/admin/objetivos/page.tsx`:

```tsx
'use client';

import { useEffect, useState } from 'react';

export default function ObjetivosPage() {
  const [objetivos, setObjetivos] = useState({
    meta_clientes_mes: 10,
    meta_receita_mes: 5000,
    max_anuncios_percent: 30,
    max_openai_percent: 20,
    taxa_conversao_esperada: 20
  });

  const handleSave = async () => {
    await fetch('http://localhost:8000/api/v1/admin/ia/objetivos', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(objetivos)
    });
    alert('Objetivos salvos!');
  };

  return (
    <div>
      <h1>Meus Objetivos</h1>
      <div className="space-y-4">
        <div>
          <label>Meta de Clientes/Mês:</label>
          <input
            type="number"
            value={objetivos.meta_clientes_mes}
            onChange={e => setObjetivos({...objetivos, meta_clientes_mes: parseInt(e.target.value)})}
          />
        </div>
        {/* Outros campos... */}
        <button onClick={handleSave}>Salvar</button>
      </div>
    </div>
  );
}
```

---

## 🧪 Testado

✅ API `/resumo-atual` retorna dados corretos
✅ Detecta novos clientes de hoje
✅ Gera dicas automaticamente
✅ Calcula métricas financeiras

---

## 📊 Dados Retornados

```json
{
  "novos_clientes": [
    {"nome": "João", "email": "joao@test.com", "hora": "10:30"}
  ],
  "trials_expirando": [
    {"nome": "Maria", "dias": 2}
  ],
  "cancelamentos": [],
  "dicas": [
    "Sua taxa de conversão está em 15% (média: 20%)"
  ],
  "financeiro": {
    "receita_mensal": 2970.00,
    "clientes_pagos": 33,
    "custo_openai": 0,
    "lucro": 2970.00,
    "margem": 100
  }
}
```

---

## 🚀 Próximos Passos

Para completar a FASE B:
1. Adicionar IAWidget no dashboard admin
2. Criar página de histórico
3. Criar página de objetivos
4. Implementar cron job para gerar resumo diário automaticamente

**Status:** Backend 100% completo, Frontend precisa integração no admin
