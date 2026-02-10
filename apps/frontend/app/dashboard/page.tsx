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
    <div className="w-full">
      {/* Trial Banner */}
      <TrialBanner />
      
      {/* Welcome Card */}
      <div className="bg-white rounded-lg shadow p-3 w-full mb-3">
        <h2 className="text-base font-bold mb-1">
          Bem-vindo, {cliente?.nome}!
        </h2>
        <p className="text-gray-600 text-xs">
          Seu dashboard está pronto. Use o menu lateral para navegar.
        </p>
      </div>
      
      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 w-full mb-3">
        <div className="bg-white rounded-lg shadow p-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[10px] text-gray-600 mb-0.5">Status da Conta</p>
              <p className="text-sm font-bold text-green-600">Ativo</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[10px] text-gray-600 mb-0.5">WhatsApp</p>
              {whatsappStatus === 'conectada' && (
                <p className="text-sm font-bold text-green-600">Conectado</p>
              )}
              {whatsappStatus === 'pendente' && (
                <p className="text-sm font-bold text-yellow-600">Pendente</p>
              )}
              {whatsappStatus === 'desconectada' && (
                <p className="text-sm font-bold text-red-600">Desconectado</p>
              )}
              {(whatsappStatus === 'não_criada' || whatsappStatus === 'carregando') && (
                <p className="text-sm font-bold text-gray-400">Não conectado</p>
              )}
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[10px] text-gray-600 mb-0.5">Conversas Hoje</p>
              <p className="text-sm font-bold">{stats.conversas_hoje}</p>
            </div>
          </div>
        </div>
      </div>
      
      {/* Quick Actions e Widget lado a lado em telas grandes */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 w-full">
        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow p-3 w-full">
          <h3 className="text-sm font-bold mb-2">Primeiros Passos</h3>
          <div className="space-y-1.5">
            <div className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
              <span className="text-xs font-medium">1.</span>
              <div>
                <p className="font-medium text-xs">Configure seu conhecimento</p>
                <p className="text-[10px] text-gray-600">Adicione informações para o bot</p>
              </div>
            </div>
            <div className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
              <span className="text-xs font-medium">2.</span>
              <div>
                <p className="font-medium text-xs">Conecte seu WhatsApp</p>
                <p className="text-[10px] text-gray-600">Escaneie o QR Code</p>
              </div>
            </div>
            <div className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
              <span className="text-xs font-medium">3.</span>
              <div>
                <p className="font-medium text-xs">Personalize as configurações</p>
                <p className="text-[10px] text-gray-600">Ajuste o tom do bot</p>
              </div>
            </div>
          </div>
        </div>
        
        {/* Widget de Assinatura */}
        <div className="w-full">
          <WidgetAssinatura />
        </div>
      </div>
    </div>
  )
}
