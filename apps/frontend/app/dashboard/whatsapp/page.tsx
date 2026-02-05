'use client'

import { useEffect, useState } from 'react'

export default function WhatsAppPage() {
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [instancia, setInstancia] = useState<any>(null)
  const [qrCode, setQrCode] = useState<string | null>(null)
  const [status, setStatus] = useState<string>('pendente')
  const [message, setMessage] = useState({ type: '', text: '' })
  
  useEffect(() => {
    carregarInstancia()
  }, [])
  
  useEffect(() => {
    // Polling de status a cada 5 segundos se estiver pendente
    if (instancia && status === 'pendente') {
      const interval = setInterval(() => {
        atualizarStatus()
      }, 5000)
      
      return () => clearInterval(interval)
    }
  }, [instancia, status])
  
  const carregarInstancia = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/api/v1/whatsapp/instance', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setInstancia(data)
        setStatus(data.status)
        
        // Se pendente, buscar QR code
        if (data.status === 'pendente') {
          buscarQRCode()
        }
      } else if (response.status === 404) {
        // Instância não existe ainda
        setInstancia(null)
      }
    } catch (err) {
      console.error('Erro ao carregar instância:', err)
    } finally {
      setLoading(false)
    }
  }
  
  const criarInstancia = async () => {
    setMessage({ type: '', text: '' })
    setCreating(true)
    
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/api/v1/whatsapp/instance', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (!response.ok) {
        throw new Error('Erro ao criar instância')
      }
      
      const data = await response.json()
      setInstancia(data)
      setStatus(data.status)
      setMessage({ type: 'success', text: 'Instância criada! Aguarde o QR Code...' })
      
      // Buscar QR code
      setTimeout(() => buscarQRCode(), 2000)
      
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message })
    } finally {
      setCreating(false)
    }
  }
  
  const buscarQRCode = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/api/v1/whatsapp/qrcode', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        if (data.qrcode) {
          setQrCode(data.qrcode)
        }
      }
    } catch (err) {
      console.error('Erro ao buscar QR code:', err)
    }
  }
  
  const atualizarStatus = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/api/v1/whatsapp/status', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setStatus(data.status)
        
        if (data.status === 'conectada') {
          setMessage({ type: 'success', text: 'WhatsApp conectado com sucesso!' })
          setQrCode(null)
        }
      }
    } catch (err) {
      console.error('Erro ao atualizar status:', err)
    }
  }
  
  const desconectar = async () => {
    if (!confirm('Deseja realmente desconectar o WhatsApp?')) {
      return
    }
    
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/api/v1/whatsapp/instance', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        setStatus('desconectada')
        setMessage({ type: 'success', text: 'WhatsApp desconectado' })
      }
    } catch (err: any) {
      setMessage({ type: 'error', text: 'Erro ao desconectar' })
    }
  }
  
  if (loading) {
    return <div>Carregando...</div>
  }
  
  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Conectar WhatsApp</h1>
      
      {message.text && (
        <div className={`p-4 rounded mb-6 ${
          message.type === 'success' 
            ? 'bg-green-50 text-green-700 border border-green-200' 
            : 'bg-red-50 text-red-700 border border-red-200'
        }`}>
          {message.text}
        </div>
      )}
      
      {/* Sem instância */}
      {!instancia && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-center py-8">
            <div className="text-6xl mb-4">📱</div>
            <h2 className="text-2xl font-semibold mb-2">Conecte seu WhatsApp</h2>
            <p className="text-gray-600 mb-6">
              Crie uma instância para conectar seu número do WhatsApp
            </p>
            <button
              onClick={criarInstancia}
              disabled={creating}
              className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              {creating ? 'Criando...' : 'Criar Instância'}
            </button>
          </div>
        </div>
      )}
      
      {/* Instância pendente - mostrar QR */}
      {instancia && status === 'pendente' && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-center">
            <h2 className="text-2xl font-semibold mb-4">Escaneie o QR Code</h2>
            <p className="text-gray-600 mb-6">
              Abra o WhatsApp no seu celular e escaneie o código abaixo
            </p>
            
            {qrCode ? (
              <div className="flex justify-center mb-6">
                <img 
                  src={qrCode} 
                  alt="QR Code" 
                  className="border-4 border-gray-300 rounded-lg"
                  style={{ width: '300px', height: '300px' }}
                />
              </div>
            ) : (
              <div className="flex justify-center mb-6">
                <div className="w-64 h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                  <div className="text-gray-400">Carregando QR Code...</div>
                </div>
              </div>
            )}
            
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-left max-w-md mx-auto">
              <h3 className="font-semibold mb-2">Como escanear:</h3>
              <ol className="text-sm text-gray-700 space-y-1 list-decimal list-inside">
                <li>Abra o WhatsApp no seu celular</li>
                <li>Toque em Mais opções (⋮) ou Configurações</li>
                <li>Toque em Aparelhos conectados</li>
                <li>Toque em Conectar um aparelho</li>
                <li>Aponte seu celular para esta tela</li>
              </ol>
            </div>
          </div>
        </div>
      )}
      
      {/* Instância conectada */}
      {instancia && status === 'conectada' && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-center py-8">
            <div className="text-6xl mb-4">✅</div>
            <h2 className="text-2xl font-semibold mb-2 text-green-600">WhatsApp Conectado!</h2>
            <p className="text-gray-600 mb-6">
              Seu bot está pronto para receber e responder mensagens
            </p>
            
            {instancia.numero && (
              <div className="bg-gray-50 rounded-lg p-4 mb-6 max-w-md mx-auto">
                <p className="text-sm text-gray-600">Número conectado:</p>
                <p className="text-lg font-semibold">{instancia.numero}</p>
              </div>
            )}
            
            <button
              onClick={desconectar}
              className="bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700"
            >
              Desconectar WhatsApp
            </button>
          </div>
        </div>
      )}
      
      {/* Instância desconectada */}
      {instancia && status === 'desconectada' && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-center py-8">
            <div className="text-6xl mb-4">⚠️</div>
            <h2 className="text-2xl font-semibold mb-2 text-orange-600">WhatsApp Desconectado</h2>
            <p className="text-gray-600 mb-6">
              Sua instância foi desconectada. Reconecte para voltar a usar o bot.
            </p>
            <button
              onClick={() => {
                setStatus('pendente')
                buscarQRCode()
              }}
              className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700"
            >
              Reconectar
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
