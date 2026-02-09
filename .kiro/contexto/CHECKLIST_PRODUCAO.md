# ✅ CHECKLIST DE PRODUÇÃO - WhatsApp AI Bot SaaS

**Data de Criação:** 08/02/2026  
**Status:** Preparação  
**Objetivo:** Garantir transição segura de desenvolvimento para produção

---

## 🔐 1. CREDENCIAIS E AUTENTICAÇÃO

### 1.1 Admin Principal
- [ ] Criar email profissional para admin (ex: admin@seudominio.com)
- [ ] Gerar senha forte (mínimo 16 caracteres, letras, números, símbolos)
- [ ] Remover credenciais de desenvolvimento (brunobiuu/admin123)
- [ ] Configurar autenticação de dois fatores (2FA) se disponível
- [ ] Documentar credenciais em local seguro (1Password, LastPass, etc)

### 1.2 Cliente de Teste
- [ ] Criar email secundário para testes (ex: teste@seudominio.com)
- [ ] Gerar senha forte para cliente teste
- [ ] Documentar credenciais de teste separadamente

### 1.3 Banco de Dados
- [ ] Alterar senha do PostgreSQL (remover senha padrão)
- [ ] Criar usuário específico para aplicação (não usar root)
- [ ] Documentar credenciais do banco

### 1.4 Redis
- [ ] Configurar senha para Redis
- [ ] Atualizar variável REDIS_URL com senha

---

## 💳 2. STRIPE (PAGAMENTOS)

### 2.1 Modo Produção
- [ ] Criar conta Stripe em modo produção
- [ ] Obter chaves de API produção (pk_live_... e sk_live_...)
- [ ] Atualizar STRIPE_SECRET_KEY no .env
- [ ] Atualizar STRIPE_PUBLISHABLE_KEY no frontend

### 2.2 Produtos e Preços
- [ ] Criar produto "Plano 1 Mês" com valor real
- [ ] Criar produto "Plano 3 Meses" com desconto 10%
- [ ] Criar produto "Plano 12 Meses" com desconto 20%
- [ ] Configurar webhooks do Stripe apontando para domínio produção
- [ ] Testar webhook em produção (usar Stripe CLI)

### 2.3 PIX (se implementado)
- [ ] Configurar PIX no Stripe
- [ ] Testar pagamento PIX em produção
- [ ] Validar confirmação automática

### 2.4 Cartão de Débito (se implementado)
- [ ] Habilitar cartão de débito no Stripe
- [ ] Testar pagamento com débito

---

## 📧 3. EMAIL (SMTP)

### 3.1 SendGrid
- [ ] Criar conta SendGrid
- [ ] Verificar domínio no SendGrid
- [ ] Obter API Key do SendGrid
- [ ] Atualizar variáveis de ambiente:
  - SMTP_HOST=smtp.sendgrid.net
  - SMTP_PORT=587
  - SMTP_USER=apikey
  - SMTP_PASSWORD=<sua_api_key>
  - SMTP_FROM=noreply@seudominio.com

### 3.2 Templates de Email
- [ ] Criar template de boas-vindas
- [ ] Criar template de recuperação de senha
- [ ] Criar template de notificação de pagamento
- [ ] Criar template de expiração de assinatura
- [ ] Testar envio de emails em produção

---

## 📱 4. WHATSAPP (EVOLUTION API)

### 4.1 Instância Produção
- [ ] Configurar Evolution API em servidor produção
- [ ] Atualizar EVOLUTION_API_URL no .env
- [ ] Atualizar EVOLUTION_API_KEY no .env
- [ ] Testar criação de instância
- [ ] Testar envio e recebimento de mensagens

### 4.2 Webhooks
- [ ] Configurar webhook da Evolution apontando para domínio produção
- [ ] Validar recebimento de mensagens
- [ ] Testar ignorar grupos

---

## 🤖 5. OPENAI

### 5.1 API Key Produção
- [ ] Criar API Key específica para produção
- [ ] Atualizar OPENAI_API_KEY no .env
- [ ] Configurar limites de uso (budget)
- [ ] Configurar alertas de uso excessivo

### 5.2 Monitoramento
- [ ] Configurar dashboard de uso no OpenAI
- [ ] Definir threshold de alerta (ex: $100/dia)
- [ ] Configurar notificações de uso

---

## 🗄️ 6. BANCO DE DADOS

### 6.1 PostgreSQL Produção
- [ ] Criar banco de dados produção
- [ ] Executar todas as migrações (alembic upgrade head)
- [ ] Criar backup inicial
- [ ] Configurar backups automáticos diários
- [ ] Testar restauração de backup

### 6.2 Redis Produção
- [ ] Configurar Redis em produção
- [ ] Configurar persistência (RDB ou AOF)
- [ ] Configurar senha
- [ ] Testar conexão

### 6.3 ChromaDB Produção
- [ ] Configurar ChromaDB em produção
- [ ] Configurar volume persistente
- [ ] Testar criação de coleções
- [ ] Testar busca de embeddings

---

## 🌐 7. DOMÍNIO E DNS

### 7.1 Domínio
- [ ] Registrar domínio (ex: seubot.com.br)
- [ ] Configurar DNS apontando para IP do servidor
- [ ] Configurar subdomínios:
  - app.seubot.com.br (frontend)
  - api.seubot.com.br (backend)
  - evolution.seubot.com.br (Evolution API)

### 7.2 SSL/HTTPS
- [ ] Instalar Certbot no servidor
- [ ] Gerar certificados SSL (Let's Encrypt)
- [ ] Configurar renovação automática
- [ ] Testar HTTPS em todos os subdomínios
- [ ] Forçar redirecionamento HTTP → HTTPS

---

## 🐳 8. INFRAESTRUTURA (VPS)

### 8.1 Servidor
- [ ] Contratar VPS (recomendado: 4GB RAM, 2 vCPU, 80GB SSD)
- [ ] Instalar Ubuntu 22.04 LTS
- [ ] Atualizar sistema (apt update && apt upgrade)
- [ ] Instalar Docker e Docker Compose
- [ ] Configurar firewall (UFW):
  - Permitir 22 (SSH)
  - Permitir 80 (HTTP)
  - Permitir 443 (HTTPS)
  - Bloquear demais portas

### 8.2 Nginx
- [ ] Instalar Nginx
- [ ] Configurar reverse proxy para backend
- [ ] Configurar reverse proxy para frontend
- [ ] Configurar reverse proxy para Evolution API
- [ ] Configurar SSL
- [ ] Testar configuração (nginx -t)

### 8.3 Docker Compose
- [ ] Copiar docker-compose.yml para servidor
- [ ] Atualizar variáveis de ambiente
- [ ] Executar docker-compose up -d
- [ ] Verificar todos os containers rodando
- [ ] Configurar restart automático (restart: always)

---

## 🔒 9. SEGURANÇA

### 9.1 Servidor
- [ ] Desabilitar login root via SSH
- [ ] Criar usuário não-root para deploy
- [ ] Configurar chave SSH (desabilitar senha)
- [ ] Instalar fail2ban (proteção contra brute force)
- [ ] Configurar firewall (UFW)

### 9.2 Aplicação
- [ ] Alterar JWT_SECRET_KEY (gerar nova chave forte)
- [ ] Alterar ADMIN_JWT_SECRET_KEY (gerar nova chave forte)
- [ ] Configurar CORS apenas para domínio produção
- [ ] Habilitar rate limiting em endpoints críticos
- [ ] Configurar logs de auditoria

### 9.3 Banco de Dados
- [ ] Configurar acesso apenas via localhost
- [ ] Criar usuário específico com permissões limitadas
- [ ] Habilitar SSL para conexões
- [ ] Configurar backups criptografados

---

## 📊 10. MONITORAMENTO

### 10.1 Uptime
- [ ] Criar conta no UptimeRobot (ou similar)
- [ ] Configurar monitoramento do frontend
- [ ] Configurar monitoramento do backend (/health)
- [ ] Configurar alertas por email/SMS

### 10.2 Logs
- [ ] Configurar rotação de logs (logrotate)
- [ ] Configurar centralização de logs (opcional: ELK Stack)
- [ ] Configurar alertas de erros críticos

### 10.3 Métricas
- [ ] Configurar monitoramento de CPU/RAM/Disco
- [ ] Configurar alertas de uso excessivo
- [ ] Configurar dashboard de métricas (opcional: Grafana)

---

## 🧪 11. TESTES EM PRODUÇÃO

### 11.1 Funcionalidades Críticas
- [ ] Testar cadastro de novo cliente
- [ ] Testar pagamento com cartão de crédito
- [ ] Testar pagamento com PIX (se implementado)
- [ ] Testar conexão WhatsApp (QR Code)
- [ ] Testar envio e recebimento de mensagens
- [ ] Testar salvamento de conhecimento
- [ ] Testar sistema de confiança e fallback
- [ ] Testar criação de tickets
- [ ] Testar sistema de agendamentos (se implementado)

### 11.2 Painel Admin
- [ ] Testar login admin
- [ ] Testar dashboard com métricas
- [ ] Testar gestão de clientes
- [ ] Testar relatórios
- [ ] Testar notificações

### 11.3 Performance
- [ ] Testar tempo de resposta do bot (< 3s)
- [ ] Testar carga com múltiplas mensagens simultâneas
- [ ] Testar geração de embeddings (< 2 minutos)

---

## 📝 12. DOCUMENTAÇÃO

### 12.1 Interna
- [ ] Atualizar README.md com instruções de produção
- [ ] Documentar processo de deploy
- [ ] Documentar processo de backup e restauração
- [ ] Documentar troubleshooting comum

### 12.2 Externa (para clientes)
- [ ] Criar página de ajuda/FAQ
- [ ] Criar tutoriais em vídeo
- [ ] Criar documentação de API (se necessário)

---

## 🚀 13. DEPLOY

### 13.1 Preparação
- [ ] Fazer backup completo do ambiente de desenvolvimento
- [ ] Testar todas as funcionalidades em staging (se houver)
- [ ] Revisar este checklist completo

### 13.2 Execução
- [ ] Fazer deploy do backend
- [ ] Fazer deploy do frontend
- [ ] Executar migrações do banco
- [ ] Verificar todos os serviços rodando
- [ ] Testar funcionalidades críticas

### 13.3 Pós-Deploy
- [ ] Monitorar logs por 24h
- [ ] Monitorar métricas de uso
- [ ] Estar disponível para correções urgentes
- [ ] Comunicar clientes sobre lançamento

---

## 📋 14. VARIÁVEIS DE AMBIENTE PRODUÇÃO

### Backend (.env)
```bash
# Banco de Dados
DATABASE_URL=postgresql://usuario_prod:senha_forte@localhost:5432/chatbot_prod

# Redis
REDIS_URL=redis://:senha_redis@localhost:6379/0

# ChromaDB
CHROMA_HOST=localhost
CHROMA_PORT=8001

# OpenAI
OPENAI_API_KEY=sk-proj-...

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Evolution API
EVOLUTION_API_URL=https://evolution.seudominio.com
EVOLUTION_API_KEY=sua_chave_evolution

# SMTP (SendGrid)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=SG.xxxxx
SMTP_FROM=noreply@seudominio.com

# JWT
JWT_SECRET_KEY=chave_super_secreta_prod_32_chars_min
ADMIN_JWT_SECRET_KEY=chave_admin_super_secreta_prod_32_chars

# Ambiente
ENVIRONMENT=production
DEBUG=false

# CORS
ALLOWED_ORIGINS=https://app.seudominio.com
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=https://api.seudominio.com
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
```

---

## ⚠️ 15. AVISOS IMPORTANTES

### 15.1 Nunca Fazer em Produção
- ❌ Usar credenciais de desenvolvimento
- ❌ Expor portas desnecessárias
- ❌ Desabilitar SSL/HTTPS
- ❌ Usar DEBUG=true
- ❌ Commitar .env no Git
- ❌ Usar senhas fracas
- ❌ Ignorar backups

### 15.2 Sempre Fazer
- ✅ Testar em staging antes de produção
- ✅ Fazer backup antes de mudanças críticas
- ✅ Monitorar logs após deploy
- ✅ Ter plano de rollback
- ✅ Documentar mudanças
- ✅ Comunicar clientes sobre manutenções

---

## 📞 16. CONTATOS DE EMERGÊNCIA

### 16.1 Serviços
- **VPS:** [provedor] - suporte@provedor.com
- **Domínio:** [registrar] - suporte@registrar.com
- **Stripe:** https://support.stripe.com
- **SendGrid:** https://support.sendgrid.com
- **OpenAI:** https://help.openai.com

### 16.2 Equipe
- **Desenvolvedor:** [seu email]
- **Admin do Sistema:** [email admin]

---

## ✅ STATUS DO CHECKLIST

**Última Atualização:** 08/02/2026  
**Itens Completos:** 0 / 150+  
**Status:** 🔴 Não Iniciado

### Progresso por Seção
- [ ] 1. Credenciais (0/12)
- [ ] 2. Stripe (0/12)
- [ ] 3. Email (0/8)
- [ ] 4. WhatsApp (0/6)
- [ ] 5. OpenAI (0/5)
- [ ] 6. Banco de Dados (0/10)
- [ ] 7. Domínio e DNS (0/9)
- [ ] 8. Infraestrutura (0/15)
- [ ] 9. Segurança (0/12)
- [ ] 10. Monitoramento (0/9)
- [ ] 11. Testes (0/15)
- [ ] 12. Documentação (0/5)
- [ ] 13. Deploy (0/9)
- [ ] 14. Variáveis (0/2)
- [ ] 15. Avisos (leitura)
- [ ] 16. Contatos (configuração)

---

**🎯 Objetivo:** Completar 100% deste checklist antes do deploy em produção (Fase 17)

**📌 Nota:** Este documento deve ser revisado e atualizado conforme o projeto evolui.
