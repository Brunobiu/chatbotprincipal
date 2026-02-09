'use client'

import { useEffect, useState } from 'react'

interface Dicas {
  resumo: string
  dicas_conversao: string[]
  sugestoes_roi: string[]
  percentual_anuncios: number
  analise_lucro: string
  progresso_objetivo: number
  metricas: {
    total_clientes: number
    clientes_ativos: number
    novos_clientes: Array<{ nome: string; email: string; data: string }>
    cancelados: Array<{ nome: string; email: string; data: string }>
  }
}

export default function WidgetDicasIA() {
  const [loading, setLoading] = useState(true)
  const [dicas, setDicas] = useState<Dicas | null>(null)
  const [objetivoMensal, setObjetivoMensal] = useState<number | null>(null)
  const [editandoObjetivo, setEditandoObjetivo] = useState(false)
  const [novoObjetivo, setNovoObjetivo] = useState('')
  
  useEffect(() => {
    carregarDicas()
  }, [])
  
  const carregarDicas = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      
      if (!token) {
        return
      }
      
      const response = await fetch('http://localhost:8000/api/v1/admin/dicas-ia', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setDicas(data.conteudo)
        setObjetivoMensal(data.objetivo_mensal)
      }
    } catch (err) {
      console.error('Erro ao carregar dicas:', err)
    } finally {
      setLoading(false)
    }
  }
  
  const salvarObjetivo = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      const valor = parseFloat(novoObjetivo)
      
      if (isNaN(valor) || valor <= 0) {
        alert('Digite um valor válido')
        return
      }
      
      const response = await fetch('http://localhost:8000/api/v1/admin/dicas-ia/objetivo-mensal', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          objetivo: valor
        })
      })
      
      if (response.ok) {
        setObjetivoMensal(valor)
        setEditandoObjetivo(false)
        setNovoObjetivo('')
        // Recarregar dicas para atualizar progresso
        carregarDicas()
      }
    } catch (err) {
      console.error('Erro ao salvar objetivo:', err)
    }
  }
  
  if (loading) {
    return (
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg shadow p-6 mb-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
        </div>
      </div>
    )
  }
  
  if (!dicas) {
    return null
  }
  
  return (
    <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg shadow p-6 mb-6 border border-purple-200">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-3xl">🤖</span>
        <h2 className="text-2xl font-bold text-gray-900">Dicas da IA</h2>
      </div>
      
      {/* Resumo */}
      <div className="bg-white rounded-lg p-4 mb-4">
        <p className="text-gray-700 font-medium">{dicas.resumo}</p>
      </div>
      
      {/* Grid de Métricas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        {/* Novos Clientes */}
        <div className="bg-white rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">👥</span>
            <h3 className="font-semibold text-gray-900">Novos Clientes</h3>
          </div>
          <p className="text-3xl font-bold text-green-600">{dicas.metricas.novos_clientes.length}</p>
          {dicas.metricas.novos_clientes.length > 0 && (
            <div className="mt-2 text-sm text-gray-600">
              <p className="font-medium">Últimos:</p>
              {dicas.metricas.novos_clientes.slice(0, 3).map((c, i) => (
                <p key={i} className="truncate">• {c.nome} ({c.data})</p>
              ))}
            </div>
          )}
        </div>
        
        {/* Cancelamentos */}
        <div className="bg-white rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">❌</span>
            <h3 className="font-semibold text-gray-900">Cancelamentos</h3>
          </div>
          <p className="text-3xl font-bold text-red-600">{dicas.metricas.cancelados.length}</p>
          {dicas.metricas.cancelados.length > 0 && (
            <div className="mt-2 text-sm text-gray-600">
              <p className="font-medium">Últimos:</p>
              {dicas.metricas.cancelados.slice(0, 3).map((c, i) => (
                <p key={i} className="truncate">• {c.nome} ({c.data})</p>
              ))}
            </div>
          )}
        </div>
        
        {/* Clientes Ativos */}
        <div className="bg-white rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">✅</span>
            <h3 className="font-semibold text-gray-900">Clientes Ativos</h3>
          </div>
          <p className="text-3xl font-bold text-blue-600">{dicas.metricas.clientes_ativos}</p>
          <p className="text-sm text-gray-600 mt-2">
            de {dicas.metricas.total_clientes} total
          </p>
        </div>
      </div>
      
      {/* Dicas de Conversão */}
      {dicas.dicas_conversao.length > 0 && (
        <div className="bg-white rounded-lg p-4 mb-4">
          <h3 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
            <span>💡</span>
            <span>Dicas de Conversão</span>
          </h3>
          <ul className="space-y-2">
            {dicas.dicas_conversao.map((dica, i) => (
              <li key={i} className="text-gray-700 flex items-start gap-2">
                <span className="text-purple-600 font-bold">•</span>
                <span>{dica}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {/* Sugestões de ROI */}
      {dicas.sugestoes_roi.length > 0 && (
        <div className="bg-white rounded-lg p-4 mb-4">
          <h3 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
            <span>📈</span>
            <span>Sugestões de ROI</span>
          </h3>
          <ul className="space-y-2">
            {dicas.sugestoes_roi.map((sugestao, i) => (
              <li key={i} className="text-gray-700 flex items-start gap-2">
                <span className="text-blue-600 font-bold">•</span>
                <span>{sugestao}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {/* Análise de Lucro e Anúncios */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div className="bg-white rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
            <span>💰</span>
            <span>Análise de Lucro</span>
          </h3>
          <p className="text-gray-700 text-sm">{dicas.analise_lucro}</p>
        </div>
        
        <div className="bg-white rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
            <span>📢</span>
            <span>Investimento em Anúncios</span>
          </h3>
          <p className="text-4xl font-bold text-purple-600">{dicas.percentual_anuncios}%</p>
          <p className="text-sm text-gray-600 mt-1">do faturamento recomendado</p>
        </div>
      </div>
      
      {/* Objetivo Mensal */}
      <div className="bg-white rounded-lg p-4">
        <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
          <span>🎯</span>
          <span>Objetivo Mensal</span>
        </h3>
        
        {editandoObjetivo ? (
          <div className="flex gap-2">
            <input
              type="number"
              value={novoObjetivo}
              onChange={(e) => setNovoObjetivo(e.target.value)}
              className="flex-1 px-3 py-2 border rounded-lg"
              placeholder="Digite o valor (ex: 10000)"
            />
            <button
              onClick={salvarObjetivo}
              className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700"
            >
              Salvar
            </button>
            <button
              onClick={() => {
                setEditandoObjetivo(false)
                setNovoObjetivo('')
              }}
              className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300"
            >
              Cancelar
            </button>
          </div>
        ) : (
          <>
            {objetivoMensal ? (
              <>
                <div className="mb-3">
                  <p className="text-sm text-gray-600 mb-1">Meta: R$ {objetivoMensal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</p>
                  <div className="w-full bg-gray-200 rounded-full h-4">
                    <div
                      className="bg-gradient-to-r from-purple-600 to-blue-600 h-4 rounded-full transition-all"
                      style={{ width: `${Math.min(dicas.progresso_objetivo, 100)}%` }}
                    />
                  </div>
                  <p className="text-sm text-gray-600 mt-1 text-right">
                    {dicas.progresso_objetivo.toFixed(1)}% alcançado
                  </p>
                </div>
                <button
                  onClick={() => setEditandoObjetivo(true)}
                  className="text-purple-600 hover:text-purple-700 text-sm font-medium"
                >
                  Alterar objetivo
                </button>
              </>
            ) : (
              <button
                onClick={() => setEditandoObjetivo(true)}
                className="w-full bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700"
              >
                Configurar Objetivo Mensal
              </button>
            )}
          </>
        )}
      </div>
    </div>
  )
}
