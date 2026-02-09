'use client'

/**
 * Página de Checkout com PIX e Cartão de Débito
 * Task 18
 */

import { useState } from 'react'
import { CreditCard, QrCode, Smartphone } from 'lucide-react'

export default function CheckoutPage() {
  const [planoSelecionado, setPlanoSelecionado] = useState<'mensal' | 'trimestral' | 'anual'>('mensal')
  const [metodoPagamento, setMetodoPagamento] = useState<'cartao' | 'pix' | 'debito'>('cartao')
  const [processando, setProcessando] = useState(false)

  // Preços (exemplo - ajustar conforme necessário)
  const precos = {
    mensal: {
      valor: 97.00,
      price_id: process.env.NEXT_PUBLIC_STRIPE_PRICE_MENSAL || 'price_mensal',
      desconto: 0
    },
    trimestral: {
      valor: 261.30, // 10% desconto
      valorOriginal: 291.00,
      price_id: process.env.NEXT_PUBLIC_STRIPE_PRICE_TRIMESTRAL || 'price_trimestral',
      desconto: 10
    },
    anual: {
      valor: 931.20, // 20% desconto
      valorOriginal: 1164.00,
      price_id: process.env.NEXT_PUBLIC_STRIPE_PRICE_ANUAL || 'price_anual',
      desconto: 20
    }
  }

  const planoAtual = precos[planoSelecionado]

  const handleCheckout = async () => {
    setProcessando(true)

    try {
      const token = localStorage.getItem('token')
      
      if (!token) {
        alert('Você precisa estar logado para fazer o checkout')
        window.location.href = '/login'
        return
      }

      let endpoint = ''
      
      // Escolher endpoint baseado no método de pagamento
      if (metodoPagamento === 'pix') {
        endpoint = 'http://localhost:8000/api/v1/billing/checkout-pix'
      } else if (metodoPagamento === 'debito') {
        endpoint = 'http://localhost:8000/api/v1/billing/checkout-debito'
      } else {
        // Cartão de crédito (endpoint padrão)
        endpoint = 'http://localhost:8000/api/v1/billing/create-checkout-session'
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          price_id: planoAtual.price_id,
          plano: planoSelecionado
        })
      })

      if (response.ok) {
        const data = await response.json()
        // Redirecionar para checkout do Stripe
        window.location.href = data.url
      } else {
        const error = await response.json()
        alert(`Erro: ${error.detail || 'Erro ao criar checkout'}`)
      }
    } catch (error) {
      console.error('Erro ao criar checkout:', error)
      alert('Erro ao processar pagamento. Tente novamente.')
    } finally {
      setProcessando(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Escolha seu Plano
          </h1>
          <p className="text-gray-600">
            Comece a automatizar seu atendimento no WhatsApp hoje mesmo
          </p>
        </div>

        {/* Seleção de Plano */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {/* Plano Mensal */}
          <button
            onClick={() => setPlanoSelecionado('mensal')}
            className={`p-6 rounded-xl border-2 transition-all ${
              planoSelecionado === 'mensal'
                ? 'border-purple-600 bg-purple-50'
                : 'border-gray-200 hover:border-purple-300'
            }`}
          >
            <div className="text-center">
              <h3 className="text-xl font-semibold mb-2">Mensal</h3>
              <div className="text-3xl font-bold text-purple-600 mb-2">
                R$ {precos.mensal.valor.toFixed(2)}
              </div>
              <p className="text-sm text-gray-600">por mês</p>
            </div>
          </button>

          {/* Plano Trimestral */}
          <button
            onClick={() => setPlanoSelecionado('trimestral')}
            className={`p-6 rounded-xl border-2 transition-all relative ${
              planoSelecionado === 'trimestral'
                ? 'border-purple-600 bg-purple-50'
                : 'border-gray-200 hover:border-purple-300'
            }`}
          >
            <div className="absolute -top-3 right-4 bg-green-500 text-white text-xs px-3 py-1 rounded-full">
              Economize 10%
            </div>
            <div className="text-center">
              <h3 className="text-xl font-semibold mb-2">Trimestral</h3>
              <div className="text-3xl font-bold text-purple-600 mb-2">
                R$ {precos.trimestral.valor.toFixed(2)}
              </div>
              <p className="text-sm text-gray-600 line-through">
                R$ {precos.trimestral.valorOriginal?.toFixed(2)}
              </p>
              <p className="text-sm text-gray-600">3 meses</p>
            </div>
          </button>

          {/* Plano Anual */}
          <button
            onClick={() => setPlanoSelecionado('anual')}
            className={`p-6 rounded-xl border-2 transition-all relative ${
              planoSelecionado === 'anual'
                ? 'border-purple-600 bg-purple-50'
                : 'border-gray-200 hover:border-purple-300'
            }`}
          >
            <div className="absolute -top-3 right-4 bg-green-500 text-white text-xs px-3 py-1 rounded-full">
              Economize 20%
            </div>
            <div className="text-center">
              <h3 className="text-xl font-semibold mb-2">Anual</h3>
              <div className="text-3xl font-bold text-purple-600 mb-2">
                R$ {precos.anual.valor.toFixed(2)}
              </div>
              <p className="text-sm text-gray-600 line-through">
                R$ {precos.anual.valorOriginal?.toFixed(2)}
              </p>
              <p className="text-sm text-gray-600">12 meses</p>
            </div>
          </button>
        </div>

        {/* Método de Pagamento */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold mb-4 text-center">
            Escolha a forma de pagamento
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Cartão de Crédito */}
            <button
              onClick={() => setMetodoPagamento('cartao')}
              className={`p-4 rounded-lg border-2 transition-all flex items-center gap-3 ${
                metodoPagamento === 'cartao'
                  ? 'border-purple-600 bg-purple-50'
                  : 'border-gray-200 hover:border-purple-300'
              }`}
            >
              <CreditCard className="w-6 h-6 text-purple-600" />
              <div className="text-left">
                <div className="font-semibold">Cartão de Crédito</div>
                <div className="text-xs text-gray-600">Aprovação imediata</div>
              </div>
            </button>

            {/* PIX */}
            <button
              onClick={() => setMetodoPagamento('pix')}
              className={`p-4 rounded-lg border-2 transition-all flex items-center gap-3 ${
                metodoPagamento === 'pix'
                  ? 'border-purple-600 bg-purple-50'
                  : 'border-gray-200 hover:border-purple-300'
              }`}
            >
              <QrCode className="w-6 h-6 text-purple-600" />
              <div className="text-left">
                <div className="font-semibold">PIX</div>
                <div className="text-xs text-gray-600">Pagamento instantâneo</div>
              </div>
            </button>

            {/* Cartão de Débito */}
            <button
              onClick={() => setMetodoPagamento('debito')}
              className={`p-4 rounded-lg border-2 transition-all flex items-center gap-3 ${
                metodoPagamento === 'debito'
                  ? 'border-purple-600 bg-purple-50'
                  : 'border-gray-200 hover:border-purple-300'
              }`}
            >
              <Smartphone className="w-6 h-6 text-purple-600" />
              <div className="text-left">
                <div className="font-semibold">Cartão de Débito</div>
                <div className="text-xs text-gray-600">Débito em conta</div>
              </div>
            </button>
          </div>
        </div>

        {/* Resumo */}
        <div className="bg-gray-50 rounded-lg p-6 mb-6">
          <h3 className="font-semibold mb-4">Resumo do Pedido</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Plano:</span>
              <span className="font-semibold capitalize">{planoSelecionado}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Método de pagamento:</span>
              <span className="font-semibold capitalize">
                {metodoPagamento === 'cartao' ? 'Cartão de Crédito' : 
                 metodoPagamento === 'pix' ? 'PIX' : 'Cartão de Débito'}
              </span>
            </div>
            {planoAtual.desconto > 0 && (
              <div className="flex justify-between text-green-600">
                <span>Desconto:</span>
                <span className="font-semibold">{planoAtual.desconto}%</span>
              </div>
            )}
            <div className="border-t pt-2 mt-2">
              <div className="flex justify-between text-lg font-bold">
                <span>Total:</span>
                <span className="text-purple-600">
                  R$ {planoAtual.valor.toFixed(2)}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Botão de Checkout */}
        <button
          onClick={handleCheckout}
          disabled={processando}
          className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 disabled:from-gray-400 disabled:to-gray-500 text-white font-semibold py-4 rounded-lg transition-all transform hover:scale-105 disabled:scale-100"
        >
          {processando ? 'Processando...' : 'Finalizar Pagamento'}
        </button>

        {/* Informações de Segurança */}
        <div className="mt-6 text-center text-sm text-gray-600">
          <p>🔒 Pagamento 100% seguro via Stripe</p>
          <p className="mt-1">Seus dados estão protegidos</p>
        </div>
      </div>
    </div>
  )
}
