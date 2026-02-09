'use client'

import { useEffect, useState } from 'react'
import WidgetAssinatura from './components/WidgetAssinatura'
import TrialBanner from '../../components/TrialBanner'

export default function DashboardPage() {
  const [cliente, setCliente] = useState<any>(null)
  const [whatsappStatus, setWhatsappStatus] = useState<string>('carregando')
  const [stats, setStats] = useState({ conversas_hoje: 0, mensagens_hoje: 0 })
  
  useEffect(() => {
    const clienteData = localStorage.getItem('cliente')
    if (clienteData) {
      setCliente(JSON.parse(clienteData))
    }
    
    // Buscar status do WhatsApp
    buscarStatusWhatsApp()
    
    // Buscar estatísticas (placeholder por enquanto)
    setStats({ conversas_hoje: 0, mensagens_hoje: 0 })
  }, [])
  
  const buscarStatusWhatsApp = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/api/v1/whatsapp/instance', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setWhatsappStatus(data.status)
      } else if (response.status === 404) {
        setWhatsappStatus('não_criada')
      }
    } catch (err) {
      console.error('Erro ao buscar status WhatsApp:', err)
      setWhatsappStatus('erro')
    }
  }
  
  return (
    <div className="p-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Coluna Principal (2/3) */}
        <div className="lg:col-span-2 space-y-8">
          {/* Trial Banner */}
          <TrialBanner />
          
          {/* Welcome Card */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold mb-2">
              Bem-vindo, {cliente?.nome}! 🎉
            </h2>
            <p className="text-gray-600">
              Seu dashboard está pronto. Use o menu lateral para navegar.
            </p>
          </div>
          
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
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
                  {whatsappStatus === 'conectada' && (
                    <p className="text-2xl font-bold text-green-600">Conectado</p>
                  )}
                  {whatsappStatus === 'pendente' && (
                    <p className="text-2xl font-bold text-yellow-600">Pendente</p>
                  )}
                  {whatsappStatus === 'desconectada' && (
                    <p className="text-2xl font-bold text-red-600">Desconectado</p>
                  )}
                  {(whatsappStatus === 'não_criada' || whatsappStatus === 'carregando') && (
                    <p className="text-2xl font-bold text-gray-400">Não conectado</p>
                  )}
                </div>
                <div className="text-4xl">
                  {whatsappStatus === 'conectada' ? '✅' : '📱'}
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Conversas Hoje</p>
                  <p className="text-2xl font-bold">{stats.conversas_hoje}</p>
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
        
        {/* Coluna Lateral (1/3) - Widget de Assinatura */}
        <div className="lg:col-span-1">
          <WidgetAssinatura />
        </div>
      </div>
    </div>
  )
}
