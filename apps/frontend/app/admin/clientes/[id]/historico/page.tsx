'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface HistoricoCompleto {
  dados_cadastrais: any
  pagamentos: any
  conversas: any
  tickets: any
  uso_openai: any
  logins: any
  timeline: any[]
}

export default function HistoricoClientePage() {
  const router = useRouter()
  const params = useParams()
  const clienteId = params.id as string
  
  const [loading, setLoading] = useState(true)
  const [historico, setHistorico] = useState<HistoricoCompleto | null>(null)
  const [abaAtiva, setAbaAtiva] = useState('visao-geral')
  
  useEffect(() => {
    carregarHistorico()
  }, [clienteId])
  
  const carregarHistorico = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      
      if (!token) {
        router.push('/admin/login')
        return
      }
      
      const response = await fetch(`http://localhost:8000/api/v1/admin/clientes/${clienteId}/historico-completo`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setHistorico(data)
      } else if (response.status === 401) {
        router.push('/admin/login')
      }
    } catch (err) {
      console.error('Erro ao carregar histórico:', err)
    } finally {
      setLoading(false)
    }
  }
  
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value)
  }
  
  const getStatusBadge = (status: string) => {
    const badges: Record<string, string> = {
      ativo: 'bg-green-100 text-green-800',
      inativo: 'bg-gray-100 text-gray-800',
      pendente: 'bg-yellow-100 text-yellow-800',
      suspenso: 'bg-red-100 text-red-800',
      succeeded: 'bg-green-100 text-green-800',
      pending: 'bg-yellow-100 text-yellow-800',
      failed: 'bg-red-100 text-red-800',
      aberto: 'bg-blue-100 text-blue-800',
      resolvido: 'bg-green-100 text-green-800',
      ativa: 'bg-green-100 text-green-800',
      finalizada: 'bg-gray-100 text-gray-800'
    }
    
    return badges[status] || 'bg-gray-100 text-gray-800'
  }
  
  const getIconeTimeline = (tipo: string) => {
    const icones: Record<string, string> = {
      cadastro: '👤',
      pagamento: '💰',
      ticket: '🎫',
      login: '🔐'
    }
    
    return icones[tipo] || '📌'
  }
  
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando histórico...</p>
        </div>
      </div>
    )
  }
  
  if (!historico) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Histórico não encontrado</p>
        <button
          onClick={() => router.push('/admin/clientes')}
          className="mt-4 text-indigo-600 hover:text-indigo-900"
        >
          Voltar para lista
        </button>
      </div>
    )
  }
  
  const { dados_cadastrais, pagamentos, conversas, tickets, uso_openai, logins, timeline } = historico
  
  // Preparar dados para gráficos
  const dadosGraficoUso = uso_openai.uso_diario.map((u: any) => ({
    data: new Date(u.data).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }),
    tokens: u.tokens_total,
    custo: u.custo_estimado,
    mensagens: u.mensagens_processadas
  })).reverse()
  
  return (
    <div>
      <div className="mb-6">
        <button
          onClick={() => router.push(`/admin/clientes/${clienteId}`)}
          className="text-gray-600 hover:text-gray-900 mb-2 text-sm md:text-base"
        >
          ← Voltar para detalhes
        </button>
        <h1 className="text-2xl md:text-3xl font-bold">Histórico Completo</h1>
        <p className="text-gray-600 mt-1 text-sm md:text-base">{dados_cadastrais.nome} - {dados_cadastrais.email}</p>
      </div>
      
      {/* Abas */}
      <div className="border-b border-gray-200 mb-6 overflow-x-auto">
        <nav className="flex space-x-4 md:space-x-8 min-w-max px-1">
          {[
            { id: 'visao-geral', label: 'Visão Geral' },
            { id: 'pagamentos', label: 'Pagamentos' },
            { id: 'conversas', label: 'Conversas' },
            { id: 'tickets', label: 'Tickets' },
            { id: 'uso-creditos', label: 'Créditos' },
            { id: 'atividade', label: 'Atividade' }
          ].map((aba) => (
            <button
              key={aba.id}
              onClick={() => setAbaAtiva(aba.id)}
              className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${
                abaAtiva === aba.id
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {aba.label}
            </button>
          ))}
        </nav>
      </div>
      
      {/* Conteúdo das Abas */}
      {abaAtiva === 'visao-geral' && (
        <div className="space-y-6">
          {/* Cards de Resumo */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Total Gasto</h3>
              <p className="text-2xl font-bold">{formatCurrency(pagamentos.total_gasto)}</p>
              <p className="text-sm text-gray-500 mt-1">{pagamentos.total_transacoes} transações</p>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Conversas</h3>
              <p className="text-2xl font-bold">{conversas.total_conversas}</p>
              <p className="text-sm text-gray-500 mt-1">{conversas.total_mensagens} mensagens</p>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Tickets</h3>
              <p className="text-2xl font-bold">{tickets.total_tickets}</p>
              <p className="text-sm text-gray-500 mt-1">{tickets.tickets_abertos} abertos</p>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Uso OpenAI</h3>
              <p className="text-2xl font-bold">{formatCurrency(uso_openai.total_custo)}</p>
              <p className="text-sm text-gray-500 mt-1">{uso_openai.total_tokens.toLocaleString()} tokens</p>
            </div>
          </div>
          
          {/* Timeline */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Timeline de Eventos</h2>
            <div className="space-y-4">
              {timeline.slice(0, 20).map((evento, index) => (
                <div key={index} className="flex items-start gap-4 pb-4 border-b last:border-b-0">
                  <div className="text-2xl">{getIconeTimeline(evento.tipo)}</div>
                  <div className="flex-1">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-medium">{evento.titulo}</h3>
                        <p className="text-sm text-gray-600">{evento.descricao}</p>
                      </div>
                      <span className="text-sm text-gray-500">{formatDate(evento.data)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
      
      {abaAtiva === 'pagamentos' && (
        <div className="space-y-6">
          {/* Resumo */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Total Gasto</h3>
              <p className="text-2xl font-bold">{formatCurrency(pagamentos.total_gasto)}</p>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Transações</h3>
              <p className="text-2xl font-bold">{pagamentos.total_transacoes}</p>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Assinaturas</h3>
              <p className="text-2xl font-bold">{pagamentos.assinaturas.length}</p>
            </div>
          </div>
          
          {/* Assinaturas */}
          {pagamentos.assinaturas.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">Assinaturas</h2>
              <div className="space-y-4">
                {pagamentos.assinaturas.map((assinatura: any) => (
                  <div key={assinatura.id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadge(assinatura.status)}`}>
                          {assinatura.status}
                        </span>
                      </div>
                      <span className="text-lg font-bold">{formatCurrency(assinatura.valor)}/{assinatura.intervalo === 'month' ? 'mês' : 'ano'}</span>
                    </div>
                    <p className="text-sm text-gray-600">Início: {formatDate(assinatura.data_inicio)}</p>
                    {assinatura.proxima_cobranca && (
                      <p className="text-sm text-gray-600">Próxima cobrança: {formatDate(assinatura.proxima_cobranca)}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Transações */}
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="p-6 border-b">
              <h2 className="text-xl font-semibold">Transações</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Data</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Descrição</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Valor</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {pagamentos.transacoes.map((transacao: any) => (
                    <tr key={transacao.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">{formatDate(transacao.data)}</td>
                      <td className="px-6 py-4 text-sm">{transacao.descricao}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">{formatCurrency(transacao.valor)}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadge(transacao.status)}`}>
                          {transacao.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
      
      {abaAtiva === 'conversas' && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Total de Conversas</h3>
              <p className="text-2xl font-bold">{conversas.total_conversas}</p>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Total de Mensagens</h3>
              <p className="text-2xl font-bold">{conversas.total_mensagens}</p>
            </div>
          </div>
          
          <div className="space-y-4">
            {conversas.conversas.map((conversa: any) => (
              <div key={conversa.id} className="bg-white rounded-lg shadow p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="font-semibold text-lg">{conversa.numero_whatsapp}</h3>
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadge(conversa.status)}`}>
                      {conversa.status}
                    </span>
                  </div>
                  <span className="text-sm text-gray-500">{formatDate(conversa.ultima_mensagem_em)}</span>
                </div>
                
                <div className="space-y-2">
                  {conversa.mensagens.map((msg: any) => (
                    <div key={msg.id} className="border-l-4 border-gray-200 pl-4 py-2">
                      <div className="flex justify-between items-start mb-1">
                        <span className="text-xs font-medium text-gray-500">{msg.tipo}</span>
                        <span className="text-xs text-gray-400">{formatDate(msg.created_at)}</span>
                      </div>
                      <p className="text-sm text-gray-700">{msg.conteudo}</p>
                      {msg.confidence_score && (
                        <span className="text-xs text-gray-500">Confiança: {(msg.confidence_score * 100).toFixed(1)}%</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {abaAtiva === 'tickets' && (
        <div className="space-y-6">
          <div className="grid grid-cols-3 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Total</h3>
              <p className="text-2xl font-bold">{tickets.total_tickets}</p>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Abertos</h3>
              <p className="text-2xl font-bold text-blue-600">{tickets.tickets_abertos}</p>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Resolvidos</h3>
              <p className="text-2xl font-bold text-green-600">{tickets.tickets_resolvidos}</p>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Assunto</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Prioridade</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Mensagens</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Criado em</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {tickets.tickets.map((ticket: any) => (
                  <tr key={ticket.id}>
                    <td className="px-6 py-4 text-sm">{ticket.assunto}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadge(ticket.status)}`}>
                        {ticket.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">{ticket.prioridade}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">{ticket.total_mensagens}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">{formatDate(ticket.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
      
      {abaAtiva === 'uso-creditos' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Custo Total (30 dias)</h3>
              <p className="text-xl md:text-2xl font-bold">{formatCurrency(uso_openai.total_custo)}</p>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Tokens Usados</h3>
              <p className="text-xl md:text-2xl font-bold">{uso_openai.total_tokens.toLocaleString()}</p>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Mensagens Processadas</h3>
              <p className="text-xl md:text-2xl font-bold">{uso_openai.total_mensagens.toLocaleString()}</p>
            </div>
          </div>
          
          {/* Gráfico de Tokens */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Uso de Tokens (Últimos 30 dias)</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={dadosGraficoUso}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="data" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="tokens" stroke="#8884d8" name="Tokens" />
              </LineChart>
            </ResponsiveContainer>
          </div>
          
          {/* Gráfico de Custo */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Custo Diário (Últimos 30 dias)</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={dadosGraficoUso}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="data" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="custo" fill="#82ca9d" name="Custo (R$)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
      
      {abaAtiva === 'atividade' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Total de Logins (30 dias)</h3>
              <p className="text-xl md:text-2xl font-bold">{logins.total_logins}</p>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Último Login</h3>
              <p className="text-xl md:text-2xl font-bold">
                {dados_cadastrais.ultimo_login ? formatDate(dados_cadastrais.ultimo_login) : 'Nunca'}
              </p>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="p-6 border-b">
              <h2 className="text-xl font-semibold">Histórico de Logins</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Data/Hora</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">IP</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User Agent</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {logins.logins.map((login: any, index: number) => (
                    <tr key={index}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">{formatDate(login.data)}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-mono">{login.ip}</td>
                      <td className="px-6 py-4 text-sm text-gray-500">{login.user_agent || 'N/A'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
