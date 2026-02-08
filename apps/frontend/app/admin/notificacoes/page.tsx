'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

interface Notificacao {
  id: number
  tipo: string
  titulo: string
  mensagem: string
  prioridade: string
  lida: boolean
  data: any
  created_at: string
}

export default function NotificacoesPage() {
  const router = useRouter()
  const [notificacoes, setNotificacoes] = useState<Notificacao[]>([])
  const [total, setTotal] = useState(0)
  const [naoLidas, setNaoLidas] = useState(0)
  const [loading, setLoading] = useState(true)
  const [filtro, setFiltro] = useState<'todas' | 'nao-lidas'>('todas')

  useEffect(() => {
    carregarNotificacoes()
  }, [filtro])

  const carregarNotificacoes = async () => {
    setLoading(true)
    try {
      const token = localStorage.getItem('admin_token')
      const url = filtro === 'nao-lidas' 
        ? 'http://localhost:8000/api/v1/admin/notificacoes?apenas_nao_lidas=true&limit=100'
        : 'http://localhost:8000/api/v1/admin/notificacoes?limit=100'
      
      const res = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (res.ok) {
        const data = await res.json()
        setNotificacoes(data.notificacoes)
        setTotal(data.total)
        setNaoLidas(data.nao_lidas)
      }
    } catch (error) {
      console.error('Erro ao carregar notificações:', error)
    } finally {
      setLoading(false)
    }
  }

  const marcarComoLida = async (id: number) => {
    try {
      const token = localStorage.getItem('admin_token')
      await fetch(`http://localhost:8000/api/v1/admin/notificacoes/${id}/ler`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      setNotificacoes(prev => prev.map(n => 
        n.id === id ? { ...n, lida: true } : n
      ))
      setNaoLidas(prev => Math.max(0, prev - 1))
    } catch (error) {
      console.error('Erro ao marcar como lida:', error)
    }
  }

  const marcarTodasComoLidas = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      await fetch('http://localhost:8000/api/v1/admin/notificacoes/ler-todas', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      setNotificacoes(prev => prev.map(n => ({ ...n, lida: true })))
      setNaoLidas(0)
    } catch (error) {
      console.error('Erro ao marcar todas como lidas:', error)
    }
  }

  const handleClickNotificacao = (notif: Notificacao) => {
    if (!notif.lida) {
      marcarComoLida(notif.id)
    }
    
    // Redirecionar baseado no tipo
    if (notif.tipo === 'novo_ticket' && notif.data.ticket_id) {
      router.push(`/admin/tickets/${notif.data.ticket_id}`)
    } else if (notif.tipo === 'novo_cliente' && notif.data.cliente_id) {
      router.push(`/admin/clientes/${notif.data.cliente_id}`)
    } else if (notif.tipo === 'tentativa_invasao') {
      router.push('/admin/seguranca')
    } else if (notif.tipo === 'alto_uso_openai' && notif.data.cliente_id) {
      router.push(`/admin/clientes/${notif.data.cliente_id}`)
    }
  }

  const getPrioridadeCor = (prioridade: string) => {
    switch (prioridade) {
      case 'urgente': return 'bg-red-100 text-red-800 border-red-200'
      case 'alta': return 'bg-orange-100 text-orange-800 border-orange-200'
      case 'normal': return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'baixa': return 'bg-gray-100 text-gray-800 border-gray-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getTipoIcone = (tipo: string) => {
    switch (tipo) {
      case 'novo_cliente': return '👤'
      case 'novo_ticket': return '🎫'
      case 'pagamento_recusado': return '💳'
      case 'plano_expirado': return '⏰'
      case 'alto_uso_openai': return '📊'
      case 'tentativa_invasao': return '🚨'
      default: return '📢'
    }
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">📢 Notificações</h1>
        <p className="text-gray-600 mt-2">
          {naoLidas > 0 ? `${naoLidas} notificações não lidas` : 'Todas as notificações lidas'}
        </p>
      </div>

      {/* Filtros e Ações */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex justify-between items-center">
          <div className="flex gap-2">
            <button
              onClick={() => setFiltro('todas')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filtro === 'todas'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Todas ({total})
            </button>
            <button
              onClick={() => setFiltro('nao-lidas')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filtro === 'nao-lidas'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Não Lidas ({naoLidas})
            </button>
          </div>

          {naoLidas > 0 && (
            <button
              onClick={marcarTodasComoLidas}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              Marcar Todas como Lidas
            </button>
          )}
        </div>
      </div>

      {/* Lista de Notificações */}
      <div className="bg-white rounded-lg shadow">
        {loading ? (
          <div className="p-12 text-center text-gray-500">
            Carregando notificações...
          </div>
        ) : notificacoes.length === 0 ? (
          <div className="p-12 text-center text-gray-500">
            {filtro === 'nao-lidas' ? 'Nenhuma notificação não lida' : 'Nenhuma notificação'}
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {notificacoes.map((notif) => (
              <div
                key={notif.id}
                onClick={() => handleClickNotificacao(notif)}
                className={`p-6 hover:bg-gray-50 cursor-pointer transition-colors ${
                  !notif.lida ? 'bg-blue-50' : ''
                }`}
              >
                <div className="flex items-start gap-4">
                  <span className="text-4xl">{getTipoIcone(notif.tipo)}</span>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-semibold text-lg text-gray-900">
                        {notif.titulo}
                      </h3>
                      {!notif.lida && (
                        <span className="w-3 h-3 bg-blue-600 rounded-full"></span>
                      )}
                      <span className={`px-3 py-1 text-xs font-semibold rounded-full border ${getPrioridadeCor(notif.prioridade)}`}>
                        {notif.prioridade.toUpperCase()}
                      </span>
                    </div>
                    
                    <p className="text-gray-700 mb-2">{notif.mensagem}</p>
                    
                    <p className="text-sm text-gray-500">
                      {new Date(notif.created_at).toLocaleString('pt-BR', {
                        day: '2-digit',
                        month: '2-digit',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
