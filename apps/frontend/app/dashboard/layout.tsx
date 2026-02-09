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
  const [menuOpen, setMenuOpen] = useState(false)
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
  }, [router])

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('cliente')
    localStorage.removeItem('from_admin')
    router.push('/login')
  }

  const handleVoltarAdmin = () => {
    // Limpar dados do cliente mas manter token admin
    localStorage.removeItem('token')
    localStorage.removeItem('cliente')
    localStorage.removeItem('user')
    localStorage.removeItem('from_admin')
    
    // Redirecionar para admin
    router.push('/admin/dashboard')
  }

  const menuItems = [
    { href: '/dashboard', label: 'Início', icon: '🏠' },
    { href: '/dashboard/perfil', label: 'Meu Perfil', icon: '👤' },
    { href: '/dashboard/conhecimento', label: 'Conhecimento', icon: '📚' },
    { href: '/dashboard/whatsapp', label: 'WhatsApp', icon: '💬' },
    { href: '/dashboard/conversas', label: 'Conversas', icon: '💭' },
    { href: '/dashboard/agendamentos', label: 'Agendamentos', icon: '📅' },
    { href: '/dashboard/plano', label: 'Meu Plano', icon: '💳' },
    { href: '/dashboard/configuracoes', label: 'Configurações', icon: '⚙️' },
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
      {/* Mobile menu button */}
      <div className="lg:hidden fixed top-0 left-0 right-0 bg-white border-b z-50 p-4">
        <button
          onClick={() => setMenuOpen(!menuOpen)}
          className="text-gray-600 hover:text-gray-900"
        >
          {menuOpen ? '✕' : '☰'} Menu
        </button>
      </div>

      {/* Sidebar */}
      <aside className={`
        fixed top-0 left-0 h-full w-64 bg-white border-r z-40
        transform transition-transform duration-200 ease-in-out
        ${menuOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0
      `}>
        <div className="p-6 border-b">
          <h1 className="text-xl font-bold">WhatsApp AI Bot</h1>
          <p className="text-sm text-gray-600 mt-1">{cliente.email}</p>
        </div>

        <nav className="p-4">
          {menuItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => setMenuOpen(false)}
              className={`
                flex items-center gap-3 px-4 py-3 rounded-lg mb-2
                transition-colors
                ${pathname === item.href
                  ? 'bg-gray-900 text-white'
                  : 'text-gray-700 hover:bg-gray-100'
                }
              `}
            >
              <span className="text-xl">{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-4 border-t">
          {fromAdmin && (
            <button
              onClick={handleVoltarAdmin}
              className="w-full flex items-center gap-3 px-4 py-3 mb-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            >
              <span className="text-xl">👨‍💼</span>
              <span>Voltar para Admin</span>
            </button>
          )}
          
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-3 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          >
            <span className="text-xl">🚪</span>
            <span>Sair</span>
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="lg:ml-64 pt-16 lg:pt-0">
        <div className="p-6">
          {children}
        </div>
      </main>

      {/* Overlay for mobile */}
      {menuOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-30 lg:hidden"
          onClick={() => setMenuOpen(false)}
        />
      )}

      {/* Chat Suporte - Widget flutuante */}
      <ChatSuporte />
    </div>
  )
}
