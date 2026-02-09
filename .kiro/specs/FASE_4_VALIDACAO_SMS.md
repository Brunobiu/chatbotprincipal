# 📱 FASE 4: VALIDAÇÃO POR TELEFONE/SMS

**Data:** 09/02/2026  
**Objetivo:** Validar identidade por SMS antes de ativar trial  
**Tempo estimado:** 2h  
**Custo:** ~R$0,10 por SMS

---

## 📋 TAREFAS

### **Backend:**
- [x] Adicionar campo `telefone` e `telefone_verificado` na tabela `clientes`
- [x] Criar tabela `sms_verification` (telefone, codigo, expires_at)
- [x] Integrar Twilio e AWS SNS (suporte para ambos)
- [x] Endpoint: `/auth/send-sms-code` - Envia código SMS
- [x] Endpoint: `/auth/verify-sms-code` - Valida código
- [x] Validar: 1 trial por telefone
- [x] Bloquear trial se telefone já foi usado
- [x] Modo desenvolvimento (retorna código no response)

### **Frontend:**
- [ ] Adicionar campo telefone no cadastro
- [ ] Tela de verificação SMS (input código)
- [ ] Enviar código ao backend
- [ ] Validar código antes de liberar acesso

---

## 🔧 TECNOLOGIAS

**Opção A: Twilio** (Recomendado)
- Mais confiável
- Suporte global
- ~R$0,10 por SMS no Brasil

**Opção B: AWS SNS**
- Mais barato (~R$0,05)
- Integrado com AWS
- Menos features

---

## 💰 CUSTO ESTIMADO

- 100 cadastros/mês = R$10/mês
- 1000 cadastros/mês = R$100/mês

---

## 📊 PROGRESSO

**Total de tarefas:** 12  
**Concluídas:** 8  
**Pendentes:** 4 (frontend)  
**Status:** 🟡 Backend completo - 67% concluído

---

## ⚠️ IMPORTANTE

Para implementar, você precisa:
1. Conta Twilio (ou AWS SNS)
2. Número de telefone Twilio
3. Credenciais API (Account SID + Auth Token)

**Você tem conta Twilio ou prefere usar AWS SNS?**
