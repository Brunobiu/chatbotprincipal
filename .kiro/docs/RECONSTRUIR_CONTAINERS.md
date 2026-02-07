# 🔄 RECONSTRUIR CONTAINERS - GUIA COMPLETO

**Situação**: Docker Desktop travado  
**Solução**: Forçar parada e reconstruir  
**Tempo**: 5-10 minutos

---

## 🚀 OPÇÃO 1: FORÇAR REINICIALIZAÇÃO (MAIS RÁPIDO)

### Passo 1: Reiniciar o PC
**Isso resolve 90% dos problemas do Docker**

1. **Salve todo o trabalho**
2. **Reinicie o computador**
3. **Aguarde o Windows inicializar**
4. **Docker Desktop deve abrir automaticamente**
5. **Aguarde 2-3 minutos** para Docker inicializar

### Passo 2: Verificar Containers
```powershell
cd C:\Users\usuario\Desktop\whatsapp_ai_bot
docker-compose ps
```

### Passo 3: Se Containers Não Estiverem Rodando
```powershell
docker-compose up -d
```

### Passo 4: Testar
```powershell
.\testar_backend.ps1
```

---

## 🔧 OPÇÃO 2: RECONSTRUIR CONTAINERS (SE OPÇÃO 1 NÃO FUNCIONAR)

### Passo 1: Parar Tudo (Forçado)
```powershell
# Tentar parar normalmente
docker-compose down

# Se não funcionar, forçar pelo PowerShell como Admin
Stop-Service -Name "com.docker.service" -Force
Start-Service -Name "com.docker.service"
```

### Passo 2: Limpar Containers Antigos
```powershell
# Remover containers parados
docker container prune -f

# Remover imagens não usadas
docker image prune -f
```

### Passo 3: Reconstruir Backend
```powershell
# Rebuild apenas o backend (mais rápido)
docker-compose build --no-cache bot

# Subir tudo novamente
docker-compose up -d
```

### Passo 4: Verificar
```powershell
docker-compose ps
docker-compose logs bot --tail 20
```

---

## 🆘 OPÇÃO 3: RESET COMPLETO (ÚLTIMO RECURSO)

**ATENÇÃO**: Isso apaga TODOS os dados dos containers!

### Passo 1: Parar e Remover Tudo
```powershell
docker-compose down -v
```

### Passo 2: Limpar Tudo
```powershell
docker system prune -a --volumes -f
```

### Passo 3: Reconstruir Tudo
```powershell
docker-compose build --no-cache
docker-compose up -d
```

### Passo 4: Recriar Banco de Dados
```powershell
# Aguardar containers subirem
Start-Sleep -Seconds 30

# Criar tabelas
docker exec -it bot python app/scripts/create_tables.py

# Criar usuário de teste
docker exec -it bot python criar_usuario_teste.py
```

---

## 📊 VERIFICAÇÃO FINAL

Após qualquer opção, execute:

```powershell
# 1. Verificar containers
docker-compose ps

# 2. Testar backend
.\testar_backend.ps1

# 3. Testar frontend
# Abra: http://localhost:3001
# Login: teste@teste.com / 123456
```

---

## 🎯 RECOMENDAÇÃO

**COMECE PELA OPÇÃO 1** (Reiniciar PC)

É a solução mais simples e resolve a maioria dos problemas do Docker Desktop no Windows.

---

**QUAL OPÇÃO VOCÊ QUER TENTAR?**

1. Reiniciar PC (2 minutos)
2. Reconstruir containers (5 minutos)
3. Reset completo (10 minutos + recriar dados)