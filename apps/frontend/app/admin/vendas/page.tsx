'use client'

import { useEffect, useState } from 'react'
import { DollarSign, TrendingUp, CreditCard, RefreshCw, Download } from 'lucide-react'

interface Transacao {
  id: string
  valor: number
  moeda: string
  status: string
  descricao: string
  cliente_id: number | null
  cliente_nome: string
  cliente_email: string
  data: string
  metodo_pagamento: string | null
  reembolsado: boolean
  valor_reembolsado: number
}

export default function VendasPage() {
  const [transacoes, setTransacoes] = useState<Transacao[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filtroStatus, setFiltroStatus] = useState('')
  const [dataInicio, setDataInicio] = useState('')
  const [dataFim, setDataFim] = useState('')

  const fetchTransacoes = async () => {
    try {
      setLoading(true)
      const token = localStorage.getItem('admin_token')
      
      let url = 'http://localhost:8000/api/v1/admin/vendas/transacoes?limite=100'
      if (filtroStatus) url += `&status=${filtroStatus}`
      if (dataInicio) url += `&data_inicio=${dataInicio}`
      if (dataFim) url += `&data_fim=${dataFim}`
      
      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (response.ok) {
        const data = await response.json()
        setTransacoes(data.transacoes || [])
        setError('')
      } else {
        setError('Erro ao carregar transações')
      }
    } catch (err) {
      setError('Erro ao conectar com o servidor')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTransacoes()
  }, [filtroStatus, dataInicio, dataFim])

  const handleReembolsar = async (chargeId: string) => {
    if (!confirm('Deseja realmente reembolsar esta transação?')) return

    try {
      const token = localStorage.getItem('admin_token')
      const response = await fetch(
        `http://localhost:8000/api/v1/admin/vendas/transacoes/${chargeId}/reembolsar`,
        {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        }
      )

      if (response.ok) {
        alert('Reembolso processado com sucesso!')
        fetchTransacoes()
      } else {
        alert('Erro ao processar reembolso')
      }
    } catch (err) {
      alert('Erro ao conectar com o servidor')
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'succeeded':
        return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400'
      case 'failed':
        return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'succeeded':
        return 'Aprovado'
      case 'pending':
        return 'Pendente'
      case 'failed':
        return 'Falhou'
      default:
        return status
    }
  }

  const calcularTotais = () => {
    const total = transacoes.reduce((acc, t) => acc + t.valor, 0)
    const aprovadas = transacoes.filter(t => t.status === 'succeeded').length
    const reembolsadas = transacoes.filter(t => t.reembolsado).length
    
    return { total, aprovadas, reembolsadas }
  }

  const totais = calcularTotais()

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Vendas e Transações</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Gerencie todas as transações e pagamentos</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={fetchTransacoes}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Atualizar
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 dark:bg-red-900/20 border border-red-400 text-red-700 dark:text-red-400 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Cards de Resumo */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total em Vendas</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                R$ {totais.total.toFixed(2)}
              </p>
            </div>
            <DollarSign className="w-10 h-10 text-green-600 dark:text-green-400" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Transações Aprovadas</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{totais.aprovadas}</p>
            </div>
            <TrendingUp className="w-10 h-10 text-blue-600 dark:text-blue-400" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Reembolsadas</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{totais.reembolsadas}</p>
            </div>
            <CreditCard className="w-10 h-10 text-orange-600 dark:text-orange-400" />
          </div>
        </div>
      </div>

      {/* Filtros */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Status
            </label>
            <select
              value={filtroStatus}
              onChange={(e) => setFiltroStatus(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="">Todos</option>
              <option value="succeeded">Aprovado</option>
              <option value="pending">Pendente</option>
              <option value="failed">Falhou</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Data Início
            </label>
            <input
              type="date"
              value={dataInicio}
              onChange={(e) => setDataInicio(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Data Fim
            </label>
            <input
              type="date"
              value={dataFim}
              onChange={(e) => setDataFim(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>
        </div>
      </div>

      {/* Tabela de Transações */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-900">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Data
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Cliente
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Descrição
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Valor
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Ações
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {transacoes.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-gray-500 dark:text-gray-400">
                    Nenhuma transação encontrada
                  </td>
                </tr>
              ) : (
                transacoes.map((transacao) => (
                  <tr key={transacao.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {new Date(transacao.data).toLocaleDateString('pt-BR')}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900 dark:text-white">
                      <div>
                        <div className="font-medium">{transacao.cliente_nome}</div>
                        <div className="text-gray-500 dark:text-gray-400 text-xs">{transacao.cliente_email}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900 dark:text-white">
                      {transacao.descricao}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                      {transacao.moeda} {transacao.valor.toFixed(2)}
                      {transacao.reembolsado && (
                        <div className="text-xs text-red-600 dark:text-red-400">
                          Reembolsado: {transacao.valor_reembolsado.toFixed(2)}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(transacao.status)}`}>
                        {getStatusText(transacao.status)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {transacao.status === 'succeeded' && !transacao.reembolsado && (
                        <button
                          onClick={() => handleReembolsar(transacao.id)}
                          className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300"
                        >
                          Reembolsar
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
