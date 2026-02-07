# 🔧 SOLUÇÃO: Docker Desktop com Erro 500

**Data**: 07/02/2026 - 03:30  
**Status**: ⚠️ PROBLEMA IDENTIFICADO

---

## 🎯 PROBLEMA

Docker Desktop está retornando erro 500:
```
request returned 500 Internal Server Error for API route and version
```

Isso impede:
- ❌ `docker-compose restart`
- ❌ `docker logs`
- ❌ `docker ps`
- ❌ Qualquer comando Docker

**Causa**: Docker Desktop instável após upgrade de RAM ou reinicialização do sistema.

---

## ✅ SOLUÇÃO COMPLETA

### Passo 1: Fechar Docker Desktop
1. **Clique com botão direito** no ícone do Docker na bandeja do sistema (canto inferior direito)
2. **Selecione**: "Quit Docker Desktop"
3. **Aguarde** até o ícone desaparecer

### Passo 2: Finalizar Processos Docker
1. **Pressione**: `Ctrl+Shift+Esc` (Gerenciador de Tarefas)
2. **Vá na aba**: "Processos"
3. **Procure e finalize** TODOS os processos que contenham "Docker":
   - Docker Desktop
   - Docker Engine
   - Docker CLI
   - com.docker.backend
   - com.docker.proxy
4. **Clique com botão direito** → "Finalizar tarefa"

### Passo 3: Limpar Cache Docker (OPCIONAL)
Se o problema persistir, execute no PowerShell como **Administrador**:

```powershell
# Parar serviços Docker
Stop-Service -Name "com.docker.service" -Force -ErrorAction SilentlyContinue

# Limpar cache
Remove-Item -Path "$env:APPDATA\Docker" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:LOCALAPPDATA\Docker" -Recurse -Force -ErrorAction SilentlyContinue
```

### Passo 4: Reiniciar Docker Desktop
1. **Abra o Docker Desktop** novamente
2. **Aguarde** a inicialização completa (pode demorar 2-3 minutos)
3. **Verifique** se o ícone fica verde na bandeja

### Passo 5: Verificar Containers
```powershell
# Verificar se containers estão rodando
docker ps

# Se não estiverem, subir novamente
docker-compose up -d

# Verificar status
docker-compose ps
```

---

## 🧪 TESTE RÁPIDO

Após reiniciar o Docker Desktop:

```powershell
# Teste 1: Docker funcionando
docker --version

# Teste 2: Containers rodando
docker ps

# Teste 3: Backend funcionando
Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing

# Teste 4: Frontend funcionando
# Abra: http://localhost:3001
```

---

## 🚨 SE AINDA NÃO FUNCIONAR

### Opção A: Reiniciar PC
1. **Salve todo o trabalho**
2. **Reinicie o computador**
3. **Abra o Docker Desktop**
4. **Execute**: `docker-compose up -d`

### Opção B: Reinstalar Docker Desktop
1. **Desinstale** o Docker Desktop pelo Painel de Controle
2. **Baixe** a versão mais recente: https://www.docker.com/products/docker-desktop/
3. **Instale** novamente
4. **Configure** novamente os containers

### Opção C: Usar Docker via WSL2 (AVANÇADO)
Se você tem WSL2 instalado:
1. **Abra** o Ubuntu/WSL2
2. **Execute**: `docker --version`
3. **Se funcionar**, use os comandos Docker pelo WSL2

---

## 📊 STATUS ATUAL

| Componente | Status | Observação |
|------------|--------|------------|
| Docker Desktop | ❌ Erro 500 | Precisa reiniciar |
| Backend | ⚠️ Provavelmente OK | Rodando no container |
| Frontend | ⚠️ Provavelmente OK | Rodando na porta 3001 |
| PostgreSQL | ⚠️ Provavelmente OK | Dados preservados |
| ChromaDB | ⚠️ Provavelmente OK | Embeddings preservados |

**IMPORTANTE**: Os dados estão preservados nos volumes Docker. Reiniciar o Docker Desktop **NÃO** apaga os dados.

---

## 🎯 RESUMO

1. **Problema**: Docker Desktop com erro 500
2. **Causa**: Instabilidade após mudanças no sistema
3. **Solução**: Reiniciar Docker Desktop completamente
4. **Dados**: Preservados nos volumes
5. **Tempo**: 5-10 minutos para resolver

---

## 📝 PRÓXIMOS PASSOS

Após resolver o Docker Desktop:

1. ✅ Verificar se containers estão rodando
2. ✅ Testar backend: `.\testar_backend.ps1`
3. ✅ Testar frontend: http://localhost:3001
4. ✅ Limpar cache do navegador: `Ctrl+Shift+R`
5. ✅ Testar salvar conhecimento

---

**Última atualização**: 07/02/2026 - 03:30  
**Status**: ⚠️ AGUARDANDO REINICIALIZAÇÃO DO DOCKER DESKTOP
