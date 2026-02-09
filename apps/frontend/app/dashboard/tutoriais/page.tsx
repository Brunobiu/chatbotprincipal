'use client'

import { useEffect, useState } from 'react'

interface Tutorial {
  id: number
  titulo: string
  descricao: string | null
  video_url: string
  thumbnail_url: string | null
  visualizado: boolean
  created_at: string
}

interface Comentario {
  id: number
  cliente_nome: string
  comentario: string
  created_at: string
}

export default function TutoriaisPage() {
  const [loading, setLoading] = useState(true)
  const [tutoriais, setTutoriais] = useState<Tutorial[]>([])
  const [tutorialSelecionado, setTutorialSelecionado] = useState<Tutorial | null>(null)
  const [comentarios, setComentarios] = useState<Comentario[]>([])
  const [novoComentario, setNovoComentario] = useState('')
  const [enviandoComentario, setEnviandoComentario] = useState(false)
  
  useEffect(() => {
    carregarTutoriais()
  }, [])
  
  const carregarTutoriais = async () => {
    try {
      const token = localStorage.getItem('token')
      
      if (!token) {
        window.location.href = '/login'
        return
      }
      
      const response = await fetch('http://localhost:8000/api/v1/tutoriais', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setTutoriais(data)
      } else if (response.status === 401) {
        localStorage.removeItem('token')
        localStorage.removeItem('cliente')
        window.location.href = '/login'
      }
    } catch (err) {
      console.error('Erro ao carregar tutoriais:', err)
    } finally {
      setLoading(false)
    }
  }
  
  const abrirTutorial = async (tutorial: Tutorial) => {
    setTutorialSelecionado(tutorial)
    
    // Marcar como visualizado
    if (!tutorial.visualizado) {
      try {
        const token = localStorage.getItem('token')
        await fetch(`http://localhost:8000/api/v1/tutoriais/${tutorial.id}/visualizar`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        
        // Atualizar lista local
        setTutoriais(prev => prev.map(t => 
          t.id === tutorial.id ? { ...t, visualizado: true } : t
        ))
      } catch (err) {
        console.error('Erro ao marcar como visualizado:', err)
      }
    }
    
    // Carregar comentários
    carregarComentarios(tutorial.id)
  }
  
  const carregarComentarios = async (tutorialId: number) => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`http://localhost:8000/api/v1/tutoriais/${tutorialId}/comentarios`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setComentarios(data)
      }
    } catch (err) {
      console.error('Erro ao carregar comentários:', err)
    }
  }
  
  const enviarComentario = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!novoComentario.trim() || !tutorialSelecionado) {
      return
    }
    
    setEnviandoComentario(true)
    
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`http://localhost:8000/api/v1/tutoriais/${tutorialSelecionado.id}/comentarios`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          comentario: novoComentario
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        setComentarios(prev => [data, ...prev])
        setNovoComentario('')
      }
    } catch (err) {
      console.error('Erro ao enviar comentário:', err)
    } finally {
      setEnviandoComentario(false)
    }
  }
  
  const fecharModal = () => {
    setTutorialSelecionado(null)
    setComentarios([])
    setNovoComentario('')
  }
  
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando tutoriais...</p>
        </div>
      </div>
    )
  }
  
  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Tutoriais</h1>
      
      {tutoriais.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <p className="text-gray-600">Nenhum tutorial disponível no momento.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {tutoriais.map(tutorial => (
            <div
              key={tutorial.id}
              onClick={() => abrirTutorial(tutorial)}
              className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer overflow-hidden"
            >
              {/* Thumbnail */}
              <div className="relative aspect-video bg-gray-200">
                {tutorial.thumbnail_url ? (
                  <img
                    src={tutorial.thumbnail_url}
                    alt={tutorial.titulo}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <span className="text-6xl">🎥</span>
                  </div>
                )}
                
                {/* Badge "Novo" */}
                {!tutorial.visualizado && (
                  <div className="absolute top-2 right-2 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-bold">
                    Novo
                  </div>
                )}
              </div>
              
              {/* Conteúdo */}
              <div className="p-4">
                <h3 className="font-bold text-lg mb-2">{tutorial.titulo}</h3>
                {tutorial.descricao && (
                  <p className="text-sm text-gray-600 line-clamp-2">{tutorial.descricao}</p>
                )}
                <div className="mt-3 flex items-center gap-2 text-xs text-gray-500">
                  {tutorial.visualizado ? (
                    <span className="flex items-center gap-1">
                      <span>✅</span>
                      <span>Visualizado</span>
                    </span>
                  ) : (
                    <span className="flex items-center gap-1">
                      <span>⏸️</span>
                      <span>Não visualizado</span>
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
      
      {/* Modal de Vídeo */}
      {tutorialSelecionado && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b">
              <h2 className="text-xl font-bold">{tutorialSelecionado.titulo}</h2>
              <button
                onClick={fecharModal}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                ×
              </button>
            </div>
            
            {/* Vídeo */}
            <div className="aspect-video bg-black">
              <iframe
                src={tutorialSelecionado.video_url}
                className="w-full h-full"
                allowFullScreen
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              />
            </div>
            
            {/* Descrição */}
            {tutorialSelecionado.descricao && (
              <div className="p-4 border-b">
                <p className="text-gray-700">{tutorialSelecionado.descricao}</p>
              </div>
            )}
            
            {/* Comentários */}
            <div className="p-4">
              <h3 className="font-bold mb-4">Comentários ({comentarios.length})</h3>
              
              {/* Formulário de novo comentário */}
              <form onSubmit={enviarComentario} className="mb-6">
                <textarea
                  value={novoComentario}
                  onChange={(e) => setNovoComentario(e.target.value)}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                  rows={3}
                  placeholder="Adicione um comentário..."
                />
                <div className="flex justify-end mt-2">
                  <button
                    type="submit"
                    disabled={enviandoComentario || !novoComentario.trim()}
                    className="bg-gray-900 text-white px-4 py-2 rounded-lg hover:bg-gray-700 disabled:opacity-50 transition-all"
                  >
                    {enviandoComentario ? 'Enviando...' : 'Comentar'}
                  </button>
                </div>
              </form>
              
              {/* Lista de comentários */}
              <div className="space-y-4">
                {comentarios.length === 0 ? (
                  <p className="text-gray-500 text-center py-4">Nenhum comentário ainda. Seja o primeiro!</p>
                ) : (
                  comentarios.map(comentario => (
                    <div key={comentario.id} className="bg-gray-50 rounded-lg p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-semibold">{comentario.cliente_nome}</span>
                        <span className="text-xs text-gray-500">
                          {new Date(comentario.created_at).toLocaleDateString('pt-BR')}
                        </span>
                      </div>
                      <p className="text-gray-700">{comentario.comentario}</p>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
