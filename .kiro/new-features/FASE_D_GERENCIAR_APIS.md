# FASE D - GERENCIAR APIs DE IA

**Prioridade:** 🟡 MÉDIA  
**Tempo Estimado:** 6-8 horas  
**Status:** ⏳ Pendente

---

## 🎯 Objetivo

Permitir que o admin configure e alterne entre diferentes provedores de IA (ChatGPT, Claude, Gemini) com gerenciamento seguro de API keys.

---

## 📋 Funcionalidades

### D1: Configurações de IA

**Nova aba lateral:** "Configurações de IA"

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ 🤖 Configurações de IA                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Modelo Ativo                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ ● ChatGPT (OpenAI)                                      │ │
│ │ ○ Claude (Anthropic)                                    │ │
│ │ ○ Gemini (Google)                                       │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ Configuração do ChatGPT                                    │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Status: ✅ Configurado                                  │ │
│ │                                                          │ │
│ │ API Key: sk-...•••• (oculta)                            │ │
│ │                                                          │ │
│ │ Modelo: [gpt-4-turbo ▼]                                 │ │
│ │   Opções: gpt-4-turbo, gpt-4, gpt-3.5-turbo            │ │
│ │                                                          │ │
│ │ [Adicionar Nova Key] [Excluir Key]                      │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ Configuração do Claude                                     │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Status: ⚠️  Não configurado                             │ │
│ │                                                          │ │
│ │ API Key: [_______________________________]              │ │
│ │                                                          │ │
│ │ Modelo: [claude-3-opus ▼]                               │ │
│ │   Opções: claude-3-opus, claude-3-sonnet               │ │
│ │                                                          │ │
│ │ [Adicionar Key]                                         │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ Configuração do Gemini                                     │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Status: ⚠️  Não configurado                             │ │
│ │                                                          │ │
│ │ API Key: [_______________________________]              │ │
│ │                                                          │ │
│ │ Modelo: [gemini-pro ▼]                                  │ │
│ │   Opções: gemini-pro, gemini-ultra                     │ │
│ │                                                          │ │
│ │ [Adicionar Key]                                         │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│                                          [Salvar Alterações] │
└─────────────────────────────────────────────────────────────┘
```

---

### D2: Regras de Funcionamento

**1. Apenas 1 Modelo Ativo:**
- Radio button: apenas 1 pode estar selecionado
- Ao selecionar outro, o anterior é desativado automaticamente
- Sistema usa APENAS o modelo ativo

**2. Segurança das API Keys:**
- API key é criptografada ao salvar no banco
- Nunca mostra a key completa depois (mostra: `sk-...••••`)
- Não tem opção "Editar" (só adicionar nova ou excluir)
- Ao adicionar nova key, substitui a anterior

**3. Bloqueio Automático:**
- Se ChatGPT ativo → Claude e Gemini ficam inativos
- Se Claude ativo → ChatGPT e Gemini ficam inativos
- Se Gemini ativo → ChatGPT e Claude ficam inativos

**4. Validação de API Key:**
- Ao adicionar key, sistema testa com chamada simples
- Se inválida, mostra erro e não salva
- Se válida, salva e marca como configurado

---

### D3: Modelos Disponíveis

**ChatGPT (OpenAI):**
- `gpt-4-turbo` (recomendado)
- `gpt-4`
- `gpt-3.5-turbo`

**Claude (Anthropic):**
- `claude-3-opus` (mais poderoso)
- `claude-3-sonnet` (balanceado)
- `claude-3-haiku` (mais rápido)

**Gemini (Google):**
- `gemini-pro` (padrão)
- `gemini-ultra` (mais avançado)

---

### D4: Integração com Sistema

**Comportamento:**
- Todos os clientes usam o modelo ativo configurado pelo admin
- Ao trocar modelo, próximas conversas usam o novo modelo
- Conversas antigas mantêm histórico do modelo usado

**Fallback:**
- Se modelo ativo falhar, sistema tenta próximo disponível
- Ordem de fallback: ChatGPT → Claude → Gemini
- Se todos falharem, mostra erro ao cliente

---

## 🗄️ Alterações no Banco de Dados

### Nova Tabela: `ia_configuracoes`

```sql
CREATE TABLE ia_configuracoes (
    id SERIAL PRIMARY KEY,
    provedor VARCHAR(20),
    -- Valores: 'openai', 'anthropic', 'google'
    api_key_encrypted TEXT,
    -- API key criptografada
    modelo VARCHAR(50),
    -- Nome do modelo (ex: 'gpt-4-turbo')
    ativo BOOLEAN DEFAULT FALSE,
    -- Apenas 1 pode estar ativo
    configurado BOOLEAN DEFAULT FALSE,
    -- Se tem API key válida
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Inserir configurações padrão
INSERT INTO ia_configuracoes (provedor, modelo) VALUES
('openai', 'gpt-4-turbo'),
('anthropic', 'claude-3-opus'),
('google', 'gemini-pro');

-- Garantir apenas 1 ativo
CREATE UNIQUE INDEX idx_ia_config_ativo ON ia_configuracoes(ativo) WHERE ativo = TRUE;
```

### Tabela `conversas` - Adicionar campo:

```sql
ALTER TABLE conversas ADD COLUMN modelo_usado VARCHAR(50);
-- Registrar qual modelo foi usado naquela conversa
```

---

## 🔧 Implementação Técnica

### Backend

**1. Serviço de Criptografia:**

**Arquivo:** `apps/backend/app/services/ia_config_service.py`

```python
from cryptography.fernet import Fernet
import os

class IAConfigService:
    def __init__(self):
        # Usar chave do .env
        self.cipher = Fernet(os.getenv("ENCRYPTION_KEY"))
    
    def encrypt_api_key(self, api_key: str) -> str:
        """Criptografa API key"""
        return self.cipher.encrypt(api_key.encode()).decode()
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        """Descriptografa API key"""
        return self.cipher.decrypt(encrypted_key.encode()).decode()
    
    def mask_api_key(self, api_key: str) -> str:
        """Mascara API key para exibição"""
        if len(api_key) < 8:
            return "••••"
        return f"{api_key[:3]}...••••"
    
    async def validar_api_key(self, provedor: str, api_key: str, modelo: str) -> bool:
        """Testa se API key é válida"""
        try:
            if provedor == "openai":
                # Testar com OpenAI
                import openai
                openai.api_key = api_key
                response = await openai.ChatCompletion.create(
                    model=modelo,
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=5
                )
                return True
            elif provedor == "anthropic":
                # Testar com Claude
                import anthropic
                client = anthropic.Client(api_key=api_key)
                response = client.messages.create(
                    model=modelo,
                    max_tokens=5,
                    messages=[{"role": "user", "content": "test"}]
                )
                return True
            elif provedor == "google":
                # Testar com Gemini
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(modelo)
                response = model.generate_content("test")
                return True
        except Exception as e:
            return False
    
    async def get_modelo_ativo(self):
        """Retorna configuração do modelo ativo"""
        config = await db.query(
            "SELECT * FROM ia_configuracoes WHERE ativo = TRUE"
        ).first()
        return config
    
    async def chamar_ia(self, mensagem: str, contexto: list):
        """Chama IA ativa com fallback"""
        config = await self.get_modelo_ativo()
        
        try:
            if config.provedor == "openai":
                return await self._chamar_openai(config, mensagem, contexto)
            elif config.provedor == "anthropic":
                return await self._chamar_claude(config, mensagem, contexto)
            elif config.provedor == "google":
                return await self._chamar_gemini(config, mensagem, contexto)
        except Exception as e:
            # Fallback para próximo disponível
            return await self._fallback(mensagem, contexto)
```

**2. Rotas da API:**

```
GET /api/v1/admin/ia-config
Response: {
  "configuracoes": [
    {
      "provedor": "openai",
      "modelo": "gpt-4-turbo",
      "ativo": true,
      "configurado": true,
      "api_key_masked": "sk-...••••"
    },
    {
      "provedor": "anthropic",
      "modelo": "claude-3-opus",
      "ativo": false,
      "configurado": false,
      "api_key_masked": null
    },
    ...
  ]
}

POST /api/v1/admin/ia-config/add-key
Body: {
  "provedor": "openai",
  "api_key": "sk-...",
  "modelo": "gpt-4-turbo"
}
Response: {
  "success": true,
  "message": "API key adicionada e validada"
}

DELETE /api/v1/admin/ia-config/remove-key
Body: {
  "provedor": "openai"
}
Response: {
  "success": true,
  "message": "API key removida"
}

PUT /api/v1/admin/ia-config/set-active
Body: {
  "provedor": "anthropic"
}
Response: {
  "success": true,
  "message": "Claude ativado como modelo principal"
}

PUT /api/v1/admin/ia-config/change-model
Body: {
  "provedor": "openai",
  "modelo": "gpt-3.5-turbo"
}
Response: {
  "success": true,
  "message": "Modelo alterado para gpt-3.5-turbo"
}
```

**3. Atualizar serviço de chat:**

```python
# apps/backend/app/services/chat_service.py

async def processar_mensagem(self, cliente_id: int, mensagem: str):
    # Buscar modelo ativo
    ia_service = IAConfigService()
    config = await ia_service.get_modelo_ativo()
    
    # Chamar IA
    resposta = await ia_service.chamar_ia(mensagem, contexto)
    
    # Salvar conversa com modelo usado
    await db.execute(
        "INSERT INTO conversas (..., modelo_usado) VALUES (..., $1)",
        config.modelo
    )
    
    return resposta
```

---

### Frontend

**1. Página de Configurações:**

**Componente:** `apps/frontend/app/admin/ia-config/page.tsx`

**Funcionalidades:**
- Listar 3 provedores
- Radio button para selecionar ativo
- Formulário para adicionar API key
- Botão para excluir key
- Dropdown para escolher modelo
- Validação em tempo real

**2. Componente de Provedor:**

**Componente:** `apps/frontend/components/admin/IAProviderCard.tsx`

**Props:**
```typescript
interface IAProviderCardProps {
  provedor: 'openai' | 'anthropic' | 'google';
  nome: string;
  ativo: boolean;
  configurado: boolean;
  apiKeyMasked: string | null;
  modelo: string;
  modelosDisponiveis: string[];
  onSetActive: () => void;
  onAddKey: (key: string) => void;
  onRemoveKey: () => void;
  onChangeModel: (model: string) => void;
}
```

**3. Modal de Confirmação:**

**Componente:** `apps/frontend/components/admin/ConfirmRemoveKeyModal.tsx`

**Uso:** Ao excluir API key

**Conteúdo:**
```
┌────────────────────────────────────────┐
│ ⚠️  Remover API Key?                  │
├────────────────────────────────────────┤
│ Tem certeza que deseja remover a API  │
│ key do ChatGPT?                        │
│                                        │
│ Você não poderá recuperá-la depois.   │
│                                        │
│ [Cancelar] [Sim, Remover]             │
└────────────────────────────────────────┘
```

---

## ✅ Checklist de Implementação

### Backend
- [ ] Gerar chave de criptografia (ENCRYPTION_KEY no .env)
- [ ] Criar tabela `ia_configuracoes`
- [ ] Adicionar campo `modelo_usado` em `conversas`
- [ ] Criar serviço `IAConfigService`
- [ ] Implementar criptografia de API keys
- [ ] Implementar validação de API keys
- [ ] Criar rota `GET /api/v1/admin/ia-config`
- [ ] Criar rota `POST /api/v1/admin/ia-config/add-key`
- [ ] Criar rota `DELETE /api/v1/admin/ia-config/remove-key`
- [ ] Criar rota `PUT /api/v1/admin/ia-config/set-active`
- [ ] Criar rota `PUT /api/v1/admin/ia-config/change-model`
- [ ] Atualizar serviço de chat para usar modelo ativo
- [ ] Implementar fallback entre modelos
- [ ] Instalar SDKs: `anthropic`, `google-generativeai`

### Frontend
- [ ] Criar página `/admin/ia-config`
- [ ] Criar componente `IAProviderCard`
- [ ] Criar componente `ConfirmRemoveKeyModal`
- [ ] Implementar formulário de adicionar key
- [ ] Implementar validação de key
- [ ] Implementar troca de modelo ativo
- [ ] Implementar exclusão de key
- [ ] Adicionar link no menu lateral

### Testes
- [ ] Testar adicionar API key válida
- [ ] Testar adicionar API key inválida
- [ ] Testar excluir API key
- [ ] Testar trocar modelo ativo
- [ ] Testar trocar modelo específico
- [ ] Testar chat com ChatGPT
- [ ] Testar chat com Claude
- [ ] Testar chat com Gemini
- [ ] Testar fallback entre modelos
- [ ] Testar criptografia/descriptografia

---

## 🧪 Casos de Teste

### CT1: Adicionar API Key Válida
1. Acessar configurações de IA
2. Adicionar API key do ChatGPT
3. **Esperado:** Key validada e salva, status "Configurado"

### CT2: Adicionar API Key Inválida
1. Adicionar API key inválida
2. **Esperado:** Erro "API key inválida", não salva

### CT3: Trocar Modelo Ativo
1. ChatGPT está ativo
2. Selecionar Claude
3. **Esperado:** Claude ativo, ChatGPT inativo

### CT4: Excluir API Key
1. Excluir API key do ChatGPT
2. **Esperado:** Key removida, status "Não configurado"

### CT5: Chat com Modelo Ativo
1. Ativar Claude
2. Cliente envia mensagem
3. **Esperado:** Resposta vem do Claude

### CT6: Fallback
1. Ativar Claude com key inválida
2. Cliente envia mensagem
3. **Esperado:** Sistema tenta ChatGPT automaticamente

### CT7: Segurança da Key
1. Adicionar API key
2. Recarregar página
3. **Esperado:** Key mascarada (sk-...••••)

---

## 📝 Notas Importantes

1. **Nunca mostrar key completa** - Sempre mascarar após salvar
2. **Validar antes de salvar** - Testar key com chamada real
3. **Apenas 1 ativo** - Garantir no banco e na UI
4. **Fallback automático** - Se modelo ativo falhar
5. **Registrar modelo usado** - Em cada conversa
6. **Criptografia forte** - Usar Fernet (symmetric encryption)

---

## 🚀 Próximos Passos

Após completar FASE D:
- [ ] Marcar como completa no README.md
- [ ] Passar para FASE F (Analytics)

---

**Status:** ⏳ Aguardando implementação
