'use client'

import { useEffect, useState } from 'react'

interface Cliente {
  id: number
  nome: string
  email: string
  telefone: string | null
  status: string
}

export default function PerfilPage() {
  const [loading, setLoading] = useState(true)
  const [cliente, setCliente] = useState<Cliente | null>(null)
  const [editando, setEditando] = useState(false)
  const [salvando, setSalvando] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })
  
  // Modal de confirmação de senha
  const [showModal, setShowModal] = useState(false)
  const [senhaConfirmacao, setSenhaConfirmacao] = useState('')
  
  // Dados do formulário
  const [formData, setFormData] = useState({
    nome: '',
    email: '',
    telefone: ''
  })
  
  useEffect(() => {
    carregarPerfil()
  }, [])
  
  const carregarPerfil = async () => {
    try {
      const token = localStorage.getItem('token')
      
      if (!token) {
        window.location.href = '/login'
        return
      }
      
      const response = await fetch('http://localhost:8000/api/v1/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setCliente(data)
        setFormData({
          nome: data.nome,
          email: data.email,
          telefone: data.telefone || ''
        })
      } else if (response.status === 401) {
        localStorage.removeItem('token')
        localStorage.removeItem('cliente')
        window.location.href = '/login'
      }
    } catch (err) {
      console.error('Erro ao carregar perfil:', err)
    } finally {
      setLoading(false)
    }
  }
  
  const handleEditar = () => {
    setEditando(true)
    setMessage({ type: '', text: '' })
  }
  
  const handleCancelar = () => {
    setEditando(false)
    if (cliente) {
      setFormData({
        nome: cliente.nome,
        email: cliente.email,
        telefone: cliente.telefone || ''
      })
    }
    setMessage({ type: '', text: '' })
  }
  
  const handleSalvar = () => {
    // Validações
    if (!formData.nome.trim()) {
      setMessage({ type: 'error', text: 'Nome é obrigatório' })
      return
    }
    
    if (!formData.email.trim()) {
      setMessage({ type: 'error', text: 'Email é obrigatório' })
      return
    }
    
    // Abrir modal de confirmação de senha
    setShowModal(true)
  }
  
  const handleConfirmarSenha = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!senhaConfirmacao) {
      setMessage({ type: 'error', text: 'Digite sua senha para confirmar' })
      return
    }
    
    setSalvando(true)
    setMessage({ type: '', text: '' })
    
    try {
      const token = localStorage.getItem('token')
      
      const response = await fetch('http://localhost:8000/api/v1/auth/perfil', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          nome: formData.nome,
          email: formData.email,
          telefone: formData.telefone || null,
          senha_confirmacao: senhaConfirmacao
        })
      })
      
      const data = await response.json()
      
      if (response.ok) {
        setCliente(data)
        setEditando(false)
        setShowModal(false)
        setSenhaConfirmacao('')
        setMessage({ type: 'success', text: '✅ Perfil atualizado com sucesso!' })
        
        // Limpar mensagem após 5 segundos
        setTimeout(() => {
          setMessage({ type: '', text: '' })
        }, 5000)
      } else {
        setMessage({ type: 'error', text: data.detail || 'Erro ao atualizar perfil' })
      }
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Erro ao atualizar perfil' })
    } finally {
      setSalvando(false)
    }
  }
  
  const handleFecharModal = () => {
    setShowModal(false)
    setSenhaConfirmacao('')
  }
  
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando perfil...</p>
        </div>
      </div>
    )
  }
  
  if (!cliente) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Erro ao carregar perfil</p>
      </div>
    )
  }
  
  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Meu Perfil</h1>
      
      {message.text && (
        <div className={`mb-6 p-4 rounded ${
          message.type === 'success' 
            ? 'bg-green-50 text-green-700 border border-green-200' 
            : 'bg-red-50 text-red-700 border border-red-200'
        }`}>
          {message.text}
        </div>
      )}
      
      <div className="bg-white rounded-lg shadow p-6 max-w-2xl">
        <div className="space-y-6">
          {/* Nome */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nome
            </label>
            {editando ? (
              <input
                type="text"
                value={formData.nome}
                onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                placeholder="Seu nome"
              />
            ) : (
              <p className="text-gray-900">{cliente.nome}</p>
            )}
          </div>
          
          {/* Email */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            {editando ? (
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                placeholder="seu@email.com"
              />
            ) : (
              <p className="text-gray-900">{cliente.email}</p>
            )}
          </div>
          
          {/* Telefone */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Telefone
            </label>
            {editando ? (
              <input
                type="tel"
                value={formData.telefone}
                onChange={(e) => setFormData({ ...formData, telefone: e.target.value })}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                placeholder="(00) 00000-0000"
              />
            ) : (
              <p className="text-gray-900">{cliente.telefone || 'Não informado'}</p>
            )}
          </div>
          
          {/* Status */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Status
            </label>
            <span className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${
              cliente.status === 'ativo' ? 'bg-green-100 text-green-800' :
              cliente.status === 'inativo' ? 'bg-red-100 text-red-800' :
              cliente.status === 'pendente' ? 'bg-yellow-100 text-yellow-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              {cliente.status.charAt(0).toUpperCase() + cliente.status.slice(1)}
            </span>
          </div>
          
          {/* Botões */}
          <div className="flex gap-3 pt-4">
            {editando ? (
              <>
                <button
                  onClick={handleSalvar}
                  disabled={salvando}
                  className="bg-gray-900 text-white px-6 py-2 rounded-lg hover:bg-gray-700 disabled:opacity-50 transition-all"
                >
                  {salvando ? 'Salvando...' : 'Salvar Alterações'}
                </button>
                <button
                  onClick={handleCancelar}
                  disabled={salvando}
                  className="bg-gray-200 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-300 disabled:opacity-50 transition-all"
                >
                  Cancelar
                </button>
              </>
            ) : (
              <button
                onClick={handleEditar}
                className="bg-gray-900 text-white px-6 py-2 rounded-lg hover:bg-gray-700 transition-all"
              >
                Editar Informações
              </button>
            )}
          </div>
        </div>
      </div>
      
      {/* Modal de Confirmação de Senha */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold mb-4">Confirmar Alterações</h3>
            <p className="text-gray-600 mb-4">
              Por segurança, digite sua senha para confirmar as alterações no perfil.
            </p>
            
            <form onSubmit={handleConfirmarSenha}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Senha
                </label>
                <input
                  type="password"
                  value={senhaConfirmacao}
                  onChange={(e) => setSenhaConfirmacao(e.target.value)}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                  placeholder="Digite sua senha"
                  autoFocus
                />
              </div>
              
              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={salvando}
                  className="flex-1 bg-gray-900 text-white px-4 py-2 rounded-lg hover:bg-gray-700 disabled:opacity-50 transition-all"
                >
                  {salvando ? 'Confirmando...' : 'Confirmar'}
                </button>
                <button
                  type="button"
                  onClick={handleFecharModal}
                  disabled={salvando}
                  className="flex-1 bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 disabled:opacity-50 transition-all"
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
