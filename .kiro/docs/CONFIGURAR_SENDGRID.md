# Como Configurar SendGrid para Envio de Emails

## Status Atual

✅ **Modo Desenvolvimento:** Emails são apenas logados (não enviados)  
⏳ **Modo Produção:** Requer configuração do SendGrid

---

## Modo Desenvolvimento (Atual)

Atualmente, o sistema está em **modo desenvolvimento**. Quando um email precisa ser enviado:

1. O sistema detecta que `SENDGRID_API_KEY` não está configurado
2. Em vez de enviar, ele **loga o email completo** no console
3. Você pode ver o conteúdo do email nos logs

### Como Testar

```bash
docker exec bot python testar_email.py
```

Você verá algo como:

```
================================================================================
📧 MODO DESENVOLVIMENTO - Email não enviado (SendGrid não configurado)
================================================================================
Para: cliente@exemplo.com
Assunto: 🎉 Bem-vindo ao WhatsApp AI Bot - Suas Credenciais de Acesso
--------------------------------------------------------------------------------
Corpo (texto):
Bem-vindo ao WhatsApp AI Bot!

Olá João Silva,

Seu pagamento foi aprovado e sua conta está pronta para uso!

SUAS CREDENCIAIS DE ACESSO:
Email: cliente@exemplo.com
Senha: SenhaSegura123!
...
================================================================================
```

---

## Configurar SendGrid (Produção)

Para enviar emails reais, você precisa:

### 1. Criar Conta no SendGrid

1. Acesse: https://sendgrid.com/
2. Crie uma conta gratuita (100 emails/dia grátis)
3. Verifique seu email

### 2. Criar API Key

1. No dashboard do SendGrid, vá em **Settings** → **API Keys**
2. Clique em **Create API Key**
3. Nome: `WhatsApp AI Bot`
4. Permissões: **Full Access** (ou apenas **Mail Send**)
5. Clique em **Create & View**
6. **COPIE A API KEY** (você não poderá ver novamente!)

### 3. Verificar Domínio de Envio (Opcional mas Recomendado)

Para evitar que emails caiam no spam:

1. Vá em **Settings** → **Sender Authentication**
2. Clique em **Verify a Single Sender**
3. Preencha seus dados:
   - From Name: `WhatsApp AI Bot`
   - From Email: `noreply@seudominio.com`
   - Reply To: `suporte@seudominio.com`
4. Verifique o email de confirmação

### 4. Configurar no .env

Adicione no arquivo `.env`:

```env
# SendGrid (Email)
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SENDGRID_FROM_EMAIL=noreply@seudominio.com
SENDGRID_FROM_NAME=WhatsApp AI Bot
DASHBOARD_URL=https://seudominio.com/login
```

### 5. Reiniciar Backend

```bash
docker-compose restart bot
```

---

## Testar Envio Real

Após configurar, teste novamente:

```bash
docker exec bot python testar_email.py
```

Agora o email será **enviado de verdade** para `cliente@exemplo.com`!

---

## Variáveis de Ambiente

| Variável | Obrigatório | Padrão | Descrição |
|----------|-------------|--------|-----------|
| `SENDGRID_API_KEY` | Não* | `None` | API Key do SendGrid |
| `SENDGRID_FROM_EMAIL` | Não | `noreply@whatsappaibot.com` | Email remetente |
| `SENDGRID_FROM_NAME` | Não | `WhatsApp AI Bot` | Nome do remetente |
| `DASHBOARD_URL` | Não | `http://localhost:3000/login` | URL do dashboard |

*Se não configurado, emails são apenas logados (modo desenvolvimento)

---

## Fluxo de Envio de Email

### Quando é Enviado?

O email de boas-vindas é enviado automaticamente quando:

1. Cliente completa o pagamento no Stripe
2. Webhook `checkout.session.completed` é recebido
3. Sistema cria conta do cliente no banco
4. Sistema gera senha aleatória
5. **Email é enviado com credenciais**

### Conteúdo do Email

- ✅ Saudação personalizada com nome do cliente
- ✅ Email e senha de acesso
- ✅ Botão para acessar o dashboard
- ✅ Próximos passos (configurar bot, conectar WhatsApp)
- ✅ Design responsivo (HTML + texto plano)

---

## Troubleshooting

### Email não está sendo enviado

1. Verifique se `SENDGRID_API_KEY` está configurado no `.env`
2. Verifique se a API Key é válida (não expirou)
3. Verifique os logs: `docker logs bot --tail 50`
4. Teste manualmente: `docker exec bot python testar_email.py`

### Email cai no spam

1. Verifique o domínio de envio no SendGrid
2. Configure SPF, DKIM e DMARC no seu domínio
3. Use um domínio verificado (não use @gmail.com, @hotmail.com)

### Erro "Invalid API Key"

1. Verifique se copiou a API Key completa
2. Verifique se não tem espaços extras no `.env`
3. Crie uma nova API Key no SendGrid

---

## Alternativas ao SendGrid

Se preferir outro serviço de email, você pode modificar o arquivo:
`apps/backend/app/services/email/email_service.py`

Serviços alternativos:
- **Mailgun** (100 emails/dia grátis)
- **Amazon SES** (62.000 emails/mês grátis)
- **Postmark** (100 emails/mês grátis)
- **Resend** (3.000 emails/mês grátis)

---

## Próximos Passos

Após configurar o email:

1. ✅ Testar envio de email
2. ⏳ Criar tela de login no frontend
3. ⏳ Integrar login com dashboard
4. ⏳ Testar fluxo completo: Pagamento → Email → Login

