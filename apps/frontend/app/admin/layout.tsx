'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import NotificationBell from './components/NotificationBell';
import ThemeToggle from './components/ThemeToggle';

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const [admin, setAdmin] = useState<any>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    // Verificar autenticação (exceto na página de login)
    if (pathname !== '/admin/login') {
      const token = localStorage.getItem('admin_token');
      const adminData = localStorage.getItem('admin_user');

      if (!token || !adminData) {
        router.push('/admin/login');
        return;
      }

      setAdmin(JSON.parse(adminData));
    }
  }, [pathname, router]);

  const handleLogout = () => {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_user');
    router.push('/admin/login');
  };

  // Se for página de login, renderizar sem layout
  if (pathname === '/admin/login') {
    return <>{children}</>;
  }

  // Se não estiver autenticado, não renderizar nada (vai redirecionar)
  if (!admin) {
    return null;
  }

  const menuItems = [
    { name: 'Dashboard', href: '/admin/dashboard', icon: '📊' },
    { name: 'Clientes', href: '/admin/clientes', icon: '👥' },
    { name: 'Uso OpenAI', href: '/admin/uso', icon: '🤖' },
    { name: 'Tickets', href: '/admin/tickets', icon: '🎫' },
    { name: 'Tutoriais', href: '/admin/tutoriais', icon: '🎥' },
    { name: 'Avisos', href: '/admin/avisos', icon: '📢' },
    { name: 'Relatórios', href: '/admin/relatorios', icon: '📈' },
    { name: 'Segurança', href: '/admin/seguranca', icon: '🔒' },
    { name: 'Sistema', href: '/admin/sistema', icon: '⚙️' },
  ];

  const handleAcessarFerramenta = async () => {
    try {
      const token = localStorage.getItem('admin_token');
      const response = await fetch('http://localhost:8000/api/v1/admin/minha-ferramenta/acessar', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        
        // Salvar token do cliente e flag de que veio do admin
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify({
          id: data.cliente_id,
          email: data.email,
          nome: data.nome
        }));
        localStorage.setItem('from_admin', 'true');
        
        // Redirecionar para dashboard do cliente
        router.push('/dashboard');
      } else {
        alert('Erro ao acessar ferramenta');
      }
    } catch (error) {
      console.error('Erro ao acessar ferramenta:', error);
      alert('Erro ao acessar ferramenta');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 z-40 h-screen transition-transform ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } bg-gray-900 dark:bg-gray-800 w-64`}
      >
        <div className="h-full px-3 py-4 overflow-y-auto">
          {/* Logo */}
          <div className="mb-6 px-3">
            <h1 className="text-xl font-bold text-white">Admin Panel</h1>
            <p className="text-xs text-gray-400">WhatsApp AI Bot</p>
          </div>

          {/* Menu */}
          <ul className="space-y-2">
            {menuItems.map((item) => (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={`flex items-center p-2 rounded-lg hover:bg-gray-700 transition-colors ${
                    pathname === item.href
                      ? 'bg-gray-700 text-white'
                      : 'text-gray-300'
                  }`}
                >
                  <span className="text-xl mr-3">{item.icon}</span>
                  <span className="text-sm font-medium">{item.name}</span>
                </Link>
              </li>
            ))}
            
            {/* Separador */}
            <li className="pt-4 mt-4 border-t border-gray-700">
              <button
                onClick={handleAcessarFerramenta}
                className="w-full flex items-center p-2 rounded-lg hover:bg-blue-600 transition-colors text-gray-300 hover:text-white"
              >
                <span className="text-xl mr-3">🚀</span>
                <span className="text-sm font-medium">Minha Ferramenta</span>
              </button>
            </li>
          </ul>
        </div>
      </aside>

      {/* Main Content */}
      <div className={`${sidebarOpen ? 'ml-64' : 'ml-0'} transition-all`}>
        {/* Header */}
        <header className="bg-white dark:bg-gray-800 shadow-sm">
          <div className="flex items-center justify-between px-6 py-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
            </button>

            <div className="flex items-center space-x-4">
              {/* Toggle Tema */}
              <ThemeToggle />
              
              {/* Notificações */}
              <NotificationBell />

              {/* Perfil */}
              <div className="flex items-center space-x-3">
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300">{admin.nome}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">{admin.role}</p>
                </div>
                <button
                  onClick={handleLogout}
                  className="px-3 py-1 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                >
                  Sair
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="p-6">{children}</main>
      </div>
    </div>
  );
}
