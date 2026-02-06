'use client'

import { useEffect, useState } from 'react'

export default function PerfilPage() {
  const [cliente, setCliente] = useState<any>(null)
  const [senhaAtual, setSenhaAtual] = useState('')
  const [novaSenha, setNovaSenha] = useState('')
  const [confirmarSenha, setConfirmarSenha] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })
  
  useEffect(() => {
    const clienteData = localStorage.getItem('cliente')
    if (clienteData) {
      setCliente(JSON.parse(clienteData))
    }
  }, [])
  
  const handleTrocarSenha = async (e: React.FormEvent) => {
    e.preventDefault()
    setMessage({ type: '', text: '' })
    
    if (novaSenha !== confirmarSenha) {
      setMessage({ type: 'error', text: 'As senhas não coincidem' })
      return
    }
    
    if (novaSenha.length < 6) {
      setMessage({ type: 'error', text: 'A senha deve ter no mínimo 6 caracteres' })
      return
    }
    
    setLoading(true)
    
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/api/v1/auth/trocar-senha', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          senha_atual: senhaAtual,
          nova_senha: novaSenha
        })
      })
      
      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Erro ao trocar senha')
      }
      
      setMessage({ type: 'success', text: 'Senha alterada com sucesso!' })
      setSenhaAtual('')
      setNovaSenha('')
      setConfirmarSenha('')
      
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message })
    } finally {
      setLoading(false)
    }
  }
  
  if (!cliente) {
    return <div>Carregando...</div>
  }
  
  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Meu Perfil</h1>
      
      {/* Dados do Cliente */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Informações da Conta</h2>
        <div className="space-y-3">
          <div>
            <label className="text-sm text-gray-600">Email</label>
            <p className="font-medium">{cliente.email}</p>
          </div>
          <div>
            <label className="text-sm text-gray-600">Nome</label>
            <p className="font-medium">{cliente.nome || 'Não informado'}</p>
          </div>
          <div>
            <label className="text-sm text-gray-600">Telefone</label>
            <p className="font-medium">{cliente.telefone || 'Não informado'}</p>
          </div>
          <div>
            <label className="text-sm text-gray-600">Status</label>
            <p className="font-medium text-green-600">Ativo</p>
          </div>
        </div>
      </div>
      
      {/* Trocar Senha */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Alterar Senha</h2>
        
        <form onSubmit={handleTrocarSenha} className="space-y-4 max-w-md">
          {message.text && (
            <div className={`p-4 rounded ${
              message.type === 'success' 
                ? 'bg-green-50 text-green-700 border border-green-200' 
                : 'bg-red-50 text-red-700 border border-red-200'
            }`}>
              {message.text}
            </div>
          )}
          
          <div>
            <label className="block text-sm font-medium mb-2">Senha Atual</label>
            <input
              type="password"
              value={senhaAtual}
              onChange={(e) => setSenhaAtual(e.target.value)}
              className="w-full px-3 py-2 border rounded"
              required
              disabled={loading}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Nova Senha</label>
            <input
              type="password"
              value={novaSenha}
              onChange={(e) => setNovaSenha(e.target.value)}
              className="w-full px-3 py-2 border rounded"
              required
              disabled={loading}
              minLength={6}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Confirmar Nova Senha</label>
            <input
              type="password"
              value={confirmarSenha}
              onChange={(e) => setConfirmarSenha(e.target.value)}
              className="w-full px-3 py-2 border rounded"
              required
              disabled={loading}
              minLength={6}
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="bg-gray-900 text-white px-6 py-2 rounded hover:bg-gray-700 disabled:opacity-50"
          >
            {loading ? 'Alterando...' : 'Alterar Senha'}
          </button>
        </form>
      </div>
    </div>
  )
}
