# FASE 12: Tasks - Sistema de Confiança e Fallback Humano

## 1. Banco de Dados e Models

- [x] 1.1 Criar migration para tabela `conversas`
- [x] 1.2 Criar migration para adicionar campos em `mensagens` (confidence_score, fallback_triggered, conversa_id)
- [x] 1.3 Criar model `Conversa` com enums `StatusConversa` e `MotivoFallback`
- [x] 1.4 Atualizar model `Mensagem` com novos campos
- [x] 1.5 Atualizar model `Cliente` com relacionamento `conversas`
- [x] 1.6 Executar migrations no banco

## 2. Service: ConfiancaService

- [x] 2.1 Criar `app/services/confianca/confianca_service.py`
- [x] 2.2 Implementar `calcular_confianca(query, documentos, resposta) -> float`
  - [x] 2.2.1 Calcular similaridade média dos documentos (peso 0.5)
  - [x] 2.2.2 Calcular overlap de palavras-chave (peso 0.3)
  - [x] 2.2.3 Calcular score de tamanho da resposta (peso 0.2)
  - [x] 2.2.4 Retornar score final ponderado
- [x] 2.3 Implementar `deve_acionar_fallback(score, threshold) -> bool`
- [x] 2.4 Implementar `detectar_solicitacao_humano(mensagem) -> bool`
- [x] 2.5 Adicionar testes unitários para ConfiancaService

## 3. Service: FallbackService

- [x] 3.1 Criar `app/services/fallback/fallback_service.py`
- [x] 3.2 Implementar `acionar_fallback(db, conversa_id, motivo, numero_whatsapp, cliente_id)`
  - [x] 3.2.1 Buscar ou criar conversa
  - [x] 3.2.2 Atualizar status para AGUARDANDO_HUMANO
  - [x] 3.2.3 Salvar motivo do fallback
  - [x] 3.2.4 Enviar mensagem_fallback configurada
- [x] 3.3 Implementar `notificar_humano(conversa_id, cliente_nome, ultima_mensagem)`
  - [x] 3.3.1 Buscar email de notificação nas configurações
  - [x] 3.3.2 Montar template de email
  - [x] 3.3.3 Enviar email via EmailService
- [x] 3.4 Implementar `assumir_conversa(db, conversa_id, atendente_email)`
- [x] 3.5 Implementar `verificar_timeout_24h(db)`
  - [x] 3.5.1 Buscar conversas aguardando há mais de 24h
  - [x] 3.5.2 Enviar mensagem_retorno_24h
  - [x] 3.5.3 Voltar status para ATIVA
- [x] 3.6 Adicionar testes unitários para FallbackService

## 4. Atualizar ConfiguracaoBot

- [x] 4.1 Adicionar campo `threshold_confianca` (default: 0.6)
- [x] 4.2 Adicionar campo `notificar_email`
- [x] 4.3 Criar migration para novos campos
- [x] 4.4 Atualizar ConfiguracaoService

## 5. Integrar com Webhook WhatsApp

- [x] 5.1 Atualizar `whatsapp_service.py` para processar mensagens com confiança
  - [x] 5.1.1 Após gerar resposta, calcular score de confiança
  - [x] 5.1.2 Verificar se deve acionar fallback (score < threshold)
  - [x] 5.1.3 Verificar se cliente solicitou humano
  - [x] 5.1.4 Se fallback: acionar FallbackService
  - [x] 5.1.5 Se não: enviar resposta normalmente
  - [x] 5.1.6 Salvar mensagem com confidence_score
- [x] 5.2 Verificar se conversa está em AGUARDANDO_HUMANO antes de responder
- [x] 5.3 Adicionar logs detalhados do fluxo de confiança

## 6. Endpoints API

- [x] 6.1 Criar `app/api/v1/conversas.py`
- [x] 6.2 Implementar `GET /api/v1/conversas/aguardando-humano`
  - [x] 6.2.1 Buscar conversas com status AGUARDANDO_HUMANO
  - [x] 6.2.2 Calcular tempo de espera
  - [x] 6.2.3 Retornar lista ordenada por tempo
- [x] 6.3 Implementar `POST /api/v1/conversas/{id}/assumir`
  - [x] 6.3.1 Validar conversa existe
  - [x] 6.3.2 Chamar FallbackService.assumir_conversa
  - [x] 6.3.3 Retornar confirmação
- [x] 6.4 Implementar `GET /api/v1/conversas/{id}/historico`
  - [x] 6.4.1 Buscar todas as mensagens da conversa
  - [x] 6.4.2 Ordenar por data
  - [x] 6.4.3 Incluir confidence_score
- [x] 6.5 Registrar rotas no `main.py`

## 7. Job Agendado

- [x] 7.1 Instalar APScheduler: `pip install apscheduler`
- [x] 7.2 Criar `app/workers/scheduler.py`
- [x] 7.3 Configurar job para rodar a cada 1 hora
- [x] 7.4 Chamar `FallbackService.verificar_timeout_24h()`
- [x] 7.5 Inicializar scheduler no `main.py`
- [x] 7.6 Adicionar logs de execução do job

## 8. Testes

- [x] 8.1 Testes unitários: ConfiancaService
  - [x] 8.1.1 test_calcular_confianca_alta
  - [x] 8.1.2 test_calcular_confianca_baixa
  - [x] 8.1.3 test_calcular_confianca_sem_documentos
  - [x] 8.1.4 test_detectar_solicitacao_humano_positivo
  - [x] 8.1.5 test_detectar_solicitacao_humano_negativo
- [x] 8.2 Testes unitários: FallbackService
  - [x] 8.2.1 test_acionar_fallback_baixa_confianca
  - [x] 8.2.2 test_acionar_fallback_solicitacao_manual
  - [x] 8.2.3 test_assumir_conversa
  - [x] 8.2.4 test_verificar_timeout_24h
- [x] 8.3 Testes de integração
  - [x] 8.3.1 test_fluxo_completo_fallback_automatico
  - [x] 8.3.2 test_fluxo_completo_solicitacao_manual
  - [x] 8.3.3 test_fluxo_retorno_24h
- [x] 8.4 Testes manuais via WhatsApp
  - [x] 8.4.1 Enviar mensagem que gera baixa confiança
  - [x] 8.4.2 Enviar "quero falar com humano"
  - [x] 8.4.3 Verificar email de notificação
  - [x] 8.4.4 Assumir conversa via API
  - [x] 8.4.5 Simular timeout de 24h

## 9. Documentação

- [x] 9.1 Atualizar README com informações da FASE 12
- [x] 9.2 Documentar endpoints da API
- [x] 9.3 Criar guia de uso para atendentes
- [x] 9.4 Documentar configuração do threshold
- [x] 9.5 Adicionar exemplos de uso

## 10. Deploy e Validação

- [x] 10.1 Atualizar requirements.txt com APScheduler
- [x] 10.2 Executar migrations em produção
- [x] 10.3 Configurar email de notificação
- [x] 10.4 Testar fluxo completo em produção
- [x] 10.5 Monitorar logs e métricas
