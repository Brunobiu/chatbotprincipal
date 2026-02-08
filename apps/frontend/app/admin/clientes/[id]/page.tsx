'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'

interface Cliente {
  id: number
  nome: string
  nome_empresa: string | null
  email: string
  telefone: string | null
  status: string
  stripe_customer_id: string | null
  stripe_subscription_id: string | null
  stripe_status: string | null
  ultimo_login: string | null
  ip_ultimo_login: string | null
  total_mensagens_enviadas: number
  created_at: string
  updated_at: string
}

export default function ClienteDetalhesPage() {
  const router = useRouter()
  const params = useParams()
  const clienteId = params.id as string
  
  const [loading, setLoading] = useState(true)
  const [cliente, setCliente] = useState<Cliente | null>(null)
  const [editando, setEditando] = useState(false)
  const [salvando, setSalvando] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })
  
  // Modal states
  const [showSuspenderModal, setShowSuspenderModal] = useState(false)
  const [showAtivarModal, setShowAtivarModal] = useState(false)
  const [showResetarSenhaModal, setShowResetarSenhaModal] = useState(false)
  const [novaSenha, setNovaSenha] = useState('')
  
  // Form states
  const [formData, setFormData] = useState({
    nome: '',
    nome_empresa: '',
    email: '',
    telefone: ''
  })
  
  useEffect(() => {
    carregarCliente()
  }, [clienteId])
  
  const carregarCliente = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      
      if (!token) {
        router.push('/admin/login')
        return
      }
      
      const response = await fetch(`http://localhost:8000/api/v1/admin/clientes/${clienteId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data: Cliente = await response.json()
        setCliente(data)
        setFormData({
          nome: data.nome,
          nome_empresa: data.nome_empresa || '',
          email: data.email,
          telefone: data.telefone || ''
        })
      } else if (response.status === 401) {
        router.push('/admin/login')
      } else if (response.status === 404) {
        setMessage({ type: 'error', text: 'Cliente não encontrado' })
      }
    } catch (err) {
      console.error('Erro ao carregar cliente:', err)
      setMessage({ type: 'error', text: 'Erro ao carregar dados do cliente' })
    } finally {
      setLoading(false)
    }
  }
  
  const handleSalvar = async () => {
    setSalvando(true)
    setMessage({ type: '', text: '' })
    
    try {
      const token = localStorage.getItem('admin_token')
      
      const response = await fetch(`http://localhost:8000/api/v1/admin/clientes/${clienteId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      })
      
      if (response.ok) {
        const data = await response.json()
        setCliente(data)
        setEditando(false)
        setMessage({ type: 'success', text: 'Cliente atualizado com sucesso!' })
      } else {
        const error = await response.json()
        setMessage({ type: 'error', text: error.detail || 'Erro ao atualizar cliente' })
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Erro ao atualizar cliente' })
    } finally {
      setSalvando(false)
    }
  }
  
  const handleSuspender = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      
      const response = await fetch(`http://localhost:8000/api/v1/admin/clientes/${clienteId}/suspender`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        setMessage({ type: 'success', text: 'Cliente suspenso com sucesso!' })
        setShowSuspenderModal(false)
        carregarCliente()
      } else {
        const error = await response.json()
        setMessage({ type: 'error', text: error.detail || 'Erro ao suspender cliente' })
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Erro ao suspender cliente' })
    }
  }
  
  const handleAtivar = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      
      const response = await fetch(`http://localhost:8000/api/v1/admin/clientes/${clienteId}/ativar`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        setMessage({ type: 'success', text: 'Cliente ativado com sucesso!' })
        setShowAtivarModal(false)
        carregarCliente()
      } else {
        const error = await response.json()
        setMessage({ type: 'error', text: error.detail || 'Erro ao ativar cliente' })
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Erro ao ativar cliente' })
    }
  }
  
  const handleResetarSenha = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      
      const response = await fetch(`http://localhost:8000/api/v1/admin/clientes/${clienteId}/resetar-senha`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setNovaSenha(data.nova_senha)
        setMessage({ type: 'success', text: data.message })
      } else {
        const error = await response.json()
        setMessage({ type: 'error', text: error.detail || 'Erro ao resetar senha' })
        setShowResetarSenhaModal(false)
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Erro ao resetar senha' })
      setShowResetarSenhaModal(false)
    }
  }
  
  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A'
    
    const date = new Date(dateString)
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  
  const getStatusBadge = (status: string) => {
    const badges = {
      ativo: 'bg-green-100 text-green-800',
      inativo: 'bg-gray-100 text-gray-800',
      pendente: 'bg-yellow-100 text-yellow-800',
      suspenso: 'bg-red-100 text-red-800'
    }
    
    return badges[status as keyof typeof badges] || 'bg-gray-100 text-gray-800'
  }
  
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando cliente...</p>
        </div>
      </div>
    )
  }
  
  if (!cliente) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Cliente não encontrado</p>
        <button
          onClick={() => router.push('/admin/clientes')}
          className="mt-4 text-indigo-600 hover:text-indigo-900"
        >
          Voltar para lista
        </button>
      </div>
    )
  }
  
  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <button
            onClick={() => router.push('/admin/clientes')}
            className="text-gray-600 hover:text-gray-900 mb-2"
          >
            ← Voltar para lista
          </button>
          <h1 className="text-3xl font-bold">Detalhes do Cliente</h1>
        </div>
        
        <div className="flex gap-2">
          {cliente.status === 'suspenso' ? (
            <button
              onClick={() => setShowAtivarModal(true)}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
            >
              Ativar Cliente
            </button>
          ) : (
            <button
              onClick={() => setShowSuspenderModal(true)}
              className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
            >
              Suspender Cliente
            </button>
          )}
          
          <button
            onClick={() => setShowResetarSenhaModal(true)}
            className="bg-yellow-600 text-white px-4 py-2 rounded-lg hover:bg-yellow-700"
          >
            Resetar Senha
          </button>
        </div>
      </div>
      
      {message.text && (
        <div className={`p-4 rounded mb-6 ${
          message.type === 'success' 
            ? 'bg-green-50 text-green-700 border border-green-200' 
            : 'bg-red-50 text-red-700 border border-red-200'
        }`}>
          {message.text}
        </div>
      )}
      
      {/* Informações Básicas */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Informações Básicas</h2>
          {!editando ? (
            <button
              onClick={() => setEditando(true)}
              className="text-indigo-600 hover:text-indigo-900"
            >
              Editar
            </button>
          ) : (
            <div className="flex gap-2">
              <button
                onClick={() => {
                  setEditando(false)
                  setFormData({
                    nome: cliente.nome,
                    nome_empresa: cliente.nome_empresa || '',
                    email: cliente.email,
                    telefone: cliente.telefone || ''
                  })
                }}
                className="px-4 py-2 border rounded-lg hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleSalvar}
                disabled={salvando}
                className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
              >
                {salvando ? 'Salvando...' : 'Salvar'}
              </button>
            </div>
          )}
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nome</label>
            {editando ? (
              <input
                type="text"
                value={formData.nome}
                onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg"
              />
            ) : (
              <p className="text-gray-900">{cliente.nome}</p>
            )}
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nome da Empresa</label>
            {editando ? (
              <input
                type="text"
                value={formData.nome_empresa}
                onChange={(e) => setFormData({ ...formData, nome_empresa: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg"
              />
            ) : (
              <p className="text-gray-900">{cliente.nome_empresa || 'N/A'}</p>
            )}
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            {editando ? (
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg"
              />
            ) : (
              <p className="text-gray-900">{cliente.email}</p>
            )}
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Telefone</label>
            {editando ? (
              <input
                type="text"
                value={formData.telefone}
                onChange={(e) => setFormData({ ...formData, telefone: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg"
              />
            ) : (
              <p className="text-gray-900">{cliente.telefone || 'N/A'}</p>
            )}
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusBadge(cliente.status)}`}>
              {cliente.status}
            </span>
          </div>
        </div>
      </div>
      
      {/* Estatísticas */}
      <div className="grid grid-cols-3 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Último Login</h3>
          <p className="text-2xl font-bold">{formatDate(cliente.ultimo_login)}</p>
          {cliente.ip_ultimo_login && (
            <p className="text-sm text-gray-500 mt-1">IP: {cliente.ip_ultimo_login}</p>
          )}
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Mensagens Enviadas</h3>
          <p className="text-2xl font-bold">{cliente.total_mensagens_enviadas.toLocaleString()}</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Cadastrado em</h3>
          <p className="text-2xl font-bold">{formatDate(cliente.created_at)}</p>
        </div>
      </div>
      
      {/* Informações Stripe */}
      {(cliente.stripe_customer_id || cliente.stripe_subscription_id) && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Informações de Pagamento</h2>
          <div className="grid grid-cols-2 gap-4">
            {cliente.stripe_customer_id && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Stripe Customer ID</label>
                <p className="text-gray-900 font-mono text-sm">{cliente.stripe_customer_id}</p>
              </div>
            )}
            
            {cliente.stripe_subscription_id && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Stripe Subscription ID</label>
                <p className="text-gray-900 font-mono text-sm">{cliente.stripe_subscription_id}</p>
              </div>
            )}
            
            {cliente.stripe_status && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Status Stripe</label>
                <p className="text-gray-900">{cliente.stripe_status}</p>
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* Modal Suspender */}
      {showSuspenderModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-semibold mb-4">Suspender Cliente</h3>
            <p className="text-gray-600 mb-6">
              Tem certeza que deseja suspender o cliente <strong>{cliente.nome}</strong>?
              O cliente não poderá mais acessar o sistema.
            </p>
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowSuspenderModal(false)}
                className="px-4 py-2 border rounded-lg hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleSuspender}
                className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
              >
                Suspender
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Modal Ativar */}
      {showAtivarModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-semibold mb-4">Ativar Cliente</h3>
            <p className="text-gray-600 mb-6">
              Tem certeza que deseja ativar o cliente <strong>{cliente.nome}</strong>?
              O cliente poderá acessar o sistema novamente.
            </p>
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowAtivarModal(false)}
                className="px-4 py-2 border rounded-lg hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleAtivar}
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
              >
                Ativar
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Modal Resetar Senha */}
      {showResetarSenhaModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-semibold mb-4">Resetar Senha</h3>
            
            {!novaSenha ? (
              <>
                <p className="text-gray-600 mb-6">
                  Tem certeza que deseja resetar a senha do cliente <strong>{cliente.nome}</strong>?
                  Uma nova senha será gerada e enviada por email.
                </p>
                <div className="flex justify-end gap-2">
                  <button
                    onClick={() => setShowResetarSenhaModal(false)}
                    className="px-4 py-2 border rounded-lg hover:bg-gray-50"
                  >
                    Cancelar
                  </button>
                  <button
                    onClick={handleResetarSenha}
                    className="bg-yellow-600 text-white px-4 py-2 rounded-lg hover:bg-yellow-700"
                  >
                    Resetar Senha
                  </button>
                </div>
              </>
            ) : (
              <>
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
                  <p className="text-sm text-green-800 mb-2">✅ Senha resetada com sucesso!</p>
                  <p className="text-sm text-green-700 mb-3">Nova senha gerada:</p>
                  <div className="bg-white border border-green-300 rounded p-3">
                    <p className="font-mono text-lg text-center select-all">{novaSenha}</p>
                  </div>
                  <p className="text-xs text-green-700 mt-2">
                    ⚠️ Copie esta senha agora. Ela não será exibida novamente.
                  </p>
                </div>
                <div className="flex justify-end">
                  <button
                    onClick={() => {
                      setShowResetarSenhaModal(false)
                      setNovaSenha('')
                    }}
                    className="bg-gray-900 text-white px-4 py-2 rounded-lg hover:bg-gray-700"
                  >
                    Fechar
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
