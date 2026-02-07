# Implementation Plan: FASE 16 - Painel Admin Completo

## Overview

Este plano implementa o painel administrativo completo do SaaS de WhatsApp AI Bot em 16 mini-fases incrementais. Cada mini-fase entrega funcionalidade completa e testável, construindo sobre as anteriores até completar todo o sistema administrativo.

A implementação seguirá a ordem: Backend → Frontend → Testes, garantindo que cada componente seja validado antes de prosseguir.

## Tasks

### Mini-Fase 16.1 - Estrutura Base + Login Admin

- [x] 1. Criar estrutura de banco de dados para administradores
  - [x] 1.1 Criar migration 016_add_admin_tables.py
    - Adicionar tabelas: admins, login_attempts, ips_bloqueados, audit_log
    - Criar índices para performance
    - _Requirements: 1.1, 9.1, 9.2, 9.4_
  
  - [x] 1.2 Criar modelo Admin em app/db/models/admin.py
    - Definir campos: id, nome, email, senha_hash, role, tema, cliente_especial_id
    - Adicionar relacionamentos
    - _Requirements: 1.1_
  
  - [x] 1.3 Criar seed script para primeiro admin
    - Script apps/backend/criar_admin_inicial.py
    - Email: admin@sistema.com, Senha: Admin@123
    - _Requirements: 1.5_

- [x] 2. Implementar serviço de autenticação admin
  - [x] 2.1 Criar AdminAuthService em app/services/admin/auth_service.py
    - Métodos: authenticate, generate_token, verify_token, check_ip_blocked
    - Usar bcrypt para hashing, JWT com role=admin
    - _Requirements: 1.1, 1.2, 1.3, 1.4_
  
  - [ ]* 2.2 Escrever testes de propriedade para autenticação
    - **Property 1: Password Hashing**
    - **Property 2: JWT Contains Admin Role**
    - **Property 3: IP Blocking After Failed Attempts**
    - **Property 4: Admin Role Required for Admin Endpoints**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4**

- [x] 3. Criar endpoints de autenticação admin
  - [x] 3.1 Criar router em app/api/v1/admin/auth.py
    - POST /api/v1/admin/auth/login
    - GET /api/v1/admin/auth/me
    - _Requirements: 1.2, 1.6_
  
  - [x] 3.2 Criar middleware AdminAuthMiddleware
    - Validar JWT e role=admin em todas as rotas /api/v1/admin/*
    - _Requirements: 1.4_
  
  - [ ]* 3.3 Escrever testes de integração para endpoints
    - Testar login com credenciais válidas/inválidas
    - Testar bloqueio de IP
    - Testar acesso com/sem token válido
    - _Requirements: 1.2, 1.3, 1.4, 1.6_

- [x] 4. Criar interface frontend de login admin
  - [x] 4.1 Criar página app/admin/login/page.tsx
    - Formulário de login (email, senha)
    - Tratamento de erros
    - Redirecionamento após login
    - _Requirements: 1.2_
  
  - [x] 4.2 Criar layout base app/admin/layout.tsx
    - Sidebar com navegação
    - Header com perfil e notificações
    - Proteção de rotas (verificar JWT)
    - _Requirements: 1.4_
  
  - [x] 4.3 Criar página dashboard app/admin/dashboard/page.tsx
    - Estrutura básica (será preenchida na Mini-Fase 16.2)
    - _Requirements: 1.6_

- [x] 5. Checkpoint - Testar autenticação admin completa
  - Verificar login, bloqueio de IP, acesso a rotas protegidas
  - Garantir que todos os testes passam

### Mini-Fase 16.2 - Dashboard Overview (Métricas)

- [ ] 6. Implementar serviço de dashboard
  - [ ] 6.1 Criar DashboardService em app/services/admin/dashboard_service.py
    - Métodos: get_metrics, get_sales_chart, get_revenue_chart, get_recent_clients
    - Implementar cache Redis (TTL 5 minutos)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_
  
  - [ ]* 6.2 Escrever testes de propriedade para dashboard
    - **Property 6: Dashboard Metrics Completeness**
    - **Property 7: Sales Chart Data Points**
    - **Property 8: Revenue Chart Data Points**
    - **Property 9: Recent Clients Limit**
    - **Property 10: Dashboard Metrics Caching**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6**

- [ ] 7. Criar endpoint de dashboard
  - [ ] 7.1 Criar router em app/api/v1/admin/dashboard.py
    - GET /api/v1/admin/dashboard/metrics
    - _Requirements: 2.1, 2.2_
  
  - [ ]* 7.2 Escrever testes de integração para endpoint
    - Testar retorno de métricas completas
    - Testar cache
    - _Requirements: 2.1, 2.2, 2.6_

- [ ] 8. Criar componentes frontend de dashboard
  - [ ] 8.1 Criar componentes de métricas
    - MetricsCards.tsx (cards com KPIs)
    - SalesChart.tsx (gráfico Recharts)
    - RevenueChart.tsx (gráfico Recharts)
    - RecentClients.tsx (lista)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [ ] 8.2 Integrar componentes na página dashboard
    - Consumir API /api/v1/admin/dashboard/metrics
    - Exibir loading e tratamento de erros
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ] 9. Checkpoint - Testar dashboard completo
  - Verificar exibição de métricas, gráficos e lista de clientes
  - Garantir que cache funciona corretamente

### Mini-Fase 16.3 - Gestão de Clientes (CRUD)

- [ ] 10. Implementar serviço de gestão de clientes
  - [ ] 10.1 Criar ClienteAdminService em app/services/admin/cliente_admin_service.py
    - Métodos: list_clientes, get_cliente_details, update_cliente, suspend_cliente, activate_cliente, reset_password
    - Integrar com AuditService
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_
  
  - [ ]* 10.2 Escrever testes de propriedade para gestão de clientes
    - **Property 11: Pagination and Filtering**
    - **Property 12: Client Details Completeness**
    - **Property 13: Client Data Update Round-Trip**
    - **Property 14: Client Suspension State Change**
    - **Property 15: Client Activation State Change**
    - **Property 16: Password Reset Invalidates Old Password**
    - **Property 17: Admin Actions Audit Logging**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7**

- [ ] 11. Adicionar campos em tabela clientes
  - [ ] 11.1 Criar migration 017_add_cliente_admin_fields.py
    - Adicionar: ultimo_login, ip_ultimo_login, total_mensagens_enviadas
    - Criar índices
    - _Requirements: 3.2_

- [ ] 12. Criar endpoints de gestão de clientes
  - [ ] 12.1 Criar router em app/api/v1/admin/clientes.py
    - GET /api/v1/admin/clientes (lista com filtros e paginação)
    - GET /api/v1/admin/clientes/:id (detalhes)
    - PUT /api/v1/admin/clientes/:id (editar)
    - POST /api/v1/admin/clientes/:id/suspender
    - POST /api/v1/admin/clientes/:id/ativar
    - POST /api/v1/admin/clientes/:id/resetar-senha
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_
  
  - [ ]* 12.2 Escrever testes de integração para endpoints
    - Testar listagem, filtros, paginação
    - Testar ações (suspender, ativar, resetar senha)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

- [ ] 13. Criar interface frontend de gestão de clientes
  - [ ] 13.1 Criar componentes de clientes
    - ClientesTable.tsx (tabela com filtros)
    - ClienteFilters.tsx (formulário de filtros)
    - ClienteActions.tsx (botões de ação)
    - _Requirements: 3.1, 3.4, 3.5, 3.6_
  
  - [ ] 13.2 Criar página de listagem app/admin/clientes/page.tsx
    - Integrar componentes
    - Consumir API
    - _Requirements: 3.1_
  
  - [ ] 13.3 Criar página de detalhes app/admin/clientes/[id]/page.tsx
    - Exibir dados completos
    - Formulário de edição
    - Ações (suspender, ativar, resetar senha)
    - _Requirements: 3.2, 3.3, 3.4, 3.5, 3.6_

- [ ] 14. Checkpoint - Testar gestão de clientes completa
  - Verificar listagem, filtros, edição e ações
  - Garantir que audit log registra todas as ações

### Mini-Fase 16.4 - Monitoramento de Uso (OpenAI)

- [ ] 15. Criar estrutura de banco de dados para uso OpenAI
  - [ ] 15.1 Criar migration 018_add_uso_openai.py
    - Adicionar tabela uso_openai
    - Criar índices
    - _Requirements: 4.1_

- [ ] 16. Implementar serviço de monitoramento de uso
  - [ ] 16.1 Criar UsageMonitorService em app/services/admin/usage_monitor_service.py
    - Métodos: record_usage, get_top_spenders, get_cliente_usage, get_alerts, calculate_cost
    - Tabela de preços OpenAI
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_
  
  - [ ]* 16.2 Escrever testes de propriedade para monitoramento de uso
    - **Property 18: Usage Recording**
    - **Property 19: Top Spenders Ordering**
    - **Property 20: Usage Alert Generation**
    - **Property 21: Cost Calculation Accuracy**
    - **Validates: Requirements 4.1, 4.2, 4.4, 4.5**

- [ ] 17. Modificar AIService para logar uso
  - [ ] 17.1 Atualizar app/services/ai/ai_service.py
    - Adicionar chamada para UsageMonitorService.record_usage após cada processamento
    - Capturar tokens de input/output
    - _Requirements: 4.1_

- [ ] 18. Criar endpoints de monitoramento de uso
  - [ ] 18.1 Criar router em app/api/v1/admin/uso.py
    - GET /api/v1/admin/uso/resumo (top 10 gastadores)
    - GET /api/v1/admin/uso/cliente/:id (histórico)
    - GET /api/v1/admin/uso/alertas (threshold)
    - _Requirements: 4.2, 4.3, 4.4_
  
  - [ ]* 18.2 Escrever testes de integração para endpoints
    - Testar resumo, histórico e alertas
    - _Requirements: 4.2, 4.3, 4.4_

- [ ] 19. Criar interface frontend de monitoramento de uso
  - [ ] 19.1 Criar componentes de uso
    - TopSpendersTable.tsx (ranking)
    - UsageChart.tsx (gráfico histórico)
    - UsageAlerts.tsx (lista de alertas)
    - _Requirements: 4.2, 4.3, 4.4_
  
  - [ ] 19.2 Criar página app/admin/uso/page.tsx
    - Integrar componentes
    - Consumir API
    - _Requirements: 4.2, 4.3, 4.4_

- [ ] 20. Checkpoint - Testar monitoramento de uso completo
  - Verificar registro de uso, ranking e alertas
  - Garantir que cálculo de custo está correto

### Mini-Fase 16.5 - Sistema de Tickets/Suporte

- [ ] 21. Criar estrutura de banco de dados para tickets
  - [ ] 21.1 Criar migration 019_add_tickets.py
    - Adicionar tabelas: tickets, ticket_mensagens, ticket_categorias
    - Criar índices
    - _Requirements: 5.1_

- [ ] 22. Implementar serviço de tickets
  - [ ] 22.1 Criar TicketService em app/services/admin/ticket_service.py
    - Métodos: create_ticket, try_auto_response, list_tickets, add_response, update_status, categorize_ticket
    - Integrar com RAGService (threshold 0.7)
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_
  
  - [ ]* 22.2 Escrever testes de propriedade para tickets
    - **Property 22: Ticket Creation with Auto-Response**
    - **Property 23: Low Confidence Tickets Marked for Human**
    - **Property 24: Admin Response Creates Message and Notification**
    - **Property 25: Ticket Status Change Recording**
    - **Property 26: Auto-Categorization**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.5, 5.6, 5.7**

- [ ] 23. Criar endpoints de tickets (Cliente)
  - [ ] 23.1 Criar router em app/api/v1/tickets.py
    - POST /api/v1/tickets (criar)
    - GET /api/v1/tickets (listar do cliente)
    - POST /api/v1/tickets/:id/mensagens (adicionar mensagem)
    - _Requirements: 5.1_
  
  - [ ]* 23.2 Escrever testes de integração para endpoints cliente
    - Testar criação, listagem e mensagens
    - _Requirements: 5.1_

- [ ] 24. Criar endpoints de tickets (Admin)
  - [ ] 24.1 Criar router em app/api/v1/admin/tickets.py
    - GET /api/v1/admin/tickets (lista com filtros)
    - POST /api/v1/admin/tickets/:id/responder
    - PUT /api/v1/admin/tickets/:id/status
    - _Requirements: 5.4, 5.5, 5.6_
  
  - [ ]* 24.2 Escrever testes de integração para endpoints admin
    - Testar listagem, resposta e mudança de status
    - _Requirements: 5.4, 5.5, 5.6_

- [ ] 25. Criar interface frontend de tickets (Cliente)
  - [ ] 25.1 Criar componentes de tickets cliente
    - TicketWidget.tsx (widget chat)
    - CreateTicketModal.tsx (modal criar)
    - TicketList.tsx (lista de tickets)
    - _Requirements: 5.1_
  
  - [ ] 25.2 Integrar widget no layout do cliente
    - Botão flutuante para abrir widget
    - _Requirements: 5.1_

- [ ] 26. Criar interface frontend de tickets (Admin)
  - [ ] 26.1 Criar componentes de tickets admin
    - TicketsTable.tsx (lista com filtros)
    - TicketChat.tsx (interface chat)
    - TicketFilters.tsx (filtros)
    - _Requirements: 5.4, 5.5, 5.6_
  
  - [ ] 26.2 Criar página app/admin/tickets/page.tsx
    - Integrar componentes
    - Consumir API
    - _Requirements: 5.4, 5.5, 5.6_

- [ ] 27. Checkpoint - Testar sistema de tickets completo
  - Verificar criação, resposta automática, resposta manual
  - Garantir que notificações funcionam

### Mini-Fase 16.6 - Gestão de Tutoriais

- [ ] 28. Criar estrutura de banco de dados para tutoriais
  - [ ] 28.1 Criar migration 020_add_tutoriais.py
    - Adicionar tabelas: tutoriais, tutorial_visualizacoes, tutorial_comentarios
    - Criar índices
    - _Requirements: 6.1_

- [ ] 29. Implementar serviço de tutoriais
  - [ ] 29.1 Criar TutorialService em app/services/admin/tutorial_service.py
    - Métodos: create_tutorial, update_tutorial, reorder_tutorials, record_view, add_comment, get_statistics
    - Integrar com NotificationService
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_
  
  - [ ]* 29.2 Escrever testes de propriedade para tutoriais
    - **Property 27: Tutorial Reordering**
    - **Property 28: View Recording**
    - **Property 29: Comment Persistence**
    - **Property 30: New Tutorial Notifications**
    - **Validates: Requirements 6.2, 6.3, 6.4, 6.5**

- [ ] 30. Criar endpoints de tutoriais (Admin)
  - [ ] 30.1 Criar router em app/api/v1/admin/tutoriais.py
    - POST /api/v1/admin/tutoriais (criar)
    - PUT /api/v1/admin/tutoriais/:id (editar)
    - DELETE /api/v1/admin/tutoriais/:id (deletar)
    - POST /api/v1/admin/tutoriais/reordenar (reordenar)
    - GET /api/v1/admin/tutoriais/:id/estatisticas
    - _Requirements: 6.1, 6.2, 6.6_
  
  - [ ]* 30.2 Escrever testes de integração para endpoints admin
    - Testar CRUD e reordenação
    - _Requirements: 6.1, 6.2_

- [ ] 31. Criar endpoints de tutoriais (Cliente)
  - [ ] 31.1 Criar router em app/api/v1/tutoriais.py
    - GET /api/v1/tutoriais (listar)
    - POST /api/v1/tutoriais/:id/visualizar (registrar visualização)
    - POST /api/v1/tutoriais/:id/comentar (adicionar comentário)
    - _Requirements: 6.3, 6.4_
  
  - [ ]* 31.2 Escrever testes de integração para endpoints cliente
    - Testar listagem, visualização e comentários
    - _Requirements: 6.3, 6.4_

- [ ] 32. Criar interface frontend de tutoriais (Admin)
  - [ ] 32.1 Criar componentes de tutoriais admin
    - TutorialsTable.tsx (lista com drag-drop)
    - TutorialForm.tsx (formulário criar/editar)
    - TutorialStats.tsx (estatísticas)
    - _Requirements: 6.1, 6.2, 6.6_
  
  - [ ] 32.2 Criar página app/admin/tutoriais/page.tsx
    - Integrar componentes
    - Consumir API
    - _Requirements: 6.1, 6.2, 6.6_

- [ ] 33. Criar interface frontend de tutoriais (Cliente)
  - [ ] 33.1 Criar componentes de tutoriais cliente
    - TutorialsGrid.tsx (grid de vídeos)
    - TutorialPlayer.tsx (player)
    - TutorialComments.tsx (comentários)
    - _Requirements: 6.3, 6.4_
  
  - [ ] 33.2 Criar página app/tutoriais/page.tsx
    - Integrar componentes
    - Badge "Novo" para tutoriais recentes
    - _Requirements: 6.3, 6.4, 6.5_

- [ ] 34. Checkpoint - Testar sistema de tutoriais completo
  - Verificar CRUD, reordenação, visualizações e comentários
  - Garantir que notificações são enviadas

### Mini-Fase 16.7 - Avisos e Anúncios

- [ ] 35. Criar estrutura de banco de dados para avisos
  - [ ] 35.1 Criar migration 021_add_avisos.py
    - Adicionar tabela avisos
    - Criar índices
    - _Requirements: 7.1_

- [ ] 36. Implementar serviço de avisos
  - [ ] 36.1 Criar AvisoService em app/services/admin/aviso_service.py
    - Métodos: create_aviso, update_aviso, deactivate_aviso, get_active_avisos, preview_aviso
    - _Requirements: 7.1, 7.2, 7.3, 7.5, 7.6_
  
  - [ ]* 36.2 Escrever testes de propriedade para avisos
    - **Property 31: Active Avisos Date Filtering**
    - **Property 32: Aviso Deactivation**
    - **Property 33: Aviso Color Mapping**
    - **Validates: Requirements 7.2, 7.3, 7.4, 7.5**

- [ ] 37. Criar endpoints de avisos
  - [ ] 37.1 Criar router em app/api/v1/admin/avisos.py
    - POST /api/v1/admin/avisos (criar)
    - PUT /api/v1/admin/avisos/:id (editar)
    - DELETE /api/v1/admin/avisos/:id (desativar)
    - POST /api/v1/admin/avisos/preview (preview)
    - _Requirements: 7.1, 7.5, 7.6_
  
  - [ ] 37.2 Criar router em app/api/v1/avisos.py
    - GET /api/v1/avisos/ativos (listar ativos)
    - _Requirements: 7.2_
  
  - [ ]* 37.3 Escrever testes de integração para endpoints
    - Testar CRUD e filtro de ativos
    - _Requirements: 7.1, 7.2, 7.5_

- [ ] 38. Criar interface frontend de avisos (Admin)
  - [ ] 38.1 Criar componentes de avisos admin
    - AvisosTable.tsx (lista)
    - AvisoForm.tsx (formulário)
    - AvisoPreview.tsx (preview)
    - _Requirements: 7.1, 7.6_
  
  - [ ] 38.2 Criar página app/admin/avisos/page.tsx
    - Integrar componentes
    - Consumir API
    - _Requirements: 7.1, 7.6_

- [ ] 39. Criar componente de avisos (Cliente)
  - [ ] 39.1 Criar AvisoBanner.tsx
    - Exibir no topo do layout
    - Cores por tipo (info=azul, warning=amarelo, error=vermelho, success=verde)
    - _Requirements: 7.2, 7.4_
  
  - [ ] 39.2 Integrar no layout do cliente
    - Consumir API /api/v1/avisos/ativos
    - _Requirements: 7.2_

- [ ] 40. Checkpoint - Testar sistema de avisos completo
  - Verificar criação, preview e exibição para clientes
  - Garantir que filtro de datas funciona

### Mini-Fase 16.8 - Relatórios (PDF/Excel)

- [ ] 41. Criar estrutura de banco de dados para relatórios
  - [ ] 41.1 Criar migration 022_add_relatorios_historico.py
    - Adicionar tabela relatorios_historico
    - Criar índices
    - _Requirements: 8.7_

- [ ] 42. Implementar serviço de relatórios
  - [ ] 42.1 Criar ReportService em app/services/admin/report_service.py
    - Métodos: generate_sales_report, generate_clients_report, generate_usage_report, generate_tickets_report
    - Usar ReportLab para PDF e openpyxl para Excel
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_
  
  - [ ] 42.2 Implementar cleanup de relatórios antigos
    - Método: cleanup_old_reports (90 dias)
    - Agendar com Celery
    - _Requirements: 8.7_
  
  - [ ]* 42.3 Escrever testes de propriedade para relatórios
    - **Property 34: Report Date Filtering**
    - **Property 35: Report Format Validity**
    - **Property 36: Report Retention**
    - **Property 57: Report Serialization Round-Trip**
    - **Validates: Requirements 8.1, 8.5, 8.6, 8.7, 17.4**

- [ ] 43. Criar endpoints de relatórios
  - [ ] 43.1 Criar router em app/api/v1/admin/relatorios.py
    - GET /api/v1/admin/relatorios/vendas (gerar vendas)
    - GET /api/v1/admin/relatorios/clientes (gerar clientes)
    - GET /api/v1/admin/relatorios/uso-openai (gerar uso)
    - GET /api/v1/admin/relatorios/tickets (gerar tickets)
    - GET /api/v1/admin/relatorios/historico (listar histórico)
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.7_
  
  - [ ]* 43.2 Escrever testes de integração para endpoints
    - Testar geração de relatórios em PDF e Excel
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [ ] 44. Criar interface frontend de relatórios
  - [ ] 44.1 Criar componentes de relatórios
    - ReportFilters.tsx (formulário de filtros)
    - ReportPreview.tsx (preview)
    - ReportHistory.tsx (histórico)
    - _Requirements: 8.1, 8.7_
  
  - [ ] 44.2 Criar página app/admin/relatorios/page.tsx
    - Integrar componentes
    - Botões exportar PDF/Excel
    - _Requirements: 8.1, 8.5, 8.6, 8.7_

- [ ] 45. Checkpoint - Testar sistema de relatórios completo
  - Verificar geração de PDF e Excel
  - Garantir que filtros funcionam e histórico é mantido

### Mini-Fase 16.9 - Segurança e Auditoria

- [ ] 46. Implementar serviço de auditoria
  - [ ] 46.1 Criar AuditService em app/services/admin/audit_service.py
    - Métodos: log_action, get_audit_log, get_entity_history
    - _Requirements: 9.3, 9.4, 9.5_
  
  - [ ]* 46.2 Escrever testes de propriedade para auditoria
    - **Property 37: Failed Login Recording**
    - **Property 38: Audit Log Completeness**
    - **Property 39: IP Unblocking with Audit**
    - **Validates: Requirements 9.1, 9.4, 9.6**

- [ ] 47. Criar endpoints de segurança
  - [ ] 47.1 Criar router em app/api/v1/admin/seguranca.py
    - GET /api/v1/admin/seguranca/tentativas-login (listar tentativas)
    - GET /api/v1/admin/seguranca/ips-bloqueados (listar IPs bloqueados)
    - POST /api/v1/admin/seguranca/ips-bloqueados/:id/desbloquear (desbloquear)
    - GET /api/v1/admin/seguranca/audit-log (listar audit log)
    - _Requirements: 9.1, 9.2, 9.5, 9.6_
  
  - [ ]* 47.2 Escrever testes de integração para endpoints
    - Testar listagem e desbloquear IP
    - _Requirements: 9.1, 9.2, 9.5, 9.6_

- [ ] 48. Criar interface frontend de segurança
  - [ ] 48.1 Criar componentes de segurança
    - LoginAttempts.tsx (tabela tentativas)
    - BlockedIPs.tsx (lista IPs bloqueados)
    - AuditLog.tsx (tabela audit log)
    - _Requirements: 9.1, 9.2, 9.5_
  
  - [ ] 48.2 Criar página app/admin/seguranca/page.tsx
    - Abas: Tentativas, IPs Bloqueados, Audit Log
    - Filtros e ação desbloquear
    - _Requirements: 9.1, 9.2, 9.5, 9.6_

- [ ] 49. Checkpoint - Testar sistema de segurança completo
  - Verificar registro de tentativas, bloqueio de IP e audit log
  - Garantir que todas as ações críticas são logadas

### Mini-Fase 16.10 - Notificações para Admin

- [ ] 50. Criar estrutura de banco de dados para notificações
  - [ ] 50.1 Criar migration 023_add_notificacoes_admin.py
    - Adicionar tabela notificacoes_admin
    - Criar índices
    - _Requirements: 10.1_

- [ ] 51. Implementar serviço de notificações
  - [ ] 51.1 Criar NotificationService em app/services/admin/notification_service.py
    - Métodos: create_notification, get_notifications, mark_as_read, get_unread_count
    - _Requirements: 10.1, 10.7, 10.8_
  
  - [ ]* 51.2 Escrever testes de propriedade para notificações
    - **Property 40: Event-Triggered Notifications**
    - **Property 41: Unread Count Accuracy**
    - **Property 42: Mark as Read State Change**
    - **Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8**

- [ ] 52. Integrar notificações em eventos do sistema
  - [ ] 52.1 Adicionar chamadas para NotificationService em:
    - ClienteService (novo cliente)
    - PaymentService (pagamento recusado, plano expirado)
    - TicketService (novo ticket não resolvido)
    - UsageMonitorService (alto uso OpenAI)
    - AdminAuthService (tentativa de invasão)
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6_

- [ ] 53. Criar endpoints de notificações
  - [ ] 53.1 Criar router em app/api/v1/admin/notificacoes.py
    - GET /api/v1/admin/notificacoes (listar)
    - PUT /api/v1/admin/notificacoes/:id/ler (marcar como lida)
    - GET /api/v1/admin/notificacoes/nao-lidas/count (contador)
    - _Requirements: 10.7, 10.8_
  
  - [ ]* 53.2 Escrever testes de integração para endpoints
    - Testar listagem, marcar como lida e contador
    - _Requirements: 10.7, 10.8_

- [ ] 54. Criar interface frontend de notificações
  - [ ] 54.1 Criar componentes de notificações
    - NotificationBell.tsx (ícone sino com badge)
    - NotificationDropdown.tsx (dropdown)
    - NotificationList.tsx (página histórico)
    - _Requirements: 10.7, 10.8_
  
  - [ ] 54.2 Integrar no header do admin
    - Polling a cada 30 segundos
    - _Requirements: 10.7_
  
  - [ ] 54.3 Criar página app/admin/notificacoes/page.tsx
    - Lista completa de notificações
    - _Requirements: 10.7, 10.8_

- [ ] 55. Checkpoint - Testar sistema de notificações completo
  - Verificar criação automática de notificações
  - Garantir que contador e badge funcionam

### Mini-Fase 16.11 - Admin usa ferramenta grátis

- [ ] 56. Criar cliente especial para admin
  - [ ] 56.1 Modificar seed script criar_admin_inicial.py
    - Criar cliente especial vinculado ao admin
    - Status ATIVO, sem cobrança
    - _Requirements: 11.1, 11.4_

- [ ] 57. Implementar acesso do admin à ferramenta
  - [ ] 57.1 Criar endpoint GET /api/v1/admin/minha-ferramenta/acessar
    - Retornar token JWT do cliente especial
    - _Requirements: 11.2_
  
  - [ ]* 57.2 Escrever testes de propriedade para acesso
    - **Property 43: Special Client No Billing**
    - **Property 44: Admin Session Restoration**
    - **Validates: Requirements 11.4, 11.5**

- [ ] 58. Criar interface frontend de acesso à ferramenta
  - [ ] 58.1 Adicionar menu "Minha Ferramenta" no sidebar admin
    - Fazer login automático no cliente especial
    - _Requirements: 11.2_
  
  - [ ] 58.2 Adicionar botão "Voltar para Admin" no layout do cliente
    - Exibir apenas quando admin está usando ferramenta
    - Restaurar sessão administrativa
    - _Requirements: 11.3, 11.5_

- [ ] 59. Checkpoint - Testar acesso do admin à ferramenta
  - Verificar login automático e volta para admin
  - Garantir que cliente especial não é cobrado

### Mini-Fase 16.12 - Tema Dark/Light

- [ ] 60. Adicionar campo tema na tabela admins
  - [ ] 60.1 Criar migration 024_add_tema_admin.py
    - Adicionar campo tema (default 'light')
    - _Requirements: 12.1_

- [ ] 61. Implementar serviço de preferências
  - [ ] 61.1 Criar endpoint PUT /api/v1/admin/preferencias
    - Atualizar tema do admin
    - _Requirements: 12.1_
  
  - [ ]* 61.2 Escrever testes de propriedade para tema
    - **Property 45: Theme Persistence Round-Trip**
    - **Property 46: Theme Synchronization**
    - **Validates: Requirements 12.1, 12.2, 12.4**

- [ ] 62. Criar interface frontend de tema
  - [ ] 62.1 Criar ThemeToggle.tsx
    - Toggle sol/lua
    - Aplicar tema usando CSS variables
    - _Requirements: 12.3_
  
  - [ ] 62.2 Integrar no header do admin
    - Sincronizar com localStorage e backend
    - Carregar tema ao fazer login
    - _Requirements: 12.2, 12.4_
  
  - [ ] 62.3 Criar CSS variables para cores
    - Definir cores para light e dark
    - _Requirements: 12.3_

- [ ] 63. Checkpoint - Testar sistema de tema completo
  - Verificar alternância, persistência e sincronização
  - Garantir que tema é carregado ao fazer login

### Mini-Fase 16.13 - Monitoramento de Sistema

- [ ] 64. Implementar serviço de monitoramento de sistema
  - [ ] 64.1 Criar SystemMonitorService em app/services/admin/system_monitor_service.py
    - Métodos: check_health, get_metrics, check_postgresql, check_redis, check_chromadb, check_evolution_api, check_openai, collect_system_metrics
    - Usar psutil para métricas de sistema
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_
  
  - [ ]* 64.2 Escrever testes de propriedade para monitoramento
    - **Property 47: Health Check Completeness**
    - **Property 48: Unhealthy Service Indication**
    - **Property 49: Metrics Completeness**
    - **Property 50: Metrics Alert Generation**
    - **Property 51: Metrics Retention**
    - **Validates: Requirements 13.1, 13.2, 13.3, 13.5, 13.6**

- [ ] 65. Criar endpoints de monitoramento
  - [ ] 65.1 Criar router em app/api/v1/admin/sistema.py
    - GET /api/v1/admin/sistema/saude (health check)
    - GET /api/v1/admin/sistema/metricas (métricas)
    - _Requirements: 13.1, 13.3_
  
  - [ ]* 65.2 Escrever testes de integração para endpoints
    - Testar health check e métricas
    - _Requirements: 13.1, 13.3_

- [ ] 66. Criar interface frontend de monitoramento
  - [ ] 66.1 Criar componentes de monitoramento
    - HealthCards.tsx (cards de status dos serviços)
    - MetricsCharts.tsx (gráficos de métricas)
    - AlertsList.tsx (lista de alertas)
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_
  
  - [ ] 66.2 Criar página app/admin/sistema/page.tsx
    - Integrar componentes
    - Atualização a cada 30 segundos
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

- [ ] 67. Checkpoint - Testar sistema de monitoramento completo
  - Verificar health check de todos os serviços
  - Garantir que métricas são coletadas e alertas gerados

### Mini-Fase 16.14 - Gestão de Vendas

- [ ] 68. Implementar serviço de gestão de vendas
  - [ ] 68.1 Criar SalesAdminService em app/services/admin/sales_admin_service.py
    - Métodos: list_vendas, list_assinaturas, cancel_subscription, reactivate_subscription, process_refund
    - Integrar com AuditService
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_
  
  - [ ]* 68.2 Escrever testes de propriedade para vendas
    - **Property 52: Subscription Cancellation**
    - **Property 53: Subscription Reactivation**
    - **Property 54: Refund Recording and Notification**
    - **Validates: Requirements 14.3, 14.4, 14.5**

- [ ] 69. Criar endpoints de gestão de vendas
  - [ ] 69.1 Criar router em app/api/v1/admin/vendas.py
    - GET /api/v1/admin/vendas (listar vendas)
    - GET /api/v1/admin/assinaturas (listar assinaturas)
    - POST /api/v1/admin/assinaturas/:id/cancelar (cancelar)
    - POST /api/v1/admin/assinaturas/:id/reativar (reativar)
    - POST /api/v1/admin/vendas/:id/reembolsar (reembolsar)
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_
  
  - [ ]* 69.2 Escrever testes de integração para endpoints
    - Testar listagem e ações (cancelar, reativar, reembolsar)
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_

- [ ] 70. Criar interface frontend de gestão de vendas
  - [ ] 70.1 Criar componentes de vendas
    - VendasTable.tsx (tabela de vendas)
    - AssinaturasTable.tsx (tabela de assinaturas)
    - ConfirmationModal.tsx (modal de confirmação)
    - _Requirements: 14.1, 14.2, 14.6_
  
  - [ ] 70.2 Criar página app/admin/vendas/page.tsx
    - Abas: Vendas, Assinaturas
    - Filtros e ações
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6_

- [ ] 71. Checkpoint - Testar gestão de vendas completa
  - Verificar listagem, cancelamento, reativação e reembolso
  - Garantir que confirmações funcionam

### Mini-Fase 16.15 - Histórico Completo do Cliente

- [ ] 72. Implementar serviço de histórico do cliente
  - [ ] 72.1 Criar ClienteHistoryService em app/services/admin/cliente_history_service.py
    - Métodos: get_complete_history, get_timeline, get_usage_chart, get_login_history, get_admin_actions
    - Agregar dados de múltiplas tabelas
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_
  
  - [ ]* 72.2 Escrever testes de propriedade para histórico
    - **Property 55: Client History Completeness**
    - **Property 56: Admin Actions on Client**
    - **Validates: Requirements 15.1, 15.2, 15.5**

- [ ] 73. Criar endpoint de histórico do cliente
  - [ ] 73.1 Criar router em app/api/v1/admin/clientes/:id/historico.py
    - GET /api/v1/admin/clientes/:id/historico-completo
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_
  
  - [ ]* 73.2 Escrever testes de integração para endpoint
    - Testar retorno de histórico completo
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_

- [ ] 74. Criar interface frontend de histórico do cliente
  - [ ] 74.1 Criar componentes de histórico
    - ClienteOverview.tsx (visão geral)
    - ClienteTimeline.tsx (timeline de eventos)
    - ClienteUsageChart.tsx (gráfico de uso)
    - ClienteLoginHistory.tsx (histórico de logins)
    - ClienteAdminActions.tsx (ações administrativas)
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_
  
  - [ ] 74.2 Criar página app/admin/clientes/[id]/historico/page.tsx
    - Abas: Visão Geral, Pagamentos, Conversas, Tickets, Créditos, Atividade
    - Integrar componentes
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6_

- [ ] 75. Checkpoint - Testar histórico completo do cliente
  - Verificar todas as abas e dados
  - Garantir que timeline está completa

### Mini-Fase 16.16 - Responsividade Mobile

- [ ] 76. Implementar responsividade no painel admin
  - [ ] 76.1 Adaptar AdminLayout para mobile
    - Sidebar → menu hambúrguer (< 768px)
    - _Requirements: 16.1_
  
  - [ ] 76.2 Adaptar tabelas para mobile
    - Transformar em cards verticais (< 768px)
    - _Requirements: 16.2_
  
  - [ ] 76.3 Adaptar gráficos para mobile
    - Ajustar dimensões mantendo legibilidade
    - _Requirements: 16.3_
  
  - [ ] 76.4 Adaptar formulários para mobile
    - Empilhar campos verticalmente
    - _Requirements: 16.4_

- [ ] 77. Implementar responsividade no painel cliente
  - [ ] 77.1 Adaptar layout do cliente para mobile
    - Menu lateral → bottom nav (< 768px)
    - _Requirements: 16.5_
  
  - [ ] 77.2 Adaptar chat para mobile
    - Fullscreen em mobile
    - Textarea adapta ao teclado
    - _Requirements: 16.6_
  
  - [ ] 77.3 Adaptar QR code para mobile
    - Centralizar e ajustar tamanho
    - _Requirements: 16.6_

- [ ] 78. Testar responsividade em múltiplas resoluções
  - [ ] 78.1 Testar em desktop (1920x1080)
    - Verificar todas as páginas admin e cliente
    - _Requirements: 16.5_
  
  - [ ] 78.2 Testar em tablet (768x1024)
    - Verificar todas as páginas admin e cliente
    - _Requirements: 16.5_
  
  - [ ] 78.3 Testar em mobile (375x667)
    - Verificar todas as páginas admin e cliente
    - Garantir funcionalidade completa
    - _Requirements: 16.5_

- [ ] 79. Checkpoint Final - Testar sistema completo
  - Verificar todas as 16 mini-fases
  - Garantir que performance está adequada (dashboard < 2s)
  - Verificar que todas as ações são logadas
  - Confirmar que mobile funciona em 375px

## Notes

- Tasks marcadas com `*` são opcionais e podem ser puladas para MVP mais rápido
- Cada mini-fase deve ser testada e commitada antes de avançar
- Admin não pode quebrar sistema de clientes
- Performance: dashboard deve carregar em < 2s
- Segurança: todas as ações críticas devem ser logadas
- Mobile: todas as telas devem funcionar em 375px
- Cada task referencia requirements específicos para rastreabilidade
- Checkpoints garantem validação incremental
- Property tests validam propriedades universais de correção
- Unit tests validam exemplos específicos e edge cases
- Testes de integração validam fluxos end-to-end
