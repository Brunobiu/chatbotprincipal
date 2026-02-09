'use client'

import { useEffect, useState } from 'react'

interface InfoAssinatura {
  status: string
  dias_restantes: number
  plano_atual: string
  data_proxima_cobranca: string | null
  valor_mensal: number
  pode_pagar_mais_mes: boolean
}

export default function WidgetAssinatura() {
  const [loading, setLoading] = useState(true)
  const [info, setInfo] = useState<InfoAssinatura | null>(null)
  const [processandoPagamento, setProcessandoPagamento] = useState(false)
  
  useEffect(() => {
    carregarInfo()
  }, [])
  
  const carregarInfo = async () => {
    try {
      const token = localStorage.getItem('token')
      
      if (!token) {
        return
      }
      
      const response = await fetch('http://localhost:8000/api/v1/billing/assinatura/info', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setInfo(data)
      }
    } catch (err) {
      console.error('Erro ao carregar info de assinatura:', err)
    } finally {
      setLoading(false)
    }
  }
  
  const handlePagarMaisMes = async () => {
    setProcessandoPagamento(true)
    
    try {
      const token = localStorage.getItem('token')
      
      const response = await fetch('http://localhost:8000/api/v1/billing/assinatura/pagar-mais-mes', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        // Redirecionar para checkout
        window.location.href = data.url
      } else {
        const error = await response.json()
        alert(error.detail || 'Erro ao criar sessão de pagamento')
      }
    } catch (err) {
      console.error('Erro ao criar pagamento:', err)
      alert('Erro ao criar sessão de pagamento')
    } finally {
      setProcessandoPagamento(false)
    }
  }
  
  const handleMudarPlano = () => {
    // TODO: Implementar mudança de plano (Task futura)
    alert('Funcionalidade de mudança de plano será implementada em breve!')
  }
  
  const handleHistoricoPagamentos = () => {
    // TODO: Implementar histórico de pagamentos (Task futura)
    alert('Histórico de pagamentos será implementado em breve!')
  }
  
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
          <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-full"></div>
        </div>
      </div>
    )
  }
  
  if (!info) {
    return null
  }
  
  // Cores por status
  const statusColors = {
    ativa: 'bg-green-100 text-green-800 border-green-200',
    cancelada: 'bg-red-100 text-red-800 border-red-200',
    expirada: 'bg-orange-100 text-orange-800 border-orange-200',
    pendente: 'bg-yellow-100 text-yellow-800 border-yellow-200'
  }
  
  const statusColor = statusColors[info.status as keyof typeof statusColors] || statusColors.pendente
  
  // Ícones por status
  const statusIcons = {
    ativa: '✅',
    cancelada: '❌',
    expirada: '⚠️',
    pendente: '⏳'
  }
  
  const statusIcon = statusIcons[info.status as keyof typeof statusIcons] || '⏳'
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">Minha Assinatura</h3>
      
      {/* Status */}
      <div className="mb-4">
        <div className={`inline-flex items-center gap-2 px-3 py-2 rounded-lg border ${statusColor}`}>
          <span className="text-xl">{statusIcon}</span>
          <span className="font-medium capitalize">{info.status}</span>
        </div>
      </div>
      
      {/* Dias Restantes */}
      {info.status === 'ativa' && (
        <div className="mb-4">
          <div className="text-sm text-gray-600 mb-1">Dias restantes de acesso</div>
          <div className="text-3xl font-bold text-gray-900">{info.dias_restantes}</div>
          {info.data_proxima_cobranca && (
            <div className="text-xs text-gray-500 mt-1">
              Próxima cobrança: {new Date(info.data_proxima_cobranca).toLocaleDateString('pt-BR')}
            </div>
          )}
        </div>
      )}
      
      {/* Plano Atual */}
      <div className="mb-4">
        <div className="text-sm text-gray-600 mb-1">Plano atual</div>
        <div className="text-lg font-semibold capitalize">{info.plano_atual}</div>
        {info.valor_mensal > 0 && (
          <div className="text-sm text-gray-600">
            R$ {info.valor_mensal.toFixed(2)}/mês
          </div>
        )}
      </div>
      
      {/* Botões */}
      <div className="space-y-2">
        {info.pode_pagar_mais_mes && info.status === 'ativa' && (
          <button
            onClick={handlePagarMaisMes}
            disabled={processandoPagamento}
            className="w-full bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 transition-all text-sm font-medium"
          >
            {processandoPagamento ? 'Processando...' : '💳 Pagar mais um mês'}
          </button>
        )}
        
        <button
          onClick={handleMudarPlano}
          className="w-full bg-gray-900 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-all text-sm font-medium"
        >
          🔄 Mudar de Plano
        </button>
        
        <button
          onClick={handleHistoricoPagamentos}
          className="w-full bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 transition-all text-sm font-medium"
        >
          📄 Histórico de Pagamentos
        </button>
      </div>
      
      {/* Avisos */}
      {info.status === 'cancelada' && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-700">
            Sua assinatura foi cancelada. Renove para continuar usando o serviço.
          </p>
        </div>
      )}
      
      {info.status === 'expirada' && (
        <div className="mt-4 p-3 bg-orange-50 border border-orange-200 rounded-lg">
          <p className="text-sm text-orange-700">
            Seu pagamento está atrasado. Regularize para continuar usando o serviço.
          </p>
        </div>
      )}
      
      {info.status === 'pendente' && (
        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm text-yellow-700">
            Sua assinatura está pendente. Complete o pagamento para ativar.
          </p>
        </div>
      )}
      
      {info.status === 'ativa' && info.dias_restantes <= 7 && (
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-blue-700">
            ⏰ Sua assinatura vence em {info.dias_restantes} dias. Renove para não perder acesso!
          </p>
        </div>
      )}
    </div>
  )
}
