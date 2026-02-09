# Correções e Melhorias - WhatsApp AI Bot SaaS

**Data de Criação:** 08/02/2026  
**Status:** Planejamento  
**Prioridade:** Alta

---

## 📋 Visão Geral

Esta spec documenta todas as correções de bugs identificados e novas funcionalidades solicitadas para melhorar o sistema antes do deploy em produção (Fase 17).

---

## 🎯 Objetivos

1. **Corrigir bugs críticos** no dashboard do cliente
2. **Implementar melhorias de segurança** no conhecimento
3. **Adicionar funcionalidades faltantes** (agendamento, chat melhorado)
4. **Melhorar UX/UI** (login, dashboard, notificações)
5. **Preparar sistema para produção** (dados reais, múltiplos planos)

---

## 👥 User Stories

### 1. Correções Críticas (Bugs)

#### 1.1 Como cliente, quero visualizar minhas conversas
**Problema:** `/dashboard/conversas` não funciona  
**Solução:** Implementar página de conversas com histórico

**Critérios de Aceite:**
- [ ] Página `/dashboard/conversas` carrega sem erros
- [ ] Lista todas as conversas do cliente
- [ ] Mostra histórico de mensagens de cada conversa
- [ ] Filtros por data e status funcionam
- [ ] Paginação implementada (20 conversas por página)
- [ ] Design responsivo (mobile-friendly)

---

#### 1.2 Como cliente, quero que o contador de mensagens funcione corretamente
**Problema:** `/dashboard/conhecimento` está diminuindo mensagens  
**Solução:** Corrigir lógica de contagem

**Critérios de Aceite:**
- [ ] Contador de mensagens não diminui incorretamente
- [ ] Salvar conhecimento não afeta contador
- [ ] Contador reflete uso real de mensagens
- [ ] Teste com múltiplas operações de salvar

---

#### 1.3 Como cliente, quero editar meu perfil
**Problema:** `/dashboard/perfil` não permite edição  
**Solução:** Adicionar funcionalidade de edição

**Critérios de Aceite:**
- [ ] Botão "Editar Informações" visível
- [ ] Permite alterar: nome, telefone, email
- [ ] Validação de email único
- [ ] Confirmação por senha antes de salvar
- [ ] Mensagem de sucesso após salvar
- [ ] Atualização reflete imediatamente

---

#### 1.4 Como cliente, quero ver informações da minha assinatura
**Problema:** Dashboard não mostra status de pagamento  
**Solução:** Adicionar widget de assinatura

**Critérios de Aceite:**
- [ ] Widget no lado direito do dashboard
- [ ] Mostra dias restantes de acesso
- [ ] Mostra status da assinatura (ativa, cancelada, expirada)
- [ ] Botão "Pagar mais um mês" (se mensal)
- [ ] Botão "Mudar de plano"
- [ ] Link para histórico de pagamentos

---

#### 1.5 Como cliente, quero ver tutoriais do admin
**Problema:** Tutoriais não refletem para clientes  
**Solução:** Corrigir sincronização de tutoriais

**Critérios de Aceite:**
- [ ] Tutoriais criados pelo admin aparecem para todos os clientes
- [ ] Notificação de novo tutorial
- [ ] Badge "Novo" em tutoriais não visualizados
- [ ] Marcar como visualizado funciona
- [ ] Comentários abaixo dos vídeos funcionam

---

### 2. Melhorias de Segurança

#### 2.1 Como cliente, quero segurança ao salvar conhecimento
**Solução:** Exigir senha ao salvar

**Critérios de Aceite:**
- [ ] Modal de confirmação ao clicar "Salvar"
- [ ] Input de senha no modal
- [ ] Validação da senha
- [ ] Mensagem de erro se senha incorreta
- [ ] Salva apenas se senha correta
- [ ] Opção "Lembrar por 10 minutos" (opcional)

---

#### 2.2 Como cliente, quero ajuda da IA para melhorar meu conhecimento
**Solução:** Botão "Deixa que a IA te ajuda"

**Critérios de Aceite:**
- [ ] Botão ao lado de "Salvar Conhecimento"
- [ ] Abre modal com textarea
- [ ] Cliente digita texto de qualquer forma
- [ ] Botão "Melhorar com IA" dentro do modal
- [ ] IA estrutura e melhora o texto
- [ ] Preview do texto melhorado
- [ ] Botão "Adicionar texto da IA"
- [ ] Texto adicionado ao conteúdo principal
- [ ] Ao salvar, pede senha novamente

---

### 3. Novas Funcionalidades

#### 3.1 Como cliente, quero sistema de agendamento
**Solução:** Bot faz agendamentos automaticamente

**Critérios de Aceite:**
- [ ] Nova aba "Agendamentos" no menu lateral
- [ ] Cliente configura horários disponíveis
- [ ] Cliente define duração de cada slot
- [ ] Bot entende pedidos de agendamento
- [ ] Bot marca automaticamente na agenda
- [ ] Cliente vê lista de agendamentos pendentes
- [ ] Cliente pode aprovar/recusar agendamento
- [ ] Notificação automática ao cliente final (WhatsApp)
- [ ] Relatório de agendamentos do dia
- [ ] Funciona para: pizzaria, clínica, odontologia, etc.

**Casos de Uso:**
- Pizzaria: pedidos com horário de entrega
- Clínica veterinária: banho, consulta
- Odontologia: consultas
- Salão de beleza: corte, manicure

---

#### 3.2 Como cliente, quero chat suporte melhorado
**Solução:** Chat com IA + sistema de tickets

**Critérios de Aceite:**
- [ ] Ícone de chat na barra lateral
- [ ] Chat abre em modal/sidebar
- [ ] IA responde automaticamente
- [ ] Quando IA não sabe: oferece abrir ticket
- [ ] Botão "Abrir Ticket" aparece
- [ ] Modal de ticket com:
  - [ ] Seleção de categoria
  - [ ] Campo de descrição
  - [ ] Upload de até 10 fotos
- [ ] Mensagem "Enviado com sucesso"
- [ ] Admin recebe notificação
- [ ] Chat bidirecional (cliente ↔ admin)

---

#### 3.3 Como admin, quero usar minha própria ferramenta
**Solução:** Admin conecta WhatsApp e vende seu produto

**Critérios de Aceite:**
- [ ] Seção no painel admin "Minha Ferramenta"
- [ ] Conectar WhatsApp (QR Code)
- [ ] Upload de conhecimento (documento de vendas)
- [ ] Configurar tom e mensagens
- [ ] IA responde clientes automaticamente
- [ ] Ver conversas em tempo real
- [ ] Fallback para admin quando necessário
- [ ] Notificação de conversa aguardando
- [ ] Responder manualmente quando necessário

---

#### 3.4 Como admin, quero dicas da IA no dashboard
**Solução:** IA analisa sistema e traz insights

**Critérios de Aceite:**
- [ ] Widget "Dicas da IA" acima das estatísticas
- [ ] Atualiza uma vez por dia (ao fazer login)
- [ ] Mostra:
  - [ ] Novos clientes (nome, data)
  - [ ] Clientes que cancelaram
  - [ ] Clientes prestes a vencer
  - [ ] Dicas de conversão
  - [ ] Sugestões de ROI
  - [ ] Porcentagem para gastar com anúncios
  - [ ] Análise de lucro
  - [ ] Progresso do objetivo mensal
- [ ] Configuração de objetivo mensal
- [ ] IA compara com objetivo e sugere ações

---

### 4. Melhorias de UX/UI

#### 4.1 Como usuário, quero login mais bonito
**Solução:** Redesign da página de login

**Critérios de Aceite:**
- [ ] Layout: metade foto, metade inputs
- [ ] Foto/ilustração moderna
- [ ] Inputs com ícones
- [ ] Animações suaves
- [ ] Responsivo (mobile-friendly)
- [ ] Loading state ao fazer login
- [ ] Mensagens de erro amigáveis

---

#### 4.2 Como cliente, quero que bot pergunte meu nome
**Solução:** Bot inicia conversa perguntando nome

**Critérios de Aceite:**
- [ ] Primeira mensagem: "Olá! Qual é o seu nome?"
- [ ] Salva nome no contexto da conversa
- [ ] Usa nome nas respostas seguintes
- [ ] Armazena nome no banco de dados
- [ ] Não pergunta novamente em conversas futuras

---

### 5. Melhorias de Pagamento

#### 5.1 Como cliente, quero mais opções de pagamento
**Solução:** Adicionar PIX e débito

**Critérios de Aceite:**
- [ ] Opção de pagamento por PIX
- [ ] Opção de cartão de débito
- [ ] Cartão de crédito (já existe)
- [ ] QR Code para PIX
- [ ] Confirmação automática de pagamento PIX
- [ ] Webhook do Stripe para débito

---

#### 5.2 Como cliente, quero escolher plano de assinatura
**Solução:** Múltiplos planos

**Critérios de Aceite:**
- [ ] Plano 1 mês (valor X)
- [ ] Plano 3 meses (desconto 10%)
- [ ] Plano 1 ano (desconto 20%)
- [ ] Página de checkout mostra todos os planos
- [ ] Cliente pode mudar de plano
- [ ] Cálculo proporcional ao mudar plano

---

### 6. Preparação para Produção

#### 6.1 Como admin, quero dados de produção
**Solução:** Checklist de mudanças para produção

**Critérios de Aceite:**
- [ ] Documento `.kiro/contexto/CHECKLIST_PRODUCAO.md` criado
- [ ] Lista todas as mudanças necessárias:
  - [ ] Credenciais admin (email e senha forte)
  - [ ] Credenciais cliente teste (email secundário)
  - [ ] Produtos reais (valores e planos)
  - [ ] Stripe modo produção
  - [ ] SMTP real (SendGrid)
  - [ ] Domínio e SSL
  - [ ] Variáveis de ambiente produção
- [ ] Script para facilitar migração

---

## 🔄 Dependências

### Correções Críticas (Prioridade 1)
- 1.1 → 1.2 → 1.3 → 1.4 → 1.5

### Melhorias de Segurança (Prioridade 2)
- 2.1 → 2.2

### Novas Funcionalidades (Prioridade 3)
- 3.1 (independente)
- 3.2 (independente)
- 3.3 (depende de 3.2)
- 3.4 (independente)

### Melhorias de UX/UI (Prioridade 4)
- 4.1 → 4.2

### Melhorias de Pagamento (Prioridade 5)
- 5.1 → 5.2

### Preparação para Produção (Prioridade 6)
- 6.1 (última etapa)

---

## 📊 Estimativa de Esforço

| Categoria | User Stories | Estimativa |
|-----------|--------------|------------|
| Correções Críticas | 5 | 2-3 dias |
| Melhorias de Segurança | 2 | 1 dia |
| Novas Funcionalidades | 4 | 5-7 dias |
| Melhorias de UX/UI | 2 | 1-2 dias |
| Melhorias de Pagamento | 2 | 2-3 dias |
| Preparação para Produção | 1 | 1 dia |
| **TOTAL** | **16** | **12-17 dias** |

---

## ✅ Critérios de Sucesso

1. **Todos os bugs críticos corrigidos** (100%)
2. **Sistema seguro** (senha ao salvar, validações)
3. **Funcionalidades novas funcionando** (agendamento, chat, dicas IA)
4. **UX melhorada** (login bonito, feedback visual)
5. **Múltiplos planos de pagamento** (1, 3, 12 meses)
6. **Checklist de produção completo**
7. **Testes realizados** em todas as funcionalidades
8. **Documentação atualizada**

---

## 🚀 Próximos Passos

1. Revisar e aprovar esta spec
2. Criar `design.md` com arquitetura técnica
3. Criar `tasks.md` com tarefas detalhadas
4. Executar tarefas por prioridade
5. Testar cada funcionalidade
6. Deploy em produção (Fase 17)

---

**Aprovação:** Pendente  
**Próxima Revisão:** Após aprovação do cliente
