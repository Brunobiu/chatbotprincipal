# 🔄 REINICIAR DOCKER DESKTOP - GUIA RÁPIDO

**Problema**: Docker Desktop com erro 500  
**Tempo**: 2-3 minutos

---

## 🚀 PASSO A PASSO

### 1. Fechar Docker Desktop
- **Clique com botão direito** no ícone do Docker (bandeja do sistema)
- **Selecione**: "Quit Docker Desktop"
- **Aguarde** o ícone desaparecer

### 2. Finalizar Processos
- **Pressione**: `Ctrl+Shift+Esc` (Gerenciador de Tarefas)
- **Procure**: Processos com "Docker" no nome
- **Finalize TODOS**: Clique com botão direito → "Finalizar tarefa"

### 3. Abrir Docker Desktop
- **Abra** o Docker Desktop novamente
- **Aguarde** 2-3 minutos para inicializar
- **Verifique** se o ícone fica verde

### 4. Verificar Containers
```powershell
docker ps
```

Se mostrar os containers, está funcionando!

---

## ✅ APÓS REINICIAR

Execute o teste:
```powershell
.\testar_backend.ps1
```

**Resultado esperado**:
- ✅ Health Check: OK
- ✅ Login: ~1s
- ✅ Buscar: ~0.03s
- ✅ Salvar: ~1-3s (DEVE FUNCIONAR!)

---

**ME AVISE QUANDO REINICIAR O DOCKER!**