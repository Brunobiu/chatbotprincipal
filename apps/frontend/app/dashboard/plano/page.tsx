'use client'

/**
 * Página de Mudança de Plano
 * Task 19
 */

import { useState, useEffect } from 'react'
import { Check, TrendingUp, Zap } from 'lucide-react'

interface Plano {
  nome: string
  valor_original: number
  valor_final: number
  desconto_percentual: number
  economia: number
  valor_mensal_equivalente: number
}

interface Planos {
  mensal: Plano
  trimestral: Plano
  anual: Plano
}

export default function MudarPlanoPage() {
  const [planos, setPlanos] = useState<Planos | null>(null)
  const [planoAtual, setPlanoAtual] = useState<string>('mensal')
  const [planoSelecionado, setPlanoSelecionado] = useState<string>('mensal')
  const [processando, setProcessando] = useState(false)
  const [carregando, setCarregando] = useState(true)

  useEffect(() => {
    carregarPlanos()
    carregarPlanoAtual()
  }, [])

  const carregarPlanos = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/billing/planos')
      if (response.ok) {
        const data = await response.json()
        setPlanos(data)
      }
    } catch (error) {
      console.error('Erro ao carregar planos:', error)
    } finally {
      setCarregando(false)
    }
  }

  const carregarPlanoAtual = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/api/v1/billing/assinatura/info', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setPlanoAtual(data.plano_atual || 'mensal')
        setPlanoSelecionado(data.plano_atual || 'mensal')
      }
    } catch (error) {
      console.error('Erro ao carregar plano atual:', error)
    }
  }

  const mudarPlano = async () => {
    if (planoSelecionado === planoAtual) {
      alert('Você já está neste plano')
      return
    }

    if (!confirm(`Deseja mudar para o plano ${planoSelecionado}? O ajuste será feito proporcionalmente na próxima fatura.`)) {
      return
    }

    setProcessando(true)

    try {
      const token = localStorage.getItem('token')
      
      // Obter price_id do plano selecionado (ajustar conforme seus price_ids)
      const priceIds: Record<string, string> = {
        mensal: process.env.NEXT_PUBLIC_STRIPE_PRICE_MENSAL || 'price_mensal',
        trimestral: process.env.NEXT_PUBLIC_STRIPE_PRICE_TRIMESTRAL || 'price_trimestral',
        anual: process.env.NEXT_PUBLIC_STRIPE_PRICE_ANUAL || 'price_anual'
      }

      const response = await fetch('http://localhost:8000/api/v1/billing/mudar-plano', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          novo_plano: planoSelecionado,
          price_id: priceIds[planoSelecionado]
        })
      })

      if (response.ok) {
        const data = await response.json()
        alert(data.mensagem || 'Plano alterado com sucesso!')
        setPlanoAtual(planoSelecionado)
        carregarPlanoAtual()
      } else {
        const error = await response.json()
        alert(`Erro: ${error.detail || 'Erro ao mudar plano'}`)
      }
    } catch (error) {
      console.error('Erro ao mudar plano:', error)
      alert('Erro ao processar mudança de plano. Tente novamente.')
    } finally {
      setProcessando(false)
    }
  }

  if (carregando || !planos) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-600">Carregando planos...</div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Gerenciar Plano
        </h1>
        <p className="text-gray-600">
          Escolha o plano ideal para o seu negócio. Economize até 20% com planos anuais.
        </p>
      </div>

      {/* Plano Atual */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8">
        <div className="flex items-center gap-2">
          <Zap className="w-5 h-5 text-blue-600" />
          <span className="font-semibold text-blue-900">
            Plano Atual: <span className="capitalize">{planoAtual}</span>
          </span>
        </div>
      </div>

      {/* Cards de Planos */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Plano Mensal */}
        <div
          onClick={() => setPlanoSelecionado('mensal')}
          className={`cursor-pointer rounded-xl border-2 p-6 transition-all hover:shadow-lg ${
            planoSelecionado === 'mensal'
              ? 'border-purple-600 bg-purple-50 shadow-lg'
              : 'border-gray-200 hover:border-purple-300'
          } ${planoAtual === 'mensal' ? 'ring-2 ring-blue-400' : ''}`}
        >
          {planoAtual === 'mensal' && (
            <div className="mb-2">
              <span className="bg-blue-500 text-white text-xs px-2 py-1 rounded-full">
                Plano Atual
              </span>
            </div>
          )}
          
          <h3 className="text-2xl font-bold mb-2">Mensal</h3>
          
          <div className="mb-4">
            <div className="text-4xl font-bold text-purple-600">
              R$ {planos.mensal.valor_final.toFixed(2)}
            </div>
            <div className="text-sm text-gray-600">por mês</div>
          </div>

          <ul className="space-y-2 mb-6">
            <li className="flex items-center gap-2 text-sm">
              <Check className="w-4 h-4 text-green-600" />
              <span>Sem compromisso</span>
            </li>
            <li className="flex items-center gap-2 text-sm">
              <Check className="w-4 h-4 text-green-600" />
              <span>Cancele quando quiser</span>
            </li>
            <li className="flex items-center gap-2 text-sm">
              <Check className="w-4 h-4 text-green-600" />
              <span>Suporte prioritário</span>
            </li>
          </ul>

          {planoSelecionado === 'mensal' && planoAtual !== 'mensal' && (
            <div className="text-sm text-purple-600 font-semibold">
              ✓ Selecionado
            </div>
          )}
        </div>

        {/* Plano Trimestral */}
        <div
          onClick={() => setPlanoSelecionado('trimestral')}
          className={`cursor-pointer rounded-xl border-2 p-6 transition-all hover:shadow-lg relative ${
            planoSelecionado === 'trimestral'
              ? 'border-purple-600 bg-purple-50 shadow-lg'
              : 'border-gray-200 hover:border-purple-300'
          } ${planoAtual === 'trimestral' ? 'ring-2 ring-blue-400' : ''}`}
        >
          <div className="absolute -top-3 right-4 bg-green-500 text-white text-xs px-3 py-1 rounded-full font-semibold">
            Economize 10%
          </div>

          {planoAtual === 'trimestral' && (
            <div className="mb-2">
              <span className="bg-blue-500 text-white text-xs px-2 py-1 rounded-full">
                Plano Atual
              </span>
            </div>
          )}
          
          <h3 className="text-2xl font-bold mb-2">Trimestral</h3>
          
          <div className="mb-4">
            <div className="text-4xl font-bold text-purple-600">
              R$ {planos.trimestral.valor_final.toFixed(2)}
            </div>
            <div className="text-sm text-gray-600 line-through">
              R$ {planos.trimestral.valor_original.toFixed(2)}
            </div>
            <div className="text-sm text-gray-600">
              R$ {planos.trimestral.valor_mensal_equivalente.toFixed(2)}/mês
            </div>
          </div>

          <ul className="space-y-2 mb-6">
            <li className="flex items-center gap-2 text-sm">
              <Check className="w-4 h-4 text-green-600" />
              <span>Economize R$ {planos.trimestral.economia.toFixed(2)}</span>
            </li>
            <li className="flex items-center gap-2 text-sm">
              <Check className="w-4 h-4 text-green-600" />
              <span>3 meses de acesso</span>
            </li>
            <li className="flex items-center gap-2 text-sm">
              <Check className="w-4 h-4 text-green-600" />
              <span>Suporte prioritário</span>
            </li>
          </ul>

          {planoSelecionado === 'trimestral' && planoAtual !== 'trimestral' && (
            <div className="text-sm text-purple-600 font-semibold">
              ✓ Selecionado
            </div>
          )}
        </div>

        {/* Plano Anual */}
        <div
          onClick={() => setPlanoSelecionado('anual')}
          className={`cursor-pointer rounded-xl border-2 p-6 transition-all hover:shadow-lg relative ${
            planoSelecionado === 'anual'
              ? 'border-purple-600 bg-purple-50 shadow-lg'
              : 'border-gray-200 hover:border-purple-300'
          } ${planoAtual === 'anual' ? 'ring-2 ring-blue-400' : ''}`}
        >
          <div className="absolute -top-3 right-4 bg-green-500 text-white text-xs px-3 py-1 rounded-full font-semibold">
            Economize 20%
          </div>

          {planoAtual === 'anual' && (
            <div className="mb-2">
              <span className="bg-blue-500 text-white text-xs px-2 py-1 rounded-full">
                Plano Atual
              </span>
            </div>
          )}
          
          <h3 className="text-2xl font-bold mb-2">Anual</h3>
          
          <div className="mb-4">
            <div className="text-4xl font-bold text-purple-600">
              R$ {planos.anual.valor_final.toFixed(2)}
            </div>
            <div className="text-sm text-gray-600 line-through">
              R$ {planos.anual.valor_original.toFixed(2)}
            </div>
            <div className="text-sm text-gray-600">
              R$ {planos.anual.valor_mensal_equivalente.toFixed(2)}/mês
            </div>
          </div>

          <ul className="space-y-2 mb-6">
            <li className="flex items-center gap-2 text-sm">
              <Check className="w-4 h-4 text-green-600" />
              <span>Economize R$ {planos.anual.economia.toFixed(2)}</span>
            </li>
            <li className="flex items-center gap-2 text-sm">
              <Check className="w-4 h-4 text-green-600" />
              <span>12 meses de acesso</span>
            </li>
            <li className="flex items-center gap-2 text-sm">
              <Check className="w-4 h-4 text-green-600" />
              <span>Melhor custo-benefício</span>
            </li>
          </ul>

          {planoSelecionado === 'anual' && planoAtual !== 'anual' && (
            <div className="text-sm text-purple-600 font-semibold">
              ✓ Selecionado
            </div>
          )}
        </div>
      </div>

      {/* Botão de Mudança */}
      {planoSelecionado !== planoAtual && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold text-lg">Mudar de Plano</h3>
              <p className="text-sm text-gray-600">
                De <span className="capitalize font-semibold">{planoAtual}</span> para{' '}
                <span className="capitalize font-semibold text-purple-600">{planoSelecionado}</span>
              </p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-purple-600">
                R$ {planos[planoSelecionado as keyof Planos].valor_final.toFixed(2)}
              </div>
              {planos[planoSelecionado as keyof Planos].desconto_percentual > 0 && (
                <div className="text-sm text-green-600 font-semibold">
                  Economize {planos[planoSelecionado as keyof Planos].desconto_percentual}%
                </div>
              )}
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
            <div className="flex items-start gap-2">
              <TrendingUp className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-blue-900">
                <p className="font-semibold mb-1">Ajuste Proporcional</p>
                <p>
                  O valor será ajustado proporcionalmente na sua próxima fatura. 
                  Você receberá crédito pelo tempo não utilizado do plano atual.
                </p>
              </div>
            </div>
          </div>

          <button
            onClick={mudarPlano}
            disabled={processando}
            className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 disabled:from-gray-400 disabled:to-gray-500 text-white font-semibold py-3 rounded-lg transition-all"
          >
            {processando ? 'Processando...' : 'Confirmar Mudança de Plano'}
          </button>
        </div>
      )}

      {/* Informações Adicionais */}
      <div className="mt-8 bg-gray-50 rounded-lg p-6">
        <h3 className="font-semibold mb-4">Perguntas Frequentes</h3>
        <div className="space-y-4 text-sm">
          <div>
            <p className="font-semibold text-gray-900 mb-1">
              Como funciona o ajuste proporcional?
            </p>
            <p className="text-gray-600">
              Quando você muda de plano, calculamos o valor não utilizado do seu plano atual 
              e aplicamos como crédito na próxima fatura. Você só paga a diferença.
            </p>
          </div>
          <div>
            <p className="font-semibold text-gray-900 mb-1">
              Posso cancelar a qualquer momento?
            </p>
            <p className="text-gray-600">
              Sim! Você pode cancelar sua assinatura a qualquer momento. 
              Seu acesso continuará até o final do período pago.
            </p>
          </div>
          <div>
            <p className="font-semibold text-gray-900 mb-1">
              Os descontos são permanentes?
            </p>
            <p className="text-gray-600">
              Sim! Os descontos de 10% (trimestral) e 20% (anual) são aplicados 
              em todas as renovações enquanto você mantiver o plano.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
