# Como Testar o Sistema de Login

## 🎯 Credenciais de Teste

**Email:** `teste@exemplo.com`  
**Senha:** `senha123`

---

## 🧪 Teste 1: Login (Obter Token)

### PowerShell (Windows)
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"email":"teste@exemplo.com","senha":"senha123"}'
```

### cURL (Linux/Mac)
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"teste@exemplo.com","senha":"senha123"}'
```

### Resposta Esperada
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

---

## 🧪 Teste 2: Endpoint Protegido (/me)

### PowerShell (Windows)
```powershell
# Primeiro, faça login e salve o token
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"email":"teste@exemplo.com","senha":"senha123"}'

$token = $response.access_token

# Agora use o token para acessar /me
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/me" `
  -Method GET `
  -Headers @{Authorization="Bearer $token"}
```

### cURL (Linux/Mac)
```bash
# Primeiro, faça login e salve o token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"teste@exemplo.com","senha":"senha123"}' \
  | jq -r '.access_token')

# Agora use o token para acessar /me
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### Resposta Esperada
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

## 🧪 Teste 3: Token Inválido (Deve Falhar)

### PowerShell (Windows)
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/me" `
  -Method GET `
  -Headers @{Authorization="Bearer token_invalido"}
```

### cURL (Linux/Mac)
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer token_invalido"
```

### Resposta Esperada
```json
{
  "detail": "Token inválido ou expirado"
}
```

Status: `401 Unauthorized`

---

## 🧪 Teste 4: Credenciais Inválidas (Deve Falhar)

### PowerShell (Windows)
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"email":"teste@exemplo.com","senha":"senhaerrada"}'
```

### cURL (Linux/Mac)
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"teste@exemplo.com","senha":"senhaerrada"}'
```

### Resposta Esperada
```json
{
  "detail": "Email ou senha incorretos"
}
```

Status: `401 Unauthorized`

---

## 🔧 Criar/Resetar Usuário de Teste

Se precisar criar um novo usuário ou resetar a senha:

```bash
docker exec -it bot python criar_usuario_teste.py
```

---

## 📝 Testar na Documentação Interativa

Você também pode testar diretamente na documentação interativa do FastAPI:

1. Abra: http://localhost:8000/docs
2. Procure por "Auth" na lista de endpoints
3. Clique em "POST /api/v1/auth/login"
4. Clique em "Try it out"
5. Preencha:
   ```json
   {
     "email": "teste@exemplo.com",
     "senha": "senha123"
   }
   ```
6. Clique em "Execute"
7. Copie o `access_token` da resposta
8. Clique no botão "Authorize" no topo da página
9. Cole o token no campo "Value" (formato: `Bearer <token>`)
10. Agora você pode testar o endpoint GET /api/v1/auth/me

---

## ✅ Checklist de Testes

- [ ] Login com credenciais corretas retorna token
- [ ] Token JWT é válido e tem formato correto
- [ ] Endpoint /me retorna dados do usuário com token válido
- [ ] Token inválido retorna 401
- [ ] Credenciais inválidas retornam 401
- [ ] Token expira após 7 dias (configurável)

---

## 🐛 Troubleshooting

### Erro: "Token inválido ou expirado"
- Verifique se o token está no formato correto: `Bearer <token>`
- Verifique se o token não expirou (validade: 7 dias)
- Faça login novamente para obter um novo token

### Erro: "Email ou senha incorretos"
- Verifique se está usando as credenciais corretas
- Execute o script de reset de senha: `docker exec -it bot python criar_usuario_teste.py`

### Erro: "Not Found" (404)
- Verifique se o backend está rodando: `docker-compose ps`
- Verifique se a URL está correta: `http://localhost:8000/api/v1/auth/login`
- Reinicie o backend: `docker-compose restart bot`
