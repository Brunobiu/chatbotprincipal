'use client';

import { useEffect, useState } from 'react';

export default function AdminDashboardPage() {
  const [admin, setAdmin] = useState<any>(null);

  useEffect(() => {
    const adminData = localStorage.getItem('admin_user');
    if (adminData) {
      setAdmin(JSON.parse(adminData));
    }
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">
          Bem-vindo de volta, {admin?.nome}!
        </p>
      </div>

      {/* Cards de Métricas - Placeholder */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Clientes</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">-</p>
            </div>
            <div className="text-4xl">👥</div>
          </div>
          <p className="text-xs text-gray-500 mt-4">
            Será implementado na Mini-Fase 16.2
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">MRR</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">-</p>
            </div>
            <div className="text-4xl">💰</div>
          </div>
          <p className="text-xs text-gray-500 mt-4">
            Será implementado na Mini-Fase 16.2
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Novos (Mês)</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">-</p>
            </div>
            <div className="text-4xl">📈</div>
          </div>
          <p className="text-xs text-gray-500 mt-4">
            Será implementado na Mini-Fase 16.2
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Cancelamentos</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">-</p>
            </div>
            <div className="text-4xl">📉</div>
          </div>
          <p className="text-xs text-gray-500 mt-4">
            Será implementado na Mini-Fase 16.2
          </p>
        </div>
      </div>

      {/* Informações do Sistema */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Status do Sistema
        </h2>
        <div className="space-y-3">
          <div className="flex items-center justify-between py-2 border-b">
            <span className="text-gray-600">Backend API</span>
            <span className="flex items-center text-green-600">
              <span className="w-2 h-2 bg-green-600 rounded-full mr-2"></span>
              Online
            </span>
          </div>
          <div className="flex items-center justify-between py-2 border-b">
            <span className="text-gray-600">PostgreSQL</span>
            <span className="flex items-center text-green-600">
              <span className="w-2 h-2 bg-green-600 rounded-full mr-2"></span>
              Conectado
            </span>
          </div>
          <div className="flex items-center justify-between py-2">
            <span className="text-gray-600">Autenticação Admin</span>
            <span className="flex items-center text-green-600">
              <span className="w-2 h-2 bg-green-600 rounded-full mr-2"></span>
              Funcionando
            </span>
          </div>
        </div>
      </div>

      {/* Próximas Implementações */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-3">
          🚀 Próximas Funcionalidades
        </h3>
        <ul className="space-y-2 text-sm text-blue-800">
          <li>✅ Mini-Fase 16.1 - Login e Autenticação (Completo)</li>
          <li>⏳ Mini-Fase 16.2 - Dashboard com Métricas</li>
          <li>⏳ Mini-Fase 16.3 - Gestão de Clientes</li>
          <li>⏳ Mini-Fase 16.4 - Monitoramento de Uso OpenAI</li>
          <li>⏳ Mini-Fase 16.5 - Sistema de Tickets</li>
          <li>⏳ E muito mais...</li>
        </ul>
      </div>
    </div>
  );
}
