'use client'

import { useEffect, useState } from 'react'

export default function PerfilPage() {
  const [loading, setLoading] = useState(true)
  const [cliente, setCliente] = useState<any>(null)
  const [editando, setEditando] = useState(false)
  const [salvando, setSalvando] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })
  const [fotoPreview, setFotoPreview] = useState<string | null>(null)
  const [fotoFile, setFotoFile] = useState<string | null>(null)
  
  const [formData, setFormData] = useState({
    nome: '',
    email: '',
    telefone: '',
    nome_empresa: ''
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
          telefone: data.telefone_cadastro || data.telefone || '',
          nome_empresa: data.nome_empresa || ''
        })
        
        localStorage.setItem('cliente', JSON.stringify(data))
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
  
  const handleFotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    
    if (file.size > 2 * 1024 * 1024) {
      setMessage({ type: 'error', text: 'Imagem muito grande. Máximo 2MB.' })
      return
    }
    
    if (!file.type.startsWith('image/')) {
      setMessage({ type: 'error', text: 'Apenas imagens são permitidas.' })
      return
    }
    
    const reader = new FileReader()
    reader.onloadend = () => {
      const base64 = reader.result as string
      setFotoPreview(base64)
      setFotoFile(base64)
    }
    reader.readAsDataURL(file)
  }
  
  const handleSalvar = async () => {
    if (!formData.nome.trim()) {
      setMessage({ type: 'error', text: 'Nome é obrigatório' })
      return
    }
    
    if (!formData.email.trim()) {
      setMessage({ type: 'error', text: 'Email é obrigatório' })
      return
    }
    
    setSalvando(true)
    setMessage({ type: '', text: '' })
    
    try {
      const token = localStorage.getItem('token')
      
      // 1. Atualizar dados do perfil
      const perfilResponse = await fetch('http://localhost:8000/api/v1/auth/perfil', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          nome: formData.nome.trim(),
          email: formData.email.trim(),
          telefone: formData.telefone.trim() || null,
          nome_empresa: formData.nome_empresa.trim() || null
        })
      })
      
      if (!perfilResponse.ok) {
        const error = await perfilResponse.json()
        console.error('Erro ao atualizar perfil:', error)
        
        let errorMsg = 'Erro ao atualizar perfil'
        if (error.detail) {
          if (Array.isArray(error.detail)) {
            errorMsg = error.detail.map((e: any) => `${e.loc?.join('.')}: ${e.msg}`).join(', ')
          } else if (typeof error.detail === 'string') {
            errorMsg = error.detail
          }
        }
        
        throw new Error(errorMsg)
      }
      
      const dadosPerfil = await perfilResponse.json()
      
      // 2. Se tiver foto nova, atualizar foto
      if (fotoFile) {
        const fotoResponse = await fetch('http://localhost:8000/api/v1/auth/foto-perfil', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ foto_base64: fotoFile })
        })
        
        if (fotoResponse.ok) {
          const dadosFoto = await fotoResponse.json()
          // Atualizar com dados que incluem foto
          setCliente(dadosFoto)
          localStorage.setItem('cliente', JSON.stringify(dadosFoto))
        }
      } else {
        // Atualizar com dados do perfil
        setCliente(dadosPerfil)
        localStorage.setItem('cliente', JSON.stringify(dadosPerfil))
      }
      
      setEditando(false)
      setFotoPreview(null)
      setFotoFile(null)
      setMessage({ type: 'success', text: '✅ Perfil atualizado com sucesso!' })
      
      // Recarregar página após 1 segundo para atualizar header
      setTimeout(() => {
        window.location.reload()
      }, 1000)
      
    } catch (err: any) {
      console.error('Erro:', err)
      setMessage({ type: 'error', text: err.message || 'Erro ao atualizar perfil' })
    } finally {
      setSalvando(false)
    }
  }
  
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-gray-600">Carregando...</div>
      </div>
    )
  }
  
  if (!cliente) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-red-600">Erro ao carregar perfil</div>
      </div>
    )
  }
  
  return (
    <div className="max-w-2xl">
      <h1 className="text-xl font-bold mb-4">Meu Perfil</h1>
      
      {message.text && (
        <div className={`mb-4 p-3 rounded-lg text-sm ${
          message.type === 'success' ? 'bg-green-50 text-green-700 border border-green-200' : 
          'bg-red-50 text-red-700 border border-red-200'
        }`}>
          {message.text}
        </div>
      )}
      
      <div className="bg-white rounded-lg shadow-sm border p-4">
        {/* Foto de perfil */}
        <div className="flex items-center gap-4 mb-6 pb-6 border-b">
          <div className="relative">
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white font-bold text-2xl overflow-hidden">
              {fotoPreview ? (
                <img src={fotoPreview} alt="Preview" className="w-full h-full object-cover" />
              ) : cliente.foto_perfil ? (
                <img src={cliente.foto_perfil} alt={cliente.nome} className="w-full h-full object-cover" />
              ) : (
                cliente.nome?.charAt(0).toUpperCase()
              )}
            </div>
          </div>
          <div>
            <h3 className="text-sm font-semibold mb-1">Foto de Perfil</h3>
            {editando ? (
              <>
                <label className="inline-block px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-lg text-xs cursor-pointer transition-colors">
                  Escolher Foto
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleFotoChange}
                    className="hidden"
                  />
                </label>
                <p className="text-[10px] text-gray-500 mt-1">JPG, PNG ou GIF. Máx 2MB</p>
              </>
            ) : (
              <p className="text-xs text-gray-500">Clique em "Editar Perfil" para alterar</p>
            )}
          </div>
        </div>
        
        {/* Informações */}
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Nome *</label>
            {editando ? (
              <input
                type="text"
                value={formData.nome}
                onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
                className="w-full px-3 py-2 text-sm border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            ) : (
              <p className="text-sm text-gray-900">{cliente.nome}</p>
            )}
          </div>
          
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Email *</label>
            <p className="text-sm text-gray-900 bg-gray-50 px-3 py-2 rounded-lg">{cliente.email}</p>
            <p className="text-[10px] text-gray-500 mt-1">O email não pode ser alterado</p>
          </div>
          
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Nome da Empresa</label>
            {editando ? (
              <input
                type="text"
                value={formData.nome_empresa}
                onChange={(e) => setFormData({ ...formData, nome_empresa: e.target.value })}
                placeholder="Nome da sua empresa"
                className="w-full px-3 py-2 text-sm border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            ) : (
              <p className="text-sm text-gray-900">{cliente.nome_empresa || 'Não informado'}</p>
            )}
          </div>
          
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Telefone</label>
            {editando ? (
              <input
                type="tel"
                value={formData.telefone}
                onChange={(e) => setFormData({ ...formData, telefone: e.target.value })}
                placeholder="(00) 00000-0000"
                className="w-full px-3 py-2 text-sm border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            ) : (
              <p className="text-sm text-gray-900">{cliente.telefone_cadastro || cliente.telefone || 'Não informado'}</p>
            )}
          </div>
          
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Status</label>
            <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${
              cliente.status === 'ativo' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
            }`}>
              {cliente.status === 'ativo' ? '✓ Ativo' : cliente.status}
            </span>
          </div>
        </div>
        
        {/* Botões */}
        <div className="flex gap-2 mt-6 pt-6 border-t">
          {editando ? (
            <>
              <button
                onClick={handleSalvar}
                disabled={salvando}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {salvando ? 'Salvando...' : 'Salvar'}
              </button>
              <button
                onClick={() => {
                  setEditando(false)
                  setFotoPreview(null)
                  setFotoFile(null)
                  setFormData({
                    nome: cliente.nome,
                    email: cliente.email,
                    telefone: cliente.telefone_cadastro || cliente.telefone || '',
                    nome_empresa: cliente.nome_empresa || ''
                  })
                  setMessage({ type: '', text: '' })
                }}
                disabled={salvando}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200 disabled:opacity-50 transition-colors"
              >
                Cancelar
              </button>
            </>
          ) : (
            <button
              onClick={() => setEditando(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
            >
              Editar Perfil
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
