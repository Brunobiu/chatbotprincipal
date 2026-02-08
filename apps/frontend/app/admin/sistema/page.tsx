'use client'

import { useEffect, useState } from 'react'
import { Activity, AlertTriangle, CheckCircle, XCircle, Database, Zap, Cloud, MessageSquare, Cpu, HardDrive, TrendingUp } from 'lucide-react'

interface ServicoStatus {
  status: string
  latencia_ms?: number
  saudavel: boolean
  erro?: string
  [key: string]: any
}

interface SaudeCompleta {
  status_geral: string
  timestamp: string
  servicos: {
    postgres: ServicoStatus
    redis: ServicoStatus
    chromadb: ServicoStatus
    evolution_api: ServicoStatus
    openai: ServicoStatus
  }
}

interface Metricas {
  timestamp: string
  cpu: {
    uso_percent: number
    alerta: boolean
  }
  memoria: {
    usado_gb: number
    total_gb: number
    uso_percent: number
    alerta: boolean
  }
  disco: {
    usado_gb: number
    total_gb: number
    uso_percent: number
    alerta: boolean
  }
  performance: {
    tempo_resposta_medio_ms: number
    requests_por_minuto: number
    erros_por_minuto: number
    alerta: boolean
  }
}

export default function SistemaPage() {
  const [saude, setSaude] = useState<SaudeCompleta | null>(null)
  const [metricas, setMetricas] = useState<Metricas | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchDados = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      
      const [saudeRes, metricasRes] = await Promise.all([
        fetch('http://localhost:8000/api/v1/admin/sistema/saude', {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch('http://localhost:8000/api/v1/admin/sistema/metricas', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ])

      if (saudeRes.ok && metricasRes.ok) {
        const saudeData = await saudeRes.json()
        const metricasData = await metricasRes.json()
        setSaude(saudeData)
        setMetricas(metricasData)
        setError('')
      } else {
        setError('Erro ao carregar dados do sistema')
      }
    } catch (err) {
      setError('Erro ao conectar com o servidor')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDados()
    const interval = setInterval(fetchDados, 10000) // Atualiza a cada 10s
    return () => clearInterval(interval)
  }, [])

  const getStatusIcon = (saudavel: boolean) => {
    return saudavel ? (
      <CheckCircle className="w-6 h-6 text-green-500" />
    ) : (
      <XCircle className="w-6 h-6 text-red-500" />
    )
  }

  const getStatusColor = (saudavel: boolean) => {
    return saudavel ? 'bg-green-100 dark:bg-green-900/20' : 'bg-red-100 dark:bg-red-900/20'
  }

  const getAlertColor = (alerta: boolean) => {
    return alerta ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400'
  }

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
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Monitoramento de Sistema</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Status de saúde e métricas de performance</p>
        </div>
        <button
          onClick={fetchDados}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Atualizar
        </button>
      </div>

      {error && (
        <div className="bg-red-100 dark:bg-red-900/20 border border-red-400 text-red-700 dark:text-red-400 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Status Geral */}
      {saude && (
        <div className={`p-6 rounded-lg border ${saude.status_geral === 'saudavel' ? 'bg-green-50 dark:bg-green-900/10 border-green-200 dark:border-green-800' : 'bg-red-50 dark:bg-red-900/10 border-red-200 dark:border-red-800'}`}>
          <div className="flex items-center gap-3">
            {saude.status_geral === 'saudavel' ? (
              <CheckCircle className="w-8 h-8 text-green-600 dark:text-green-400" />
            ) : (
              <AlertTriangle className="w-8 h-8 text-red-600 dark:text-red-400" />
            )}
            <div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                {saude.status_geral === 'saudavel' ? 'Sistema Saudável' : 'Problemas Detectados'}
              </h2>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Última verificação: {new Date(saude.timestamp).toLocaleString('pt-BR')}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Serviços */}
      {saude && (
        <div>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Serviços</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* PostgreSQL */}
            <div className={`p-4 rounded-lg border ${getStatusColor(saude.servicos.postgres.saudavel)}`}>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Database className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  <h3 className="font-semibold text-gray-900 dark:text-white">PostgreSQL</h3>
                </div>
                {getStatusIcon(saude.servicos.postgres.saudavel)}
              </div>
              <div className="space-y-1 text-sm">
                <p className="text-gray-700 dark:text-gray-300">Status: {saude.servicos.postgres.status}</p>
                {saude.servicos.postgres.latencia_ms && (
                  <p className="text-gray-700 dark:text-gray-300">Latência: {saude.servicos.postgres.latencia_ms}ms</p>
                )}
                {saude.servicos.postgres.erro && (
                  <p className="text-red-600 dark:text-red-400 text-xs">{saude.servicos.postgres.erro}</p>
                )}
              </div>
            </div>

            {/* Redis */}
            <div className={`p-4 rounded-lg border ${getStatusColor(saude.servicos.redis.saudavel)}`}>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Zap className="w-5 h-5 text-red-600 dark:text-red-400" />
                  <h3 className="font-semibold text-gray-900 dark:text-white">Redis</h3>
                </div>
                {getStatusIcon(saude.servicos.redis.saudavel)}
              </div>
              <div className="space-y-1 text-sm">
                <p className="text-gray-700 dark:text-gray-300">Status: {saude.servicos.redis.status}</p>
                {saude.servicos.redis.latencia_ms && (
                  <p className="text-gray-700 dark:text-gray-300">Latência: {saude.servicos.redis.latencia_ms}ms</p>
                )}
                {saude.servicos.redis.memoria_usada_mb && (
                  <p className="text-gray-700 dark:text-gray-300">Memória: {saude.servicos.redis.memoria_usada_mb}MB</p>
                )}
                {saude.servicos.redis.erro && (
                  <p className="text-red-600 dark:text-red-400 text-xs">{saude.servicos.redis.erro}</p>
                )}
              </div>
            </div>

            {/* ChromaDB */}
            <div className={`p-4 rounded-lg border ${getStatusColor(saude.servicos.chromadb.saudavel)}`}>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Database className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                  <h3 className="font-semibold text-gray-900 dark:text-white">ChromaDB</h3>
                </div>
                {getStatusIcon(saude.servicos.chromadb.saudavel)}
              </div>
              <div className="space-y-1 text-sm">
                <p className="text-gray-700 dark:text-gray-300">Status: {saude.servicos.chromadb.status}</p>
                {saude.servicos.chromadb.latencia_ms && (
                  <p className="text-gray-700 dark:text-gray-300">Latência: {saude.servicos.chromadb.latencia_ms}ms</p>
                )}
                {saude.servicos.chromadb.colecoes !== undefined && (
                  <p className="text-gray-700 dark:text-gray-300">Coleções: {saude.servicos.chromadb.colecoes}</p>
                )}
                {saude.servicos.chromadb.erro && (
                  <p className="text-red-600 dark:text-red-400 text-xs">{saude.servicos.chromadb.erro}</p>
                )}
              </div>
            </div>

            {/* Evolution API */}
            <div className={`p-4 rounded-lg border ${getStatusColor(saude.servicos.evolution_api.saudavel)}`}>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <MessageSquare className="w-5 h-5 text-green-600 dark:text-green-400" />
                  <h3 className="font-semibold text-gray-900 dark:text-white">Evolution API</h3>
                </div>
                {getStatusIcon(saude.servicos.evolution_api.saudavel)}
              </div>
              <div className="space-y-1 text-sm">
                <p className="text-gray-700 dark:text-gray-300">Status: {saude.servicos.evolution_api.status}</p>
                {saude.servicos.evolution_api.latencia_ms && (
                  <p className="text-gray-700 dark:text-gray-300">Latência: {saude.servicos.evolution_api.latencia_ms}ms</p>
                )}
                {saude.servicos.evolution_api.instancias_total !== undefined && (
                  <p className="text-gray-700 dark:text-gray-300">
                    Instâncias: {saude.servicos.evolution_api.instancias_conectadas}/{saude.servicos.evolution_api.instancias_total}
                  </p>
                )}
                {saude.servicos.evolution_api.erro && (
                  <p className="text-red-600 dark:text-red-400 text-xs">{saude.servicos.evolution_api.erro}</p>
                )}
              </div>
            </div>

            {/* OpenAI */}
            <div className={`p-4 rounded-lg border ${getStatusColor(saude.servicos.openai.saudavel)}`}>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Cloud className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                  <h3 className="font-semibold text-gray-900 dark:text-white">OpenAI</h3>
                </div>
                {getStatusIcon(saude.servicos.openai.saudavel)}
              </div>
              <div className="space-y-1 text-sm">
                <p className="text-gray-700 dark:text-gray-300">Status: {saude.servicos.openai.status}</p>
                {saude.servicos.openai.latencia_ms && (
                  <p className="text-gray-700 dark:text-gray-300">Latência: {saude.servicos.openai.latencia_ms}ms</p>
                )}
                {saude.servicos.openai.api_key_valida !== undefined && (
                  <p className="text-gray-700 dark:text-gray-300">
                    API Key: {saude.servicos.openai.api_key_valida ? 'Válida' : 'Inválida'}
                  </p>
                )}
                {saude.servicos.openai.erro && (
                  <p className="text-red-600 dark:text-red-400 text-xs">{saude.servicos.openai.erro}</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Métricas de Recursos */}
      {metricas && (
        <div>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recursos do Sistema</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* CPU */}
            <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="flex items-center gap-2 mb-3">
                <Cpu className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                <h3 className="font-semibold text-gray-900 dark:text-white">CPU</h3>
              </div>
              <p className={`text-3xl font-bold ${getAlertColor(metricas.cpu.alerta)}`}>
                {metricas.cpu.uso_percent}%
              </p>
              {metricas.cpu.alerta && (
                <p className="text-xs text-red-600 dark:text-red-400 mt-1">⚠️ Uso elevado</p>
              )}
            </div>

            {/* Memória */}
            <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="flex items-center gap-2 mb-3">
                <Activity className="w-5 h-5 text-green-600 dark:text-green-400" />
                <h3 className="font-semibold text-gray-900 dark:text-white">Memória</h3>
              </div>
              <p className={`text-3xl font-bold ${getAlertColor(metricas.memoria.alerta)}`}>
                {metricas.memoria.uso_percent}%
              </p>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                {metricas.memoria.usado_gb.toFixed(1)}GB / {metricas.memoria.total_gb.toFixed(1)}GB
              </p>
              {metricas.memoria.alerta && (
                <p className="text-xs text-red-600 dark:text-red-400 mt-1">⚠️ Uso elevado</p>
              )}
            </div>

            {/* Disco */}
            <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="flex items-center gap-2 mb-3">
                <HardDrive className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                <h3 className="font-semibold text-gray-900 dark:text-white">Disco</h3>
              </div>
              <p className={`text-3xl font-bold ${getAlertColor(metricas.disco.alerta)}`}>
                {metricas.disco.uso_percent}%
              </p>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                {metricas.disco.usado_gb.toFixed(1)}GB / {metricas.disco.total_gb.toFixed(1)}GB
              </p>
              {metricas.disco.alerta && (
                <p className="text-xs text-red-600 dark:text-red-400 mt-1">⚠️ Uso elevado</p>
              )}
            </div>

            {/* Performance */}
            <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="flex items-center gap-2 mb-3">
                <TrendingUp className="w-5 h-5 text-orange-600 dark:text-orange-400" />
                <h3 className="font-semibold text-gray-900 dark:text-white">Performance</h3>
              </div>
              <p className={`text-2xl font-bold ${getAlertColor(metricas.performance.alerta)}`}>
                {metricas.performance.tempo_resposta_medio_ms}ms
              </p>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                {metricas.performance.requests_por_minuto} req/min
              </p>
              <p className="text-xs text-gray-600 dark:text-gray-400">
                {metricas.performance.erros_por_minuto.toFixed(1)} erros/min
              </p>
              {metricas.performance.alerta && (
                <p className="text-xs text-red-600 dark:text-red-400 mt-1">⚠️ Performance degradada</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
