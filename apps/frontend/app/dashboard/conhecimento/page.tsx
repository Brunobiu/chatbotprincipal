'use client'

import { useEffect, useState } from 'react'

export default function ConhecimentoPage() {
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })
  const [progress, setProgress] = useState(0)
  
  const [conteudo, setConteudo] = useState('')
  const [maxChars] = useState(50000)
  
  // Modal de confirmação de senha
  const [showModalSenha, setShowModalSenha] = useState(false)
  const [senha, setSenha] = useState('')
  
  // Modal de IA
  const [showModalIA, setShowModalIA] = useState(false)
  const [textoIA, setTextoIA] = useState('')
  const [textoMelhorado, setTextoMelhorado] = useState('')
  const [melhorandoIA, setMelhorandoIA] = useState(false)
  
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
    
    // Abrir modal de senha
    setShowModalSenha(true)
  }
  
  const handleConfirmarSenha = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!senha) {
      setMessage({ type: 'error', text: 'Digite sua senha para confirmar' })
      return
    }
    
    setSaving(true)
    setProgress(0)
    
    // Simular progresso enquanto processa
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 90) return prev // Para em 90% até terminar de verdade
        return prev + 10
      })
    }, 3000) // Incrementa a cada 3 segundos
    
    try {
      const token = localStorage.getItem('token')
      
      if (!token) {
        throw new Error('Você não está autenticado. Faça login novamente.')
      }
      
      // Timeout de 120 segundos (geração de embeddings pode demorar)
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 120000)
      
      const response = await fetch('http://localhost:8000/api/v1/knowledge', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          conteudo_texto: conteudo,
          senha: senha
        }),
        signal: controller.signal
      })
      
      clearTimeout(timeoutId)
      clearInterval(progressInterval)
      setProgress(100)
      
      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Erro ao salvar conhecimento')
      }
      
      setMessage({ type: 'success', text: '✅ Conhecimento salvo e embeddings gerados com sucesso!' })
      setShowModalSenha(false)
      setSenha('')
      
      // Limpar mensagem após 5 segundos
      setTimeout(() => {
        setMessage({ type: '', text: '' })
        setProgress(0)
      }, 5000)
      
    } catch (err: any) {
      clearInterval(progressInterval)
      setProgress(0)
      
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
  
  const handleFecharModalSenha = () => {
    setShowModalSenha(false)
    setSenha('')
  }
  
  const handleAbrirModalIA = () => {
    setShowModalIA(true)
    setTextoIA('')
    setTextoMelhorado('')
  }
  
  const handleFecharModalIA = () => {
    setShowModalIA(false)
    setTextoIA('')
    setTextoMelhorado('')
  }
  
  const handleMelhorarComIA = async () => {
    if (!textoIA.trim()) {
      setMessage({ type: 'error', text: 'Digite um texto para melhorar' })
      return
    }
    
    setMelhorandoIA(true)
    setMessage({ type: '', text: '' })
    
    try {
      const token = localStorage.getItem('token')
      
      const response = await fetch('http://localhost:8000/api/v1/knowledge/melhorar-ia', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          texto: textoIA
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        setTextoMelhorado(data.texto_melhorado)
      } else {
        const error = await response.json()
        setMessage({ type: 'error', text: error.detail || 'Erro ao melhorar texto' })
      }
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Erro ao melhorar texto' })
    } finally {
      setMelhorandoIA(false)
    }
  }
  
  const handleAdicionarTextoIA = () => {
    if (textoMelhorado) {
      // Adicionar ao final do conteúdo existente
      setConteudo(prev => {
        if (prev.trim()) {
          return prev + '\n\n' + textoMelhorado
        }
        return textoMelhorado
      })
      handleFecharModalIA()
      setMessage({ type: 'success', text: '✅ Texto da IA adicionado! Não esqueça de salvar.' })
      setTimeout(() => setMessage({ type: '', text: '' }), 5000)
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
        <div className="flex justify-end gap-3">
          <button
            type="button"
            onClick={handleAbrirModalIA}
            className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition-all flex items-center gap-2"
          >
            <span>🤖</span>
            <span>Deixa que a IA te ajuda</span>
          </button>
          
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
                Salvando e gerando embeddings... {progress}%
              </span>
            ) : (
              'Salvar Conhecimento'
            )}
          </button>
        </div>
        
        {/* Barra de progresso durante salvamento */}
        {saving && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center gap-3 mb-2">
              <svg className="animate-spin h-5 w-5 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <div className="flex-1">
                <p className="text-sm font-medium text-blue-900">
                  Processando conhecimento...
                </p>
                <p className="text-xs text-blue-700 mt-1">
                  {progress < 30 && '📝 Salvando texto no banco de dados...'}
                  {progress >= 30 && progress < 60 && '✂️ Dividindo em chunks inteligentes...'}
                  {progress >= 60 && progress < 90 && '🧠 Gerando embeddings com IA...'}
                  {progress >= 90 && '💾 Salvando no ChromaDB...'}
                </p>
              </div>
              <span className="text-sm font-semibold text-blue-600">{progress}%</span>
            </div>
            <div className="w-full bg-blue-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="text-xs text-blue-600 mt-2">
              ⏱️ Isso pode levar até 2 minutos dependendo do tamanho do texto
            </p>
          </div>
        )}
      </form>
      
      {/* Modal de Confirmação de Senha */}
      {showModalSenha && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold mb-4">Confirmar Salvamento</h3>
            <p className="text-gray-600 mb-4">
              Por segurança, digite sua senha para confirmar o salvamento do conhecimento.
            </p>
            
            <form onSubmit={handleConfirmarSenha}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Senha
                </label>
                <input
                  type="password"
                  value={senha}
                  onChange={(e) => setSenha(e.target.value)}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                  placeholder="Digite sua senha"
                  autoFocus
                />
              </div>
              
              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={saving}
                  className="flex-1 bg-gray-900 text-white px-4 py-2 rounded-lg hover:bg-gray-700 disabled:opacity-50 transition-all"
                >
                  {saving ? 'Salvando...' : 'Confirmar'}
                </button>
                <button
                  type="button"
                  onClick={handleFecharModalSenha}
                  disabled={saving}
                  className="flex-1 bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 disabled:opacity-50 transition-all"
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      
      {/* Modal de IA */}
      {showModalIA && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold flex items-center gap-2">
                  <span>🤖</span>
                  <span>Deixa que a IA te ajuda</span>
                </h3>
                <button
                  onClick={handleFecharModalIA}
                  className="text-gray-500 hover:text-gray-700 text-2xl"
                >
                  ×
                </button>
              </div>
              
              <p className="text-gray-600 mb-4">
                Digite seu texto de qualquer forma e a IA vai estruturar e melhorar para você!
              </p>
              
              {/* Textarea para texto original */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Seu texto (pode ser bagunçado, a IA organiza!)
                </label>
                <textarea
                  value={textoIA}
                  onChange={(e) => setTextoIA(e.target.value)}
                  className="w-full px-4 py-3 border rounded-lg font-mono text-sm"
                  rows={8}
                  placeholder="Digite aqui... Exemplo:
                  
vendemos pizza margherita 35 reais
calabresa 40 reais
entregamos de segunda a sabado das 18h as 23h
domingo nao abrimos
aceitamos pix cartao dinheiro"
                />
              </div>
              
              {/* Botão Melhorar */}
              <div className="mb-4">
                <button
                  onClick={handleMelhorarComIA}
                  disabled={melhorandoIA || !textoIA.trim()}
                  className="w-full bg-purple-600 text-white px-4 py-3 rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-all"
                >
                  {melhorandoIA ? (
                    <span className="flex items-center justify-center gap-2">
                      <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Melhorando com IA...
                    </span>
                  ) : (
                    '✨ Melhorar com IA'
                  )}
                </button>
              </div>
              
              {/* Preview do texto melhorado */}
              {textoMelhorado && (
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Texto melhorado pela IA
                  </label>
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <pre className="whitespace-pre-wrap font-sans text-sm text-gray-800">
                      {textoMelhorado}
                    </pre>
                  </div>
                  
                  <div className="flex gap-3 mt-4">
                    <button
                      onClick={handleAdicionarTextoIA}
                      className="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-all"
                    >
                      ✅ Adicionar texto da IA
                    </button>
                    <button
                      onClick={() => setTextoMelhorado('')}
                      className="flex-1 bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 transition-all"
                    >
                      🔄 Tentar novamente
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
