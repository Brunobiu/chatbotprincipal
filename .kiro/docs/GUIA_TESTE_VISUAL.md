# 🎯 Guia Visual - Testar Login no Navegador

## Passo 1: Abrir Documentação Interativa

Abra no navegador: **http://localhost:8000/docs**

Você verá uma página com todos os endpoints da API.

---

## Passo 2: Testar o Login

1. Procure a seção **"Auth"** na lista
2. Clique em **"POST /api/v1/auth/login"**
3. Clique no botão **"Try it out"** (canto direito)
4. No campo "Request body", cole:
   ```json
   {
     "email": "teste@exemplo.com",
     "senha": "senha123"
   }
   ```
5. Clique em **"Execute"**

### ✅ Resultado Esperado:
Você verá uma resposta com:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "cliente": {
    "id": 1,
    "nome": "Cliente Teste",
    "email": "teste@exemplo.com",
    "status": "ativo"
  }
}
```

**COPIE O TOKEN** (o texto longo que começa com "eyJ...")

---

## Passo 3: Autorizar com o Token

1. No topo da página, clique no botão **"Authorize"** (cadeado verde)
2. Cole o token que você copiou no campo **"Value"**
3. Clique em **"Authorize"**
4. Clique em **"Close"**

Agora você está autenticado! 🎉

---

## Passo 4: Testar Endpoint Protegido (/me)

1. Procure **"GET /api/v1/auth/me"** na lista
2. Clique nele
3. Clique em **"Try it out"**
4. Clique em **"Execute"**

### ✅ Resultado Esperado:
```json
{
  "id": 1,
  "nome": "Cliente Teste",
  "email": "teste@exemplo.com",
  "telefone": "+5511999999999",
  "status": "ativo"
}
```

---

## 🎉 Pronto!

Se você viu essas respostas, o login está funcionando perfeitamente!

---

## 🐛 Se der erro:

### Erro 404 (Not Found)
- Verifique se o backend está rodando: `docker-compose ps`
- Reinicie: `docker-compose restart bot`

### Erro 401 (Unauthorized)
- Verifique se copiou o token completo
- Tente fazer login novamente
