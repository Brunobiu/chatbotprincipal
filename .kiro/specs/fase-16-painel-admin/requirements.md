# Requirements Document - FASE 16: Painel Admin Completo

## Introduction

Este documento especifica os requisitos para o painel administrativo completo do SaaS de WhatsApp AI Bot. O painel permitirá ao dono do SaaS gerenciar clientes, monitorar vendas, fornecer suporte, criar tutoriais, garantir segurança e monitorar todas as operações do negócio através de uma interface web centralizada.

O sistema deve fornecer visibilidade completa sobre o negócio, permitir ações administrativas críticas com segurança, e manter auditoria de todas as operações realizadas.

## Glossary

- **Admin**: Usuário administrador do SaaS com permissões elevadas para gerenciar o sistema
- **Cliente**: Usuário final que assina o serviço de chatbot WhatsApp
- **Sistema**: O SaaS de WhatsApp AI Bot como um todo
- **Dashboard**: Painel principal com métricas e visão geral do negócio
- **MRR**: Monthly Recurring Revenue (Receita Recorrente Mensal)
- **Ticket**: Solicitação de suporte criada por um cliente
- **Tutorial**: Conteúdo educacional em vídeo para clientes
- **Aviso**: Anúncio ou notificação exibida para todos os clientes
- **Audit_Log**: Registro de auditoria de ações administrativas
- **JWT**: JSON Web Token usado para autenticação
- **RAG**: Retrieval-Augmented Generation (sistema de IA com base de conhecimento)
- **ChromaDB**: Banco de dados vetorial para armazenamento de embeddings
- **Evolution_API**: API externa para integração com WhatsApp

## Requirements

### Requirement 1: Autenticação e Autorização de Administradores

**User Story:** Como dono do SaaS, eu quero fazer login no painel administrativo com credenciais seguras, para que apenas pessoas autorizadas possam acessar funcionalidades críticas do sistema.

#### Acceptance Criteria

1. THE Sistema SHALL armazenar credenciais de administradores com senha hash usando bcrypt
2. WHEN um administrador submete credenciais válidas, THE Sistema SHALL retornar um JWT com role=admin
3. WHEN um administrador submete credenciais inválidas, THE Sistema SHALL incrementar contador de tentativas e bloquear IP após 5 falhas
4. WHEN um token JWT é validado, THE Sistema SHALL verificar se o role é admin antes de permitir acesso a endpoints administrativos
5. THE Sistema SHALL criar um administrador inicial via seed script na primeira execução
6. WHEN um administrador acessa GET /api/v1/admin/auth/me, THE Sistema SHALL retornar dados do perfil do administrador autenticado

### Requirement 2: Dashboard com Métricas de Negócio

**User Story:** Como administrador, eu quero visualizar métricas chave do negócio em um dashboard, para que eu possa monitorar a saúde e crescimento do SaaS.

#### Acceptance Criteria

1. WHEN um administrador acessa o dashboard, THE Sistema SHALL exibir total de clientes ativos, MRR atual, novos clientes do mês e cancelamentos do mês
2. WHEN métricas são calculadas, THE Sistema SHALL incluir taxa de conversão e ticket médio
3. THE Sistema SHALL gerar gráfico de vendas por dia dos últimos 30 dias
4. THE Sistema SHALL gerar gráfico de receita mensal dos últimos 6 meses
5. WHEN o dashboard é carregado, THE Sistema SHALL exibir lista dos 5 clientes mais recentes
6. THE Sistema SHALL cachear métricas do dashboard por 5 minutos para otimizar performance

### Requirement 3: Gestão Completa de Clientes

**User Story:** Como administrador, eu quero gerenciar clientes (visualizar, editar, suspender, ativar), para que eu possa administrar a base de usuários do SaaS.

#### Acceptance Criteria

1. WHEN um administrador lista clientes, THE Sistema SHALL retornar dados paginados com filtros por status, plano e data de cadastro
2. WHEN um administrador visualiza detalhes de um cliente, THE Sistema SHALL exibir dados completos incluindo último login, IP, total de mensagens enviadas
3. WHEN um administrador edita dados de um cliente, THE Sistema SHALL validar e persistir as alterações
4. WHEN um administrador suspende um cliente, THE Sistema SHALL alterar status para SUSPENSO e impedir login
5. WHEN um administrador ativa um cliente suspenso, THE Sistema SHALL alterar status para ATIVO e permitir login
6. WHEN um administrador reseta senha de um cliente, THE Sistema SHALL gerar nova senha temporária e enviar por email
7. THE Sistema SHALL logar todas ações administrativas sobre clientes no audit log

### Requirement 4: Monitoramento de Uso de OpenAI

**User Story:** Como administrador, eu quero monitorar o uso da API OpenAI por cliente, para que eu possa controlar custos e identificar uso excessivo.

#### Acceptance Criteria

1. WHEN o AIService processa uma mensagem, THE Sistema SHALL registrar tokens usados, custo estimado e cliente_id
2. WHEN um administrador acessa resumo de uso, THE Sistema SHALL exibir top 10 clientes com maior gasto
3. WHEN um administrador visualiza uso de um cliente específico, THE Sistema SHALL exibir histórico diário de tokens e custos
4. WHEN uso de um cliente excede threshold configurado, THE Sistema SHALL gerar alerta automático
5. THE Sistema SHALL calcular custo estimado usando tabela de preços da OpenAI (input tokens e output tokens)
6. THE Sistema SHALL agregar dados de uso por dia para otimizar consultas

### Requirement 5: Sistema de Tickets de Suporte

**User Story:** Como administrador, eu quero gerenciar tickets de suporte dos clientes, para que eu possa fornecer atendimento eficiente e rastrear problemas.

#### Acceptance Criteria

1. WHEN um cliente cria um ticket, THE Sistema SHALL armazenar título, descrição, categoria e status ABERTO
2. WHEN um ticket é criado, THE Sistema SHALL tentar responder automaticamente usando RAG com threshold de confiança 0.7
3. IF confiança da resposta automática é menor que 0.7, THEN THE Sistema SHALL marcar ticket para atendimento humano
4. WHEN um administrador lista tickets, THE Sistema SHALL permitir filtros por status, categoria e cliente
5. WHEN um administrador responde um ticket, THE Sistema SHALL adicionar mensagem e notificar cliente por email
6. WHEN um administrador altera status de um ticket, THE Sistema SHALL registrar mudança com timestamp
7. THE Sistema SHALL categorizar tickets automaticamente usando IA quando categoria não for especificada

### Requirement 6: Gestão de Tutoriais em Vídeo

**User Story:** Como administrador, eu quero criar e gerenciar tutoriais em vídeo, para que clientes possam aprender a usar o sistema de forma autônoma.

#### Acceptance Criteria

1. WHEN um administrador cria um tutorial, THE Sistema SHALL armazenar título, descrição, URL do vídeo, categoria e ordem de exibição
2. WHEN um administrador reordena tutoriais, THE Sistema SHALL atualizar campo ordem usando drag-and-drop
3. WHEN um cliente visualiza um tutorial, THE Sistema SHALL registrar visualização com timestamp
4. WHEN um cliente comenta em um tutorial, THE Sistema SHALL armazenar comentário e exibir para outros clientes
5. WHEN um novo tutorial é publicado, THE Sistema SHALL notificar todos os clientes ativos
6. THE Sistema SHALL calcular estatísticas de visualizações e engajamento por tutorial

### Requirement 7: Sistema de Avisos e Anúncios

**User Story:** Como administrador, eu quero publicar avisos para todos os clientes, para que eu possa comunicar manutenções, novidades e informações importantes.

#### Acceptance Criteria

1. WHEN um administrador cria um aviso, THE Sistema SHALL armazenar tipo (info, warning, error, success), título, mensagem, data_inicio e data_fim
2. WHEN um cliente acessa o sistema, THE Sistema SHALL exibir avisos ativos no topo da interface
3. WHEN um aviso expira (data_fim < hoje), THE Sistema SHALL parar de exibir automaticamente
4. THE Sistema SHALL aplicar cores diferentes por tipo de aviso (azul=info, amarelo=warning, vermelho=error, verde=success)
5. WHEN um administrador desativa um aviso, THE Sistema SHALL parar de exibir imediatamente
6. THE Sistema SHALL permitir preview do aviso antes de publicar

### Requirement 8: Geração de Relatórios

**User Story:** Como administrador, eu quero gerar relatórios em PDF e Excel, para que eu possa analisar dados e compartilhar com stakeholders.

#### Acceptance Criteria

1. WHEN um administrador solicita relatório de vendas, THE Sistema SHALL gerar documento com filtros de período aplicados
2. WHEN um administrador solicita relatório de clientes, THE Sistema SHALL incluir dados demográficos e de uso
3. WHEN um administrador solicita relatório de uso OpenAI, THE Sistema SHALL incluir custos por cliente e totais
4. WHEN um administrador solicita relatório de tickets, THE Sistema SHALL incluir métricas de tempo de resposta e resolução
5. THE Sistema SHALL gerar relatórios em formato PDF usando ReportLab
6. THE Sistema SHALL gerar relatórios em formato Excel usando openpyxl
7. THE Sistema SHALL armazenar histórico de relatórios gerados por 90 dias

### Requirement 9: Segurança e Auditoria

**User Story:** Como administrador, eu quero monitorar tentativas de login e ações críticas, para que eu possa garantir a segurança do sistema.

#### Acceptance Criteria

1. WHEN uma tentativa de login falha, THE Sistema SHALL registrar IP, timestamp e credenciais tentadas
2. WHEN um IP tem 5 tentativas de login falhadas em 15 minutos, THE Sistema SHALL bloquear o IP por 1 hora
3. WHEN um administrador executa ação crítica (suspender cliente, resetar senha, cancelar assinatura), THE Sistema SHALL registrar no audit log
4. THE Sistema SHALL armazenar no audit log: admin_id, ação, entidade afetada, dados anteriores, dados novos, timestamp, IP
5. WHEN um administrador visualiza audit log, THE Sistema SHALL permitir filtros por admin, ação, entidade e período
6. WHEN um administrador desbloqueia um IP, THE Sistema SHALL remover bloqueio e registrar ação no audit log

### Requirement 10: Notificações para Administradores

**User Story:** Como administrador, eu quero receber notificações sobre eventos importantes, para que eu possa agir rapidamente quando necessário.

#### Acceptance Criteria

1. WHEN um novo cliente se cadastra, THE Sistema SHALL criar notificação para administradores
2. WHEN um pagamento é recusado, THE Sistema SHALL criar notificação com prioridade alta
3. WHEN um plano expira, THE Sistema SHALL criar notificação 3 dias antes e no dia
4. WHEN um novo ticket é criado, THE Sistema SHALL criar notificação se não foi resolvido automaticamente
5. WHEN uso de OpenAI de um cliente excede threshold, THE Sistema SHALL criar notificação de alerta
6. WHEN há tentativa de invasão (múltiplas falhas de login), THE Sistema SHALL criar notificação de segurança
7. WHEN um administrador acessa notificações, THE Sistema SHALL exibir badge com contador de não lidas
8. WHEN um administrador marca notificação como lida, THE Sistema SHALL atualizar status e remover do contador

### Requirement 11: Acesso do Admin à Ferramenta como Cliente

**User Story:** Como administrador, eu quero usar a ferramenta como se fosse um cliente, para que eu possa testar funcionalidades e entender a experiência do usuário.

#### Acceptance Criteria

1. THE Sistema SHALL criar um cliente especial vinculado ao administrador com status ATIVO permanente
2. WHEN um administrador acessa "Minha Ferramenta", THE Sistema SHALL fazer login automático no cliente especial
3. THE Sistema SHALL exibir botão "Voltar para Admin" quando administrador está usando ferramenta como cliente
4. THE Sistema SHALL não cobrar o cliente especial do administrador
5. WHEN administrador volta para painel admin, THE Sistema SHALL restaurar sessão administrativa

### Requirement 12: Preferências de Tema

**User Story:** Como administrador, eu quero alternar entre tema claro e escuro, para que eu possa usar o painel confortavelmente em diferentes ambientes.

#### Acceptance Criteria

1. WHEN um administrador alterna tema, THE Sistema SHALL persistir preferência no banco de dados
2. WHEN um administrador faz login, THE Sistema SHALL carregar tema salvo
3. THE Sistema SHALL aplicar tema usando CSS variables para cores
4. THE Sistema SHALL sincronizar tema entre localStorage e backend
5. THE Sistema SHALL exibir toggle visual (ícone sol/lua) para alternar tema

### Requirement 13: Monitoramento de Saúde do Sistema

**User Story:** Como administrador, eu quero monitorar a saúde dos serviços e infraestrutura, para que eu possa identificar e resolver problemas rapidamente.

#### Acceptance Criteria

1. WHEN um administrador acessa monitoramento, THE Sistema SHALL verificar conectividade com PostgreSQL, Redis, ChromaDB, Evolution API e OpenAI
2. WHEN um serviço está inacessível, THE Sistema SHALL exibir indicador vermelho e mensagem de erro
3. THE Sistema SHALL coletar métricas de CPU, memória, disco, tempo de resposta médio, requests por minuto e erros por minuto
4. THE Sistema SHALL exibir gráficos de métricas em tempo real com atualização a cada 30 segundos
5. WHEN uma métrica excede threshold crítico, THE Sistema SHALL exibir alerta visual
6. THE Sistema SHALL armazenar histórico de métricas por 7 dias para análise de tendências

### Requirement 14: Gestão de Vendas e Assinaturas

**User Story:** Como administrador, eu quero gerenciar vendas e assinaturas, para que eu possa resolver problemas de cobrança e atender solicitações de clientes.

#### Acceptance Criteria

1. WHEN um administrador lista vendas, THE Sistema SHALL exibir todas as transações com filtros por status, período e cliente
2. WHEN um administrador lista assinaturas, THE Sistema SHALL exibir status, plano, próxima cobrança e histórico de pagamentos
3. WHEN um administrador cancela uma assinatura, THE Sistema SHALL alterar status e impedir cobranças futuras
4. WHEN um administrador reativa uma assinatura, THE Sistema SHALL restaurar status ativo e agendar próxima cobrança
5. WHEN um administrador processa reembolso, THE Sistema SHALL registrar transação e notificar cliente
6. THE Sistema SHALL exigir confirmação para ações críticas (cancelamento, reembolso)

### Requirement 15: Histórico Completo do Cliente

**User Story:** Como administrador, eu quero visualizar histórico completo de um cliente, para que eu possa entender todo o relacionamento e resolver problemas de forma contextualizada.

#### Acceptance Criteria

1. WHEN um administrador acessa histórico de um cliente, THE Sistema SHALL exibir dados cadastrais, plano atual e status
2. THE Sistema SHALL exibir timeline com todos os eventos: cadastro, mudanças de plano, pagamentos, tickets, conversas
3. THE Sistema SHALL exibir gráfico de uso de OpenAI ao longo do tempo
4. THE Sistema SHALL exibir histórico de logins com IPs e timestamps
5. THE Sistema SHALL exibir todas as ações administrativas realizadas sobre o cliente
6. THE Sistema SHALL organizar informações em abas para facilitar navegação

### Requirement 16: Responsividade Mobile

**User Story:** Como administrador, eu quero acessar o painel em dispositivos móveis, para que eu possa gerenciar o sistema de qualquer lugar.

#### Acceptance Criteria

1. WHEN o painel é acessado em mobile (largura < 768px), THE Sistema SHALL colapsar sidebar em menu hambúrguer
2. WHEN tabelas são exibidas em mobile, THE Sistema SHALL transformar em cards verticais
3. WHEN gráficos são exibidos em mobile, THE Sistema SHALL ajustar dimensões mantendo legibilidade
4. WHEN formulários são exibidos em mobile, THE Sistema SHALL empilhar campos verticalmente
5. THE Sistema SHALL manter funcionalidade completa em resoluções 375x667 (mobile), 768x1024 (tablet) e 1920x1080 (desktop)
6. WHEN cliente acessa ferramenta em mobile, THE Sistema SHALL adaptar chat para fullscreen e textarea responsiva

## Parser and Serializer Requirements

### Requirement 17: Serialização de Dados de Relatórios

**User Story:** Como desenvolvedor, eu quero serializar dados de relatórios para JSON, para que o frontend possa consumir e exibir as informações.

#### Acceptance Criteria

1. WHEN dados de relatório são serializados, THE Sistema SHALL converter objetos Python para JSON válido
2. WHEN dados de relatório são desserializados, THE Sistema SHALL reconstruir objetos Python equivalentes
3. THE Sistema SHALL incluir pretty printer para formatar JSON de relatórios
4. FOR ALL objetos de relatório válidos, serializar então desserializar então serializar SHALL produzir JSON equivalente (round-trip property)

### Requirement 18: Parsing de Filtros de Consulta

**User Story:** Como desenvolvedor, eu quero parsear filtros de consulta da URL, para que o sistema possa aplicar filtros complexos em listagens.

#### Acceptance Criteria

1. WHEN filtros são recebidos como query params, THE Sistema SHALL parsear para objetos de filtro tipados
2. WHEN filtros inválidos são recebidos, THE Sistema SHALL retornar erro descritivo
3. THE Sistema SHALL incluir pretty printer para formatar filtros de volta para query string
4. FOR ALL objetos de filtro válidos, parsear então formatar então parsear SHALL produzir objeto equivalente (round-trip property)
