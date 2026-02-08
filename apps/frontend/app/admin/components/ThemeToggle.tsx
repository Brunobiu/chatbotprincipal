'use client'

import { useState, useEffect } from 'react'

export default function ThemeToggle() {
  const [tema, setTema] = useState<'light' | 'dark'>('light')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    // Carregar tema do localStorage
    const temaLocal = localStorage.getItem('admin_tema') as 'light' | 'dark' | null
    if (temaLocal) {
      setTema(temaLocal)
      aplicarTema(temaLocal)
    } else {
      // Carregar do backend
      carregarTema()
    }
  }, [])

  const carregarTema = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      const res = await fetch('http://localhost:8000/api/v1/admin/preferencias', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (res.ok) {
        const data = await res.json()
        setTema(data.tema)
        localStorage.setItem('admin_tema', data.tema)
        aplicarTema(data.tema)
      }
    } catch (error) {
      console.error('Erro ao carregar tema:', error)
    }
  }

  const aplicarTema = (novoTema: 'light' | 'dark') => {
    if (novoTema === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  const toggleTema = async () => {
    const novoTema = tema === 'light' ? 'dark' : 'light'
    setLoading(true)

    try {
      const token = localStorage.getItem('admin_token')
      const res = await fetch('http://localhost:8000/api/v1/admin/preferencias', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ tema: novoTema })
      })

      if (res.ok) {
        setTema(novoTema)
        localStorage.setItem('admin_tema', novoTema)
        aplicarTema(novoTema)
      }
    } catch (error) {
      console.error('Erro ao atualizar tema:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <button
      onClick={toggleTema}
      disabled={loading}
      className="p-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
      title={tema === 'light' ? 'Ativar tema escuro' : 'Ativar tema claro'}
    >
      {tema === 'light' ? (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
        </svg>
      ) : (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
      )}
    </button>
  )
}
