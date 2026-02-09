# FASE 2 - Exemplos de Uso do Ownership Validator

## 🎯 Como Usar nas Rotas

### Antes (VULNERÁVEL ❌)

```python
@router.get("/conversas/{conversa_id}")
def get_conversa(
    conversa_id: int,
    db: Session = Depends(get_db)
):
    # ❌ VULNERÁVEL: Qualquer um pode acessar qualquer conversa
    conversa = db.query(Conversa).filter(Conversa.id == conversa_id).first()
    if not conversa:
        raise HTTPException(404, "Não encontrada")
    return conversa
```

**Problema:** Cliente A pode acessar conversas do Cliente B só mudando o ID na URL!

---

### Depois (SEGURO ✅)

```python
from app.core.ownership import verify_conversa_ownership
from app.core.security import get_current_cliente

@router.get("/conversas/{conversa_id}")
def get_conversa(
    conversa_id: int,
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    # ✅ SEGURO: Valida que a conversa pertence ao cliente
    conversa = verify_conversa_ownership(db, conversa_id, cliente)
    return conversa
```

**Proteção:** Se tentar acessar conversa de outro cliente, retorna 404!

---

## 📋 Exemplos por Recurso

### 1. Conversas

```python
from app.core.ownership import verify_conversa_ownership, OwnershipValidator

# Buscar uma conversa específica
@router.get("/conversas/{conversa_id}")
def get_conversa(
    conversa_id: int,
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    conversa = verify_conversa_ownership(db, conversa_id, cliente)
    return conversa

# Listar todas as conversas do cliente
@router.get("/conversas")
def list_conversas(
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    conversas = OwnershipValidator.get_cliente_conversas(db, cliente, skip, limit)
    return conversas

# Deletar conversa
@router.delete("/conversas/{conversa_id}")
def delete_conversa(
    conversa_id: int,
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    conversa = verify_conversa_ownership(db, conversa_id, cliente)
    db.delete(conversa)
    db.commit()
    return {"message": "Conversa deletada"}
```

### 2. Instâncias WhatsApp

```python
from app.core.ownership import verify_instancia_ownership

@router.get("/whatsapp/instancias/{instancia_id}")
def get_instancia(
    instancia_id: int,
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    instancia = verify_instancia_ownership(db, instancia_id, cliente)
    return instancia

@router.put("/whatsapp/instancias/{instancia_id}")
def update_instancia(
    instancia_id: int,
    data: InstanciaUpdate,
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    instancia = verify_instancia_ownership(db, instancia_id, cliente)
    # Atualizar instância...
    return instancia
```

### 3. Tickets

```python
from app.core.ownership import verify_ticket_ownership, OwnershipValidator

@router.get("/tickets/{ticket_id}")
def get_ticket(
    ticket_id: int,
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    ticket = verify_ticket_ownership(db, ticket_id, cliente)
    return ticket

@router.get("/tickets")
def list_tickets(
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    tickets = OwnershipValidator.get_cliente_tickets(db, cliente)
    return tickets
```

### 4. Agendamentos

```python
from app.core.ownership import verify_agendamento_ownership, OwnershipValidator

@router.get("/agendamentos/{agendamento_id}")
def get_agendamento(
    agendamento_id: int,
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    agendamento = verify_agendamento_ownership(db, agendamento_id, cliente)
    return agendamento

@router.delete("/agendamentos/{agendamento_id}")
def delete_agendamento(
    agendamento_id: int,
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    agendamento = verify_agendamento_ownership(db, agendamento_id, cliente)
    db.delete(agendamento)
    db.commit()
    return {"message": "Agendamento deletado"}
```

### 5. Conhecimento e Configurações

```python
from app.core.ownership import OwnershipValidator

@router.get("/conhecimento")
def get_conhecimento(
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    conhecimento = OwnershipValidator.verify_conhecimento_ownership(db, cliente)
    return conhecimento

@router.get("/configuracoes")
def get_configuracoes(
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    config = OwnershipValidator.verify_configuracao_ownership(db, cliente)
    return config
```

---

## 🔒 Padrão de Segurança

### Regra de Ouro

**SEMPRE:**
1. Adicionar `cliente = Depends(get_current_cliente)` na rota
2. Usar `verify_*_ownership()` antes de acessar o recurso
3. Filtrar por `cliente_id` em queries de listagem

**NUNCA:**
1. Confiar no ID vindo do frontend
2. Fazer query sem filtrar por `cliente_id`
3. Retornar dados sem validar ownership

---

## 🧪 Como Testar

### Teste Manual

```bash
# 1. Login como Cliente A
RESPONSE_A=$(curl -X POST http://localhost:8000/api/v1/auth-v2/login \
  -H "Content-Type: application/json" \
  -d '{"email": "clienteA@example.com", "senha": "senha123"}')

TOKEN_A=$(echo $RESPONSE_A | jq -r '.access_token')

# 2. Login como Cliente B
RESPONSE_B=$(curl -X POST http://localhost:8000/api/v1/auth-v2/login \
  -H "Content-Type: application/json" \
  -d '{"email": "clienteB@example.com", "senha": "senha123"}')

TOKEN_B=$(echo $RESPONSE_B | jq -r '.access_token')

# 3. Cliente A cria uma conversa
CONVERSA_A=$(curl -X POST http://localhost:8000/api/v1/conversas \
  -H "Authorization: Bearer $TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "123456"}')

CONVERSA_ID=$(echo $CONVERSA_A | jq -r '.id')

# 4. Cliente B tenta acessar conversa do Cliente A
curl -X GET http://localhost:8000/api/v1/conversas/$CONVERSA_ID \
  -H "Authorization: Bearer $TOKEN_B"

# Deve retornar 404 (não encontrada)
# ✅ PROTEÇÃO FUNCIONANDO!
```

### Teste Automatizado

```python
# tests/test_ownership.py

def test_cannot_access_other_user_conversa(client, db):
    # Criar dois clientes
    cliente_a = create_test_cliente(db, "a@test.com")
    cliente_b = create_test_cliente(db, "b@test.com")
    
    # Cliente A cria conversa
    conversa = create_test_conversa(db, cliente_a.id)
    
    # Cliente B tenta acessar
    token_b = create_access_token(cliente_b.id)
    response = client.get(
        f"/api/v1/conversas/{conversa.id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    
    # Deve retornar 404
    assert response.status_code == 404
    assert "não encontrada" in response.json()["detail"].lower()
```

---

## ✅ Checklist de Implementação

Para cada rota que acessa recursos do cliente:

- [ ] Adiciona `cliente = Depends(get_current_cliente)`
- [ ] Usa `verify_*_ownership()` para recursos específicos
- [ ] Usa `get_cliente_*()` para listagens
- [ ] Testa com dois clientes diferentes
- [ ] Confirma que retorna 404 ao tentar acesso cruzado

---

## 🎯 Resultado

Com o Ownership Validator:
- ✅ Impossível acessar dados de outros usuários
- ✅ Proteção contra IDOR
- ✅ Código limpo e reutilizável
- ✅ Fácil de testar
- ✅ Mensagens de erro consistentes

**Sistema 100% isolado por usuário!** 🔒
