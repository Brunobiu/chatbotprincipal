'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'

interface ResumoGeral {
  periodo_dias: number
  tokens_total: number
  custo_total: number
  mensagens_total: number
  clientes_ativos: number
  custo_hoje: number
  custo_medio_por_mensagem: number
}

interface TopGastador {
  cliente_id: number
  nome: string
  email: string
  tokens_total: number
  custo_total: number
  mensagens_total: number
  custo_medio_por_mensagem: number
}

interface Alerta {
  cliente_id: number
  nome: string
  email: string
  custo_hoje: number
  tokens_hoje: number
  mensagens_hoje: number
  threshold: number
  percentual_acima: number
}

export default function UsoOpenAIPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [resumo, setResumo] = useState<ResumoGeral | null>(null)
  const [topGastadores, setTopGastadores] = useState<TopGastador[]>([])
  const [alertas, setAlertas] = useState<Alerta[]>([])
  const [periodo, setPeriodo] = useState(30)
  
  useEffect(() => {
    carregarDados()
  }, [periodo])
  
  const carregarDados = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      
      if (!token) {
        router.push('/admin/login')
        return
      }
      
      // Carregar resumo geral
      const resumoRes = await fetch(`http://localhost:8000/api/v1/admin/uso/resumo?dias=${periodo}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (resumoRes.ok) {
        const data = await resumoRes.json()
        setResumo(data)
      }
      
      // Carregar top gastadores
      const topRes = await fetch(`http://localhost:8000/api/v1/admin/uso/top-gastadores?limite=10&dias=${periodo}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (topRes.ok) {
        const data = await topRes.json()
        setTopGastadores(data)
      }
      
      // Carregar alertas
      const alertasRes = await fetch(`http://localhost:8000/api/v1/admin/uso/alertas`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (alertasRes.ok) {
        const data = await alertasRes.json()
        setAlertas(data)
      }
      
    } catch (err) {
      console.error('Erro ao carregar dados:', err)
    } finally {
      setLoading(false)
    }
  }
  
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'USD'
    }).format(value)
  }
  
  const formatNumber = (value: number) => {
    return new Intl.NumberFormat('pt-BR').format(value)
  }
  
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando dados de uso...</p>
        </div>
      </div>
    )
  }
  
  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">Monitoramento de Uso OpenAI</h1>
          <p className="text-gray-600 mt-1">Controle de custos e créditos</p>
        </div>
        
        <select
          value={periodo}
          onChange={(e) => setPeriodo(Number(e.target.value))}
          className="px-4 py-2 border rounded-lg"
        >
          <option value={7}>Últimos 7 dias</option>
          <option value={30}>Últimos 30 dias</option>
          <option value={90}>Últimos 90 dias</option>
        </select>
      </div>
      
      {/* Alertas */}
      {alertas.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <h3 className="font-semibold text-red-800 mb-2">⚠️ Alertas de Uso Excessivo</h3>
          <p className="text-sm text-red-700 mb-3">
            {alertas.length} cliente(s) ultrapassaram o limite de custo diário
          </p>
          <div className="space-y-2">
            {alertas.map((alerta) => (
              <div key={alerta.cliente_id} className="bg-white rounded p-3 flex justify-between items-center">
                <div>
                  <p className="font-medium text-gray-900">{alerta.nome}</p>
                  <p className="text-sm text-gray-600">{alerta.email}</p>
                </div>
                <div className="text-right">
                  <p className="font-bold text-red-600">{formatCurrency(alerta.custo_hoje)}</p>
                  <p className="text-xs text-gray-500">
                    {alerta.percentual_acima.toFixed(0)}% acima do limite
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Cards de Resumo */}
      {resumo && (
        <div className="grid grid-cols-4 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Custo Total</h3>
            <p className="text-3xl font-bold text-gray-900">{formatCurrency(resumo.custo_total)}</p>
            <p className="text-sm text-gray-500 mt-1">Últimos {resumo.periodo_dias} dias</p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Custo Hoje</h3>
            <p className="text-3xl font-bold text-blue-600">{formatCurrency(resumo.custo_hoje)}</p>
            <p className="text-sm text-gray-500 mt-1">Gasto do dia atual</p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Tokens Usados</h3>
            <p className="text-3xl font-bold text-gray-900">{formatNumber(resumo.tokens_total)}</p>
            <p className="text-sm text-gray-500 mt-1">{formatNumber(resumo.mensagens_total)} mensagens</p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Custo Médio</h3>
            <p className="text-3xl font-bold text-gray-900">{formatCurrency(resumo.custo_medio_por_mensagem)}</p>
            <p className="text-sm text-gray-500 mt-1">Por mensagem</p>
          </div>
        </div>
      )}
      
      {/* Top Gastadores */}
      <div className="bg-white rounded-lg shadow mb-6">
        <div className="px-6 py-4 border-b">
          <h2 className="text-xl font-semibold">Top 10 Clientes que Mais Gastam</h2>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  #
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Cliente
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tokens
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Mensagens
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Custo Total
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Custo/Msg
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Ações
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {topGastadores.map((cliente, index) => (
                <tr key={cliente.cliente_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {index + 1}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{cliente.nome}</div>
                      <div className="text-sm text-gray-500">{cliente.email}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                    {formatNumber(cliente.tokens_total)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                    {formatNumber(cliente.mensagens_total)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-bold text-gray-900">
                    {formatCurrency(cliente.custo_total)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-500">
                    {formatCurrency(cliente.custo_medio_por_mensagem)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => router.push(`/admin/clientes/${cliente.cliente_id}`)}
                      className="text-indigo-600 hover:text-indigo-900"
                    >
                      Ver Detalhes
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {topGastadores.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-500">Nenhum dado de uso disponível no período selecionado</p>
            </div>
          )}
        </div>
      </div>
      
      {/* Informações */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-semibold text-blue-900 mb-2">ℹ️ Sobre os Custos</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Os custos são estimados baseados nos preços da OpenAI</li>
          <li>• Valores em dólares (USD)</li>
          <li>• Threshold de alerta padrão: $10/dia por cliente</li>
          <li>• Tokens incluem prompt + completion</li>
        </ul>
      </div>
    </div>
  )
}
