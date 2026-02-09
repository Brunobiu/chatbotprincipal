# FASE 2 - Isolamento Total de Usuários (Anti-IDOR)

## 🎯 Objetivo
Garantir que um usuário **NUNCA** consiga acessar dados de outro usuário, mesmo alterando IDs na URL ou manipulando requisições.

---

## 🔴 O Problema: IDOR (Insecure Direct Object Reference)

### Exemplo de Vulnerabilidade
```python
# ❌ VULNERÁVEL - Qualquer usuário pode acessar qualquer conversa
@router.get("/conversas/{conversa_id}")
async def get_conversa(conversa_id: int, db: Session = Depends(get_db)):
    conversa = db.query(Conversa).filter(Conversa.id == conversa_id).first()
    return conversa

# Hacker faz:
# GET /conversas/1 → vê conversa do usuário A
# GET /conversas/2 → vê conversa do usuário B
# GET /conversas/3 → vê conversa do usuário C
```

### Solução
```python
# ✅ SEGURO - Só retorna se pertencer ao usuário autenticado
@router.get("/conversas/{conversa_id}")
async def get_conversa(
    conversa_id: int,
    db: Session = Depends(get_db),
    cliente: Cliente = Depends(get_current_cliente)
):
    conversa = db.query(Conversa).filter(
        Conversa.id == conversa_id,
        Conversa.cliente_id == cliente.id  # ← CRÍTICO
    ).first()
    
    if not conversa:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    
    return conversa
```

---

## 📋 Auditoria de Rotas Vulneráveis

### Rotas que DEVEM ser auditadas:

#### 1. Conversas
- `GET /api/v1/conversas/{id}` ⚠️
- `GET /api/v1/conversas` ⚠️
- `DELETE /api/v1/conversas/{id}` ⚠️
- `GET /api/v1/conversas/{id}/mensagens` ⚠️

#### 2. Instâncias WhatsApp
- `GET /api/v1/whatsapp/instancias/{id}` ⚠️
- `PUT /api/v1/whatsapp/instancias/{id}` ⚠️
- `DELETE /api/v1/whatsapp/instancias/{id}` ⚠️

#### 3. Conhecimentos (RAG)
- `GET /api/v1/conhecimento/{id}` ⚠️
- `DELETE /api/v1/conhecimento/{id}` ⚠️
- `PUT /api/v1/conhecimento/{id}` ⚠️

#### 4. Configurações
- `GET /api/v1/configuracoes` ⚠️
- `PUT /api/v1/configuracoes` ⚠️

#### 5. Tickets
- `GET /api/v1/tickets/{id}` ⚠️
- `PUT /api/v1/tickets/{id}` ⚠️

#### 6. Agendamentos
- `GET /api/v1/agendamentos/{id}` ⚠️
- `PUT /api/v1/agendamentos/{id}` ⚠️
- `DELETE /api/v1/agendamentos/{id}` ⚠️

#### 7. Billing
- `GET /api/v1/billing/subscription` ⚠️
- `POST /api/v1/billing/cancel` ⚠️

---

## 🔧 Implementações Necessárias

### 2.1 Middleware de Verificação de Ownership

**Novo arquivo:** `apps/backend/app/core/ownership.py`

```python
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Type, Any
from app.db.models.cliente import Cliente

class OwnershipVerifier:
    """
    Verifica se o recurso pertence ao usuário autenticado
    """
    
    @staticmethod
    def verify_ownership(
        db: Session,
        model: Type[Any],
        resource_id: int,
        cliente: Cliente,
        id_field: str = "id",
        owner_field: str = "cliente_id"
    ) -> Any:
        """
        Verifica ownership e retorna o recurso ou 404
        
        Args:
            db: Sessão do banco
            model: Modelo SQLAlchemy (ex: Conversa)
            resource_id: ID do recurso
            cliente: Cliente autenticado
            id_field: Nome do campo ID (padrão: "id")
            owner_field: Nome do campo de ownership (padrão: "cliente_id")
        
        Returns:
            Recurso se pertencer ao cliente
            
        Raises:
            HTTPException 404 se não encontrar ou não pertencer
        """
        filters = {
            id_field: resource_id,
            owner_field: cliente.id
        }
        
        resource = db.query(model).filter_by(**filters).first()
        
        if not resource:
            # Não diferencia "não existe" de "não é seu"
            # Ambos retornam 404 para não vazar informação
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{model.__name__} não encontrado"
            )
        
        return resource
    
    @staticmethod
    def verify_list_ownership(
        query: Any,
        cliente: Cliente,
        owner_field: str = "cliente_id"
    ) -> Any:
        """
        Adiciona filtro de ownership em queries de listagem
        
        Args:
            query: Query SQLAlchemy
            cliente: Cliente autenticado
            owner_field: Nome do campo de ownership
            
        Returns:
            Query filtrada
        """
        return query.filter_by(**{owner_field: cliente.id})
```

---

### 2.2 Atualizar TODAS as Rotas

#### Exemplo: Conversas

**Arquivo:** `apps/backend/app/api/v1/conversas.py`

**ANTES (vulnerável):**
```python
@router.get("/{conversa_id}")
async def get_conversa(conversa_id: int, db: Session = Depends(get_db)):
    conversa = db.query(Conversa).filter(Conversa.id == conversa_id).first()
    if not conversa:
        raise HTTPException(status_code=404)
    return conversa
```

**DEPOIS (seguro):**
```python
from app.core.ownership import OwnershipVerifier

@router.get("/{conversa_id}")
async def get_conversa(
    conversa_id: int,
    db: Session = Depends(get_db),
    cliente: Cliente = Depends(get_current_cliente)
):
    conversa = OwnershipVerifier.verify_ownership(
        db=db,
        model=Conversa,
        resource_id=conversa_id,
        cliente=cliente
    )
    return conversa
```

**Listagem:**
```python
@router.get("/")
async def list_conversas(
    db: Session = Depends(get_db),
    cliente: Cliente = Depends(get_current_cliente)
):
    query = db.query(Conversa)
    query = OwnershipVerifier.verify_list_ownership(query, cliente)
    conversas = query.all()
    return conversas
```

---

### 2.3 Validação em Queries Complexas

**Exemplo: Mensagens de uma Conversa**

```python
@router.get("/{conversa_id}/mensagens")
async def get_mensagens(
    conversa_id: int,
    db: Session = Depends(get_db),
    cliente: Cliente = Depends(get_current_cliente)
):
    # PRIMEIRO: Verificar que a conversa pertence ao cliente
    conversa = OwnershipVerifier.verify_ownership(
        db=db,
        model=Conversa,
        resource_id=conversa_id,
        cliente=cliente
    )
    
    # DEPOIS: Buscar mensagens (já sabemos que conversa é dele)
    mensagens = db.query(Mensagem).filter(
        Mensagem.conversa_id == conversa_id
    ).all()
    
    return mensagens
```

---

### 2.4 Proteção em Relacionamentos

**Problema:** Usuário pode acessar dados via relacionamentos

```python
# ❌ VULNERÁVEL
@router.get("/instancias/{instancia_id}/conversas")
async def get_conversas_instancia(instancia_id: int, db: Session = Depends(get_db)):
    # Se não validar ownership da instância, pode ver conversas de outros
    conversas = db.query(Conversa).filter(Conversa.instancia_id == instancia_id).all()
    return conversas
```

```python
# ✅ SEGURO
@router.get("/instancias/{instancia_id}/conversas")
async def get_conversas_instancia(
    instancia_id: int,
    db: Session = Depends(get_db),
    cliente: Cliente = Depends(get_current_cliente)
):
    # Validar que instância pertence ao cliente
    instancia = OwnershipVerifier.verify_ownership(
        db=db,
        model=InstanciaWhatsApp,
        resource_id=instancia_id,
        cliente=cliente
    )
    
    # Agora pode buscar conversas (já validou ownership)
    conversas = db.query(Conversa).filter(
        Conversa.instancia_id == instancia_id
    ).all()
    
    return conversas
```

---

### 2.5 Admin: Acesso Total com Validação

**Admins podem ver tudo, mas com auditoria**

```python
@router.get("/admin/clientes/{cliente_id}/conversas")
async def admin_get_conversas(
    cliente_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)  # ← Valida que é admin
):
    # Log de acesso admin
    security_logger.info(
        f"Admin {admin.email} acessou conversas do cliente {cliente_id}"
    )
    
    conversas = db.query(Conversa).filter(
        Conversa.cliente_id == cliente_id
    ).all()
    
    return conversas
```

---

## 🧪 Testes Automatizados

### Teste 1: IDOR em Conversas
```python
def test_idor_conversa():
    # Criar usuário A e conversa dele
    user_a = create_user("a@test.com")
    conversa_a = create_conversa(user_a.id)
    
    # Criar usuário B
    user_b = create_user("b@test.com")
    token_b = login(user_b)
    
    # Tentar acessar conversa de A com token de B
    response = client.get(
        f"/api/v1/conversas/{conversa_a.id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    
    # DEVE retornar 404 (não 200, não 403)
    assert response.status_code == 404
```

### Teste 2: Listagem Só Retorna Próprios Dados
```python
def test_list_only_own_data():
    # Criar 3 usuários com conversas
    user_a = create_user("a@test.com")
    create_conversa(user_a.id, "Conversa A")
    
    user_b = create_user("b@test.com")
    create_conversa(user_b.id, "Conversa B")
    
    user_c = create_user("c@test.com")
    create_conversa(user_c.id, "Conversa C")
    
    # Logar como B
    token_b = login(user_b)
    
    # Listar conversas
    response = client.get(
        "/api/v1/conversas",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    
    conversas = response.json()
    
    # DEVE retornar apenas 1 conversa (a de B)
    assert len(conversas) == 1
    assert conversas[0]["cliente_id"] == user_b.id
```

### Teste 3: Fuzzing de IDs
```python
def test_idor_fuzzing():
    # Criar usuário
    user = create_user("test@test.com")
    token = login(user)
    
    # Tentar acessar 1000 IDs aleatórios
    for i in range(1, 1001):
        response = client.get(
            f"/api/v1/conversas/{i}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # TODOS devem retornar 404 (exceto os dele)
        assert response.status_code in [404, 200]
        
        if response.status_code == 200:
            # Se retornou 200, DEVE ser dele
            conversa = response.json()
            assert conversa["cliente_id"] == user.id
```

---

## 📝 Checklist de Implementação

### Código
- [ ] Criar `ownership.py` com `OwnershipVerifier`
- [ ] Auditar TODAS as rotas de `conversas.py`
- [ ] Auditar TODAS as rotas de `whatsapp.py`
- [ ] Auditar TODAS as rotas de `conhecimento.py`
- [ ] Auditar TODAS as rotas de `configuracoes.py`
- [ ] Auditar TODAS as rotas de `tickets.py`
- [ ] Auditar TODAS as rotas de `agendamentos.py`
- [ ] Auditar TODAS as rotas de `billing.py`
- [ ] Adicionar logging de acesso admin

### Testes
- [ ] Teste IDOR em cada recurso
- [ ] Teste de listagem (só retorna próprios dados)
- [ ] Teste de fuzzing de IDs
- [ ] Teste de acesso via relacionamentos
- [ ] Teste de admin (pode acessar tudo)

### Documentação
- [ ] Documentar `OwnershipVerifier`
- [ ] Atualizar README com padrão de ownership
- [ ] Criar guia para novos endpoints

---

## 🚨 Pontos Críticos

### 1. NUNCA Retornar 403
```python
# ❌ ERRADO - Vaza informação
if conversa.cliente_id != cliente.id:
    raise HTTPException(status_code=403, detail="Não autorizado")

# ✅ CORRETO - Não diferencia "não existe" de "não é seu"
conversa = db.query(Conversa).filter(
    Conversa.id == conversa_id,
    Conversa.cliente_id == cliente.id
).first()

if not conversa:
    raise HTTPException(status_code=404, detail="Não encontrado")
```

**Por quê?**
- 403 → "Existe, mas não é seu" (vaza informação)
- 404 → "Não existe ou não é seu" (seguro)

### 2. Validar em TODAS as Operações
```python
# GET, POST, PUT, DELETE - TODAS precisam validar ownership
```

### 3. Cuidado com Queries Complexas
```python
# ❌ VULNERÁVEL
mensagens = db.query(Mensagem).join(Conversa).filter(
    Mensagem.conversa_id == conversa_id
).all()  # Não validou ownership da conversa!

# ✅ SEGURO
conversa = verify_ownership(...)  # Valida primeiro
mensagens = db.query(Mensagem).filter(
    Mensagem.conversa_id == conversa.id
).all()
```

---

## 📊 Métricas de Sucesso

✅ **100% das rotas validam ownership**  
✅ **Testes de IDOR passam em todos recursos**  
✅ **Fuzzing de 1000 IDs não vaza dados**  
✅ **Listagens só retornam dados do usuário**  
✅ **Admin pode acessar tudo (com log)**

---

## 🔄 Próximos Passos

1. Implementar `OwnershipVerifier`
2. Auditar e corrigir TODAS as rotas
3. Criar testes automatizados
4. Rodar testes
5. Fazer code review
6. **Aguardar aprovação antes de FASE 3**

---

**Status:** 🔴 Não iniciado  
**Prioridade:** CRÍTICA  
**Tempo estimado:** 6-8 horas  
**Depende de:** FASE 1 concluída
