# Implementation Plan: Correções e Melhorias

## Overview

Este plano de implementação organiza todas as correções de bugs e novas funcionalidades em tarefas executáveis, seguindo a ordem de prioridades definida nos requisitos.

**Stack Técnico:**
- Backend: Python (FastAPI)
- Frontend: TypeScript (Next.js 14)
- Banco de Dados: PostgreSQL
- Cache: Redis
- Vetores: ChromaDB

**Estratégia de Execução:**
- Implementar por prioridade (1 a 6)
- Testar cada funcionalidade antes de avançar
- Commits frequentes após cada tarefa completa
- Checkpoints para validação com usuário

---

## Tasks

### PRIORIDADE 1 - Correções Críticas

- [x] 1. Corrigir página de conversas
  - [x] 1.1 Criar endpoint GET /api/v1/conversas com filtros e paginação
    - Implementar `ConversaService.listar_conversas()` com suporte a filtros de data e status
    - Adicionar paginação (20 conversas por página)
    - Garantir isolamento por cliente (WHERE cliente_id = current_user.id)
    - _Requirements: 1.1_
  
  - [ ]* 1.2 Escrever testes de propriedade para conversas
    - **Property 1: Isolamento de conversas por cliente**
    - **Property 2: Filtros de data funcionam corretamente**
    - **Property 3: Paginação consistente**
    - **Validates: Requirements 1.1**
  
  - [x] 1.3 Criar endpoint GET /api/v1/conversas/{id}/mensagens
    - Implementar `ConversaService.obter_historico_conversa()`
    - Retornar todas as mensagens ordenadas cronologicamente
    - Validar que conversa pertence ao cliente
    - _Requirements: 1.1_
  
  - [ ]* 1.4 Escrever teste de propriedade para histórico
    - **Property 4: Histórico completo de mensagens**
    - **Validates: Requirements 1.1**
  
  - [x] 1.5 Criar página frontend /dashboard/conversas
    - Implementar componente `ConversasList` com tabela de conversas
    - Adicionar filtros de data (início e fim) e status
    - Implementar paginação com botões anterior/próximo
    - Adicionar modal para visualizar histórico de mensagens
    - _Requirements: 1.1_
  
  - [ ]* 1.6 Escrever testes unitários para página de conversas
    - Testar renderização da página
    - Testar aplicação de filtros
    - Testar navegação de paginação
    - _Requirements: 1.1_


- [x] 2. Corrigir bug do contador de mensagens no conhecimento
  - [x] 2.1 Analisar e corrigir lógica do contador em ConhecimentoService
    - Identificar onde o contador está sendo decrementado incorretamente
    - Garantir que contador só aumenta ao enviar mensagens WhatsApp
    - Garantir que salvar conhecimento NÃO afeta o contador
    - Adicionar validação: contador nunca pode diminuir
    - _Requirements: 1.2_
  
  - [ ]* 2.2 Escrever testes de propriedade para contador
    - **Property 5: Contador monotônico**
    - **Property 6: Salvar conhecimento não afeta contador**
    - **Validates: Requirements 1.2**
  
  - [x] 2.3 Atualizar frontend para exibir contador corretamente
    - Verificado: contador já está sendo exibido no admin (clientes/page.tsx e clientes/[id]/page.tsx)
    - Não há componente separado, está integrado nas páginas
    - Contador atualiza automaticamente ao carregar dados do cliente
    - _Requirements: 1.2_

- [x] 3. Adicionar funcionalidade de edição de perfil
  - [x] 3.1 Criar endpoint PUT /api/v1/perfil
    - Implementado `PerfilService.editar_perfil()` com validação de senha
    - Validado email único (não pode usar email de outro cliente)
    - Permite editar: nome, telefone, email
    - Retorna dados atualizados após salvar
    - _Requirements: 1.3_
  
  - [ ]* 3.2 Escrever testes de propriedade para edição de perfil
    - **Property 9: Email único**
    - **Property 10: Confirmação de senha obrigatória**
    - **Property 11: Atualização imediata**
    - **Validates: Requirements 1.3**
  
  - [x] 3.3 Atualizar página /dashboard/perfil no frontend
    - Criada página completa com formulário editável
    - Botão "Editar Informações" implementado
    - Formulário permite editar: nome, telefone, email
    - Modal de confirmação de senha implementado
    - Mensagem de sucesso após salvar
    - Atualização reflete imediatamente
    - _Requirements: 1.3_
  
  - [ ]* 3.4 Escrever testes unitários para edição de perfil
    - Testar botão "Editar Informações" visível
    - Testar validação de email duplicado
    - Testar mensagem de sucesso
    - _Requirements: 1.3_

- [x] 4. Adicionar widget de informações de assinatura
  - [x] 4.1 Criar endpoint GET /api/v1/assinatura/info
    - Implementado `AssinaturaService.obter_info_assinatura()`
    - Retorna: status, dias_restantes, plano_atual, data_proxima_cobranca, valor_mensal
    - Implementado cálculo correto de dias restantes
    - Integração com Stripe API para buscar dados reais
    - _Requirements: 1.4_
  
  - [ ]* 4.2 Escrever testes de propriedade para assinatura
    - **Property 12: Cálculo preciso de dias restantes**
    - **Property 13: Status correto da assinatura**
    - **Validates: Requirements 1.4**
  
  - [x] 4.3 Criar componente WidgetAssinatura no frontend
    - Exibe dias restantes de acesso
    - Exibe status (ativa, cancelada, expirada) com cores
    - Botão "Pagar mais um mês" (apenas se plano mensal)
    - Botão "Mudar de Plano" (placeholder)
    - Link para histórico de pagamentos (placeholder)
    - _Requirements: 1.4_
  
  - [x] 4.4 Integrar widget no dashboard home
    - Widget adicionado no lado direito do dashboard
    - Layout responsivo com grid 2/3 + 1/3
    - _Requirements: 1.4_
  
  - [ ]* 4.5 Escrever testes unitários para widget
    - Testar exibição de dias restantes
    - Testar botão "Pagar mais um mês" aparece apenas para mensal
    - _Requirements: 1.4_

- [x] 5. Corrigir sincronização de tutoriais
  - [x] 5.1 Analisar e corrigir TutorialService
    - Verificado: TutorialService já estava correto
    - Tutoriais ativos são visíveis para todos os clientes
    - Criado endpoint para clientes acessarem tutoriais
    - _Requirements: 1.5_
  
  - [ ]* 5.2 Escrever testes de propriedade para tutoriais
    - **Property 14: Visibilidade global de tutoriais**
    - **Property 15: Notificação de novos tutoriais**
    - **Property 16: Badge de tutorial não visualizado**
    - **Property 17: Marcar como visualizado persiste**
    - **Validates: Requirements 1.5**
  
  - [x] 5.3 Atualizar frontend de tutoriais
    - Criada página /dashboard/tutoriais completa
    - Badge "Novo" em tutoriais não visualizados
    - Marcar como visualizado ao abrir tutorial
    - Seção de comentários implementada
    - Modal com vídeo e comentários
    - _Requirements: 1.5_
  
  - [ ]* 5.4 Escrever testes unitários para tutoriais
    - Testar badge "Novo" aparece
    - Testar marcar como visualizado funciona
    - _Requirements: 1.5_

- [ ] 6. Checkpoint - Validar correções críticas
  - Testar todas as 5 correções implementadas
  - Verificar que bugs foram resolvidos
  - Garantir que testes passam
  - Perguntar ao usuário se há dúvidas ou ajustes necessários

### PRIORIDADE 2 - Melhorias de Segurança

- [x] 7. Adicionar validação de senha ao salvar conhecimento
  - [x] 7.1 Modificar endpoint PUT /api/v1/conhecimento
    - Adicionado campo `senha` no request body
    - Validação de senha antes de salvar implementada
    - Retorna erro 401 se senha incorreta
    - _Requirements: 2.1_
  
  - [ ]* 7.2 Escrever testes de propriedade para validação
    - **Property 7: Validação de senha obrigatória**
    - **Validates: Requirements 2.1**
  
  - [x] 7.3 Atualizar frontend /dashboard/conhecimento
    - Modal de confirmação implementado ao clicar "Salvar"
    - Input de senha no modal
    - Mensagem de erro se senha incorreta
    - _Requirements: 2.1_
  
  - [ ]* 7.4 Escrever testes unitários para modal de senha
    - Testar modal abre ao clicar "Salvar"
    - Testar validação de senha
    - _Requirements: 2.1_

- [x] 8. Adicionar feature "IA te ajuda" no conhecimento
  - [x] 8.1 Criar endpoint POST /api/v1/conhecimento/melhorar-ia
    - Implementado `AIService.melhorar_conhecimento()`
    - Usa OpenAI para estruturar e melhorar texto
    - Retorna texto melhorado
    - _Requirements: 2.2_
  
  - [ ]* 8.2 Escrever teste de propriedade para IA melhora texto
    - **Property 8: IA melhora texto**
    - **Validates: Requirements 2.2**
  
  - [x] 8.3 Adicionar botão "Deixa que a IA te ajuda" no frontend
    - Botão posicionado ao lado de "Salvar Conhecimento"
    - Modal com textarea implementado
    - Botão "Melhorar com IA" no modal
    - Preview do texto melhorado
    - Botão "Adicionar texto da IA"
    - Texto adicionado ao conteúdo principal
    - Ao salvar, pede senha novamente (já implementado na Task 7)
    - _Requirements: 2.2_

- [x] 9. Checkpoint - Validar melhorias de segurança
  - ✅ Validação de senha ao salvar conhecimento funciona
  - ✅ Feature "IA te ajuda" funciona e melhora textos
  - ✅ Integração entre as duas funcionalidades perfeita
  - ✅ Todas as tasks da Prioridade 2 completas
  - Pronto para avançar para Prioridade 3

### PRIORIDADE 3 - Novas Funcionalidades

- [ ] 10. Implementar sistema de agendamentos
  - [x] 10.1 Criar migração para tabelas de agendamentos
    - Criada tabela `agendamentos`
    - Criada tabela `configuracoes_horarios`
    - Adicionados índices apropriados
    - _Requirements: 3.1_
  
  - [x] 10.2 Implementar AgendamentoService
    - Implementado `configurar_horarios()`
    - Implementado `criar_agendamento()`
    - Implementado `listar_agendamentos_pendentes()`
    - Implementado `aprovar_agendamento()`
    - Implementado `recusar_agendamento()`
    - Implementado `cancelar_agendamento()`
    - Implementado `agendamentos_do_dia()`
    - _Requirements: 3.1_
  
  - [x] 10.3 Implementar AgendamentoAIParser
    - Usa OpenAI para identificar intenção de agendamento
    - Extrai data/hora, tipo de serviço e observações
    - Gera mensagens de confirmação, aprovação e recusa
    - _Requirements: 3.1_
  
  - [x] 10.4 Criar endpoints de agendamentos
    - POST /api/v1/agendamentos/configurar-horarios
    - GET /api/v1/agendamentos/pendentes
    - GET /api/v1/agendamentos/
    - POST /api/v1/agendamentos/{id}/aprovar
    - POST /api/v1/agendamentos/{id}/recusar
    - POST /api/v1/agendamentos/{id}/cancelar
    - GET /api/v1/agendamentos/dia/{data}
    - _Requirements: 3.1_
  
  - [ ]* 10.5 Escrever testes de propriedade para agendamentos
    - **Property 18: Persistência de configuração de horários**
    - **Property 19: Identificação de pedidos de agendamento**
    - **Property 20: Criação automática de agendamento**
    - **Property 21: Listagem completa de pendentes**
    - **Property 22: Mudança de status de agendamento**
    - **Property 23: Notificação de mudança de status**
    - **Validates: Requirements 3.1**
  
  - [ ] 10.6 Integrar com bot WhatsApp
    - Modificar `BotService` para detectar pedidos de agendamento
    - Criar agendamento automaticamente quando detectado
    - _Requirements: 3.1_
  
  - [ ] 10.7 Implementar notificações WhatsApp
    - Enviar notificação ao aprovar agendamento
    - Enviar notificação ao recusar agendamento
    - _Requirements: 3.1_
  
  - [ ] 10.8 Criar página /dashboard/agendamentos no frontend
    - Criar componente `ConfiguracaoHorarios`
    - Criar componente `ListaAgendamentos`
    - Criar componente `CardAgendamento`
    - Criar componente `RelatorioAgendamentos`
    - _Requirements: 3.1_
  
  - [ ]* 10.9 Escrever testes unitários para agendamentos
    - Testar configuração de horários
    - Testar aprovação/recusa
    - Testar notificações
    - _Requirements: 3.1_


- [ ] 11. Implementar chat suporte melhorado
  - [ ] 11.1 Criar migração para tabela chat_suporte_mensagens
    - Criar tabela com campos: cliente_id, remetente_tipo, mensagem, confianca, created_at
    - Adicionar índices apropriados
    - _Requirements: 3.2_
  
  - [ ] 11.2 Implementar ChatSuporteService
    - Implementar `enviar_mensagem()` com resposta automática da IA
    - Implementar `responder_com_ia()` usando conhecimento do admin
    - Calcular confiança da resposta
    - Oferecer abrir ticket se confiança < 0.7
    - _Requirements: 3.2_
  
  - [ ]* 11.3 Escrever testes de propriedade para chat suporte
    - **Property 24: IA responde primeiro**
    - **Property 25: Escalação baseada em confiança**
    - **Validates: Requirements 3.2**
  
  - [ ] 11.4 Modificar TicketService para suportar anexos
    - Implementar `criar_ticket_com_anexos()` (até 10 arquivos)
    - Implementar `responder_ticket_ia()` para resposta automática
    - Adicionar campos resposta_ia e confianca_ia na tabela tickets
    - _Requirements: 3.2_
  
  - [ ]* 11.5 Escrever teste de propriedade para notificação de ticket
    - **Property 26: Notificação de novo ticket**
    - **Validates: Requirements 3.2**
  
  - [ ] 11.6 Criar endpoints de chat suporte
    - POST /api/v1/chat-suporte/mensagem
    - GET /api/v1/chat-suporte/historico
    - _Requirements: 3.2_
  
  - [ ] 11.7 Criar componente ChatSuporte no frontend
    - Criar widget flutuante de chat
    - Implementar lista de mensagens
    - Adicionar botão "Abrir Ticket" quando IA não sabe
    - Criar modal de criação de ticket com upload de arquivos
    - _Requirements: 3.2_
  
  - [ ]* 11.8 Escrever testes unitários para chat suporte
    - Testar widget abre
    - Testar IA responde
    - Testar modal de ticket
    - Testar upload de arquivos
    - _Requirements: 3.2_

- [x] 12. Implementar "Admin usa própria ferramenta"
  - [x] 12.1 Modificar modelo Cliente
    - Adicionados campos: eh_cliente_admin, admin_vinculado_id
    - Criada migração 020_add_admin_cliente_fields
    - _Requirements: 3.3_
  
  - [x] 12.2 Implementar AdminClienteService
    - Implementado `criar_cliente_admin()` (status sempre ATIVO, sem cobrança)
    - Implementado `obter_token_cliente_admin()` para gerar JWT
    - Cliente admin criado automaticamente com email admin+ferramenta
    - _Requirements: 3.3_
  
  - [ ]* 12.3 Escrever testes de propriedade para admin usa ferramenta
    - **Property 27: Cliente admin sempre ativo**
    - **Property 28: IA responde automaticamente para admin**
    - **Property 29: Fallback para admin**
    - **Validates: Requirements 3.3**
  
  - [x] 12.4 Criar endpoint GET /api/v1/admin/minha-ferramenta/acessar
    - Endpoint criado retornando token de cliente para admin
    - Endpoint GET /status para verificar se cliente admin existe
    - _Requirements: 3.3_
  
  - [x] 12.5 Criar página /admin/minha-ferramenta no frontend
    - Página completa com botão "Acessar Minha Ferramenta"
    - Mostra status do cliente admin
    - Faz login automático como cliente
    - Redireciona para /dashboard
    - Botão "Voltar para Admin" no dashboard do cliente (já existia no layout)
    - Botão "Minha Ferramenta" no menu lateral do admin (já existia no layout)
    - _Requirements: 3.3_
  
  - [ ]* 12.6 Escrever testes unitários para admin usa ferramenta
    - Testar criação de cliente admin
    - Testar acesso à ferramenta
    - _Requirements: 3.3_
    - **Validates: Requirements 3.3**
  
  - [ ] 12.4 Criar endpoint GET /api/v1/admin/minha-ferramenta/acessar
    - Retornar token de cliente para admin
    - _Requirements: 3.3_
  
  - [ ] 12.5 Criar página /admin/minha-ferramenta no frontend
    - Adicionar botão "Acessar Minha Ferramenta"
    - Fazer login automático como cliente
    - Redirecionar para /dashboard
    - Adicionar botão "Voltar para Admin" no dashboard do cliente
    - _Requirements: 3.3_
  
  - [ ]* 12.6 Escrever testes unitários para admin usa ferramenta
    - Testar criação de cliente admin
    - Testar acesso à ferramenta
    - _Requirements: 3.3_

- [x] 13. Implementar dicas da IA no dashboard admin
  - [x] 13.1 Criar migração para tabela dicas_ia
    - Criada tabela com campos: admin_id, conteudo (JSON), objetivo_mensal, created_at
    - _Requirements: 3.4_
  
  - [x] 13.2 Implementar DicasIAService
    - Implementado `gerar_dicas_diarias()` com análise de métricas
    - Implementado `configurar_objetivo_mensal()`
    - Implementado `deve_atualizar_dicas()` (verificar 24h)
    - Usa OpenAI para gerar insights e sugestões
    - _Requirements: 3.4_
  
  - [ ]* 13.3 Escrever testes de propriedade para dicas IA
    - **Property 30: Atualização diária**
    - **Property 31: Dados reais nas dicas**
    - **Property 32: Cálculo de progresso do objetivo**
    - **Validates: Requirements 3.4**
  
  - [x] 13.4 Criar endpoints de dicas IA
    - GET /api/v1/admin/dicas-ia
    - POST /api/v1/admin/dicas-ia/objetivo-mensal
    - _Requirements: 3.4_
  
  - [x] 13.5 Criar componente DicasIA no frontend admin
    - Criado WidgetDicasIA como componente separado
    - Mostra: novos clientes, cancelamentos, clientes ativos
    - Mostra: dicas de conversão, sugestões de ROI, percentual para anúncios
    - Mostra: análise de lucro, progresso do objetivo mensal
    - Formulário para configurar objetivo mensal
    - Design com gradiente roxo/azul
    - Integrado no dashboard admin (/admin/dashboard)
    - _Requirements: 3.4_
  
  - [ ]* 13.6 Escrever testes unitários para dicas IA
    - Testar widget aparece
    - Testar configuração de objetivo
    - Testar cálculo de progresso
    - _Requirements: 3.4_

- [ ] 14. Checkpoint - Validar novas funcionalidades
  - Testar sistema de agendamentos completo
  - Testar chat suporte com IA e tickets
  - Testar admin usando ferramenta
  - Testar dicas da IA
  - Garantir que testes passam
  - Perguntar ao usuário se há ajustes necessários

### PRIORIDADE 4 - Melhorias de UX/UI

- [x] 15. Redesenhar página de login
  - [x] 15.1 Criar novo layout de login
    - Layout: metade foto/ilustração (gradiente roxo/azul), metade inputs
    - Ilustração moderna com ícone de robô e features
    - Inputs com ícones (email e senha)
    - Animações suaves (fade-in, slide-up, shake para erros)
    - Loading state ao fazer login com spinner
    - Mensagens de erro amigáveis com ícone
    - _Requirements: 4.1_
  
  - [ ]* 15.2 Escrever teste de propriedade para mensagens de erro
    - **Property 40: Mensagens de erro amigáveis**
    - **Validates: Requirements 4.1**
  
  - [x] 15.3 Garantir responsividade
    - Desktop: layout split 50/50
    - Tablet/Mobile: apenas formulário, logo no topo
    - Testado em diferentes resoluções
    - _Requirements: 4.1_
    - Implementar animações suaves (CSS transitions)
    - Adicionar loading state ao fazer login
    - Melhorar mensagens de erro (mais amigáveis)
    - _Requirements: 4.1_
  
  - [ ]* 15.2 Escrever teste de propriedade para mensagens de erro
    - **Property 40: Mensagens de erro amigáveis**
    - **Validates: Requirements 4.1**
  
  - [ ] 15.3 Garantir responsividade
    - Testar em desktop (1920x1080)
    - Testar em tablet (768x1024)
    - Testar em mobile (375x667)
    - _Requirements: 4.1_
  
  - [ ]* 15.4 Escrever testes unitários para login
    - Testar renderização
    - Testar loading state
    - _Requirements: 4.1_

- [x] 16. Implementar bot pergunta nome do usuário
  - [x] 16.1 Criar migração para tabela contexto_usuarios_whatsapp
    - Criada tabela com campos: cliente_id, numero_usuario, nome, primeira_interacao, ultima_interacao
    - Índice único para cliente_id + numero_usuario
    - _Requirements: 4.2_
  
  - [x] 16.2 Modificar BotService
    - Implementado `ContextoUsuarioService` completo
    - `eh_primeira_interacao()` verifica se é primeira vez
    - `salvar_nome_usuario()` armazena nome
    - `obter_nome_usuario()` recupera nome
    - `detectar_nome_na_mensagem()` extrai nome da resposta
    - Modificado message_buffer.py para perguntar nome na primeira mensagem
    - Bot usa nome nas respostas seguintes via AIService
    - _Requirements: 4.2_
  
  - [ ]* 16.3 Escrever testes de propriedade para bot pergunta nome
    - **Property 33: Pergunta nome na primeira interação**
    - **Property 34: Persistência do nome**
    - **Property 35: Uso do nome nas respostas**
    - **Property 36: Nome não perguntado novamente**
    - **Validates: Requirements 4.2**
  
  - [ ]* 16.4 Escrever testes unitários para bot pergunta nome
    - Testar primeira mensagem é "Olá! Qual é o seu nome?"
    - Testar nome é salvo
    - Testar nome é usado nas respostas
    - _Requirements: 4.2_

- [ ] 17. Checkpoint - Validar melhorias de UX/UI
  - Testar novo login em diferentes dispositivos
  - Testar bot perguntando nome
  - Garantir que testes passam
  - Perguntar ao usuário se há ajustes necessários

### PRIORIDADE 5 - Melhorias de Pagamento

- [ ] 18. Adicionar suporte a PIX e cartão de débito
  - [ ] 18.1 Implementar checkout PIX no BillingService
    - Implementar `criar_checkout_pix()` usando Stripe
    - Gerar QR Code PIX
    - Retornar QR Code e URL
    - _Requirements: 5.1_
  
  - [ ] 18.2 Implementar webhook para PIX
    - Implementar `processar_webhook_pix()` para confirmação automática
    - Atualizar status da assinatura ao confirmar pagamento
    - _Requirements: 5.1_
  
  - [ ]* 18.3 Escrever teste de propriedade para confirmação PIX
    - **Property 37: Confirmação automática PIX**
    - **Validates: Requirements 5.1**
  
  - [ ] 18.4 Adicionar suporte a cartão de débito
    - Configurar Stripe para aceitar débito
    - Adicionar opção no checkout
    - _Requirements: 5.1_
  
  - [ ] 18.5 Criar endpoint POST /api/v1/billing/checkout-pix
    - Retornar QR Code e informações do pagamento
    - _Requirements: 5.1_
  
  - [ ] 18.6 Atualizar frontend de checkout
    - Adicionar opção "Pagar com PIX"
    - Adicionar opção "Cartão de Débito"
    - Exibir QR Code para PIX
    - Adicionar polling para verificar confirmação
    - _Requirements: 5.1_
  
  - [ ]* 18.7 Escrever testes unitários para PIX
    - Testar geração de QR Code
    - Testar webhook de confirmação
    - _Requirements: 5.1_

- [ ] 19. Implementar múltiplos planos de assinatura
  - [ ] 19.1 Implementar cálculo de valores no BillingService
    - Implementar `calcular_valor_plano()` com descontos
    - 1 mês: valor cheio
    - 3 meses: 10% desconto
    - 12 meses: 20% desconto
    - _Requirements: 5.2_
  
  - [ ] 19.2 Implementar mudança de plano
    - Implementar `mudar_plano()` com cálculo proporcional
    - Calcular crédito/débito baseado em dias restantes
    - _Requirements: 5.2_
  
  - [ ]* 19.3 Escrever testes de propriedade para planos
    - **Property 38: Mudança de plano permitida**
    - **Property 39: Cálculo proporcional correto**
    - **Validates: Requirements 5.2**
  
  - [ ] 19.4 Criar endpoint POST /api/v1/billing/mudar-plano
    - Processar mudança de plano
    - Retornar novo valor e data de cobrança
    - _Requirements: 5.2_
  
  - [ ] 19.5 Atualizar página de checkout
    - Exibir 3 opções de plano (1, 3, 12 meses)
    - Destacar descontos (10% e 20%)
    - Mostrar economia em reais
    - _Requirements: 5.2_
  
  - [ ] 19.6 Adicionar página de mudança de plano
    - Mostrar plano atual
    - Mostrar opções de novos planos
    - Calcular e exibir diferença proporcional
    - Confirmar mudança
    - _Requirements: 5.2_
  
  - [ ]* 19.7 Escrever testes unitários para planos
    - Testar cálculo de descontos
    - Testar cálculo proporcional
    - Testar mudança de plano
    - _Requirements: 5.2_

- [ ] 20. Checkpoint - Validar melhorias de pagamento
  - Testar checkout PIX completo
  - Testar cartão de débito
  - Testar múltiplos planos
  - Testar mudança de plano
  - Garantir que testes passam
  - Perguntar ao usuário se há ajustes necessários

### PRIORIDADE 6 - Preparação para Produção

- [x] 21. Criar checklist de produção
  - [x] 21.1 Criar documento .kiro/contexto/CHECKLIST_PRODUCAO.md
    - Documento criado com todas as mudanças necessárias
    - Incluídas seções: Credenciais, Produtos, Integrações, Infraestrutura, Variáveis, Testes, Documentação
    - _Requirements: 6.1_
  
  - [x] 21.2 Documentar credenciais de produção
    - Admin: email e senha forte
    - Cliente teste: email secundário
    - Remover credenciais de desenvolvimento
    - _Requirements: 6.1_
  
  - [x] 21.3 Documentar configuração de produtos
    - Valores reais dos planos no Stripe
    - Descontos configurados (10% e 20%)
    - _Requirements: 6.1_
  
  - [x] 21.4 Documentar integrações
    - Stripe modo produção
    - SMTP real (SendGrid)
    - Evolution API produção
    - OpenAI API key produção
    - _Requirements: 6.1_
  
  - [x] 21.5 Documentar infraestrutura
    - Domínio e DNS
    - SSL/HTTPS
    - Backups automáticos
    - Monitoramento de uptime
    - _Requirements: 6.1_
  
  - [x] 21.6 Documentar variáveis de ambiente
    - Listadas todas as variáveis necessárias
    - Indicados valores de produção (sem expor secrets)
    - _Requirements: 6.1_

- [ ] 22. Checkpoint final - Validar preparação para produção
  - Revisar checklist completo
  - Garantir que todos os testes passam
  - Validar documentação atualizada
  - Perguntar ao usuário se está pronto para deploy

---

## Notes

### Ordem de Execução

As tarefas estão organizadas por prioridade (1 a 6). Recomenda-se:
1. Executar todas as tarefas de uma prioridade antes de avançar
2. Fazer commit após cada tarefa completa
3. Executar testes após cada checkpoint
4. Validar com usuário nos checkpoints

### Tarefas Opcionais

Tarefas marcadas com `*` são opcionais (testes). Podem ser puladas para MVP mais rápido, mas são recomendadas para garantir qualidade.

### Estimativa de Tempo

- Prioridade 1 (Correções Críticas): 2-3 dias
- Prioridade 2 (Segurança): 1 dia
- Prioridade 3 (Novas Funcionalidades): 5-7 dias
- Prioridade 4 (UX/UI): 1-2 dias
- Prioridade 5 (Pagamento): 2-3 dias
- Prioridade 6 (Produção): 1 dia

**Total estimado: 12-17 dias**

### Dependências Externas

- Stripe (modo teste e produção)
- OpenAI API
- Evolution API
- SendGrid (email)

### Ambiente de Desenvolvimento

- Docker Compose para serviços locais
- PostgreSQL, Redis, ChromaDB em containers
- Hot reload no backend e frontend

---

**Status:** Pronto para execução  
**Próximo Passo:** Iniciar Prioridade 1 - Correções Críticas

