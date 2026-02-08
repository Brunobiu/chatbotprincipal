'use client'

import { useState, useEffect } from 'react'

interface Tutorial {
  id: number
  titulo: string
  descricao: string | null
  video_url: string
  thumbnail_url: string | null
  ordem: number
  ativo: boolean
  created_at: string
}

export default function TutoriaisAdminPage() {
  const [tutoriais, setTutoriais] = useState<Tutorial[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editando, setEditando] = useState<Tutorial | null>(null)
  const [form, setForm] = useState({
    titulo: '',
    descricao: '',
    video_url: '',
    thumbnail_url: ''
  })

  useEffect(() => {
    carregarTutoriais()
  }, [])

  const carregarTutoriais = async () => {
    try {
      setLoading(true)
      const token = localStorage.getItem('admin_token')
      const res = await fetch('http://localhost:8000/api/v1/admin/tutoriais', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (res.ok) {
        const data = await res.json()
        setTutoriais(data)
      }
    } catch (error) {
      console.error('Erro ao carregar tutoriais:', error)
    } finally {
      setLoading(false)
    }
  }

  const abrirModal = (tutorial?: Tutorial) => {
    if (tutorial) {
      setEditando(tutorial)
      setForm({
        titulo: tutorial.titulo,
        descricao: tutorial.descricao || '',
        video_url: tutorial.video_url,
        thumbnail_url: tutorial.thumbnail_url || ''
      })
    } else {
      setEditando(null)
      setForm({
        titulo: '',
        descricao: '',
        video_url: '',
        thumbnail_url: ''
      })
    }
    setShowModal(true)
  }

  const salvarTutorial = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      const url = editando 
        ? `http://localhost:8000/api/v1/admin/tutoriais/${editando.id}`
        : 'http://localhost:8000/api/v1/admin/tutoriais'
      
      const res = await fetch(url, {
        method: editando ? 'PUT' : 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(form)
      })
      
      if (res.ok) {
        setShowModal(false)
        await carregarTutoriais()
      } else {
        alert('Erro ao salvar tutorial')
      }
    } catch (error) {
      console.error('Erro ao salvar tutorial:', error)
      alert('Erro ao salvar tutorial')
    }
  }

  const deletarTutorial = async (id: number) => {
    if (!confirm('Tem certeza que deseja deletar este tutorial?')) return
    
    try {
      const token = localStorage.getItem('admin_token')
      const res = await fetch(`http://localhost:8000/api/v1/admin/tutoriais/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (res.ok) {
        await carregarTutoriais()
      } else {
        alert('Erro ao deletar tutorial')
      }
    } catch (error) {
      console.error('Erro ao deletar tutorial:', error)
      alert('Erro ao deletar tutorial')
    }
  }

  const toggleAtivo = async (tutorial: Tutorial) => {
    try {
      const token = localStorage.getItem('admin_token')
      const res = await fetch(`http://localhost:8000/api/v1/admin/tutoriais/${tutorial.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ativo: !tutorial.ativo
        })
      })
      
      if (res.ok) {
        await carregarTutoriais()
      }
    } catch (error) {
      console.error('Erro ao atualizar status:', error)
    }
  }

  return (
    <div className="p-8">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">🎥 Tutoriais</h1>
          <p className="text-gray-600 mt-2">Gerencie os vídeos de tutorial para os clientes</p>
        </div>
        <button
          onClick={() => abrirModal()}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          + Novo Tutorial
        </button>
      </div>

      {loading ? (
        <div className="text-center text-gray-500">Carregando...</div>
      ) : tutoriais.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
          Nenhum tutorial cadastrado
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {tutoriais.map((tutorial) => (
            <div key={tutorial.id} className="bg-white rounded-lg shadow overflow-hidden">
              {tutorial.thumbnail_url ? (
                <img 
                  src={tutorial.thumbnail_url} 
                  alt={tutorial.titulo}
                  className="w-full h-48 object-cover"
                />
              ) : (
                <div className="w-full h-48 bg-gray-200 flex items-center justify-center">
                  <span className="text-gray-400 text-4xl">🎥</span>
                </div>
              )}
              
              <div className="p-4">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="text-lg font-semibold text-gray-900">{tutorial.titulo}</h3>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    tutorial.ativo ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {tutorial.ativo ? 'Ativo' : 'Inativo'}
                  </span>
                </div>
                
                {tutorial.descricao && (
                  <p className="text-sm text-gray-600 mb-4 line-clamp-2">{tutorial.descricao}</p>
                )}
                
                <div className="flex gap-2">
                  <button
                    onClick={() => abrirModal(tutorial)}
                    className="flex-1 px-3 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                  >
                    Editar
                  </button>
                  <button
                    onClick={() => toggleAtivo(tutorial)}
                    className="flex-1 px-3 py-2 bg-gray-600 text-white text-sm rounded hover:bg-gray-700"
                  >
                    {tutorial.ativo ? 'Desativar' : 'Ativar'}
                  </button>
                  <button
                    onClick={() => deletarTutorial(tutorial.id)}
                    className="px-3 py-2 bg-red-600 text-white text-sm rounded hover:bg-red-700"
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
              {editando ? 'Editar Tutorial' : 'Novo Tutorial'}
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Título *
                </label>
                <input
                  type="text"
                  value={form.titulo}
                  onChange={(e) => setForm({...form, titulo: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Ex: Como conectar o WhatsApp"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Descrição
                </label>
                <textarea
                  value={form.descricao}
                  onChange={(e) => setForm({...form, descricao: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  rows={3}
                  placeholder="Descrição do tutorial..."
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  URL do Vídeo (YouTube/Vimeo) *
                </label>
                <input
                  type="text"
                  value={form.video_url}
                  onChange={(e) => setForm({...form, video_url: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="https://www.youtube.com/watch?v=..."
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  URL da Thumbnail (opcional)
                </label>
                <input
                  type="text"
                  value={form.thumbnail_url}
                  onChange={(e) => setForm({...form, thumbnail_url: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="https://..."
                />
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
                onClick={salvarTutorial}
                disabled={!form.titulo || !form.video_url}
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
