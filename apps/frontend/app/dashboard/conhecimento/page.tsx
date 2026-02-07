'use client'

import { useEffect, useState } from 'react'

export default function ConhecimentoPage() {
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })
  
  const [conteudo, setConteudo] = useState('')
  const [maxChars] = useState(50000)
  
  useEffect(() => {
    carregarConhecimento()
  }, [])
  
  const carregarConhecimento = async () => {
    try {
      const token = localStorage.getItem('token')
      
      if (!token) {
        console.error('Token não encontrado no localStorage')
        setLoading(false)
        return
      }
      
      const response = await fetch('http://localhost:8000/api/v1/knowledge', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setConteudo(data.conteudo_texto || '')
      } else {
        console.error('Erro ao carregar conhecimento:', response.status)
        // Se token inválido, redirecionar para login
        if (response.status === 401) {
          localStorage.removeItem('token')
          localStorage.removeItem('cliente')
          window.location.href = '/login'
        }
      }
    } catch (err) {
      console.error('Erro ao carregar conhecimento:', err)
    } finally {
      setLoading(false)
    }
  }
  
  const handleSalvar = async (e: React.FormEvent) => {
    e.preventDefault()
    setMessage({ type: '', text: '' })
    
    if (conteudo.length > maxChars) {
      setMessage({ 
        type: 'error', 
        text: `O conteúdo excede o limite de ${maxChars.toLocaleString()} caracteres` 
      })
      return
    }
    
    setSaving(true)
    
    try {
      const token = localStorage.getItem('token')
      
      if (!token) {
        throw new Error('Você não está autenticado. Faça login novamente.')
      }
      
      // Timeout de 60 segundos (geração de embeddings pode demorar)
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 60000)
      
      const response = await fetch('http://localhost:8000/api/v1/knowledge', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          conteudo_texto: conteudo
        }),
        signal: controller.signal
      })
      
      clearTimeout(timeoutId)
      
      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Erro ao salvar conhecimento')
      }
      
      setMessage({ type: 'success', text: '✅ Conhecimento salvo com sucesso!' })
      
      // Limpar mensagem após 5 segundos
      setTimeout(() => {
        setMessage({ type: '', text: '' })
      }, 5000)
      
    } catch (err: any) {
      if (err.name === 'AbortError') {
        setMessage({ 
          type: 'error', 
          text: 'Timeout: A operação demorou muito. Tente novamente ou reduza o tamanho do texto.' 
        })
      } else {
        setMessage({ type: 'error', text: err.message || 'Erro ao salvar conhecimento' })
      }
    } finally {
      setSaving(false)
    }
  }
  
  const charsRestantes = maxChars - conteudo.length
  const percentUsed = (conteudo.length / maxChars) * 100
  
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando conhecimento...</p>
        </div>
      </div>
    )
  }
  
  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Base de Conhecimento</h1>
      
      <form onSubmit={handleSalvar} className="space-y-6">
        {message.text && (
          <div className={`p-4 rounded ${
            message.type === 'success' 
              ? 'bg-green-50 text-green-700 border border-green-200' 
              : 'bg-red-50 text-red-700 border border-red-200'
          }`}>
            {message.text}
          </div>
        )}
        
        {/* Info Card */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold mb-2">💡 Como funciona</h3>
          <ul className="text-sm text-gray-700 space-y-1">
            <li>• Adicione até 50.000 caracteres de informações sobre seu negócio</li>
            <li>• O bot usará esse conhecimento para responder perguntas dos clientes</li>
            <li>• Quanto mais detalhado, melhores serão as respostas</li>
            <li>• O texto será automaticamente dividido em chunks para processamento</li>
            <li>• ⚠️ Embeddings temporariamente desabilitados (FASE 11 em desenvolvimento)</li>
          </ul>
        </div>
        
        {/* Editor */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Conteúdo</h2>
            <div className="text-sm">
              <span className={`font-medium ${
                charsRestantes < 5000 ? 'text-red-600' : 
                charsRestantes < 10000 ? 'text-orange-600' : 
                'text-gray-600'
              }`}>
                {conteudo.length.toLocaleString()} / {maxChars.toLocaleString()}
              </span>
              <span className="text-gray-500 ml-2">
                ({charsRestantes.toLocaleString()} restantes)
              </span>
            </div>
          </div>
          
          {/* Progress Bar */}
          <div className="mb-4">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className={`h-2 rounded-full transition-all ${
                  percentUsed >= 100 ? 'bg-red-600' :
                  percentUsed >= 90 ? 'bg-orange-600' :
                  percentUsed >= 70 ? 'bg-yellow-600' :
                  'bg-green-600'
                }`}
                style={{ width: `${Math.min(percentUsed, 100)}%` }}
              />
            </div>
          </div>
          
          <textarea
            value={conteudo}
            onChange={(e) => setConteudo(e.target.value)}
            className="w-full px-4 py-3 border rounded-lg font-mono text-sm"
            rows={20}
            placeholder="Digite aqui o conhecimento do seu bot...

Exemplo:
- Informações sobre produtos e serviços
- Horários de funcionamento
- Políticas de devolução
- Perguntas frequentes
- Procedimentos internos
- etc."
          />
          
          <p className="text-xs text-gray-500 mt-2">
            Dica: Organize o conteúdo em tópicos claros para facilitar o entendimento do bot
          </p>
        </div>
        
        {/* Botão Salvar */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={saving || conteudo.length > maxChars}
            className="bg-gray-900 text-white px-6 py-3 rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            {saving ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Salvando...
              </span>
            ) : (
              'Salvar Conhecimento'
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
