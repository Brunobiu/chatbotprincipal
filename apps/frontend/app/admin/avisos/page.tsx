'use client'

import { useState, useEffect } from 'react'

interface Aviso {
  id: number
  tipo: string
  titulo: string
  mensagem: string
  ativo: boolean
  dismissivel: boolean
  data_inicio: string | null
  data_fim: string | null
  created_at: string
}

const TIPO_LABELS: Record<string, string> = {
  info: 'Informação',
  warning: 'Aviso',
  error: 'Erro',
  success: 'Sucesso'
}

const TIPO_COLORS: Record<string, string> = {
  info: 'bg-blue-100 text-blue-800 border-blue-300',
  warning: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  error: 'bg-red-100 text-red-800 border-red-300',
  success: 'bg-green-100 text-green-800 border-green-300'
}

export default function AvisosAdminPage() {
  const [avisos, setAvisos] = useState<Aviso[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editando, setEditando] = useState<Aviso | null>(null)
  const [form, setForm] = useState({
    tipo: 'info',
    titulo: '',
    mensagem: '',
    dismissivel: true,
    data_inicio: '',
    data_fim: ''
  })

  useEffect(() => {
    carregarAvisos()
  }, [])

  const carregarAvisos = async () => {
    try {
      setLoading(true)
      const token = localStorage.getItem('admin_token')
      const res = await fetch('http://localhost:8000/api/v1/admin/avisos', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (res.ok) {
        const data = await res.json()
        setAvisos(data)
      }
    } catch (error) {
      console.error('Erro ao carregar avisos:', error)
    } finally {
      setLoading(false)
    }
  }

  const abrirModal = (aviso?: Aviso) => {
    if (aviso) {
      setEditando(aviso)
      setForm({
        tipo: aviso.tipo,
        titulo: aviso.titulo,
        mensagem: aviso.mensagem,
        dismissivel: aviso.dismissivel,
        data_inicio: aviso.data_inicio ? aviso.data_inicio.split('T')[0] : '',
        data_fim: aviso.data_fim ? aviso.data_fim.split('T')[0] : ''
      })
    } else {
      setEditando(null)
      setForm({
        tipo: 'info',
        titulo: '',
        mensagem: '',
        dismissivel: true,
        data_inicio: '',
        data_fim: ''
      })
    }
    setShowModal(true)
  }

  const salvarAviso = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      const url = editando 
        ? `http://localhost:8000/api/v1/admin/avisos/${editando.id}`
        : 'http://localhost:8000/api/v1/admin/avisos'
      
      const body: any = {
        tipo: form.tipo,
        titulo: form.titulo,
        mensagem: form.mensagem,
        dismissivel: form.dismissivel
      }
      
      if (form.data_inicio) {
        body.data_inicio = new Date(form.data_inicio).toISOString()
      }
      if (form.data_fim) {
        body.data_fim = new Date(form.data_fim).toISOString()
      }
      
      const res = await fetch(url, {
        method: editando ? 'PUT' : 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
      })
      
      if (res.ok) {
        setShowModal(false)
        await carregarAvisos()
      } else {
        alert('Erro ao salvar aviso')
      }
    } catch (error) {
      console.error('Erro ao salvar aviso:', error)
      alert('Erro ao salvar aviso')
    }
  }

  const deletarAviso = async (id: number) => {
    if (!confirm('Tem certeza que deseja deletar este aviso?')) return
    
    try {
      const token = localStorage.getItem('admin_token')
      const res = await fetch(`http://localhost:8000/api/v1/admin/avisos/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (res.ok) {
        await carregarAvisos()
      } else {
        alert('Erro ao deletar aviso')
      }
    } catch (error) {
      console.error('Erro ao deletar aviso:', error)
      alert('Erro ao deletar aviso')
    }
  }

  const toggleAtivo = async (aviso: Aviso) => {
    try {
      const token = localStorage.getItem('admin_token')
      const res = await fetch(`http://localhost:8000/api/v1/admin/avisos/${aviso.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ativo: !aviso.ativo
        })
      })
      
      if (res.ok) {
        await carregarAvisos()
      }
    } catch (error) {
      console.error('Erro ao atualizar status:', error)
    }
  }

  const formatarData = (data: string | null) => {
    if (!data) return '-'
    return new Date(data).toLocaleDateString('pt-BR')
  }

  return (
    <div className="p-8">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">📢 Avisos do Sistema</h1>
          <p className="text-gray-600 mt-2">Gerencie avisos que aparecem para todos os clientes</p>
        </div>
        <button
          onClick={() => abrirModal()}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          + Novo Aviso
        </button>
      </div>

      {loading ? (
        <div className="text-center text-gray-500">Carregando...</div>
      ) : avisos.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
          Nenhum aviso cadastrado
        </div>
      ) : (
        <div className="space-y-4">
          {avisos.map((aviso) => (
            <div 
              key={aviso.id} 
              className={`border-l-4 rounded-lg p-6 ${TIPO_COLORS[aviso.tipo]} ${
                !aviso.ativo ? 'opacity-50' : ''
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="px-3 py-1 bg-white rounded-full text-sm font-semibold">
                      {TIPO_LABELS[aviso.tipo]}
                    </span>
                    <span className={`px-3 py-1 rounded-full text-sm ${
                      aviso.ativo ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {aviso.ativo ? 'Ativo' : 'Inativo'}
                    </span>
                    {aviso.dismissivel && (
                      <span className="text-sm text-gray-600">✕ Pode fechar</span>
                    )}
                  </div>
                  
                  <h3 className="text-xl font-bold mb-2">{aviso.titulo}</h3>
                  <p className="text-gray-700 mb-3">{aviso.mensagem}</p>
                  
                  <div className="flex gap-4 text-sm text-gray-600">
                    <span>Início: {formatarData(aviso.data_inicio)}</span>
                    <span>Fim: {formatarData(aviso.data_fim)}</span>
                  </div>
                </div>
                
                <div className="flex gap-2 ml-4">
                  <button
                    onClick={() => abrirModal(aviso)}
                    className="px-4 py-2 bg-white text-gray-700 rounded hover:bg-gray-50 border"
                  >
                    Editar
                  </button>
                  <button
                    onClick={() => toggleAtivo(aviso)}
                    className="px-4 py-2 bg-white text-gray-700 rounded hover:bg-gray-50 border"
                  >
                    {aviso.ativo ? 'Desativar' : 'Ativar'}
                  </button>
                  <button
                    onClick={() => deletarAviso(aviso.id)}
                    className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">
              {editando ? 'Editar Aviso' : 'Novo Aviso'}
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tipo *
                </label>
                <select
                  value={form.tipo}
                  onChange={(e) => setForm({...form, tipo: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="info">Informação (Azul)</option>
                  <option value="warning">Aviso (Amarelo)</option>
                  <option value="error">Erro (Vermelho)</option>
                  <option value="success">Sucesso (Verde)</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Título *
                </label>
                <input
                  type="text"
                  value={form.titulo}
                  onChange={(e) => setForm({...form, titulo: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Ex: Manutenção programada"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Mensagem *
                </label>
                <textarea
                  value={form.mensagem}
                  onChange={(e) => setForm({...form, mensagem: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  rows={3}
                  placeholder="Mensagem do aviso..."
                />
              </div>
              
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="dismissivel"
                  checked={form.dismissivel}
                  onChange={(e) => setForm({...form, dismissivel: e.target.checked})}
                  className="w-4 h-4"
                />
                <label htmlFor="dismissivel" className="text-sm text-gray-700">
                  Permitir que clientes fechem o aviso
                </label>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Data Início (opcional)
                  </label>
                  <input
                    type="date"
                    value={form.data_inicio}
                    onChange={(e) => setForm({...form, data_inicio: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Data Fim (opcional)
                  </label>
                  <input
                    type="date"
                    value={form.data_fim}
                    onChange={(e) => setForm({...form, data_fim: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>
            
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowModal(false)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                onClick={salvarAviso}
                disabled={!form.titulo || !form.mensagem}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Salvar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
