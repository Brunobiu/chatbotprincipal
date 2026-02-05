'use client'

import { useState } from 'react'
import Link from 'next/link'

export default function CheckoutPage() {
  const [loading, setLoading] = useState(false)

  const handleCheckout = async () => {
    try {
      setLoading(true)
      const backend = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
      const lookup = process.env.NEXT_PUBLIC_STRIPE_PRICE_LOOKUP_KEY || ''
      const res = await fetch(`${backend}/api/v1/billing/create-checkout-session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lookup_key: lookup }),
      })
      const data = await res.json()
      if (data.url) {
        window.location.href = data.url
      } else {
        alert('Erro ao criar sessão de checkout')
      }
    } catch (err) {
      console.error(err)
      alert('Erro ao iniciar checkout')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full text-center">
        <h1 className="text-3xl font-bold mb-4">Assinar plano</h1>
        <p className="text-gray-600 mb-8">Assine o plano mensal para começar a usar o serviço.</p>

        <div className="bg-white p-6 rounded border border-gray-200 mb-8">
          <h2 className="text-xl font-semibold mb-4">Starter — R$2,00/mês</h2>
          <p className="text-gray-700 mb-4">Assinatura mensal para uso do bot</p>
          <button
            onClick={handleCheckout}
            disabled={loading}
            className="inline-block bg-green-600 text-white px-6 py-3 font-semibold rounded hover:bg-green-700 transition"
          >
            {loading ? 'Redirecionando...' : 'Assinar com Stripe'}
          </button>
        </div>

        <Link href="/" className="inline-block text-sm text-gray-600 hover:underline">
          Voltar para home
        </Link>
      </div>
    </div>
  )
}
