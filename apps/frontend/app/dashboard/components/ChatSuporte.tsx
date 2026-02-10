'use client'

/**
 * ChatSuporte - Widget flutuante de chat com IA
 * Task 11.7
 */

import { useState, useEffect, useRef } from 'react'
import { X, Send, Paperclip, AlertCircle, Ticket } from 'lucide-react'

interface Mensagem {
  id: number
  remetente_tipo: 'cliente' | 'ia'
  mensagem: string
  confianca: number | null
  created_at: string
}

interface RespostaSuporte {
  resposta: string
  confianca: number
  deve_abrir_ticket: boolean
}

export default function ChatSuporte() {
  const [aberto, setAberto] = useState(false)
  const [mensagens, setMensagens] = useState<Mensagem[]>([])
  const [inputMensagem, setInputMensagem] = useState('')
  const [carregando, setCarregando] = useState(false)
  const [mostrarModalTicket, setMostrarModalTicket] = useState(false)
  const [deveAbrirTicket, setDeveAbrirTicket] = useState(false)
  const [adminStatus, setAdminStatus] = useState({ online: false, mensagem: 'Verificando...' })
  const [ultimoIdMensagem, setUltimoIdMensagem] = useState(0)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Verificar status do admin a cada 30 segundos
  useEffect(() => {
    if (aberto) {
      verificarStatusAdmin()
      const interval = setInterval(verificarStatusAdmin, 30000)
      return () => clearInterval(interval)
    }
  }, [aberto])

  const verificarStatusAdmin = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/chat-suporte/admin/status')
      if (response.ok) {
        const data = await response.json()
        setAdminStatus(data)
      }
    } catch (error) {
      console.error('Erro ao verificar status do admin:', error)
    }
  }

  // Carregar histórico ao abrir
  useEffect(() => {
    if (aberto) {
      carregarHistorico()
      const interval = setInterval(carregarHistorico, 5000) // Atualizar a cada 5s
      return () => clearInterval(interval)
    }
  }, [aberto])

  // Auto-scroll para última mensagem
  useEffect(() => {
    scrollToBottom()
  }, [mensagens])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const carregarHistorico = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/api/v1/chat-suporte/historico', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setMensagens(data.mensagens || [])
        setDeveAbrirTicket(data.deve_sugerir_ticket || false)
      }
    } catch (error) {
      console.error('Erro ao carregar histórico:', error)
    }
  }

  const enviarMensagem = async () => {
    if (!inputMensagem.trim() || carregando) return

    const mensagemTexto = inputMensagem.trim()
    setInputMensagem('')
    setCarregando(true)

    // Adicionar mensagem do cliente imediatamente na UI
    const novaMensagem: any = {
      id: Date.now(),
      remetente_tipo: 'cliente',
      mensagem: mensagemTexto,
      created_at: new Date().toISOString()
    }
    setMensagens(prev => [...prev, novaMensagem])

    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/api/v1/chat-suporte/mensagem', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ mensagem: mensagemTexto })
      })

      if (response.ok) {
        // Recarregar histórico após 6s para pegar mensagem automática
        setTimeout(() => {
          carregarHistorico()
        }, 6000)
      }
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error)
    } finally {
      setCarregando(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      enviarMensagem()
    }
  }

  const abrirModalTicket = () => {
    setMostrarModalTicket(true)
    setDeveAbrirTicket(false)
  }

  return (
    <>
      {/* Botão flutuante */}
      {!aberto && (
        <button
          onClick={() => setAberto(true)}
          className="fixed bottom-6 right-6 bg-purple-600 hover:bg-purple-700 text-white rounded-full p-4 shadow-lg transition-all duration-300 hover:scale-110 z-50"
          title="Abrir chat de suporte"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        </button>
      )}

      {/* Widget de chat */}
      {aberto && (
        <div className="fixed bottom-6 right-6 w-80 h-[500px] bg-white rounded-lg shadow-2xl flex flex-col z-50 border border-gray-200">
          {/* Header */}
          <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-3 rounded-t-lg flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center">
                <span className="text-xl">🤖</span>
              </div>
              <div>
                <h3 className="font-semibold text-sm">Suporte</h3>
                <div className="flex items-center gap-1.5 text-[10px] opacity-90">
                  <span className={`w-1.5 h-1.5 rounded-full ${adminStatus.online ? 'bg-green-400' : 'bg-gray-400'}`}></span>
                  <span>{adminStatus.mensagem}</span>
                </div>
              </div>
            </div>
            <button
              onClick={() => setAberto(false)}
              className="hover:bg-white/20 rounded-full p-1 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Mensagens */}
          <div className="flex-1 overflow-y-auto p-3 space-y-3 bg-gray-50">
            {mensagens.length === 0 && (
              <div className="text-center text-gray-500 mt-8">
                <p className="text-xs">👋 Olá! Como posso ajudar você hoje?</p>
              </div>
            )}

            {mensagens.map((msg: any) => (
              <div
                key={msg.id}
                className={`flex ${msg.remetente_tipo === 'cliente' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-2.5 ${
                    msg.remetente_tipo === 'cliente'
                      ? 'bg-purple-600 text-white'
                      : msg.remetente_tipo === 'sistema'
                      ? 'bg-blue-50 border border-blue-200 text-blue-800'
                      : 'bg-white border border-gray-200 text-gray-800'
                  }`}
                >
                  <p className="text-xs whitespace-pre-wrap">{msg.mensagem}</p>
                </div>
              </div>
            ))}

            {carregando && (
              <div className="flex justify-start">
                <div className="bg-white border border-gray-200 rounded-lg p-2.5">
                  <div className="flex gap-1">
                    <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Alerta para abrir ticket */}
          {deveAbrirTicket && (
            <div className="bg-yellow-50 border-t border-yellow-200 p-2.5">
              <div className="flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-yellow-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="text-xs text-yellow-800">
                    Não consegui responder com confiança. Deseja abrir um ticket?
                  </p>
                  <button
                    onClick={abrirModalTicket}
                    className="mt-1.5 text-xs bg-yellow-600 hover:bg-yellow-700 text-white px-2.5 py-1 rounded transition-colors"
                  >
                    <Ticket className="w-3 h-3 inline mr-1" />
                    Abrir Ticket
                  </button>
                </div>
                <button
                  onClick={() => setDeveAbrirTicket(false)}
                  className="text-yellow-600 hover:text-yellow-800"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            </div>
          )}

          {/* Input */}
          <div className="border-t border-gray-200 p-3 bg-white rounded-b-lg">
            <div className="flex gap-2">
              <input
                type="text"
                value={inputMensagem}
                onChange={(e) => setInputMensagem(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Digite sua mensagem..."
                className="flex-1 border border-gray-300 rounded-lg px-2.5 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-purple-500"
                disabled={carregando}
              />
              <button
                onClick={enviarMensagem}
                disabled={carregando || !inputMensagem.trim()}
                className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-300 text-white rounded-lg px-3 py-1.5 transition-colors"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de criar ticket */}
      {mostrarModalTicket && (
        <ModalCriarTicket
          onClose={() => setMostrarModalTicket(false)}
          mensagemInicial={mensagens[mensagens.length - 2]?.mensagem || ''}
        />
      )}
    </>
  )
}

// Modal de criar ticket
function ModalCriarTicket({ onClose, mensagemInicial }: { onClose: () => void, mensagemInicial: string }) {
  const [assunto, setAssunto] = useState('')
  const [categoria, setCategoria] = useState('')
  const [descricao, setDescricao] = useState(mensagemInicial)
  const [anexos, setAnexos] = useState<File[]>([])
  const [enviando, setEnviando] = useState(false)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const novosAnexos = Array.from(e.target.files).slice(0, 10 - anexos.length)
      setAnexos(prev => [...prev, ...novosAnexos])
    }
  }

  const removerAnexo = (index: number) => {
    setAnexos(prev => prev.filter((_, i) => i !== index))
  }

  const enviarTicket = async () => {
    if (!assunto.trim() || !descricao.trim()) {
      alert('Preencha assunto e descrição')
      return
    }

    setEnviando(true)

    try {
      // TODO: Implementar upload de anexos
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/api/v1/tickets', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          assunto,
          mensagem: descricao,
          categoria_id: categoria ? parseInt(categoria) : null
        })
      })

      if (response.ok) {
        alert('Ticket criado com sucesso!')
        onClose()
      } else {
        alert('Erro ao criar ticket')
      }
    } catch (error) {
      console.error('Erro ao criar ticket:', error)
      alert('Erro ao criar ticket')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[60]">
      <div className="bg-white rounded-lg p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-semibold">Abrir Ticket de Suporte</h3>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Assunto *
            </label>
            <input
              type="text"
              value={assunto}
              onChange={(e) => setAssunto(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Resumo do problema"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Categoria
            </label>
            <select
              value={categoria}
              onChange={(e) => setCategoria(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="">Selecione...</option>
              <option value="1">Técnico</option>
              <option value="2">Financeiro</option>
              <option value="3">Dúvida</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Descrição *
            </label>
            <textarea
              value={descricao}
              onChange={(e) => setDescricao(e.target.value)}
              rows={5}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Descreva seu problema em detalhes..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Anexos (máximo 10)
            </label>
            <input
              type="file"
              multiple
              accept="image/*"
              onChange={handleFileChange}
              disabled={anexos.length >= 10}
              className="w-full text-sm"
            />
            {anexos.length > 0 && (
              <div className="mt-2 space-y-1">
                {anexos.map((file, index) => (
                  <div key={index} className="flex items-center justify-between bg-gray-50 p-2 rounded">
                    <span className="text-sm text-gray-700 truncate">{file.name}</span>
                    <button
                      onClick={() => removerAnexo(index)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="flex gap-3 pt-4">
            <button
              onClick={onClose}
              className="flex-1 border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancelar
            </button>
            <button
              onClick={enviarTicket}
              disabled={enviando}
              className="flex-1 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-300 text-white px-4 py-2 rounded-lg transition-colors"
            >
              {enviando ? 'Enviando...' : 'Criar Ticket'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
