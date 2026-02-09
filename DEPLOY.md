# 🚀 Guia de Deploy para Produção

Este guia detalha os passos necessários para fazer deploy do WhatsApp AI Bot SaaS em produção.

---

## 📋 Pré-requisitos

Antes de iniciar o deploy, certifique-se de ter:

- [ ] Servidor com Docker e Docker Compose instalados
- [ ] Domínio configurado e apontando para o servidor
- [ ] Certificado SSL (Let's Encrypt recomendado)
- [ ] Conta Stripe em modo produção
- [ ] Conta SendGrid ou outro provedor SMTP
- [ ] API Key da OpenAI
- [ ] Instância Evolution API configurada

---

## 🔧 1. Preparação do Ambiente

### 1.1 Clonar Repositório

```bash
git clone <seu-repositorio>
cd chatbotprincipal
```

### 1.2 Criar Arquivo .env de Produção

Copie o arquivo de exemplo e edite com valores de produção:

```bash
cp .env.example .env.production
nano .env.production
```

**Variáveis Críticas:**

```env
# Ambiente
NODE_ENV=production
DEBUG=False

# URLs
FRONTEND_URL=https://seudominio.com
BACKEND_URL=https://api.seudominio.com

# Banco de Dados
DATABASE_URL=postgresql://usuario:senha@host:5432/database

# Redis
REDIS_URL=redis://:senha@host:6379/0

# Segurança
SECRET_KEY=<gerar-chave-forte-32-chars>
JWT_SECRET_KEY=<gerar-chave-forte-32-chars>

# Stripe (PRODUÇÃO)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# OpenAI
OPENAI_API_KEY=sk-...

# Email (SendGrid)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<sua-api-key>
SMTP_FROM=noreply@seudominio.com

# Evolution API
EVOLUTION_API_URL=https://evolution.seudominio.com
EVOLUTION_INSTANCE_NAME=<nome-instancia>
EVOLUTION_AUTHENTICATION_API_KEY=<sua-api-key>
```

### 1.3 Validar Configurações

Execute o script de validação:

```bash
cd apps/backend
python scripts/validate_production.py
```

Corrija todos os erros antes de continuar.

---

## 🗄️ 2. Banco de Dados

### 2.1 Criar Banco de Dados

```bash
# PostgreSQL
createdb whatsapp_ai_bot_prod

# Ou via SQL
psql -U postgres
CREATE DATABASE whatsapp_ai_bot_prod;
CREATE USER bot_user WITH PASSWORD 'senha-forte';
GRANT ALL PRIVILEGES ON DATABASE whatsapp_ai_bot_prod TO bot_user;
```

### 2.2 Executar Migrações

```bash
cd apps/backend
alembic upgrade head
```

### 2.3 Criar Admin Inicial

```bash
python scripts/create_admin.py \
  --email admin@seudominio.com \
  --senha <senha-forte> \
  --nome "Admin Principal"
```

---

## 🐳 3. Docker Deploy

### 3.1 Build das Imagens

```bash
# Backend
docker build -t whatsapp-bot-backend:latest ./apps/backend

# Frontend
docker build -t whatsapp-bot-frontend:latest ./apps/frontend
```

### 3.2 Docker Compose

Crie `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    image: whatsapp-bot-backend:latest
    env_file: .env.production
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    restart: always

  frontend:
    image: whatsapp-bot-frontend:latest
    env_file: .env.production
    ports:
      - "3000:3000"
    depends_on:
      - backend
    restart: always

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: whatsapp_ai_bot_prod
      POSTGRES_USER: bot_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    restart: always

volumes:
  postgres_data:
  redis_data:
```

### 3.3 Iniciar Serviços

```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🌐 4. Nginx e SSL

### 4.1 Instalar Certbot

```bash
sudo apt install certbot python3-certbot-nginx
```

### 4.2 Obter Certificado SSL

```bash
sudo certbot --nginx -d seudominio.com -d api.seudominio.com
```

### 4.3 Configurar Nginx

```nginx
# /etc/nginx/sites-available/whatsapp-bot

# Frontend
server {
    listen 80;
    server_name seudominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name seudominio.com;

    ssl_certificate /etc/letsencrypt/live/seudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seudominio.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}

# Backend API
server {
    listen 80;
    server_name api.seudominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.seudominio.com;

    ssl_certificate /etc/letsencrypt/live/seudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seudominio.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4.4 Ativar Configuração

```bash
sudo ln -s /etc/nginx/sites-available/whatsapp-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 💳 5. Configurar Stripe

### 5.1 Criar Produtos

No dashboard do Stripe (modo produção):

1. Criar produto "Plano 1 Mês" - R$ 97,00/mês
2. Criar produto "Plano 3 Meses" - R$ 261,90 (10% desconto)
3. Criar produto "Plano 12 Meses" - R$ 931,20 (20% desconto)

### 5.2 Configurar Webhooks

URL: `https://api.seudominio.com/api/v1/billing/webhook`

Eventos:
- `checkout.session.completed`
- `invoice.payment_succeeded`
- `customer.subscription.updated`
- `customer.subscription.deleted`

### 5.3 Testar Webhook

```bash
stripe listen --forward-to https://api.seudominio.com/api/v1/billing/webhook
```

---

## 📧 6. Configurar Email

### 6.1 SendGrid

1. Criar conta no SendGrid
2. Verificar domínio
3. Criar API Key
4. Atualizar variáveis SMTP no .env

### 6.2 Testar Envio

```bash
python scripts/test_email.py admin@seudominio.com
```

---

## 🔍 7. Monitoramento

### 7.1 Logs

```bash
# Ver logs em tempo real
docker-compose -f docker-compose.prod.yml logs -f

# Logs específicos
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
```

### 7.2 Health Checks

Configure health checks para monitorar:
- Backend: `https://api.seudominio.com/health`
- Frontend: `https://seudominio.com`
- Banco de Dados
- Redis

Ferramentas recomendadas:
- UptimeRobot
- Pingdom
- New Relic

---

## 💾 8. Backups

### 8.1 Backup Automático do Banco

```bash
# Criar script de backup
cat > /usr/local/bin/backup-db.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/postgres"
mkdir -p $BACKUP_DIR

docker exec postgres pg_dump -U bot_user whatsapp_ai_bot_prod | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Manter apenas últimos 30 dias
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete
EOF

chmod +x /usr/local/bin/backup-db.sh
```

### 8.2 Cron para Backup Diário

```bash
# Adicionar ao crontab
crontab -e

# Backup diário às 3h da manhã
0 3 * * * /usr/local/bin/backup-db.sh
```

---

## ✅ 9. Checklist Final

Antes de liberar para usuários:

- [ ] Todas as variáveis de ambiente configuradas
- [ ] Script de validação passou sem erros
- [ ] Migrações do banco executadas
- [ ] Admin criado e testado login
- [ ] SSL configurado e funcionando
- [ ] Stripe em modo produção e testado
- [ ] Webhooks do Stripe configurados
- [ ] Email funcionando (teste de envio)
- [ ] Evolution API conectada
- [ ] Backups automáticos configurados
- [ ] Monitoramento ativo
- [ ] Logs sendo coletados
- [ ] Documentação atualizada

---

## 🆘 10. Troubleshooting

### Erro de Conexão com Banco

```bash
# Verificar se PostgreSQL está rodando
docker-compose -f docker-compose.prod.yml ps postgres

# Ver logs
docker-compose -f docker-compose.prod.yml logs postgres
```

### Erro 502 Bad Gateway

```bash
# Verificar se backend está rodando
docker-compose -f docker-compose.prod.yml ps backend

# Reiniciar serviços
docker-compose -f docker-compose.prod.yml restart backend
```

### Webhook do Stripe não funciona

1. Verificar URL está acessível publicamente
2. Verificar STRIPE_WEBHOOK_SECRET está correto
3. Ver logs do backend durante webhook

---

## 📞 Suporte

Para problemas ou dúvidas:
- Documentação: `.kiro/contexto/`
- Checklist: `.kiro/contexto/CHECKLIST_PRODUCAO.md`
- Issues: GitHub Issues

---

**Última atualização:** 08/02/2026
