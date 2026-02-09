'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'

interface Cliente {
  id: number
  nome: string
  nome_empresa: string | null
  email: string
  telefone: string | null
  status: string
  stripe_status: string | null
  ultimo_login: string | null
  total_mensagens_enviadas: number
  created_at: string
}

interface ListaResponse {
  total: number
  page: number
  per_page: number
  total_pages: number
  clientes: Cliente[]
}

export default function ClientesPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [clientes, setClientes] = useState<Cliente[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  
  useEffect(() => {
    carregarClientes()
  }, [page, statusFilter])
  
  const carregarClientes = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      
      if (!token) {
        router.push('/admin/login')
        return
      }
      
      const params = new URLSearchParams({
        page: page.toString(),
        per_page: '20'
      })
      
      if (statusFilter) {
        params.append('status', statusFilter)
      }
      
      if (search) {
        params.append('search', search)
      }
      
      const response = await fetch(`http://localhost:8000/api/v1/admin/clientes?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data: ListaResponse = await response.json()
        setClientes(data.clientes)
        setTotal(data.total)
        setTotalPages(data.total_pages)
      } else if (response.status === 401) {
        router.push('/admin/login')
      }
    } catch (err) {
      console.error('Erro ao carregar clientes:', err)
    } finally {
      setLoading(false)
    }
  }
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1)
    carregarClientes()
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
  
  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Nunca'
    
    const date = new Date(dateString)
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando clientes...</p>
        </div>
      </div>
    )
  }
  
  return (
    <div>
      <div className="flex flex-col md:flex-row md:justify-between md:items-center mb-6 gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold">Gestão de Clientes</h1>
          <p className="text-gray-600 mt-1">{total} clientes cadastrados</p>
        </div>
      </div>
      
      {/* Filtros */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Buscar por nome, email ou empresa..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full px-4 py-2 border rounded-lg"
            />
          </div>
          
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value)
              setPage(1)
            }}
            className="px-4 py-2 border rounded-lg"
          >
            <option value="">Todos os status</option>
            <option value="ativo">Ativo</option>
            <option value="inativo">Inativo</option>
            <option value="pendente">Pendente</option>
            <option value="suspenso">Suspenso</option>
          </select>
          
          <button
            type="submit"
            className="bg-gray-900 text-white px-6 py-2 rounded-lg hover:bg-gray-700"
          >
            Buscar
          </button>
        </form>
      </div>
      
      {/* Tabela Desktop / Cards Mobile */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {/* Desktop: Tabela */}
        <div className="hidden md:block">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Cliente
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Contato
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Último Login
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Mensagens
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Cadastro
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Ações
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {clientes.map((cliente) => (
                <tr key={cliente.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{cliente.nome}</div>
                      {cliente.nome_empresa && (
                        <div className="text-sm text-gray-500">{cliente.nome_empresa}</div>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{cliente.email}</div>
                    {cliente.telefone && (
                      <div className="text-sm text-gray-500">{cliente.telefone}</div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusBadge(cliente.status)}`}>
                      {cliente.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(cliente.ultimo_login)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {cliente.total_mensagens_enviadas.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(cliente.created_at)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => router.push(`/admin/clientes/${cliente.id}`)}
                      className="text-indigo-600 hover:text-indigo-900 mr-4"
                    >
                      Ver Detalhes
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {/* Mobile: Cards */}
        <div className="md:hidden divide-y divide-gray-200">
          {clientes.map((cliente) => (
            <div key={cliente.id} className="p-4">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h3 className="font-medium text-gray-900">{cliente.nome}</h3>
                  {cliente.nome_empresa && (
                    <p className="text-sm text-gray-500">{cliente.nome_empresa}</p>
                  )}
                </div>
                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadge(cliente.status)}`}>
                  {cliente.status}
                </span>
              </div>
              
              <div className="space-y-2 text-sm mb-3">
                <div className="flex justify-between">
                  <span className="text-gray-500">Email:</span>
                  <span className="text-gray-900">{cliente.email}</span>
                </div>
                {cliente.telefone && (
                  <div className="flex justify-between">
                    <span className="text-gray-500">Telefone:</span>
                    <span className="text-gray-900">{cliente.telefone}</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-gray-500">Mensagens:</span>
                  <span className="text-gray-900">{cliente.total_mensagens_enviadas.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Último Login:</span>
                  <span className="text-gray-900">{formatDate(cliente.ultimo_login)}</span>
                </div>
              </div>
              
              <button
                onClick={() => router.push(`/admin/clientes/${cliente.id}`)}
                className="w-full bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 text-sm font-medium"
              >
                Ver Detalhes
              </button>
            </div>
          ))}
        </div>
      </div>
      
      {/* Paginação */}
      {totalPages > 1 && (
        <div className="flex justify-center items-center gap-2 mt-6">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            Anterior
          </button>
          
          <span className="px-4 py-2">
            Página {page} de {totalPages}
          </span>
          
          <button
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            Próxima
          </button>
        </div>
      )}
    </div>
  )
}
