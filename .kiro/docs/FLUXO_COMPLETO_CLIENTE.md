# 🔄 Fluxo Completo do Cliente - Do Pagamento ao Login

## Visão Geral

Este documento explica o fluxo completo desde o momento que o cliente paga até ele fazer login e usar o sistema.

---

## 📋 Passo a Passo

### 1️⃣ Cliente Acessa o Site
- Cliente visita: `http://localhost:3000`
- Vê a landing page com informações do produto
- Clica no botão **"Quero Assinar"**

### 2️⃣ Cliente é Redirecionado para Stripe
- Sistema cria sessão de checkout no Stripe
- Cliente preenche:
  - **Nome completo**
  - **Email** (será usado para login)
  - **Dados do cartão**
- Cliente confirma pagamento

### 3️⃣ Stripe Processa Pagamento
- Stripe valida cartão
- Cobra o valor (R$ 5,00/mês no teste)
- Pagamento aprovado ✅

### 4️⃣ Webhook Recebe Notificação
- Stripe envia webhook para: `POST /api/v1/billing/webhook`
- Evento: `checkout.session.completed`
- Dados incluem: email, nome, customer_id, subscription_id

### 5️⃣ Sistema Cria Conta Automaticamente
```python
# O que acontece no backend:
1. Busca se cliente já existe (por email)
2. Se não existe:
   - Gera senha aleatória segura (ex: "Abc123!@#XyZ")
   - Cria hash bcrypt da senha
   - Salva cliente no banco com status ATIVO
3. Se já existe:
   - Atualiza dados do Stripe
   - Mantém senha existente
```

### 6️⃣ Email é Enviado Automaticamente
```
Para: cliente@exemplo.com
Assunto: 🎉 Bem-vindo ao WhatsApp AI Bot

Olá João Silva,

Seu pagamento foi aprovado!

🔑 SUAS CREDENCIAIS:
Email: cliente@exemplo.com
Senha: Abc123!@#XyZ

[Botão: Acessar Dashboard]

Próximos Passos:
1. Faça login
2. Configure seu conhecimento
3. Conecte WhatsApp
4. Comece a atender!
```

**Nota:** Atualmente em modo desenvolvimento, o email é apenas logado no console.


### 7️⃣ Cliente Recebe Email
- Cliente abre email no Gmail/Outlook/etc
- Vê suas credenciais:
  - **Email:** O mesmo usado no pagamento
  - **Senha:** Gerada automaticamente
- Clica no botão "Acessar Dashboard"

### 8️⃣ Cliente Faz Login
- Acessa: `http://localhost:3000/login` (ou clica no botão do email)
- Preenche formulário:
  - **Email:** cliente@exemplo.com
  - **Senha:** Abc123!@#XyZ (a que recebeu no email)
- Clica em "Entrar"

### 9️⃣ Sistema Valida Credenciais
```python
# O que acontece no backend:
1. Recebe email + senha
2. Busca cliente no banco por email
3. Verifica senha com bcrypt
4. Se correto:
   - Gera token JWT (validade 7 dias)
   - Retorna token + dados do cliente
5. Se incorreto:
   - Retorna erro 401 Unauthorized
```

### 🔟 Cliente Entra no Dashboard
- Token JWT é armazenado no navegador
- Cliente é redirecionado para: `/dashboard`
- Vê menu lateral com opções:
  - Meu Perfil
  - Meu Conhecimento
  - Conectar WhatsApp
  - Conversas
  - Configurações
  - Sair

---

## 🔐 Trocar Senha

O cliente pode trocar a senha a qualquer momento:

### No Dashboard
1. Cliente vai em **"Meu Perfil"**
2. Clica em **"Trocar Senha"**
3. Preenche:
   - **Senha Atual:** Abc123!@#XyZ
   - **Senha Nova:** MinhaNovaSenh@123
   - **Confirmar Senha:** MinhaNovaSenh@123
4. Clica em **"Salvar"**

### O que acontece
```python
# Backend valida:
1. Verifica se senha atual está correta
2. Valida senha nova (mínimo 6 caracteres)
3. Cria novo hash bcrypt
4. Atualiza no banco
5. Retorna sucesso
```

### Próximo Login
- Cliente usa a **senha nova**
- Senha antiga não funciona mais

---

## 📊 Diagrama do Fluxo

```
Cliente → Landing Page → Botão "Assinar"
    ↓
Stripe Checkout → Preenche dados → Paga
    ↓
Webhook ← Stripe envia notificação
    ↓
Backend → Cria conta + Gera senha
    ↓
Email ← Cliente recebe credenciais
    ↓
Login → Cliente usa email + senha
    ↓
Dashboard → Cliente acessa sistema
    ↓
(Opcional) Trocar Senha → Nova senha
```

---

## ✅ Endpoints Disponíveis

### POST /api/v1/auth/login
Faz login e retorna token JWT

**Request:**
```json
{
  "email": "cliente@exemplo.com",
  "senha": "Abc123!@#XyZ"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "cliente": {
    "id": 1,
    "nome": "João Silva",
    "email": "cliente@exemplo.com",
    "status": "ativo"
  }
}
```

### GET /api/v1/auth/me
Retorna dados do cliente autenticado

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "nome": "João Silva",
  "email": "cliente@exemplo.com",
  "telefone": "+5511999999999",
  "status": "ativo"
}
```

### POST /api/v1/auth/trocar-senha
Troca a senha do cliente autenticado

**Headers:**
```
Authorization: Bearer <token>
```

**Request:**
```json
{
  "senha_atual": "Abc123!@#XyZ",
  "senha_nova": "MinhaNovaSenh@123"
}
```

**Response:**
```json
{
  "message": "Senha alterada com sucesso"
}
```

---

## 🧪 Como Testar

### 1. Testar Login
```bash
# Abra no navegador:
http://localhost:8000/docs

# Ou use PowerShell:
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"email":"teste@exemplo.com","senha":"senha123"}'
```

### 2. Testar Trocar Senha
```bash
# 1. Faça login e pegue o token
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"email":"teste@exemplo.com","senha":"senha123"}'

$token = $response.access_token

# 2. Troque a senha
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/trocar-senha" `
  -Method POST `
  -ContentType "application/json" `
  -Headers @{Authorization="Bearer $token"} `
  -Body '{"senha_atual":"senha123","senha_nova":"novaSenha456"}'

# 3. Teste login com senha nova
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"email":"teste@exemplo.com","senha":"novaSenha456"}'
```

---

## 🔒 Segurança

### Senhas
- ✅ Armazenadas com hash bcrypt (irreversível)
- ✅ Geradas automaticamente com caracteres seguros
- ✅ Mínimo 6 caracteres para trocar
- ✅ Validação de senha atual antes de trocar

### Tokens JWT
- ✅ Validade de 7 dias
- ✅ Assinados com chave secreta
- ✅ Validados em todas as rotas protegidas
- ✅ Incluem ID e email do cliente

### Email
- ✅ Enviado apenas para email do pagamento
- ✅ Credenciais enviadas uma única vez
- ✅ Cliente pode trocar senha depois

---

## ❓ Perguntas Frequentes

### O cliente pode escolher a senha no pagamento?
Não. A senha é gerada automaticamente por segurança. O cliente pode trocá-la depois no dashboard.

### E se o cliente perder o email com a senha?
Você precisará implementar "Esqueci minha senha" (não implementado ainda). Por enquanto, você pode resetar manualmente no banco.

### A senha expira?
Não. A senha é válida até o cliente trocá-la.

### O token JWT expira?
Sim, após 7 dias. O cliente precisa fazer login novamente.

### Posso usar outro serviço de email?
Sim! Modifique `apps/backend/app/services/email/email_service.py` para usar Mailgun, Amazon SES, etc.

---

## 📝 Próximos Passos

1. ✅ Sistema de login funcionando
2. ✅ Envio de email implementado
3. ✅ Trocar senha implementado
4. ⏳ Criar tela de login no frontend
5. ⏳ Criar dashboard no frontend
6. ⏳ Implementar "Esqueci minha senha"
7. ⏳ Implementar "Meu Perfil" com trocar senha
