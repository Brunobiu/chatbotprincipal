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

export default function NotificationBell() {
  const router = useRouter()
  const [notificacoes, setNotificacoes] = useState<Notificacao[]>([])
  const [naoLidas, setNaoLidas] = useState(0)
  const [mostrarDropdown, setMostrarDropdown] = useState(false)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    carregarNaoLidas()
    
    // Atualizar a cada 30 segundos
    const interval = setInterval(carregarNaoLidas, 30000)
    return () => clearInterval(interval)
  }, [])

  const carregarNaoLidas = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      const res = await fetch('http://localhost:8000/api/v1/admin/notificacoes/nao-lidas/count', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (res.ok) {
        const data = await res.json()
        setNaoLidas(data.count)
      }
    } catch (error) {
      console.error('Erro ao carregar contagem:', error)
    }
  }

  const carregarNotificacoes = async () => {
    if (notificacoes.length > 0) return // Já carregou
    
    setLoading(true)
    try {
      const token = localStorage.getItem('admin_token')
      const res = await fetch('http://localhost:8000/api/v1/admin/notificacoes?limit=10', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (res.ok) {
        const data = await res.json()
        setNotificacoes(data.notificacoes)
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
      
      // Atualizar estado local
      setNotificacoes(prev => prev.map(n => 
        n.id === id ? { ...n, lida: true } : n
      ))
      setNaoLidas(prev => Math.max(0, prev - 1))
    } catch (error) {
      console.error('Erro ao marcar como lida:', error)
    }
  }

  const handleClickNotificacao = (notif: Notificacao) => {
    marcarComoLida(notif.id)
    setMostrarDropdown(false)
    
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

  const toggleDropdown = () => {
    if (!mostrarDropdown) {
      carregarNotificacoes()
    }
    setMostrarDropdown(!mostrarDropdown)
  }

  const getPrioridadeCor = (prioridade: string) => {
    switch (prioridade) {
      case 'urgente': return 'text-red-600'
      case 'alta': return 'text-orange-600'
      case 'normal': return 'text-blue-600'
      case 'baixa': return 'text-gray-600'
      default: return 'text-gray-600'
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
    <div className="relative">
      <button
        onClick={toggleDropdown}
        className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
        
        {naoLidas > 0 && (
          <span className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 bg-red-600 rounded-full">
            {naoLidas > 99 ? '99+' : naoLidas}
          </span>
        )}
      </button>

      {mostrarDropdown && (
        <>
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setMostrarDropdown(false)}
          />
          
          <div className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-xl border border-gray-200 z-20">
            <div className="p-4 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h3 className="font-semibold text-gray-900">Notificações</h3>
                {naoLidas > 0 && (
                  <span className="text-sm text-gray-500">{naoLidas} não lidas</span>
                )}
              </div>
            </div>

            <div className="max-h-96 overflow-y-auto">
              {loading ? (
                <div className="p-8 text-center text-gray-500">
                  Carregando...
                </div>
              ) : notificacoes.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  Nenhuma notificação
                </div>
              ) : (
                notificacoes.map((notif) => (
                  <div
                    key={notif.id}
                    onClick={() => handleClickNotificacao(notif)}
                    className={`p-4 border-b border-gray-100 hover:bg-gray-50 cursor-pointer transition-colors ${
                      !notif.lida ? 'bg-blue-50' : ''
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <span className="text-2xl">{getTipoIcone(notif.tipo)}</span>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <p className={`font-semibold text-sm ${getPrioridadeCor(notif.prioridade)}`}>
                            {notif.titulo}
                          </p>
                          {!notif.lida && (
                            <span className="w-2 h-2 bg-blue-600 rounded-full"></span>
                          )}
                        </div>
                        <p className="text-sm text-gray-600 mt-1">{notif.mensagem}</p>
                        <p className="text-xs text-gray-400 mt-1">
                          {new Date(notif.created_at).toLocaleString('pt-BR')}
                        </p>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>

            <div className="p-3 border-t border-gray-200 text-center">
              <button
                onClick={() => {
                  setMostrarDropdown(false)
                  router.push('/admin/notificacoes')
                }}
                className="text-sm text-blue-600 hover:text-blue-800 font-medium"
              >
                Ver todas as notificações
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
