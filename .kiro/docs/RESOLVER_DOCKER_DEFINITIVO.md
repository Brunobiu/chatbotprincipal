# 🔧 RESOLVER DOCKER DEFINITIVAMENTE

**Problema**: Docker Desktop com erro 500 na API  
**Causa**: Versão da API incompatível ou Docker corrompido  
**Solução**: Reset completo do Docker Desktop

---

## 🚀 SOLUÇÃO DEFINITIVA (5 minutos)

### Passo 1: Fechar Docker Desktop Completamente

1. **Gerenciador de Tarefas**: `Ctrl+Shift+Esc`
2. **Finalize TODOS os processos Docker**:
   - Docker Desktop
   - Docker Desktop Service
   - com.docker.backend
   - com.docker.service
   - com.docker.proxy
   - Qualquer processo com "Docker"

### Passo 2: Limpar Dados do Docker (IMPORTANTE)

Abra PowerShell como **Administrador** e execute:

```powershell
# Parar serviços
Stop-Service -Name "com.docker.service" -Force -ErrorAction SilentlyContinue

# Limpar cache e dados temporários
Remove-Item -Path "$env:APPDATA\Docker" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:LOCALAPPDATA\Docker" -Recurse -Force -ErrorAction SilentlyContinue

# Limpar dados do WSL (se usar WSL2)
wsl --shutdown
```

### Passo 3: Reiniciar Docker Desktop

1. **Abra o Docker Desktop**
2. **Aguarde 3-5 minutos** para inicializar completamente
3. **Aceite** qualquer atualização que aparecer
4. **Aguarde** o ícone ficar verde

### Passo 4: Verificar se Funcionou

```powershell
docker --version
docker ps
```

Se mostrar a versão e os containers, está funcionando!

---

## ✅ APÓS DOCKER FUNCIONAR

### Subir os Containers Novamente

```powershell
cd C:\Users\usuario\Desktop\whatsapp_ai_bot

# Subir todos os containers
docker-compose up -d

# Aguardar inicializar
Start-Sleep -Seconds 30

# Verificar
docker-compose ps
```

### Testar Backend

```powershell
.\testar_backend.ps1
```

**Resultado esperado**:
- ✅ Health Check: OK
- ✅ Login: ~0.6s
- ✅ Buscar: ~0.04s
- ✅ Salvar: ~1s (DEVE FUNCIONAR!)

---

## 🆘 SE AINDA NÃO FUNCIONAR

### Opção A: Reinstalar Docker Desktop

1. **Desinstale** o Docker Desktop pelo Painel de Controle
2. **Reinicie** o computador
3. **Baixe** a versão mais recente: https://www.docker.com/products/docker-desktop/
4. **Instale** novamente
5. **Abra** e aguarde inicializar
6. **Execute** os comandos acima para subir os containers

### Opção B: Usar WSL2 Diretamente (Avançado)

Se você tem WSL2 instalado:

```powershell
# Abrir Ubuntu/WSL2
wsl

# Dentro do WSL2
cd /mnt/c/Users/usuario/Desktop/whatsapp_ai_bot
docker-compose up -d
```

---

## 📊 CHECKLIST

- [ ] Finalizei todos os processos Docker
- [ ] Limpei cache do Docker
- [ ] Reiniciei Docker Desktop
- [ ] Docker Desktop está verde
- [ ] `docker ps` funciona
- [ ] Subi os containers com `docker-compose up -d`
- [ ] Testei com `.\testar_backend.ps1`

---

## 🎯 RESUMO

1. **Feche** todos os processos Docker (Gerenciador de Tarefas)
2. **Limpe** cache do Docker (PowerShell Admin)
3. **Abra** Docker Desktop novamente
4. **Suba** containers: `docker-compose up -d`
5. **Teste**: `.\testar_backend.ps1`

---

**QUAL PASSO VOCÊ ESTÁ AGORA?**