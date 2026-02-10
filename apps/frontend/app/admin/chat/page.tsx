'use client'

import { useState, useEffect } from 'react'

export default function AdminChatPage() {
  const [conversas, setConversas] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    carregarConversas()
    const interval = setInterval(carregarConversas, 5000)
    return () => clearInterval(interval)
  }, [])

  const carregarConversas = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      const response = await fetch('http://localhost:8000/api/v1/chat-suporte/admin/conversas', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (response.ok) {
        const data = await response.json()
        setConversas(data)
      }
    } catch (error) {
      console.error('Erro ao carregar conversas:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="p-6">Carregando...</div>
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Chat de Suporte</h1>

      {conversas.length === 0 ? (
        <div className="text-center text-gray-500 py-12">
          Nenhuma conversa ativa no momento
        </div>
      ) : (
        <div className="grid gap-4">
          {conversas.map((conv) => (
            <a
              key={conv.id}
              href={`/admin/chat/${conv.id}`}
              className="block bg-white p-4 rounded-lg shadow border hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold">
                    {conv.cliente_nome.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <h3 className="font-semibold">{conv.cliente_nome}</h3>
                    <p className="text-sm text-gray-500">
                      {conv.status === 'nao_respondido' ? '📥 Não respondido' : '💬 Respondido'}
                    </p>
                  </div>
                </div>
                {conv.mensagens_nao_vistas > 0 && (
                  <span className="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full">
                    {conv.mensagens_nao_vistas}
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-600 truncate">{conv.ultima_mensagem}</p>
              <p className="text-xs text-gray-400 mt-1">
                {new Date(conv.ultima_mensagem_em).toLocaleString('pt-BR')}
              </p>
            </a>
          ))}
        </div>
      )}
    </div>
  )
}
