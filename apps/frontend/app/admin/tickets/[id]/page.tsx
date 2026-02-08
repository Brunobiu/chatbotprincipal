'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter, useParams } from 'next/navigation'

interface Mensagem {
  id: number
  remetente_tipo: string
  remetente_id: number | null
  mensagem: string
  anexos: any[] | null
  lida: boolean
  created_at: string
}

interface Ticket {
  id: number
  cliente: {
    id: number
    nome: string
    email: string
  }
  assunto: string
  status: string
  prioridade: string
  categoria: {
    id: number
    nome: string
  } | null
  atribuido_admin: {
    id: number
    nome: string
  } | null
  ia_respondeu: boolean
  confianca_ia: number | null
  created_at: string
  updated_at: string
  resolvido_em: string | null
  mensagens: Mensagem[]
}

const STATUS_LABELS: Record<string, string> = {
  aberto: 'Aberto',
  em_andamento: 'Em Andamento',
  aguardando_cliente: 'Aguardando Cliente',
  resolvido: 'Resolvido',
  fechado: 'Fechado'
}

export default function TicketDetalhesPage() {
  const router = useRouter()
  const params = useParams()
  const ticketId = params.id as string
  
  const [ticket, setTicket] = useState<Ticket | null>(null)
  const [loading, setLoading] = useState(true)
  const [novaMensagem, setNovaMensagem] = useState('')
  const [enviando, setEnviando] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    carregarTicket()
    const interval = setInterval(carregarTicket, 5000) // Atualizar a cada 5s
    return () => clearInterval(interval)
  }, [ticketId])

  useEffect(() => {
    scrollToBottom()
  }, [ticket?.mensagens])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const carregarTicket = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      const res = await fetch(`http://localhost:8000/api/v1/admin/tickets/${ticketId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (res.ok) {
        const data = await res.json()
        setTicket(data)
      }
    } catch (error) {
      console.error('Erro ao carregar ticket:', error)
    } finally {
      setLoading(false)
    }
  }

  const enviarMensagem = async () => {
    if (!novaMensagem.trim()) return
    
    try {
      setEnviando(true)
      const token = localStorage.getItem('admin_token')
      const res = await fetch(`http://localhost:8000/api/v1/admin/tickets/${ticketId}/mensagens`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          mensagem: novaMensagem
        })
      })
      
      if (res.ok) {
        setNovaMensagem('')
        await carregarTicket()
      }
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error)
      alert('Erro ao enviar mensagem')
    } finally {
      setEnviando(false)
    }
  }

  const atualizarStatus = async (novoStatus: string) => {
    try {
      const token = localStorage.getItem('admin_token')
      const res = await fetch(`http://localhost:8000/api/v1/admin/tickets/${ticketId}/status`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          status: novoStatus
        })
      })
      
      if (res.ok) {
        await carregarTicket()
      }
    } catch (error) {
      console.error('Erro ao atualizar status:', error)
      alert('Erro ao atualizar status')
    }
  }

  const formatarData = (data: string) => {
    return new Date(data).toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="p-8">
        <div className="text-center text-gray-500">Carregando...</div>
      </div>
    )
  }

  if (!ticket) {
    return (
      <div className="p-8">
        <div className="text-center text-gray-500">Ticket não encontrado</div>
      </div>
    )
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => router.push('/admin/tickets')}
          className="text-blue-600 hover:text-blue-800 mb-4 flex items-center gap-2"
        >
          ← Voltar para Tickets
        </button>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Ticket #{ticket.id}</h1>
            <p className="text-gray-600 mt-2">{ticket.assunto}</p>
          </div>
          <div className="flex gap-2">
            {ticket.status !== 'resolvido' && (
              <button
                onClick={() => atualizarStatus('resolvido')}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                Marcar como Resolvido
              </button>
            )}
            {ticket.status === 'resolvido' && (
              <button
                onClick={() => atualizarStatus('fechado')}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
              >
                Fechar Ticket
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Informações do Ticket */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow p-6 space-y-4">
            <div>
              <div className="text-sm text-gray-600">Cliente</div>
              <div className="font-medium text-gray-900">{ticket.cliente.nome}</div>
              <div className="text-sm text-gray-500">{ticket.cliente.email}</div>
            </div>
            
            <div>
              <div className="text-sm text-gray-600">Status</div>
              <select
                value={ticket.status}
                onChange={(e) => atualizarStatus(e.target.value)}
                className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="aberto">Aberto</option>
                <option value="em_andamento">Em Andamento</option>
                <option value="aguardando_cliente">Aguardando Cliente</option>
                <option value="resolvido">Resolvido</option>
                <option value="fechado">Fechado</option>
              </select>
            </div>
            
            <div>
              <div className="text-sm text-gray-600">Categoria</div>
              <div className="font-medium text-gray-900">
                {ticket.categoria?.nome || 'Sem categoria'}
              </div>
            </div>
            
            <div>
              <div className="text-sm text-gray-600">Prioridade</div>
              <div className="font-medium text-gray-900 capitalize">{ticket.prioridade}</div>
            </div>
            
            {ticket.ia_respondeu && (
              <div>
                <div className="text-sm text-gray-600">IA Respondeu</div>
                <div className="font-medium text-green-600">
                  Sim (Confiança: {(ticket.confianca_ia! * 100).toFixed(0)}%)
                </div>
              </div>
            )}
            
            <div>
              <div className="text-sm text-gray-600">Criado em</div>
              <div className="font-medium text-gray-900">{formatarData(ticket.created_at)}</div>
            </div>
            
            {ticket.resolvido_em && (
              <div>
                <div className="text-sm text-gray-600">Resolvido em</div>
                <div className="font-medium text-gray-900">{formatarData(ticket.resolvido_em)}</div>
              </div>
            )}
          </div>
        </div>

        {/* Chat */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow flex flex-col h-[600px]">
            {/* Mensagens */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {ticket.mensagens.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.remetente_tipo === 'admin' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[70%] rounded-lg p-4 ${
                      msg.remetente_tipo === 'admin'
                        ? 'bg-blue-600 text-white'
                        : msg.remetente_tipo === 'ia'
                        ? 'bg-purple-100 text-purple-900'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    <div className="text-xs opacity-75 mb-1">
                      {msg.remetente_tipo === 'admin' ? 'Você (Admin)' : 
                       msg.remetente_tipo === 'ia' ? '🤖 IA' : 
                       ticket.cliente.nome}
                    </div>
                    <div className="whitespace-pre-wrap">{msg.mensagem}</div>
                    <div className="text-xs opacity-75 mt-2">
                      {formatarData(msg.created_at)}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* Input de Mensagem */}
            <div className="border-t border-gray-200 p-4">
              <div className="flex gap-2">
                <textarea
                  value={novaMensagem}
                  onChange={(e) => setNovaMensagem(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault()
                      enviarMensagem()
                    }
                  }}
                  placeholder="Digite sua resposta..."
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows={3}
                  disabled={enviando || ticket.status === 'fechado'}
                />
                <button
                  onClick={enviarMensagem}
                  disabled={enviando || !novaMensagem.trim() || ticket.status === 'fechado'}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {enviando ? 'Enviando...' : 'Enviar'}
                </button>
              </div>
              <div className="text-xs text-gray-500 mt-2">
                Pressione Enter para enviar, Shift+Enter para nova linha
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
