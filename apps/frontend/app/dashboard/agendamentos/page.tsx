'use client'

import { useState, useEffect } from 'react'

interface Agendamento {
  id: number
  numero_usuario: string
  nome_usuario: string | null
  data_hora: string
  tipo_servico: string | null
  observacoes: string | null
  status: string
  mensagem_original: string | null
  created_at: string
}

interface ConfiguracaoHorarios {
  id: number
  horarios_disponiveis: Record<string, Array<{inicio: string, fim: string}>>
  duracao_slot_minutos: number
  tipos_servico: string[] | null
}

export default function AgendamentosPage() {
  const [agendamentos, setAgendamentos] = useState<Agendamento[]>([])
  const [pendentes, setPendentes] = useState<Agendamento[]>([])
  const [configuracao, setConfiguracao] = useState<ConfiguracaoHorarios | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [abaSelecionada, setAbaSelecionada] = useState<'pendentes' | 'todos' | 'config'>('pendentes')
  
  // Estados para configuração
  const [editandoConfig, setEditandoConfig] = useState(false)
  const [duracaoSlot, setDuracaoSlot] = useState(30)
  const [tiposServico, setTiposServico] = useState('')
  const [horarios, setHorarios] = useState<Record<string, Array<{inicio: string, fim: string}>>>({
    segunda: [{inicio: '09:00', fim: '18:00'}],
    terca: [{inicio: '09:00', fim: '18:00'}],
    quarta: [{inicio: '09:00', fim: '18:00'}],
    quinta: [{inicio: '09:00', fim: '18:00'}],
    sexta: [{inicio: '09:00', fim: '18:00'}],
    sabado: [],
    domingo: []
  })
  
  useEffect(() => {
    carregarDados()
  }, [])
  
  const carregarDados = async () => {
    try {
      const token = localStorage.getItem('token')
      
      if (!token) {
        setError('Token não encontrado')
        return
      }
      
      // Carregar configuração
      const configResponse = await fetch('http://localhost:8000/api/v1/agendamentos/configuracao', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (configResponse.ok) {
        const configData = await configResponse.json()
        if (configData) {
          setConfiguracao(configData)
          setHorarios(configData.horarios_disponiveis)
          setDuracaoSlot(configData.duracao_slot_minutos)
          setTiposServico(configData.tipos_servico?.join(', ') || '')
        }
      }
      
      // Carregar pendentes
      const pendentesResponse = await fetch('http://localhost:8000/api/v1/agendamentos/pendentes', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (pendentesResponse.ok) {
        const pendentesData = await pendentesResponse.json()
        setPendentes(pendentesData)
      }
      
      // Carregar todos
      const todosResponse = await fetch('http://localhost:8000/api/v1/agendamentos/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (todosResponse.ok) {
        const todosData = await todosResponse.json()
        setAgendamentos(todosData)
      }
      
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }
  
  const salvarConfiguracao = async () => {
    try {
      const token = localStorage.getItem('token')
      
      const tiposArray = tiposServico.split(',').map(t => t.trim()).filter(t => t)
      
      const response = await fetch('http://localhost:8000/api/v1/agendamentos/configurar-horarios', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          horarios_disponiveis: horarios,
          duracao_slot_minutos: duracaoSlot,
          tipos_servico: tiposArray.length > 0 ? tiposArray : null
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        setConfiguracao(data)
        setEditandoConfig(false)
        alert('Configuração salva com sucesso!')
      } else {
        alert('Erro ao salvar configuração')
      }
    } catch (err) {
      alert('Erro ao salvar configuração')
    }
  }
  
  const aprovarAgendamento = async (id: number) => {
    try {
      const token = localStorage.getItem('token')
      
      const response = await fetch(`http://localhost:8000/api/v1/agendamentos/${id}/aprovar`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        alert('Agendamento aprovado! Notificação enviada ao cliente.')
        carregarDados()
      } else {
        alert('Erro ao aprovar agendamento')
      }
    } catch (err) {
      alert('Erro ao aprovar agendamento')
    }
  }
  
  const recusarAgendamento = async (id: number) => {
    try {
      const token = localStorage.getItem('token')
      
      const response = await fetch(`http://localhost:8000/api/v1/agendamentos/${id}/recusar`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        alert('Agendamento recusado! Notificação enviada ao cliente.')
        carregarDados()
      } else {
        alert('Erro ao recusar agendamento')
      }
    } catch (err) {
      alert('Erro ao recusar agendamento')
    }
  }
  
  const formatarDataHora = (dataHora: string) => {
    const date = new Date(dataHora)
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pendente':
        return 'bg-yellow-100 text-yellow-800'
      case 'aprovado':
        return 'bg-green-100 text-green-800'
      case 'recusado':
        return 'bg-red-100 text-red-800'
      case 'cancelado':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }
  
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Carregando agendamentos...</p>
        </div>
      </div>
    )
  }
  
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold text-gray-900">Agendamentos</h1>
        <p className="text-gray-600 mt-1">
          Gerencie agendamentos criados automaticamente pelo bot
        </p>
      </div>
      
      {/* Abas */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          <button
            onClick={() => setAbaSelecionada('pendentes')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              abaSelecionada === 'pendentes'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Pendentes ({pendentes.length})
          </button>
          <button
            onClick={() => setAbaSelecionada('todos')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              abaSelecionada === 'todos'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Todos ({agendamentos.length})
          </button>
          <button
            onClick={() => setAbaSelecionada('config')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              abaSelecionada === 'config'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Configuração
          </button>
        </nav>
      </div>
      
      {/* Conteúdo das Abas */}
      {abaSelecionada === 'pendentes' && (
        <div className="space-y-4">
          {pendentes.length === 0 ? (
            <div className="bg-white rounded-lg shadow p-8 text-center">
              <p className="text-gray-500">Nenhum agendamento pendente</p>
            </div>
          ) : (
            pendentes.map((agendamento) => (
              <div key={agendamento.id} className="bg-white rounded-lg shadow p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {agendamento.nome_usuario || agendamento.numero_usuario}
                      </h3>
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(agendamento.status)}`}>
                        {agendamento.status}
                      </span>
                    </div>
                    
                    <div className="space-y-1 text-sm text-gray-600">
                      <p>📅 {formatarDataHora(agendamento.data_hora)}</p>
                      {agendamento.tipo_servico && (
                        <p>🔧 {agendamento.tipo_servico}</p>
                      )}
                      {agendamento.observacoes && (
                        <p>📝 {agendamento.observacoes}</p>
                      )}
                      <p>📱 {agendamento.numero_usuario}</p>
                    </div>
                    
                    {agendamento.mensagem_original && (
                      <div className="mt-3 p-3 bg-gray-50 rounded text-sm text-gray-700">
                        <strong>Mensagem original:</strong> {agendamento.mensagem_original}
                      </div>
                    )}
                  </div>
                  
                  <div className="flex gap-2 ml-4">
                    <button
                      onClick={() => aprovarAgendamento(agendamento.id)}
                      className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                    >
                      ✓ Aprovar
                    </button>
                    <button
                      onClick={() => recusarAgendamento(agendamento.id)}
                      className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                    >
                      ✗ Recusar
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
      
      {abaSelecionada === 'todos' && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cliente</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Data/Hora</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Serviço</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {agendamentos.map((agendamento) => (
                <tr key={agendamento.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {agendamento.nome_usuario || agendamento.numero_usuario}
                    </div>
                    <div className="text-sm text-gray-500">{agendamento.numero_usuario}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatarDataHora(agendamento.data_hora)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {agendamento.tipo_servico || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(agendamento.status)}`}>
                      {agendamento.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      
      {abaSelecionada === 'config' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Configuração de Horários</h2>
          
          {!configuracao && !editandoConfig ? (
            <div className="text-center py-8">
              <p className="text-gray-600 mb-4">Você ainda não configurou seus horários de atendimento</p>
              <button
                onClick={() => setEditandoConfig(true)}
                className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Configurar Horários
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Duração de cada slot (minutos)
                </label>
                <input
                  type="number"
                  value={duracaoSlot}
                  onChange={(e) => setDuracaoSlot(parseInt(e.target.value))}
                  disabled={!editandoConfig}
                  className="w-full px-3 py-2 border rounded-lg disabled:bg-gray-100"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tipos de serviço (separados por vírgula)
                </label>
                <input
                  type="text"
                  value={tiposServico}
                  onChange={(e) => setTiposServico(e.target.value)}
                  disabled={!editandoConfig}
                  placeholder="Ex: consulta, banho, corte"
                  className="w-full px-3 py-2 border rounded-lg disabled:bg-gray-100"
                />
              </div>
              
              <div>
                <p className="text-sm font-medium text-gray-700 mb-3">Horários por dia da semana</p>
                <p className="text-xs text-gray-500 mb-4">
                  Configure os horários de atendimento. Deixe vazio para dias sem atendimento.
                </p>
                
                {Object.entries(horarios).map(([dia, slots]) => (
                  <div key={dia} className="mb-4 p-4 bg-gray-50 rounded-lg">
                    <h4 className="font-medium text-gray-900 mb-2 capitalize">{dia}</h4>
                    {slots.length === 0 ? (
                      <p className="text-sm text-gray-500">Sem atendimento</p>
                    ) : (
                      slots.map((slot, index) => (
                        <div key={index} className="flex gap-2 items-center mb-2">
                          <input
                            type="time"
                            value={slot.inicio}
                            disabled={!editandoConfig}
                            className="px-3 py-2 border rounded disabled:bg-gray-100"
                            readOnly
                          />
                          <span>até</span>
                          <input
                            type="time"
                            value={slot.fim}
                            disabled={!editandoConfig}
                            className="px-3 py-2 border rounded disabled:bg-gray-100"
                            readOnly
                          />
                        </div>
                      ))
                    )}
                  </div>
                ))}
              </div>
              
              <div className="flex gap-3">
                {editandoConfig ? (
                  <>
                    <button
                      onClick={salvarConfiguracao}
                      className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      Salvar Configuração
                    </button>
                    <button
                      onClick={() => {
                        setEditandoConfig(false)
                        if (configuracao) {
                          setHorarios(configuracao.horarios_disponiveis)
                          setDuracaoSlot(configuracao.duracao_slot_minutos)
                          setTiposServico(configuracao.tipos_servico?.join(', ') || '')
                        }
                      }}
                      className="px-6 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
                    >
                      Cancelar
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => setEditandoConfig(true)}
                    className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    Editar Configuração
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
