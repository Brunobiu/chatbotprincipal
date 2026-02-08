'use client'

import { useState } from 'react'

type TipoRelatorio = 'geral' | 'clientes' | 'uso-openai' | 'tickets' | 'conversas'

export default function RelatoriosAdminPage() {
  const [tipoRelatorio, setTipoRelatorio] = useState<TipoRelatorio>('geral')
  const [dataInicio, setDataInicio] = useState('')
  const [dataFim, setDataFim] = useState('')
  const [relatorio, setRelatorio] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const gerarRelatorio = async () => {
    try {
      setLoading(true)
      const token = localStorage.getItem('admin_token')
      
      const params = new URLSearchParams()
      if (dataInicio) params.append('data_inicio', new Date(dataInicio).toISOString())
      if (dataFim) params.append('data_fim', new Date(dataFim).toISOString())
      
      const res = await fetch(`http://localhost:8000/api/v1/admin/relatorios/${tipoRelatorio}?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (res.ok) {
        const data = await res.json()
        setRelatorio(data)
      } else {
        alert('Erro ao gerar relatório')
      }
    } catch (error) {
      console.error('Erro ao gerar relatório:', error)
      alert('Erro ao gerar relatório')
    } finally {
      setLoading(false)
    }
  }

  const exportarJSON = () => {
    if (!relatorio) return
    
    const dataStr = JSON.stringify(relatorio, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `relatorio-${tipoRelatorio}-${new Date().toISOString()}.json`
    link.click()
  }

  const exportarCSV = () => {
    if (!relatorio) return
    
    let csv = ''
    
    // Cabeçalho baseado no tipo de relatório
    if (tipoRelatorio === 'clientes' && relatorio.clientes) {
      csv = 'ID,Nome,Email,Status,Criado Em,Último Login,Total Mensagens\n'
      relatorio.clientes.forEach((c: any) => {
        csv += `${c.id},"${c.nome}","${c.email}",${c.status},${c.created_at},${c.ultimo_login || ''},${c.total_mensagens}\n`
      })
    } else if (tipoRelatorio === 'uso-openai' && relatorio.registros) {
      csv = 'Cliente ID,Data,Tokens Total,Custo,Mensagens,Modelo\n'
      relatorio.registros.forEach((r: any) => {
        csv += `${r.cliente_id},${r.data},${r.tokens_total},${r.custo_estimado},${r.mensagens_processadas},${r.modelo}\n`
      })
    } else if (tipoRelatorio === 'tickets' && relatorio.tickets) {
      csv = 'ID,Cliente ID,Assunto,Status,Categoria,IA Respondeu,Criado Em\n'
      relatorio.tickets.forEach((t: any) => {
        csv += `${t.id},${t.cliente_id},"${t.assunto}",${t.status},${t.categoria || ''},${t.ia_respondeu},${t.created_at}\n`
      })
    }
    
    const dataBlob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `relatorio-${tipoRelatorio}-${new Date().toISOString()}.csv`
    link.click()
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">📈 Relatórios</h1>
        <p className="text-gray-600 mt-2">Gere relatórios detalhados do sistema</p>
      </div>

      {/* Filtros */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tipo de Relatório
            </label>
            <select
              value={tipoRelatorio}
              onChange={(e) => setTipoRelatorio(e.target.value as TipoRelatorio)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="geral">Relatório Geral</option>
              <option value="clientes">Clientes</option>
              <option value="uso-openai">Uso OpenAI</option>
              <option value="tickets">Tickets</option>
              <option value="conversas">Conversas</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Data Início
            </label>
            <input
              type="date"
              value={dataInicio}
              onChange={(e) => setDataInicio(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Data Fim
            </label>
            <input
              type="date"
              value={dataFim}
              onChange={(e) => setDataFim(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        
        <div className="flex gap-3">
          <button
            onClick={gerarRelatorio}
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Gerando...' : 'Gerar Relatório'}
          </button>
          
          {relatorio && (
            <>
              <button
                onClick={exportarJSON}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                Exportar JSON
              </button>
              <button
                onClick={exportarCSV}
                className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
              >
                Exportar CSV
              </button>
            </>
          )}
        </div>
      </div>

      {/* Resultado */}
      {relatorio && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-bold mb-4">Resultado do Relatório</h2>
          
          {/* Relatório Geral */}
          {tipoRelatorio === 'geral' && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Total de Clientes</div>
                <div className="text-2xl font-bold text-blue-600">{relatorio.clientes.total}</div>
                <div className="text-sm text-gray-500">Ativos: {relatorio.clientes.ativos}</div>
              </div>
              
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Custo OpenAI</div>
                <div className="text-2xl font-bold text-green-600">${relatorio.uso_openai.custo_total}</div>
              </div>
              
              <div className="bg-purple-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Total de Tickets</div>
                <div className="text-2xl font-bold text-purple-600">{relatorio.tickets.total}</div>
                <div className="text-sm text-gray-500">Taxa Resolução: {relatorio.tickets.taxa_resolucao}%</div>
              </div>
              
              <div className="bg-orange-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Total de Conversas</div>
                <div className="text-2xl font-bold text-orange-600">{relatorio.conversas.total}</div>
              </div>
            </div>
          )}
          
          {/* Relatório de Clientes */}
          {tipoRelatorio === 'clientes' && (
            <div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="text-sm text-gray-600">Total</div>
                  <div className="text-2xl font-bold text-blue-600">{relatorio.total}</div>
                </div>
                {Object.entries(relatorio.por_status).map(([status, count]: [string, any]) => (
                  <div key={status} className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600 capitalize">{status}</div>
                    <div className="text-2xl font-bold text-gray-900">{count}</div>
                  </div>
                ))}
              </div>
              
              <div className="text-sm text-gray-600 mb-2">
                {relatorio.clientes.length} clientes encontrados
              </div>
            </div>
          )}
          
          {/* Relatório de Uso OpenAI */}
          {tipoRelatorio === 'uso-openai' && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Total de Tokens</div>
                <div className="text-2xl font-bold text-blue-600">{relatorio.total_tokens.toLocaleString()}</div>
              </div>
              
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Custo Total</div>
                <div className="text-2xl font-bold text-green-600">${relatorio.total_custo}</div>
              </div>
              
              <div className="bg-purple-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Mensagens Processadas</div>
                <div className="text-2xl font-bold text-purple-600">{relatorio.total_mensagens}</div>
              </div>
            </div>
          )}
          
          {/* Relatório de Tickets */}
          {tipoRelatorio === 'tickets' && (
            <div>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="text-sm text-gray-600">Total</div>
                  <div className="text-2xl font-bold text-blue-600">{relatorio.total}</div>
                </div>
                
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="text-sm text-gray-600">IA Respondeu</div>
                  <div className="text-2xl font-bold text-green-600">{relatorio.ia_respondeu}</div>
                  <div className="text-sm text-gray-500">{relatorio.taxa_ia}%</div>
                </div>
                
                {Object.entries(relatorio.por_status).slice(0, 2).map(([status, count]: [string, any]) => (
                  <div key={status} className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600 capitalize">{status}</div>
                    <div className="text-2xl font-bold text-gray-900">{count}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Relatório de Conversas */}
          {tipoRelatorio === 'conversas' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Total de Conversas</div>
                <div className="text-2xl font-bold text-blue-600">{relatorio.total_conversas}</div>
              </div>
              
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Total de Mensagens</div>
                <div className="text-2xl font-bold text-green-600">{relatorio.total_mensagens}</div>
              </div>
            </div>
          )}
          
          {/* JSON Raw */}
          <details className="mt-6">
            <summary className="cursor-pointer text-sm text-gray-600 hover:text-gray-900">
              Ver dados completos (JSON)
            </summary>
            <pre className="mt-4 p-4 bg-gray-50 rounded-lg overflow-auto text-xs">
              {JSON.stringify(relatorio, null, 2)}
            </pre>
          </details>
        </div>
      )}
    </div>
  )
}
