'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'

export default function AdminChatConversaPage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const [mensagens, setMensagens] = useState<any[]>([])
  const [inputMensagem, setInputMensagem] = useState('')
  const [loading, setLoading] = useState(true)
  const [enviando, setEnviando] = useState(false)
  const [cliente, setCliente] = useState<any>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    carregarMensagens()
    const interval = setInterval(carregarMensagens, 5000) // Atualizar a cada 5s
    return () => clearInterval(interval)
  }, [params.id])

  useEffect(() => {
    scrollToBottom()
  }, [mensagens])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const carregarMensagens = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      const response = await fetch(`http://localhost:8000/api/v1/chat-suporte/admin/conversas/${params.id}/mensagens`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (response.ok) {
        const data = await response.json()
        setMensagens(data)
        
        // Buscar info do cliente se ainda não tiver
        if (!cliente && data.length > 0) {
          const conversasResponse = await fetch('http://localhost:8000/api/v1/chat-suporte/admin/conversas', {
            headers: { 'Authorization': `Bearer ${token}` }
          })
          if (conversasResponse.ok) {
            const conversas = await conversasResponse.json()
            const conv = conversas.find((c: any) => c.id === parseInt(params.id))
            if (conv) setCliente({ nome: conv.cliente_nome })
          }
        }
      }
    } catch (error) {
      console.error('Erro ao carregar mensagens:', error)
    } finally {
      setLoading(false)
    }
  }

  const enviarMensagem = async () => {
    if (!inputMensagem.trim() || enviando) return

    const mensagemTexto = inputMensagem.trim()
    setInputMensagem('')
    setEnviando(true)

    try {
      const token = localStorage.getItem('admin_token')
      const response = await fetch(`http://localhost:8000/api/v1/chat-suporte/admin/conversas/${params.id}/responder`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ mensagem: mensagemTexto })
      })

      if (response.ok) {
        carregarMensagens()
      }
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error)
    } finally {
      setEnviando(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      enviarMensagem()
    }
  }

  const encerrarConversa = async () => {
    if (!confirm('Deseja encerrar esta conversa?')) return

    try {
      const token = localStorage.getItem('admin_token')
      const response = await fetch(`http://localhost:8000/api/v1/chat-suporte/admin/conversas/${params.id}/encerrar`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (response.ok) {
        alert('Conversa encerrada!')
        router.push('/admin/chat')
      }
    } catch (error) {
      console.error('Erro ao encerrar conversa:', error)
    }
  }

  if (loading) {
    return <div className="p-6">Carregando...</div>
  }

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col">
      {/* Header */}
      <div className="bg-white border-b p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.push('/admin/chat')}
            className="text-gray-600 hover:text-gray-900"
          >
            ← Voltar
          </button>
          <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold">
            {cliente?.nome?.charAt(0).toUpperCase() || 'C'}
          </div>
          <div>
            <h2 className="font-semibold">{cliente?.nome || 'Cliente'}</h2>
            <p className="text-sm text-gray-500">{mensagens.length} mensagens</p>
          </div>
        </div>
        <button
          onClick={encerrarConversa}
          className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          Encerrar Conversa
        </button>
      </div>

      {/* Mensagens */}
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
        {mensagens.length === 0 ? (
          <div className="text-center text-gray-500 py-12">
            Nenhuma mensagem ainda
          </div>
        ) : (
          <div className="space-y-4 max-w-4xl mx-auto">
            {mensagens.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.remetente_tipo === 'admin' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[70%] rounded-lg p-3 ${
                    msg.remetente_tipo === 'admin'
                      ? 'bg-blue-600 text-white'
                      : msg.remetente_tipo === 'sistema'
                      ? 'bg-yellow-50 border border-yellow-200 text-yellow-800'
                      : 'bg-white border border-gray-200 text-gray-800'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{msg.mensagem}</p>
                  <p className="text-xs mt-1 opacity-75">
                    {new Date(msg.created_at).toLocaleTimeString('pt-BR', { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </p>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <div className="bg-white border-t p-4">
        <div className="max-w-4xl mx-auto flex gap-2">
          <input
            type="text"
            value={inputMensagem}
            onChange={(e) => setInputMensagem(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Digite sua resposta..."
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={enviando}
          />
          <button
            onClick={enviarMensagem}
            disabled={enviando || !inputMensagem.trim()}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white px-6 py-2 rounded-lg font-medium transition-colors"
          >
            {enviando ? 'Enviando...' : 'Enviar'}
          </button>
        </div>
      </div>
    </div>
  )
}
