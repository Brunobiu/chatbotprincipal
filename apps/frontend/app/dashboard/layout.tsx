'use client'

import { useEffect, useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import Link from 'next/link'
import ChatSuporte from './components/ChatSuporte'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const pathname = usePathname()
  const [cliente, setCliente] = useState<any>(null)
  const [profileMenuOpen, setProfileMenuOpen] = useState(false)
  const [fromAdmin, setFromAdmin] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('token')
    const clienteData = localStorage.getItem('cliente')
    const isFromAdmin = localStorage.getItem('from_admin') === 'true'
    
    setFromAdmin(isFromAdmin)
    
    if (!token || !clienteData) {
      router.push('/login')
      return
    }
    
    setCliente(JSON.parse(clienteData))
  }, [router, pathname]) // Recarrega quando muda de página

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('cliente')
    localStorage.removeItem('from_admin')
    router.push('/login')
  }

  const handleVoltarAdmin = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('cliente')
    localStorage.removeItem('user')
    localStorage.removeItem('from_admin')
    router.push('/admin/dashboard')
  }

  const menuItems = [
    { 
      href: '/dashboard', 
      label: 'Início',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
      )
    },
    { 
      href: '/dashboard/conhecimento', 
      label: 'Conhecimento',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
      )
    },
    { 
      href: '/dashboard/whatsapp', 
      label: 'Conexões',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
        </svg>
      )
    },
    { 
      href: '/dashboard/conversas', 
      label: 'Conversas',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      )
    },
    { 
      href: '/dashboard/agendamentos', 
      label: 'Agendamentos',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      )
    },
    { 
      href: '/dashboard/plano', 
      label: 'Meu Plano',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
        </svg>
      )
    },
  ]

  if (!cliente) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-600">Carregando...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 h-14 bg-white border-b z-50 flex items-center justify-between px-4">
        {/* Logo */}
        <div className="lg:w-56">
          <h1 className="text-lg font-bold">WhatsApp AI Bot</h1>
        </div>

        {/* User info */}
        <div className="flex items-center gap-2 ml-auto">
          {/* Nome da Empresa */}
          <div className="text-sm font-medium text-gray-900">
            {cliente.nome_empresa || 'Minha Empresa'}
          </div>
          
          {/* Logo da Empresa (foto de perfil) */}
          <div className="relative">
            <button
              onClick={() => setProfileMenuOpen(!profileMenuOpen)}
              className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white font-semibold text-sm hover:shadow-lg transition-shadow overflow-hidden"
            >
              {cliente.foto_perfil ? (
                <img src={cliente.foto_perfil} alt="Logo" className="w-full h-full object-cover" />
              ) : (
                <span>{(cliente.nome_empresa || cliente.nome)?.charAt(0).toUpperCase()}</span>
              )}
            </button>

            {/* Dropdown menu */}
            {profileMenuOpen && (
              <>
                <div 
                  className="fixed inset-0 z-40" 
                  onClick={() => setProfileMenuOpen(false)}
                />
                <div className="absolute right-0 mt-2 w-44 bg-white rounded-lg shadow-lg border py-1 z-50">
                  <Link
                    href="/dashboard/perfil"
                    onClick={() => setProfileMenuOpen(false)}
                    className="flex items-center gap-2 px-3 py-2 text-xs text-gray-700 hover:bg-gray-50"
                  >
                    <span>👤</span>
                    <span>Meu Perfil</span>
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center gap-2 px-3 py-2 text-xs text-red-600 hover:bg-red-50"
                  >
                    <span>🚪</span>
                    <span>Sair</span>
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Sidebar */}
      <aside className="fixed top-14 left-0 h-[calc(100vh-3.5rem)] w-56 md:w-48 lg:w-56 bg-white border-r z-40">
        <nav className="p-2">
          {menuItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`
                flex items-center gap-3 px-3 py-2 rounded-lg mb-1 text-xs font-medium
                transition-colors
                ${pathname === item.href
                  ? 'bg-gray-900 text-white'
                  : 'text-gray-600 hover:bg-gray-900 hover:text-white'
                }
              `}
            >
              {item.icon}
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>

        {fromAdmin && (
          <div className="absolute bottom-12 left-0 right-0 p-2 border-t">
            <button
              onClick={handleVoltarAdmin}
              className="w-full flex items-center gap-2 px-2 py-1.5 text-xs text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            >
              <span className="text-sm">👨‍💼</span>
              <span>Voltar Admin</span>
            </button>
          </div>
        )}
        
        {/* Configurações no canto inferior */}
        <div className="absolute bottom-2 left-2">
          <Link
            href="/dashboard/configuracoes"
            className={`
              flex items-center justify-center p-2 rounded-lg transition-colors
              ${pathname === '/dashboard/configuracoes'
                ? 'bg-gray-900 text-white'
                : 'text-gray-600 hover:bg-gray-900 hover:text-white'
              }
            `}
            title="Configurações"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </Link>
        </div>
      </aside>

      {/* Main content */}
      <main className="ml-56 md:ml-48 lg:ml-56 pt-14">
        <div className="p-4">
          {children}
        </div>
      </main>

      {/* Chat Suporte */}
      <ChatSuporte />
    </div>
  )
}
