# Como Acessar a Tela de Login

## Status
✅ Frontend reiniciado e funcionando na porta 3001

## Acesso
Abra seu navegador e acesse:
```
http://localhost:3001/login
```

## Credenciais de Teste
- **Email**: `teste@exemplo.com`
- **Senha**: `senha123`

## Fluxo Completo
1. Acesse `http://localhost:3001/login`
2. Digite email e senha
3. Clique em "Entrar"
4. Você será redirecionado para `/dashboard`
5. No dashboard você verá seus dados e poderá fazer logout

## Links na Página de Login
- **"Ainda não tem conta? Assine agora"** → Redireciona para landing page (`/`)
- **"← Voltar para home"** → Redireciona para landing page (`/`)

## Troubleshooting
Se ainda aparecer "Not Found":
1. Limpe o cache do navegador (Ctrl+Shift+Delete)
2. Tente em modo anônimo/privado
3. Tente outro navegador
4. Verifique se está acessando a porta correta (3001, não 3000)

## Próximos Passos
Depois de testar o login:
1. Testar fluxo completo: login → dashboard → logout
2. Testar erro de credenciais inválidas
3. Testar proteção de rota (acessar /dashboard sem login)
