'use client';

import { useEffect, useState } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import WidgetDicasIA from '../components/WidgetDicasIA';

interface DashboardMetrics {
  total_clientes: number;
  clientes_ativos: number;
  clientes_suspensos: number;
  clientes_pendentes: number;
  novos_hoje: number;
  novos_semana: number;
  novos_mes: number;
  cancelamentos_mes: number;
  mrr: number;
  ticket_medio: number;
  taxa_conversao: number;
}

interface VendaDiaria {
  data: string;
  quantidade: number;
  receita: number;
}

interface ReceitaMensal {
  mes: string;
  receita: number;
}

interface ClienteRecente {
  id: number;
  nome: string;
  email: string;
  status: string;
  created_at: string;
}

interface DashboardData {
  metrics: DashboardMetrics;
  vendas_diarias: VendaDiaria[];
  receita_mensal: ReceitaMensal[];
  clientes_recentes: ClienteRecente[];
}

export default function AdminDashboardPage() {
  const [admin, setAdmin] = useState<any>(null);
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const adminData = localStorage.getItem('admin_user');
    if (adminData) {
      setAdmin(JSON.parse(adminData));
    }
    
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('admin_token');
      if (!token) {
        setError('Token não encontrado');
        return;
      }

      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      const response = await fetch(`${backendUrl}/api/v1/admin/dashboard/metrics`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Erro ao buscar métricas');
      }

      const dashboardData = await response.json();
      setData(dashboardData);
    } catch (err: any) {
      setError(err.message);
      console.error('Erro ao buscar dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ativo':
        return 'bg-green-100 text-green-800';
      case 'suspenso':
        return 'bg-red-100 text-red-800';
      case 'pendente':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Carregando métricas...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-red-900 mb-2">Erro ao carregar dashboard</h3>
        <p className="text-red-700">{error}</p>
        <button
          onClick={fetchDashboardData}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Tentar Novamente
        </button>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl md:text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">
          Bem-vindo de volta, {admin?.nome}!
        </p>
      </div>

      {/* Widget Dicas da IA */}
      <WidgetDicasIA />

      {/* Cards de Métricas Principais */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Clientes</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{data.metrics.total_clientes}</p>
              <p className="text-xs text-green-600 mt-2">
                ✓ {data.metrics.clientes_ativos} ativos
              </p>
            </div>
            <div className="text-4xl">👥</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">MRR</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{formatCurrency(data.metrics.mrr)}</p>
              <p className="text-xs text-gray-500 mt-2">
                Receita mensal recorrente
              </p>
            </div>
            <div className="text-4xl">💰</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Novos (Mês)</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{data.metrics.novos_mes}</p>
              <p className="text-xs text-blue-600 mt-2">
                +{data.metrics.novos_hoje} hoje
              </p>
            </div>
            <div className="text-4xl">📈</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Taxa Conversão</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{data.metrics.taxa_conversao}%</p>
              <p className="text-xs text-gray-500 mt-2">
                Ativos / Total
              </p>
            </div>
            <div className="text-4xl">🎯</div>
          </div>
        </div>
      </div>

      {/* Cards Secundários */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm font-medium text-gray-600">Clientes Suspensos</p>
          <p className="text-2xl font-bold text-red-600 mt-2">{data.metrics.clientes_suspensos}</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm font-medium text-gray-600">Clientes Pendentes</p>
          <p className="text-2xl font-bold text-yellow-600 mt-2">{data.metrics.clientes_pendentes}</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm font-medium text-gray-600">Cancelamentos (Mês)</p>
          <p className="text-2xl font-bold text-gray-900 mt-2">{data.metrics.cancelamentos_mes}</p>
        </div>
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Vendas Diárias */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Vendas Diárias (Últimos 30 dias)
          </h2>
          {data.vendas_diarias.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={data.vendas_diarias}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="data" 
                  tickFormatter={(value) => formatDate(value)}
                  fontSize={12}
                />
                <YAxis fontSize={12} />
                <Tooltip 
                  labelFormatter={(value) => formatDate(value)}
                  formatter={(value: any) => [value, 'Clientes']}
                />
                <Bar dataKey="quantidade" fill="#3b82f6" name="Novos Clientes" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-500 text-center py-12">Nenhuma venda nos últimos 30 dias</p>
          )}
        </div>

        {/* Receita Mensal */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Receita Mensal (Últimos 6 meses)
          </h2>
          {data.receita_mensal.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={data.receita_mensal}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="mes" fontSize={12} />
                <YAxis fontSize={12} />
                <Tooltip formatter={(value: any) => [formatCurrency(value), 'Receita']} />
                <Line 
                  type="monotone" 
                  dataKey="receita" 
                  stroke="#10b981" 
                  strokeWidth={2}
                  name="Receita"
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-500 text-center py-12">Nenhuma receita nos últimos 6 meses</p>
          )}
        </div>
      </div>

      {/* Últimos Clientes */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Últimos Clientes Cadastrados
        </h2>
        {data.clientes_recentes.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Nome
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Cadastrado em
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {data.clientes_recentes.map((cliente) => (
                  <tr key={cliente.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {cliente.nome}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {cliente.email}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(cliente.status)}`}>
                        {cliente.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(cliente.created_at).toLocaleDateString('pt-BR')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">Nenhum cliente cadastrado ainda</p>
        )}
      </div>

    </div>
  );
}
