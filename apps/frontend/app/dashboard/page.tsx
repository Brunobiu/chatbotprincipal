'use client'

import { useEffect, useState } from 'react'

export default function DashboardPage() {
  const [cliente, setCliente] = useState<any>(null)
  
  useEffect(() => {
    const clienteData = localStorage.getItem('cliente')
    if (clienteData) {
      setCliente(JSON.parse(clienteData))
    }
  }, [])
  
  return (
    <div className="p-8">
      {/* Welcome Card */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-2xl font-bold mb-2">
          Bem-vindo, {cliente?.nome}! 🎉
        </h2>
        <p className="text-gray-600">
          Seu dashboard está pronto. Use o menu lateral para navegar.
        </p>
      </div>
      
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Status da Conta</p>
              <p className="text-2xl font-bold text-green-600">Ativo</p>
            </div>
            <div className="text-4xl">✅</div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">WhatsApp</p>
              <p className="text-2xl font-bold text-gray-400">Não conectado</p>
            </div>
            <div className="text-4xl">📱</div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Conversas Hoje</p>
              <p className="text-2xl font-bold">0</p>
            </div>
            <div className="text-4xl">💬</div>
          </div>
        </div>
      </div>
      
      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-bold mb-4">Primeiros Passos</h3>
        <div className="space-y-3">
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
            <span className="text-2xl">1️⃣</span>
            <div>
              <p className="font-medium">Configure seu conhecimento</p>
              <p className="text-sm text-gray-600">Adicione informações para o bot responder</p>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
            <span className="text-2xl">2️⃣</span>
            <div>
              <p className="font-medium">Conecte seu WhatsApp</p>
              <p className="text-sm text-gray-600">Escaneie o QR Code para conectar</p>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
            <span className="text-2xl">3️⃣</span>
            <div>
              <p className="font-medium">Personalize as configurações</p>
              <p className="text-sm text-gray-600">Ajuste o tom e comportamento do bot</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
