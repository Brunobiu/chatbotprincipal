'use client'

import { useEffect, useState } from 'react'

export default function ConfiguracoesPage() {
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })
  
  const [config, setConfig] = useState({
    tom: 'casual',
    mensagem_saudacao: '',
    mensagem_fallback: '',
    mensagem_espera: '',
    mensagem_retorno_24h: ''
  })
  
  useEffect(() => {
    carregarConfiguracoes()
  }, [])
  
  const carregarConfiguracoes = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/api/v1/config', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setConfig(data)
      }
    } catch (err) {
      console.error('Erro ao carregar configurações:', err)
    } finally {
      setLoading(false)
    }
  }
  
  const handleSalvar = async (e: React.FormEvent) => {
    e.preventDefault()
    setMessage({ type: '', text: '' })
    setSaving(true)
    
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/api/v1/config', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(config)
      })
      
      if (!response.ok) {
        throw new Error('Erro ao salvar configurações')
      }
      
      setMessage({ type: 'success', text: 'Configurações salvas com sucesso!' })
      
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message })
    } finally {
      setSaving(false)
    }
  }
  
  if (loading) {
    return <div>Carregando...</div>
  }
  
  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Configurações do Bot</h1>
      
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
        
        {/* Tom das Mensagens */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Tom das Mensagens</h2>
          <p className="text-gray-600 mb-4">
            Escolha como o bot deve se comunicar com seus clientes
          </p>
          
          <div className="space-y-3">
            <label className="flex items-center gap-3 p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
              <input
                type="radio"
                name="tom"
                value="formal"
                checked={config.tom === 'formal'}
                onChange={(e) => setConfig({ ...config, tom: e.target.value })}
                className="w-4 h-4"
              />
              <div>
                <div className="font-medium">Formal</div>
                <div className="text-sm text-gray-600">Linguagem profissional e respeitosa</div>
              </div>
            </label>
            
            <label className="flex items-center gap-3 p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
              <input
                type="radio"
                name="tom"
                value="casual"
                checked={config.tom === 'casual'}
                onChange={(e) => setConfig({ ...config, tom: e.target.value })}
                className="w-4 h-4"
              />
              <div>
                <div className="font-medium">Casual</div>
                <div className="text-sm text-gray-600">Linguagem amigável e descontraída</div>
              </div>
            </label>
            
            <label className="flex items-center gap-3 p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
              <input
                type="radio"
                name="tom"
                value="tecnico"
                checked={config.tom === 'tecnico'}
                onChange={(e) => setConfig({ ...config, tom: e.target.value })}
                className="w-4 h-4"
              />
              <div>
                <div className="font-medium">Técnico</div>
                <div className="text-sm text-gray-600">Linguagem especializada e precisa</div>
              </div>
            </label>
          </div>
        </div>
        
        {/* Mensagens Personalizadas */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Mensagens Personalizadas</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Mensagem de Saudação
              </label>
              <textarea
                value={config.mensagem_saudacao}
                onChange={(e) => setConfig({ ...config, mensagem_saudacao: e.target.value })}
                className="w-full px-3 py-2 border rounded h-20"
                placeholder="Olá! 👋 Como posso ajudar você hoje?"
              />
              <p className="text-xs text-gray-500 mt-1">
                Primeira mensagem enviada quando o cliente inicia uma conversa
              </p>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">
                Mensagem de Fallback
              </label>
              <textarea
                value={config.mensagem_fallback}
                onChange={(e) => setConfig({ ...config, mensagem_fallback: e.target.value })}
                className="w-full px-3 py-2 border rounded h-20"
                placeholder="Desculpe, não tenho informações sobre isso..."
              />
              <p className="text-xs text-gray-500 mt-1">
                Enviada quando o bot não sabe responder (confiança baixa)
              </p>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">
                Mensagem de Espera
              </label>
              <textarea
                value={config.mensagem_espera}
                onChange={(e) => setConfig({ ...config, mensagem_espera: e.target.value })}
                className="w-full px-3 py-2 border rounded h-20"
                placeholder="Aguarde um momento..."
              />
              <p className="text-xs text-gray-500 mt-1">
                Enviada enquanto o bot processa a resposta
              </p>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">
                Mensagem de Retorno (24h)
              </label>
              <textarea
                value={config.mensagem_retorno_24h}
                onChange={(e) => setConfig({ ...config, mensagem_retorno_24h: e.target.value })}
                className="w-full px-3 py-2 border rounded h-20"
                placeholder="Olá! Notei que você tinha uma dúvida..."
              />
              <p className="text-xs text-gray-500 mt-1">
                Enviada automaticamente após 24h sem resposta humana
              </p>
            </div>
          </div>
        </div>
        
        {/* Botão Salvar */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="bg-gray-900 text-white px-6 py-3 rounded-lg hover:bg-gray-700 disabled:opacity-50"
          >
            {saving ? 'Salvando...' : 'Salvar Configurações'}
          </button>
        </div>
      </form>
    </div>
  )
}
