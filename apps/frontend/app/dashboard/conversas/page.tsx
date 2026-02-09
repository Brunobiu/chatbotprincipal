'use client'

import { useEffect, useState } from 'react'

interface Conversa {
  id: number
  numero_whatsapp: string
  status: string
  motivo_fallback: string | null
  created_at: string
  updated_at: string
  ultima_mensagem: {
    conteudo: string
    remetente: string
    created_at: string
  } | null
}

interface Mensagem {
  id: number
  remetente: string
  conteudo: string
  tipo: string
  confidence_score: number | null
  fallback_triggered: boolean
  created_at: string
}

export default function ConversasPage() {
  const [conversas, setConversas] = useState<Conversa[]>([])
  const [loading, setLoading] = useState(true)
  const [pagina, setPagina] = useState(1)
  const [totalPaginas, setTotalPaginas] = useState(1)
  const [total, setTotal] = useState(0)
  
  // Filtros
  const [filtroDataInicio, setFiltroDataInicio] = useState('')
  const [filtroDataFim, setFiltroDataFim] = useState('')
  const [filtroStatus, setFiltroStatus] = useState('')
  
  // Modal de histórico
  const [conversaSelecionada, setConversaSelecionada] = useState<number | null>(null)
  const [mensagens, setMensagens] = useState<Mensagem[]>([])
  const [loadingMensagens, setLoadingMensagens] = useState(false)
  
  useEffect(() => {
    carregarConversas()
  }, [pagina, filtroDataInicio, filtroDataFim, filtroStatus])
  
  const carregarConversas = async () => {
    try {
      setLoading(true)
      const token = localStorage.getItem('token')
      
      // Montar query params
      const params = new URLSearchParams()
      params.append('pagina', pagina.toString())
      if (filtroDataInicio) params.append('filtro_data_inicio', filtroDataInicio)
      if (filtroDataFim) params.append('filtro_data_fim', filtroDataFim)
      if (filtroStatus) params.append('filtro_status', filtroStatus)
      
      const response = await fetch(`http://localhost:8000/api/v1/conversas?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setConversas(data.conversas)
        setTotal(data.total)
        setTotalPaginas(data.total_paginas)
      } else {
        console.error('Erro ao carregar conversas:', response.status)
      }
    } catch (err) {
      console.error('Erro ao carregar conversas:', err)
    } finally {
      setLoading(false)
    }
  }
  
  const carregarMensagens = async (conversaId: number) => {
    try {
      setLoadingMensagens(true)
      const token = localStorage.getItem('token')
      
      const response = await fetch(`http://localhost:8000/api/v1/conversas/${conversaId}/mensagens`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setMensagens(data.mensagens)
        setConversaSelecionada(conversaId)
      }
    } catch (err) {
      console.error('Erro ao carregar mensagens:', err)
    } finally {
      setLoadingMensagens(false)
    }
  }
  
  const limparFiltros = () => {
    setFiltroDataInicio('')
    setFiltroDataFim('')
    setFiltroStatus('')
    setPagina(1)
  }
  
  const formatarData = (dataStr: string) => {
    const data = new Date(dataStr)
    return data.toLocaleString('pt-BR')
  }
  
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ia_ativa': return 'bg-green-100 text-green-800'
      case 'aguardando_humano': return 'bg-yellow-100 text-yellow-800'
      case 'humano_respondeu': return 'bg-blue-100 text-blue-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }
  
  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'ia_ativa': return 'IA Ativa'
      case 'aguardando_humano': return 'Aguardando Humano'
      case 'humano_respondeu': return 'Humano Respondeu'
      default: return status
    }
  }
  
  if (loading && pagina === 1) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando conversas...</p>
        </div>
      </div>
    )
  }
  
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Conversas</h1>
      
      {/* Filtros */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <h2 className="text-lg font-semibold mb-4">Filtros</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Data Início</label>
            <input
              type="date"
              value={filtroDataInicio}
              onChange={(e) => {
                setFiltroDataInicio(e.target.value)
                setPagina(1)
              }}
              className="w-full px-3 py-2 border rounded"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Data Fim</label>
            <input
              type="date"
              value={filtroDataFim}
              onChange={(e) => {
                setFiltroDataFim(e.target.value)
                setPagina(1)
              }}
              className="w-full px-3 py-2 border rounded"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Status</label>
            <select
              value={filtroStatus}
              onChange={(e) => {
                setFiltroStatus(e.target.value)
                setPagina(1)
              }}
              className="w-full px-3 py-2 border rounded"
            >
              <option value="">Todos</option>
              <option value="ia_ativa">IA Ativa</option>
              <option value="aguardando_humano">Aguardando Humano</option>
              <option value="humano_respondeu">Humano Respondeu</option>
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={limparFiltros}
              className="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
            >
              Limpar Filtros
            </button>
          </div>
        </div>
      </div>
      
      {/* Lista de Conversas */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-4 border-b">
          <p className="text-sm text-gray-600">
            Total: {total} conversas | Página {pagina} de {totalPaginas}
          </p>
        </div>
        
        {conversas.length === 0 ? (
          <div className="p-12 text-center text-gray-500">
            <div className="text-6xl mb-4">💭</div>
            <p>Nenhuma conversa encontrada</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">WhatsApp</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Última Mensagem</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Data</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ações</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {conversas.map((conversa) => (
                  <tr key={conversa.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{conversa.numero_whatsapp}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(conversa.status)}`}>
                        {getStatusLabel(conversa.status)}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900 truncate max-w-xs">
                        {conversa.ultima_mensagem?.conteudo || 'Sem mensagens'}
                      </div>
                      <div className="text-xs text-gray-500">
                        {conversa.ultima_mensagem?.remetente}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatarData(conversa.created_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <button
                        onClick={() => carregarMensagens(conversa.id)}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        Ver Histórico
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        
        {/* Paginação */}
        {totalPaginas > 1 && (
          <div className="p-4 border-t flex justify-between items-center">
            <button
              onClick={() => setPagina(p => Math.max(1, p - 1))}
              disabled={pagina === 1}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Anterior
            </button>
            <span className="text-sm text-gray-600">
              Página {pagina} de {totalPaginas}
            </span>
            <button
              onClick={() => setPagina(p => Math.min(totalPaginas, p + 1))}
              disabled={pagina === totalPaginas}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Próxima
            </button>
          </div>
        )}
      </div>
      
      {/* Modal de Histórico */}
      {conversaSelecionada && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-3xl w-full max-h-[80vh] overflow-hidden flex flex-col">
            <div className="p-4 border-b flex justify-between items-center">
              <h2 className="text-xl font-semibold">Histórico de Mensagens</h2>
              <button
                onClick={() => {
                  setConversaSelecionada(null)
                  setMensagens([])
                }}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-4">
              {loadingMensagens ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
                </div>
              ) : mensagens.length === 0 ? (
                <p className="text-center text-gray-500 py-8">Nenhuma mensagem encontrada</p>
              ) : (
                <div className="space-y-4">
                  {mensagens.map((msg) => (
                    <div
                      key={msg.id}
                      className={`p-4 rounded-lg ${
                        msg.remetente === 'usuario' 
                          ? 'bg-blue-50 ml-8' 
                          : 'bg-gray-50 mr-8'
                      }`}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <span className="font-semibold text-sm">
                          {msg.remetente === 'usuario' ? '👤 Usuário' : '🤖 Bot'}
                        </span>
                        <span className="text-xs text-gray-500">
                          {formatarData(msg.created_at)}
                        </span>
                      </div>
                      <p className="text-sm text-gray-800">{msg.conteudo}</p>
                      {msg.confidence_score !== null && (
                        <div className="mt-2 text-xs text-gray-500">
                          Confiança: {(msg.confidence_score * 100).toFixed(0)}%
                          {msg.fallback_triggered && (
                            <span className="ml-2 text-yellow-600">⚠️ Fallback ativado</span>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
