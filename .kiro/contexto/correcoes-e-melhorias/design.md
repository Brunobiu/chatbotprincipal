# Design Document - Correções e Melhorias

**Feature:** correcoes-e-melhorias  
**Data de Criação:** 08/02/2026  
**Status:** Em Design  
**Linguagem de Implementação:** Python (Backend) + TypeScript (Frontend)

---

## 1. Overview

Este documento detalha a arquitetura técnica para implementar todas as correções de bugs e novas funcionalidades identificadas antes do deploy em produção (Fase 17).

### 1.1 Contexto

O sistema é um SaaS de chatbot WhatsApp com IA que já possui:
- Backend FastAPI com PostgreSQL, Redis e ChromaDB
- Frontend Next.js 14 com Tailwind CSS
- Painel admin completo (Fase 16 concluída)
- Sistema de pagamentos com Stripe
- Integração WhatsApp via Evolution API
- Sistema RAG com OpenAI GPT-4

### 1.2 Objetivos do Design

1. **Corrigir bugs críticos** que impedem uso adequado do sistema
2. **Adicionar funcionalidades faltantes** para completar MVP
3. **Melhorar segurança** com validações e confirmações
4. **Aprimorar UX/UI** para melhor experiência do usuário
5. **Preparar sistema para produção** com checklist completo

### 1.3 Escopo

Este design cobre 6 categorias principais:
- Correções Críticas (5 bugs)
- Melhorias de Segurança (2 features)
- Novas Funcionalidades (4 features)
- Melhorias de UX/UI (2 features)
- Melhorias de Pagamento (2 features)
- Preparação para Produção (1 checklist)

---

## 2. Architecture

### 2.1 Arquitetura Geral


O sistema mantém a arquitetura existente com adições específicas:

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js 14)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Cliente    │  │    Admin     │  │    Login     │      │
│  │  Dashboard   │  │   Dashboard  │  │  Redesigned  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Conversas   │  │ Agendamentos │  │   Tickets    │      │
│  │   Service    │  │   Service    │  │   Service    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Conhecimento │  │   Perfil     │  │   Billing    │      │
│  │   Service    │  │   Service    │  │   Service    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATA LAYER                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  PostgreSQL  │  │    Redis     │  │  ChromaDB    │      │
│  │  (Relacional)│  │   (Cache)    │  │  (Vetores)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 EXTERNAL SERVICES                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Evolution   │  │   OpenAI     │  │   Stripe     │      │
│  │     API      │  │    GPT-4     │  │  Payments    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Novos Componentes

#### 2.2.1 Sistema de Agendamentos
- **AgendamentoService**: Gerencia slots de horários e reservas
- **AgendamentoAIParser**: Extrai intenção de agendamento de mensagens
- **AgendamentoNotifier**: Envia notificações WhatsApp sobre agendamentos

#### 2.2.2 Chat Suporte Melhorado
- **ChatSupporteService**: Gerencia chat com IA + tickets
- **TicketEscalationService**: Decide quando escalar para humano
- **TicketAIResponder**: IA responde tickets automaticamente

#### 2.2.3 Admin Usa Ferramenta
- **AdminClienteService**: Cria cliente especial para admin
- **AdminToolAccessService**: Gerencia acesso do admin à ferramenta

#### 2.2.4 Dicas da IA
- **DicasIAService**: Analisa métricas e gera insights
- **DicasIAScheduler**: Atualiza dicas diariamente

### 2.3 Modificações em Componentes Existentes

#### 2.3.1 ConversasService
- Adicionar listagem completa de conversas
- Implementar filtros por data e status
- Adicionar paginação

#### 2.3.2 ConhecimentoService
- Adicionar validação de senha antes de salvar
- Implementar feature "IA te ajuda" para melhorar texto
- Corrigir bug do contador de mensagens

#### 2.3.3 PerfilService
- Adicionar endpoint de edição de perfil
- Implementar validação de email único
- Adicionar confirmação por senha

#### 2.3.4 BillingService
- Adicionar suporte a PIX
- Adicionar suporte a cartão de débito
- Implementar múltiplos planos (1, 3, 12 meses)
- Adicionar cálculo proporcional ao mudar plano

#### 2.3.5 TutorialService
- Corrigir sincronização de tutoriais para clientes
- Adicionar notificações de novos tutoriais

---

## 3. Components and Interfaces

### 3.1 Backend Components

#### 3.1.1 Conversas (Correção Bug)

**Arquivo:** `apps/backend/app/services/conversas/conversa_service.py`

```python
class ConversaService:
    async def listar_conversas(
        self,
        cliente_id: int,
        filtro_data_inicio: Optional[datetime] = None,
        filtro_data_fim: Optional[datetime] = None,
        filtro_status: Optional[str] = None,
        pagina: int = 1,
        itens_por_pagina: int = 20
    ) -> Dict[str, Any]:
        """
        Lista conversas do cliente com filtros e paginação.
        
        Returns:
            {
                "conversas": [...],
                "total": int,
                "pagina": int,
                "total_paginas": int
            }
        """
        pass
    
    async def obter_historico_conversa(
        self,
        conversa_id: int,
        cliente_id: int
    ) -> List[Dict[str, Any]]:
        """
        Retorna todas as mensagens de uma conversa.
        """
        pass
```

**Endpoint:** `apps/backend/app/api/v1/conversas.py`

```python
@router.get("/conversas")
async def listar_conversas(
    filtro_data_inicio: Optional[str] = None,
    filtro_data_fim: Optional[str] = None,
    filtro_status: Optional[str] = None,
    pagina: int = 1,
    current_user: Cliente = Depends(get_current_user)
):
    """Lista conversas do cliente com filtros."""
    pass

@router.get("/conversas/{conversa_id}/mensagens")
async def obter_mensagens_conversa(
    conversa_id: int,
    current_user: Cliente = Depends(get_current_user)
):
    """Retorna histórico de mensagens de uma conversa."""
    pass
```

#### 3.1.2 Conhecimento (Correção Bug + Melhorias)

**Arquivo:** `apps/backend/app/services/conhecimento/conhecimento_service.py`

```python
class ConhecimentoService:
    async def salvar_conhecimento(
        self,
        cliente_id: int,
        conteudo: str,
        senha: str
    ) -> Dict[str, Any]:
        """
        Salva conhecimento após validar senha.
        NÃO decrementa contador de mensagens.
        """
        pass
    
    async def melhorar_texto_com_ia(
        self,
        texto_original: str,
        cliente_id: int
    ) -> str:
        """
        Usa OpenAI para estruturar e melhorar texto.
        """
        pass
    
    async def obter_contador_mensagens(
        self,
        cliente_id: int
    ) -> int:
        """
        Retorna contador atual de mensagens.
        Contador só aumenta, nunca diminui.
        """
        pass
```

**Endpoint:** `apps/backend/app/api/v1/conhecimento.py`

```python
@router.put("/conhecimento")
async def salvar_conhecimento(
    dados: SalvarConhecimentoRequest,  # conteudo + senha
    current_user: Cliente = Depends(get_current_user)
):
    """Salva conhecimento após validar senha."""
    pass

@router.post("/conhecimento/melhorar-ia")
async def melhorar_texto_ia(
    dados: MelhorarTextoRequest,  # texto_original
    current_user: Cliente = Depends(get_current_user)
):
    """IA melhora e estrutura o texto fornecido."""
    pass
```

#### 3.1.3 Perfil (Correção Bug)

**Arquivo:** `apps/backend/app/services/perfil/perfil_service.py`

```python
class PerfilService:
    async def editar_perfil(
        self,
        cliente_id: int,
        nome: Optional[str],
        telefone: Optional[str],
        email: Optional[str],
        senha_confirmacao: str
    ) -> Dict[str, Any]:
        """
        Edita informações do perfil após validar senha.
        Valida email único se alterado.
        """
        pass
    
    async def validar_email_unico(
        self,
        email: str,
        cliente_id: int
    ) -> bool:
        """
        Verifica se email já está em uso por outro cliente.
        """
        pass
```

**Endpoint:** `apps/backend/app/api/v1/perfil.py`

```python
@router.put("/perfil")
async def editar_perfil(
    dados: EditarPerfilRequest,
    current_user: Cliente = Depends(get_current_user)
):
    """Edita perfil do cliente após validar senha."""
    pass
```

#### 3.1.4 Assinatura (Nova Feature)

**Arquivo:** `apps/backend/app/services/assinatura/assinatura_service.py`

```python
class AssinaturaService:
    async def obter_info_assinatura(
        self,
        cliente_id: int
    ) -> Dict[str, Any]:
        """
        Retorna informações da assinatura:
        - status (ativa, cancelada, expirada)
        - dias_restantes
        - plano_atual
        - data_proxima_cobranca
        - valor_mensal
        """
        pass
    
    async def calcular_dias_restantes(
        self,
        data_expiracao: datetime
    ) -> int:
        """Calcula dias restantes até expiração."""
        pass
```

**Endpoint:** `apps/backend/app/api/v1/assinatura.py`

```python
@router.get("/assinatura/info")
async def obter_info_assinatura(
    current_user: Cliente = Depends(get_current_user)
):
    """Retorna informações da assinatura do cliente."""
    pass
```


#### 3.1.5 Agendamentos (Nova Feature)

**Arquivo:** `apps/backend/app/services/agendamentos/agendamento_service.py`

```python
class AgendamentoService:
    async def configurar_horarios(
        self,
        cliente_id: int,
        horarios_disponiveis: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Configura horários disponíveis para agendamento.
        
        horarios_disponiveis: [
            {
                "dia_semana": "segunda",
                "hora_inicio": "09:00",
                "hora_fim": "18:00",
                "duracao_slot": 30  # minutos
            }
        ]
        """
        pass
    
    async def criar_agendamento(
        self,
        cliente_id: int,
        numero_usuario: str,
        data_hora: datetime,
        tipo_servico: str,
        observacoes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Cria novo agendamento (status: pendente).
        """
        pass
    
    async def listar_agendamentos_pendentes(
        self,
        cliente_id: int
    ) -> List[Dict[str, Any]]:
        """Lista agendamentos com status pendente."""
        pass
    
    async def aprovar_agendamento(
        self,
        agendamento_id: int,
        cliente_id: int
    ) -> Dict[str, Any]:
        """Aprova agendamento e envia notificação WhatsApp."""
        pass
    
    async def recusar_agendamento(
        self,
        agendamento_id: int,
        cliente_id: int,
        motivo: Optional[str] = None
    ) -> Dict[str, Any]:
        """Recusa agendamento e envia notificação WhatsApp."""
        pass
```

**Arquivo:** `apps/backend/app/services/agendamentos/agendamento_ai_parser.py`

```python
class AgendamentoAIParser:
    async def extrair_intencao_agendamento(
        self,
        mensagem: str,
        contexto_cliente: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Usa OpenAI para identificar se mensagem é pedido de agendamento.
        
        Returns:
            {
                "eh_agendamento": bool,
                "data_hora_sugerida": datetime,
                "tipo_servico": str,
                "observacoes": str
            } ou None
        """
        pass
```

**Endpoints:** `apps/backend/app/api/v1/agendamentos.py`

```python
@router.post("/agendamentos/configurar-horarios")
async def configurar_horarios(
    dados: ConfigurarHorariosRequest,
    current_user: Cliente = Depends(get_current_user)
):
    """Configura horários disponíveis."""
    pass

@router.get("/agendamentos/pendentes")
async def listar_pendentes(
    current_user: Cliente = Depends(get_current_user)
):
    """Lista agendamentos pendentes."""
    pass

@router.post("/agendamentos/{agendamento_id}/aprovar")
async def aprovar_agendamento(
    agendamento_id: int,
    current_user: Cliente = Depends(get_current_user)
):
    """Aprova agendamento."""
    pass

@router.post("/agendamentos/{agendamento_id}/recusar")
async def recusar_agendamento(
    agendamento_id: int,
    dados: RecusarAgendamentoRequest,
    current_user: Cliente = Depends(get_current_user)
):
    """Recusa agendamento."""
    pass
```

#### 3.1.6 Chat Suporte (Nova Feature)

**Arquivo:** `apps/backend/app/services/chat_suporte/chat_suporte_service.py`

```python
class ChatSuporteService:
    async def enviar_mensagem(
        self,
        cliente_id: int,
        mensagem: str
    ) -> Dict[str, Any]:
        """
        Envia mensagem no chat suporte.
        IA responde automaticamente.
        Se confiança < 0.7, oferece abrir ticket.
        
        Returns:
            {
                "resposta_ia": str,
                "confianca": float,
                "sugerir_ticket": bool
            }
        """
        pass
    
    async def responder_com_ia(
        self,
        mensagem: str,
        historico: List[Dict[str, Any]]
    ) -> Tuple[str, float]:
        """
        IA responde usando conhecimento do admin.
        Returns: (resposta, confianca)
        """
        pass
```

**Arquivo:** `apps/backend/app/services/tickets/ticket_service.py` (Modificação)

```python
class TicketService:
    # ... métodos existentes ...
    
    async def criar_ticket_com_anexos(
        self,
        cliente_id: int,
        categoria_id: int,
        assunto: str,
        descricao: str,
        anexos: List[UploadFile]
    ) -> Dict[str, Any]:
        """
        Cria ticket com até 10 anexos.
        Notifica admin.
        IA tenta responder automaticamente.
        """
        pass
    
    async def responder_ticket_ia(
        self,
        ticket_id: int
    ) -> Optional[str]:
        """
        IA tenta responder ticket.
        Returns resposta se confiança > 0.7, None caso contrário.
        """
        pass
```

**Endpoints:** `apps/backend/app/api/v1/chat_suporte.py`

```python
@router.post("/chat-suporte/mensagem")
async def enviar_mensagem_suporte(
    dados: MensagemSuporteRequest,
    current_user: Cliente = Depends(get_current_user)
):
    """Envia mensagem no chat suporte."""
    pass

@router.get("/chat-suporte/historico")
async def obter_historico_suporte(
    current_user: Cliente = Depends(get_current_user)
):
    """Retorna histórico do chat suporte."""
    pass
```

#### 3.1.7 Admin Usa Ferramenta (Nova Feature)

**Arquivo:** `apps/backend/app/services/admin/admin_cliente_service.py`

```python
class AdminClienteService:
    async def criar_cliente_admin(
        self,
        admin_id: int
    ) -> Dict[str, Any]:
        """
        Cria cliente especial vinculado ao admin.
        Status sempre ATIVO, sem cobrança.
        """
        pass
    
    async def obter_token_cliente_admin(
        self,
        admin_id: int
    ) -> str:
        """
        Gera JWT de cliente para o admin acessar ferramenta.
        """
        pass
```

**Endpoint:** `apps/backend/app/api/v1/admin/minha_ferramenta.py`

```python
@router.get("/admin/minha-ferramenta/acessar")
async def acessar_ferramenta(
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Retorna token de cliente para admin acessar ferramenta.
    """
    pass
```

#### 3.1.8 Dicas da IA (Nova Feature)

**Arquivo:** `apps/backend/app/services/dicas_ia/dicas_ia_service.py`

```python
class DicasIAService:
    async def gerar_dicas_diarias(
        self,
        admin_id: int
    ) -> Dict[str, Any]:
        """
        Analisa métricas e gera insights com IA.
        
        Returns:
            {
                "novos_clientes": [...],
                "clientes_cancelados": [...],
                "clientes_prestes_vencer": [...],
                "dicas_conversao": str,
                "sugestoes_roi": str,
                "percentual_anuncios": float,
                "analise_lucro": str,
                "progresso_objetivo": {
                    "objetivo_mensal": float,
                    "receita_atual": float,
                    "percentual": float,
                    "sugestoes": str
                }
            }
        """
        pass
    
    async def configurar_objetivo_mensal(
        self,
        admin_id: int,
        valor_objetivo: float
    ) -> Dict[str, Any]:
        """Configura objetivo mensal de receita."""
        pass
    
    async def deve_atualizar_dicas(
        self,
        admin_id: int
    ) -> bool:
        """Verifica se passaram 24h desde última atualização."""
        pass
```

**Endpoint:** `apps/backend/app/api/v1/admin/dicas_ia.py`

```python
@router.get("/admin/dicas-ia")
async def obter_dicas_ia(
    current_admin: Admin = Depends(get_current_admin)
):
    """Retorna dicas da IA (atualiza se necessário)."""
    pass

@router.post("/admin/dicas-ia/objetivo-mensal")
async def configurar_objetivo(
    dados: ObjetivoMensalRequest,
    current_admin: Admin = Depends(get_current_admin)
):
    """Configura objetivo mensal."""
    pass
```

#### 3.1.9 Billing (Melhorias)

**Arquivo:** `apps/backend/app/services/billing/billing_service.py` (Modificação)

```python
class BillingService:
    # ... métodos existentes ...
    
    async def criar_checkout_pix(
        self,
        cliente_id: int,
        plano: str  # "1_mes", "3_meses", "12_meses"
    ) -> Dict[str, Any]:
        """
        Cria checkout PIX no Stripe.
        
        Returns:
            {
                "qr_code": str,
                "qr_code_url": str,
                "valor": float,
                "expira_em": datetime
            }
        """
        pass
    
    async def processar_webhook_pix(
        self,
        evento: Dict[str, Any]
    ) -> None:
        """Processa confirmação de pagamento PIX."""
        pass
    
    async def calcular_valor_plano(
        self,
        plano: str
    ) -> float:
        """
        Calcula valor com desconto:
        - 1 mês: valor cheio
        - 3 meses: 10% desconto
        - 12 meses: 20% desconto
        """
        pass
    
    async def mudar_plano(
        self,
        cliente_id: int,
        novo_plano: str
    ) -> Dict[str, Any]:
        """
        Muda plano do cliente.
        Calcula crédito/débito proporcional.
        """
        pass
```

**Endpoint:** `apps/backend/app/api/v1/billing.py` (Modificação)

```python
@router.post("/billing/checkout-pix")
async def criar_checkout_pix(
    dados: CheckoutPIXRequest,
    current_user: Cliente = Depends(get_current_user)
):
    """Cria checkout PIX."""
    pass

@router.post("/billing/mudar-plano")
async def mudar_plano(
    dados: MudarPlanoRequest,
    current_user: Cliente = Depends(get_current_user)
):
    """Muda plano do cliente."""
    pass
```

#### 3.1.10 Bot WhatsApp (Melhorias)

**Arquivo:** `apps/backend/app/services/whatsapp/bot_service.py` (Modificação)

```python
class BotService:
    # ... métodos existentes ...
    
    async def processar_primeira_mensagem(
        self,
        numero_usuario: str,
        cliente_id: int
    ) -> str:
        """
        Verifica se é primeira interação.
        Se sim, pergunta nome do usuário.
        """
        pass
    
    async def salvar_nome_usuario(
        self,
        numero_usuario: str,
        cliente_id: int,
        nome: str
    ) -> None:
        """Salva nome do usuário no contexto."""
        pass
    
    async def obter_nome_usuario(
        self,
        numero_usuario: str,
        cliente_id: int
    ) -> Optional[str]:
        """Retorna nome do usuário se já capturado."""
        pass
```

### 3.2 Frontend Components

#### 3.2.1 Página Conversas (Nova)

**Arquivo:** `apps/frontend/app/dashboard/conversas/page.tsx`

```typescript
export default function ConversasPage() {
  // Lista conversas com filtros e paginação
  // Mostra histórico de mensagens ao clicar
  // Filtros: data início, data fim, status
  // Paginação: 20 por página
}
```

**Componentes:**
- `ConversasList`: Lista de conversas
- `ConversaCard`: Card individual de conversa
- `MensagensHistorico`: Histórico de mensagens
- `FiltrosConversas`: Filtros de data e status

#### 3.2.2 Página Conhecimento (Melhorias)

**Arquivo:** `apps/frontend/app/dashboard/conhecimento/page.tsx` (Modificação)

```typescript
export default function ConhecimentoPage() {
  // Adicionar modal de confirmação de senha ao salvar
  // Adicionar botão "Deixa que a IA te ajuda"
  // Corrigir exibição do contador de mensagens
}
```

**Novos Componentes:**
- `ModalConfirmacaoSenha`: Modal para validar senha
- `ModalMelhorarIA`: Modal para IA melhorar texto
- `ContadorMensagens`: Exibe contador corretamente

#### 3.2.3 Página Perfil (Melhorias)

**Arquivo:** `apps/frontend/app/dashboard/perfil/page.tsx` (Modificação)

```typescript
export default function PerfilPage() {
  // Adicionar botão "Editar Informações"
  // Adicionar formulário de edição
  // Adicionar modal de confirmação de senha
}
```

**Novos Componentes:**
- `FormularioEdicaoPerfil`: Formulário editável
- `ModalConfirmacaoEdicao`: Modal de confirmação

#### 3.2.4 Dashboard Home (Melhorias)

**Arquivo:** `apps/frontend/app/dashboard/page.tsx` (Modificação)

```typescript
export default function DashboardPage() {
  // Adicionar widget de assinatura no lado direito
}
```

**Novo Componente:**
- `WidgetAssinatura`: Widget com info de assinatura

#### 3.2.5 Página Agendamentos (Nova)

**Arquivo:** `apps/frontend/app/dashboard/agendamentos/page.tsx`

```typescript
export default function AgendamentosPage() {
  // Configurar horários disponíveis
  // Listar agendamentos pendentes
  // Aprovar/recusar agendamentos
  // Relatório de agendamentos do dia
}
```

**Componentes:**
- `ConfiguracaoHorarios`: Configurar slots
- `ListaAgendamentos`: Lista de agendamentos
- `CardAgendamento`: Card individual
- `RelatorioAgendamentos`: Relatório do dia

#### 3.2.6 Chat Suporte (Novo)

**Arquivo:** `apps/frontend/app/dashboard/components/ChatSuporte.tsx`

```typescript
export default function ChatSuporte() {
  // Widget flutuante de chat
  // IA responde automaticamente
  // Botão "Abrir Ticket" quando IA não sabe
  // Modal de criação de ticket com upload
}
```

**Componentes:**
- `ChatWidget`: Widget flutuante
- `ChatMensagens`: Lista de mensagens
- `ModalCriarTicket`: Modal de ticket

#### 3.2.7 Login (Redesign)

**Arquivo:** `apps/frontend/app/login/page.tsx` (Redesign completo)

```typescript
export default function LoginPage() {
  // Layout: metade foto, metade inputs
  // Foto/ilustração moderna
  // Inputs com ícones
  // Animações suaves
  // Loading state
  // Mensagens de erro amigáveis
}
```

#### 3.2.8 Admin - Minha Ferramenta

**Arquivo:** `apps/frontend/app/admin/minha-ferramenta/page.tsx`

```typescript
export default function MinhaFerramentaPage() {
  // Botão para acessar ferramenta como cliente
  // Redireciona para dashboard do cliente
  // Botão "Voltar para Admin" no dashboard
}
```

#### 3.2.9 Admin - Dicas da IA

**Arquivo:** `apps/frontend/app/admin/components/DicasIA.tsx`

```typescript
export default function DicasIA() {
  // Widget acima das estatísticas
  // Mostra insights diários
  // Configuração de objetivo mensal
  // Progresso do objetivo
}
```

---

## 4. Data Models

### 4.1 Novos Modelos

#### 4.1.1 Agendamentos

```python
class Agendamento(Base):
    __tablename__ = "agendamentos"
    
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    numero_usuario = Column(String(20))  # WhatsApp do usuário final
    data_hora = Column(DateTime)
    tipo_servico = Column(String(100))
    observacoes = Column(Text, nullable=True)
    status = Column(String(20))  # pendente, aprovado, recusado, concluido
    motivo_recusa = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
```

#### 4.1.2 Configuração de Horários

```python
class ConfiguracaoHorario(Base):
    __tablename__ = "configuracoes_horarios"
    
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    dia_semana = Column(String(20))  # segunda, terca, etc
    hora_inicio = Column(Time)
    hora_fim = Column(Time)
    duracao_slot = Column(Integer)  # minutos
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

#### 4.1.3 Chat Suporte

```python
class ChatSuporteMensagem(Base):
    __tablename__ = "chat_suporte_mensagens"
    
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    remetente_tipo = Column(String(20))  # cliente, ia, admin
    mensagem = Column(Text)
    confianca = Column(Float, nullable=True)  # só para IA
    created_at = Column(DateTime, default=datetime.utcnow)
```

#### 4.1.4 Dicas IA

```python
class DicasIA(Base):
    __tablename__ = "dicas_ia"
    
    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer, ForeignKey("admins.id"))
    conteudo = Column(JSON)  # todas as dicas em JSON
    objetivo_mensal = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

#### 4.1.5 Contexto Usuário WhatsApp

```python
class ContextoUsuarioWhatsApp(Base):
    __tablename__ = "contexto_usuarios_whatsapp"
    
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    numero_usuario = Column(String(20))
    nome = Column(String(100), nullable=True)
    primeira_interacao = Column(DateTime)
    ultima_interacao = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### 4.2 Modificações em Modelos Existentes

#### 4.2.1 Cliente

```python
class Cliente(Base):
    # ... campos existentes ...
    
    # Adicionar campo para cliente especial do admin
    eh_cliente_admin = Column(Boolean, default=False)
    admin_vinculado_id = Column(Integer, ForeignKey("admins.id"), nullable=True)
```

#### 4.2.2 Ticket

```python
class Ticket(Base):
    # ... campos existentes ...
    
    # Adicionar campo para resposta automática da IA
    resposta_ia = Column(Text, nullable=True)
    confianca_ia = Column(Float, nullable=True)
```

---

## 5. Correctness Properties

*Uma propriedade é uma característica ou comportamento que deve ser verdadeiro em todas as execuções válidas de um sistema - essencialmente, uma declaração formal sobre o que o sistema deve fazer. Propriedades servem como ponte entre especificações legíveis por humanos e garantias de corretude verificáveis por máquina.*

### 5.1 Propriedades de Conversas

**Property 1: Isolamento de conversas por cliente**  
*Para qualquer* cliente, a listagem de conversas deve retornar apenas conversas pertencentes a esse cliente, nunca de outros clientes.  
**Validates: Requirements 1.1**

**Property 2: Filtros de data funcionam corretamente**  
*Para qualquer* conjunto de conversas e filtros de data aplicados, apenas conversas dentro do intervalo especificado devem ser retornadas.  
**Validates: Requirements 1.1**

**Property 3: Paginação consistente**  
*Para qualquer* lista de conversas com mais de 20 itens, cada página deve conter exatamente 20 conversas (exceto a última página que pode ter menos).  
**Validates: Requirements 1.1**

**Property 4: Histórico completo de mensagens**  
*Para qualquer* conversa, todas as mensagens associadas devem ser retornadas no histórico, ordenadas cronologicamente.  
**Validates: Requirements 1.1**

### 5.2 Propriedades de Conhecimento

**Property 5: Contador monotônico**  
*Para qualquer* sequência de operações no sistema, o contador de mensagens nunca deve diminuir, apenas aumentar ou permanecer igual.  
**Validates: Requirements 1.2**

**Property 6: Salvar conhecimento não afeta contador**  
*Para qualquer* operação de salvar conhecimento, o contador de mensagens antes e depois deve ser idêntico.  
**Validates: Requirements 1.2**

**Property 7: Validação de senha obrigatória**  
*Para qualquer* tentativa de salvar conhecimento sem senha correta, a operação deve ser rejeitada e o conhecimento não deve ser alterado.  
**Validates: Requirements 2.1**

**Property 8: IA melhora texto**  
*Para qualquer* texto fornecido à IA para melhoria, o texto retornado deve ser estruturado e diferente do original.  
**Validates: Requirements 2.2**

### 5.3 Propriedades de Perfil

**Property 9: Email único**  
*Para qualquer* tentativa de alterar email para um já existente (de outro cliente), a operação deve ser rejeitada.  
**Validates: Requirements 1.3**

**Property 10: Confirmação de senha obrigatória**  
*Para qualquer* tentativa de editar perfil sem senha correta, a operação deve ser rejeitada.  
**Validates: Requirements 1.3**

**Property 11: Atualização imediata**  
*Para qualquer* edição de perfil bem-sucedida, os dados atualizados devem ser visíveis imediatamente na próxima consulta.  
**Validates: Requirements 1.3**

### 5.4 Propriedades de Assinatura

**Property 12: Cálculo preciso de dias restantes**  
*Para qualquer* assinatura ativa, o número de dias restantes deve ser calculado corretamente como (data_expiracao - data_atual).  
**Validates: Requirements 1.4**

**Property 13: Status correto da assinatura**  
*Para qualquer* assinatura, o status exibido deve corresponder ao estado real no banco de dados.  
**Validates: Requirements 1.4**

### 5.5 Propriedades de Tutoriais

**Property 14: Visibilidade global de tutoriais**  
*Para qualquer* tutorial criado pelo admin, todos os clientes ativos devem poder visualizá-lo.  
**Validates: Requirements 1.5**

**Property 15: Notificação de novos tutoriais**  
*Para qualquer* novo tutorial publicado, todos os clientes devem receber uma notificação.  
**Validates: Requirements 1.5**

**Property 16: Badge de tutorial não visualizado**  
*Para qualquer* tutorial não visualizado por um cliente, o badge "Novo" deve aparecer até que seja marcado como visualizado.  
**Validates: Requirements 1.5**

**Property 17: Marcar como visualizado persiste**  
*Para qualquer* tutorial marcado como visualizado por um cliente, o badge não deve reaparecer em consultas futuras.  
**Validates: Requirements 1.5**


### 5.6 Propriedades de Agendamentos

**Property 18: Persistência de configuração de horários**  
*Para qualquer* configuração de horários salva, ela deve ser recuperável em consultas futuras sem alterações.  
**Validates: Requirements 3.1**

**Property 19: Identificação de pedidos de agendamento**  
*Para qualquer* mensagem contendo intenção clara de agendamento, o bot deve identificá-la corretamente.  
**Validates: Requirements 3.1**

**Property 20: Criação automática de agendamento**  
*Para qualquer* pedido de agendamento válido identificado, um registro de agendamento deve ser criado com status "pendente".  
**Validates: Requirements 3.1**

**Property 21: Listagem completa de pendentes**  
*Para qualquer* cliente, todos os agendamentos com status "pendente" devem aparecer na listagem.  
**Validates: Requirements 3.1**

**Property 22: Mudança de status de agendamento**  
*Para qualquer* agendamento aprovado ou recusado, o status deve ser atualizado corretamente no banco de dados.  
**Validates: Requirements 3.1**

**Property 23: Notificação de mudança de status**  
*Para qualquer* mudança de status de agendamento (aprovado/recusado), uma notificação WhatsApp deve ser enviada ao usuário final.  
**Validates: Requirements 3.1**

### 5.7 Propriedades de Chat Suporte

**Property 24: IA responde primeiro**  
*Para qualquer* mensagem no chat suporte, a IA deve tentar responder antes de oferecer abrir ticket.  
**Validates: Requirements 3.2**

**Property 25: Escalação baseada em confiança**  
*Para qualquer* resposta da IA com confiança < 0.7, o sistema deve oferecer abrir ticket.  
**Validates: Requirements 3.2**

**Property 26: Notificação de novo ticket**  
*Para qualquer* ticket criado, o admin deve receber uma notificação.  
**Validates: Requirements 3.2**

### 5.8 Propriedades de Admin Usa Ferramenta

**Property 27: Cliente admin sempre ativo**  
*Para qualquer* cliente vinculado a um admin, o status deve sempre ser "ATIVO" independente de pagamentos.  
**Validates: Requirements 3.3**

**Property 28: IA responde automaticamente para admin**  
*Para qualquer* mensagem recebida pelo WhatsApp do admin, a IA deve tentar responder automaticamente.  
**Validates: Requirements 3.3**

**Property 29: Fallback para admin**  
*Para qualquer* mensagem com confiança < 0.5 no WhatsApp do admin, o sistema deve notificar o admin para resposta manual.  
**Validates: Requirements 3.3**

### 5.9 Propriedades de Dicas da IA

**Property 30: Atualização diária**  
*Para qualquer* login do admin após 24h da última atualização, as dicas devem ser regeneradas.  
**Validates: Requirements 3.4**

**Property 31: Dados reais nas dicas**  
*Para qualquer* dica gerada, os dados (novos clientes, cancelamentos, etc) devem corresponder aos dados reais do banco.  
**Validates: Requirements 3.4**

**Property 32: Cálculo de progresso do objetivo**  
*Para qualquer* objetivo mensal configurado, o percentual de progresso deve ser calculado como (receita_atual / objetivo_mensal) * 100.  
**Validates: Requirements 3.4**

### 5.10 Propriedades de Bot WhatsApp

**Property 33: Pergunta nome na primeira interação**  
*Para qualquer* usuário sem nome salvo no contexto, a primeira mensagem do bot deve perguntar o nome.  
**Validates: Requirements 4.2**

**Property 34: Persistência do nome**  
*Para qualquer* nome capturado, ele deve ser armazenado no contexto e recuperável em interações futuras.  
**Validates: Requirements 4.2**

**Property 35: Uso do nome nas respostas**  
*Para qualquer* resposta do bot após capturar o nome, o nome deve ser utilizado na mensagem.  
**Validates: Requirements 4.2**

**Property 36: Nome não perguntado novamente**  
*Para qualquer* usuário com nome já salvo, o bot não deve perguntar o nome novamente em conversas futuras.  
**Validates: Requirements 4.2**

### 5.11 Propriedades de Pagamento

**Property 37: Confirmação automática PIX**  
*Para qualquer* pagamento PIX confirmado pelo Stripe, o status da assinatura do cliente deve ser atualizado automaticamente.  
**Validates: Requirements 5.1**

**Property 38: Mudança de plano permitida**  
*Para qualquer* cliente com assinatura ativa, deve ser possível mudar para outro plano.  
**Validates: Requirements 5.2**

**Property 39: Cálculo proporcional correto**  
*Para qualquer* mudança de plano, o cálculo de crédito/débito proporcional deve considerar dias restantes e diferença de valor.  
**Validates: Requirements 5.2**

---

## 6. Error Handling

### 6.1 Estratégia Geral

Todas as operações devem seguir o padrão:
1. Validar entrada
2. Executar operação
3. Retornar resultado ou erro estruturado

### 6.2 Códigos de Erro

```python
class ErrorCodes:
    # Autenticação
    SENHA_INCORRETA = "AUTH_001"
    TOKEN_INVALIDO = "AUTH_002"
    
    # Validação
    EMAIL_JA_EXISTE = "VAL_001"
    DADOS_INVALIDOS = "VAL_002"
    LIMITE_EXCEDIDO = "VAL_003"
    
    # Negócio
    ASSINATURA_INATIVA = "BUS_001"
    AGENDAMENTO_NAO_ENCONTRADO = "BUS_002"
    HORARIO_INDISPONIVEL = "BUS_003"
    
    # Sistema
    ERRO_BANCO_DADOS = "SYS_001"
    ERRO_SERVICO_EXTERNO = "SYS_002"
    ERRO_IA = "SYS_003"
```

### 6.3 Tratamento por Componente

#### 6.3.1 Conversas
- **Conversa não encontrada**: Retornar 404 com mensagem clara
- **Acesso negado**: Retornar 403 se conversa não pertence ao cliente
- **Erro de paginação**: Validar página >= 1

#### 6.3.2 Conhecimento
- **Senha incorreta**: Retornar erro AUTH_001 sem salvar
- **Limite excedido**: Retornar erro VAL_003 (50k chars)
- **Erro IA**: Retornar erro SYS_003 com fallback

#### 6.3.3 Perfil
- **Email duplicado**: Retornar erro VAL_001
- **Senha incorreta**: Retornar erro AUTH_001
- **Dados inválidos**: Retornar erro VAL_002 com detalhes

#### 6.3.4 Agendamentos
- **Horário indisponível**: Retornar erro BUS_003
- **Agendamento não encontrado**: Retornar 404
- **Conflito de horário**: Retornar erro com sugestões

#### 6.3.5 Chat Suporte
- **Erro IA**: Fallback para "Desculpe, tive um problema. Pode reformular?"
- **Upload falhou**: Retornar erro com limite de tamanho
- **Ticket não criado**: Retornar erro SYS_001

#### 6.3.6 Pagamento
- **PIX expirado**: Retornar erro com opção de gerar novo
- **Webhook inválido**: Logar e ignorar (segurança)
- **Mudança de plano falhou**: Retornar erro com rollback

### 6.4 Logging

Todos os erros devem ser logados com:
- Timestamp
- Cliente ID (se aplicável)
- Endpoint/Função
- Código de erro
- Stack trace (se erro de sistema)
- Contexto adicional

---

## 7. Testing Strategy

### 7.1 Abordagem Dual de Testes

Este projeto utilizará **testes unitários** e **testes baseados em propriedades** de forma complementar:

- **Testes Unitários**: Verificam exemplos específicos, casos extremos e condições de erro
- **Testes de Propriedade**: Verificam propriedades universais através de múltiplas entradas geradas

Ambos são necessários para cobertura abrangente:
- Testes unitários capturam bugs concretos
- Testes de propriedade verificam corretude geral

### 7.2 Biblioteca de Property-Based Testing

**Backend (Python)**: Hypothesis  
**Frontend (TypeScript)**: fast-check

### 7.3 Configuração de Testes de Propriedade

Cada teste de propriedade deve:
- Executar **mínimo 100 iterações** (devido à randomização)
- Incluir tag de referência ao design
- Formato da tag: `# Feature: correcoes-e-melhorias, Property {número}: {texto}`

### 7.4 Estratégia por Componente

#### 7.4.1 Conversas

**Testes Unitários:**
- Página carrega sem erros (exemplo específico)
- Filtros com datas específicas retornam resultados esperados
- Paginação com 25 conversas retorna 2 páginas

**Testes de Propriedade:**
- Property 1: Isolamento de conversas por cliente
- Property 2: Filtros de data funcionam corretamente
- Property 3: Paginação consistente
- Property 4: Histórico completo de mensagens

#### 7.4.2 Conhecimento

**Testes Unitários:**
- Salvar com senha incorreta retorna erro específico
- Limite de 50k caracteres é respeitado
- IA melhora texto específico de exemplo

**Testes de Propriedade:**
- Property 5: Contador monotônico
- Property 6: Salvar conhecimento não afeta contador
- Property 7: Validação de senha obrigatória
- Property 8: IA melhora texto

#### 7.4.3 Perfil

**Testes Unitários:**
- Botão "Editar Informações" está visível
- Mensagem de sucesso aparece após salvar
- Email específico duplicado retorna erro

**Testes de Propriedade:**
- Property 9: Email único
- Property 10: Confirmação de senha obrigatória
- Property 11: Atualização imediata

#### 7.4.4 Assinatura

**Testes Unitários:**
- Widget aparece no lado direito
- Botão "Pagar mais um mês" aparece apenas para plano mensal

**Testes de Propriedade:**
- Property 12: Cálculo preciso de dias restantes
- Property 13: Status correto da assinatura

#### 7.4.5 Tutoriais

**Testes Unitários:**
- Tutorial criado aparece na lista
- Badge "Novo" aparece para tutorial não visualizado

**Testes de Propriedade:**
- Property 14: Visibilidade global de tutoriais
- Property 15: Notificação de novos tutoriais
- Property 16: Badge de tutorial não visualizado
- Property 17: Marcar como visualizado persiste

#### 7.4.6 Agendamentos

**Testes Unitários:**
- Configuração de horário específico é salva
- Agendamento específico é criado corretamente
- Notificação WhatsApp é enviada

**Testes de Propriedade:**
- Property 18: Persistência de configuração de horários
- Property 19: Identificação de pedidos de agendamento
- Property 20: Criação automática de agendamento
- Property 21: Listagem completa de pendentes
- Property 22: Mudança de status de agendamento
- Property 23: Notificação de mudança de status

#### 7.4.7 Chat Suporte

**Testes Unitários:**
- Modal de ticket abre corretamente
- Upload de arquivo funciona
- Admin recebe notificação

**Testes de Propriedade:**
- Property 24: IA responde primeiro
- Property 25: Escalação baseada em confiança
- Property 26: Notificação de novo ticket

#### 7.4.8 Admin Usa Ferramenta

**Testes Unitários:**
- QR Code é exibido
- Admin consegue conectar WhatsApp

**Testes de Propriedade:**
- Property 27: Cliente admin sempre ativo
- Property 28: IA responde automaticamente para admin
- Property 29: Fallback para admin

#### 7.4.9 Dicas da IA

**Testes Unitários:**
- Widget aparece acima das estatísticas
- Configuração de objetivo é salva

**Testes de Propriedade:**
- Property 30: Atualização diária
- Property 31: Dados reais nas dicas
- Property 32: Cálculo de progresso do objetivo

#### 7.4.10 Bot WhatsApp

**Testes Unitários:**
- Primeira mensagem é "Olá! Qual é o seu nome?"

**Testes de Propriedade:**
- Property 33: Pergunta nome na primeira interação
- Property 34: Persistência do nome
- Property 35: Uso do nome nas respostas
- Property 36: Nome não perguntado novamente

#### 7.4.11 Pagamento

**Testes Unitários:**
- Opção PIX aparece no checkout
- QR Code é gerado

**Testes de Propriedade:**
- Property 37: Confirmação automática PIX
- Property 38: Mudança de plano permitida
- Property 39: Cálculo proporcional correto

### 7.5 Testes de Integração

Além dos testes unitários e de propriedade, testes de integração devem cobrir:

1. **Fluxo completo de agendamento**:
   - Usuário envia mensagem → Bot identifica → Cria agendamento → Cliente aprova → Notificação enviada

2. **Fluxo completo de chat suporte**:
   - Cliente envia mensagem → IA responde → Confiança baixa → Oferece ticket → Ticket criado → Admin notificado

3. **Fluxo completo de pagamento PIX**:
   - Cliente escolhe PIX → QR Code gerado → Pagamento confirmado → Webhook recebido → Assinatura ativada

4. **Fluxo completo de admin usa ferramenta**:
   - Admin acessa ferramenta → Cliente especial criado → WhatsApp conectado → Mensagem recebida → IA responde

### 7.6 Testes de UI (Manual)

Alguns aspectos visuais devem ser testados manualmente:
- Layout responsivo em diferentes tamanhos de tela
- Animações suaves no login
- Posicionamento correto de widgets
- Contraste e legibilidade em diferentes temas

### 7.7 Ambiente de Testes

- **Banco de dados**: PostgreSQL de teste (separado de dev/prod)
- **Redis**: Instância de teste
- **ChromaDB**: Instância de teste
- **Evolution API**: Modo sandbox
- **OpenAI**: Usar mock ou API key de teste
- **Stripe**: Modo teste

### 7.8 Cobertura de Código

Meta de cobertura:
- **Backend**: Mínimo 80% de cobertura
- **Frontend**: Mínimo 70% de cobertura (componentes críticos)

Ferramentas:
- Backend: pytest-cov
- Frontend: Jest + React Testing Library

---

## 8. Implementation Notes

### 8.1 Ordem de Implementação Recomendada

Seguir a ordem de prioridades do requirements.md:

**Prioridade 1 - Correções Críticas:**
1. Conversas (1.1)
2. Conhecimento - Bug contador (1.2)
3. Perfil - Edição (1.3)
4. Assinatura - Widget (1.4)
5. Tutoriais - Sincronização (1.5)

**Prioridade 2 - Melhorias de Segurança:**
6. Conhecimento - Senha (2.1)
7. Conhecimento - IA ajuda (2.2)

**Prioridade 3 - Novas Funcionalidades:**
8. Agendamentos (3.1)
9. Chat Suporte (3.2)
10. Admin Usa Ferramenta (3.3)
11. Dicas da IA (3.4)

**Prioridade 4 - Melhorias de UX/UI:**
12. Login Redesign (4.1)
13. Bot Pergunta Nome (4.2)

**Prioridade 5 - Melhorias de Pagamento:**
14. PIX e Débito (5.1)
15. Múltiplos Planos (5.2)

**Prioridade 6 - Preparação para Produção:**
16. Checklist de Produção (6.1)

### 8.2 Migrações de Banco de Dados

Criar migrações Alembic para:
- Tabela `agendamentos`
- Tabela `configuracoes_horarios`
- Tabela `chat_suporte_mensagens`
- Tabela `dicas_ia`
- Tabela `contexto_usuarios_whatsapp`
- Adicionar campos em `clientes` (eh_cliente_admin, admin_vinculado_id)
- Adicionar campos em `tickets` (resposta_ia, confianca_ia)

### 8.3 Variáveis de Ambiente

Adicionar ao `.env`:
```
# Agendamentos
AGENDAMENTO_DURACAO_PADRAO=30

# Chat Suporte
CHAT_SUPORTE_CONFIANCA_MINIMA=0.7

# Dicas IA
DICAS_IA_INTERVALO_HORAS=24

# Bot WhatsApp
BOT_PERGUNTA_NOME=true

# Pagamento
STRIPE_PIX_ENABLED=true
STRIPE_DEBITO_ENABLED=true
PLANO_1_MES_VALOR=99.90
PLANO_3_MESES_DESCONTO=0.10
PLANO_12_MESES_DESCONTO=0.20
```

### 8.4 Dependências Adicionais

**Backend:**
```
# requirements.txt
hypothesis>=6.0.0  # Property-based testing
```

**Frontend:**
```json
// package.json
{
  "devDependencies": {
    "fast-check": "^3.0.0"
  }
}
```

### 8.5 Considerações de Performance

1. **Conversas**: Indexar `cliente_id` e `created_at` para filtros rápidos
2. **Agendamentos**: Indexar `cliente_id`, `data_hora` e `status`
3. **Chat Suporte**: Usar Redis para cache de histórico recente
4. **Dicas IA**: Cachear resultado por 24h no Redis
5. **Tutoriais**: Usar cache para lista de tutoriais ativos

### 8.6 Segurança

1. **Validação de senha**: Usar bcrypt para hash
2. **Rate limiting**: Limitar tentativas de login e salvamento de conhecimento
3. **Sanitização**: Sanitizar inputs antes de salvar no banco
4. **CORS**: Configurar CORS adequadamente para produção
5. **Webhooks**: Validar assinatura de webhooks (Stripe, Evolution)

### 8.7 Monitoramento

Adicionar logs estruturados para:
- Todas as operações de agendamento
- Respostas da IA (confiança baixa)
- Erros de pagamento
- Falhas de integração (Evolution, OpenAI, Stripe)
- Mudanças de plano

### 8.8 Documentação

Atualizar documentação:
- API docs (Swagger/OpenAPI)
- README com novas features
- Guia de uso para clientes
- Guia de administração

---

## 9. Checklist de Produção

### 9.1 Credenciais

- [ ] Criar admin com email e senha forte de produção
- [ ] Criar cliente teste com email secundário
- [ ] Remover credenciais de desenvolvimento

### 9.2 Produtos e Planos

- [ ] Configurar valores reais dos planos no Stripe
- [ ] Configurar descontos (3 meses: 10%, 12 meses: 20%)
- [ ] Testar checkout com valores reais

### 9.3 Integrações

- [ ] Stripe em modo produção
- [ ] SMTP real (SendGrid) configurado
- [ ] Evolution API em produção
- [ ] OpenAI API key de produção

### 9.4 Infraestrutura

- [ ] Domínio configurado
- [ ] SSL/HTTPS ativo
- [ ] Backups automáticos do PostgreSQL
- [ ] Monitoramento de uptime ativo

### 9.5 Variáveis de Ambiente

- [ ] Todas as variáveis de produção configuradas
- [ ] Secrets seguros (não commitados)
- [ ] JWT secrets fortes e únicos

### 9.6 Testes Finais

- [ ] Todos os testes passando
- [ ] Testes de integração executados
- [ ] Testes manuais de UI realizados
- [ ] Teste de carga básico realizado

### 9.7 Documentação

- [ ] README atualizado
- [ ] Guia de uso para clientes criado
- [ ] Documentação de API atualizada
- [ ] Runbook de operações criado

---

## 10. Conclusão

Este design document fornece a arquitetura técnica completa para implementar todas as correções e melhorias identificadas. A implementação deve seguir a ordem de prioridades, com testes adequados em cada etapa.

**Próximos Passos:**
1. Revisar e aprovar este design
2. Criar tasks.md com tarefas executáveis
3. Implementar por prioridade
4. Testar cada funcionalidade
5. Deploy em produção

---

**Aprovação:** Pendente  
**Próxima Revisão:** Após feedback do cliente

