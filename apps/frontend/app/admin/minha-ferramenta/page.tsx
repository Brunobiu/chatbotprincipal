'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function MinhaFerramentaPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  
  useEffect(() => {
    verificarStatus()
  }, [])
  
  const verificarStatus = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      
      if (!token) {
        setError('Token não encontrado')
        return
      }
      
      const response = await fetch('http://localhost:8000/api/v1/admin/minha-ferramenta/status', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setStatus(data)
      }
    } catch (err) {
      console.error('Erro ao verificar status:', err)
    }
  }
  
  const acessarFerramenta = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const token = localStorage.getItem('admin_token')
      
      if (!token) {
        setError('Token não encontrado')
        return
      }
      
      const response = await fetch('http://localhost:8000/api/v1/admin/minha-ferramenta/acessar', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (!response.ok) {
        throw new Error('Erro ao gerar token de acesso')
      }
      
      const data = await response.json()
      
      // Salvar token do cliente no localStorage
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('user', JSON.stringify(data.cliente))
      localStorage.setItem('cliente', JSON.stringify(data.cliente))
      localStorage.setItem('from_admin', 'true')  // Marcar que veio do admin
      
      // Redirecionar para dashboard do cliente
      router.push('/dashboard')
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold text-gray-900">Minha Ferramenta</h1>
        <p className="text-gray-600 mt-1">
          Use sua própria ferramenta como cliente
        </p>
      </div>
      
      {/* Card Principal */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center gap-4 mb-6">
          <div className="text-6xl">🤖</div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              Teste sua ferramenta
            </h2>
            <p className="text-gray-600 mt-1">
              Conecte seu WhatsApp e venda seu produto usando a IA
            </p>
          </div>
        </div>
        
        {/* Status */}
        {status && (
          <div className="mb-6 p-4 bg-blue-50 rounded-lg">
            {status.existe ? (
              <div>
                <p className="text-sm font-medium text-blue-900 mb-2">
                  ✅ Cliente admin já criado
                </p>
                <div className="text-sm text-blue-700">
                  <p><strong>Nome:</strong> {status.cliente.nome}</p>
                  <p><strong>Email:</strong> {status.cliente.email}</p>
                  <p><strong>Status:</strong> {status.cliente.status}</p>
                </div>
              </div>
            ) : (
              <p className="text-sm text-blue-700">
                ℹ️ Cliente admin será criado automaticamente ao acessar
              </p>
            )}
          </div>
        )}
        
        {/* Erro */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}
        
        {/* Botão de Acesso */}
        <button
          onClick={acessarFerramenta}
          disabled={loading}
          className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white px-6 py-3 rounded-lg hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium text-lg"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Acessando...
            </span>
          ) : (
            '🚀 Acessar Minha Ferramenta'
          )}
        </button>
        
        {/* Informações */}
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-semibold text-gray-900 mb-3">O que você pode fazer:</h3>
          <ul className="space-y-2 text-sm text-gray-700">
            <li className="flex items-start gap-2">
              <span className="text-green-600">✓</span>
              <span>Conectar seu WhatsApp pessoal</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-600">✓</span>
              <span>Adicionar conhecimento sobre seu produto/serviço</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-600">✓</span>
              <span>Configurar tom e mensagens da IA</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-600">✓</span>
              <span>Ver conversas em tempo real</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-600">✓</span>
              <span>IA responde automaticamente seus clientes</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-600">✓</span>
              <span>Responder manualmente quando necessário</span>
            </li>
          </ul>
        </div>
        
        {/* Nota */}
        <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm text-yellow-800">
            <strong>Nota:</strong> Sua conta admin tem acesso ilimitado e gratuito à ferramenta. 
            Não há cobrança para você usar o sistema.
          </p>
        </div>
      </div>
    </div>
  )
}
