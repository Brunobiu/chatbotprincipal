'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

interface Plano {
  id: string;
  nome: string;
  preco_mensal: number;
  valor_total: number;
  periodo_meses: number;
  desconto_percent: number;
  economia: number;
}

export default function PlanosPage() {
  const router = useRouter();
  const [planos, setPlanos] = useState<Plano[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPlanos();
  }, []);

  const fetchPlanos = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/billing/planos');
      const data = await res.json();
      setPlanos(data);
    } catch (error) {
      console.error('Erro ao buscar planos:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAssinar = async (planoId: string) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/login');
        return;
      }

      const res = await fetch('http://localhost:8000/api/v1/billing/create-checkout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ plano: planoId })
      });

      const data = await res.json();
      
      if (res.ok) {
        // Redirecionar para dashboard
        router.push('/dashboard');
        window.location.reload();
      }
    } catch (error) {
      console.error('Erro ao assinar:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-xl">Carregando planos...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Escolha seu Plano
          </h1>
          <p className="text-xl text-gray-600">
            Todos os recursos incluídos • Cancele quando quiser
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {planos.map((plano) => (
            <div
              key={plano.id}
              className={`bg-white rounded-2xl shadow-xl p-8 ${
                plano.id === 'semestral' ? 'ring-4 ring-blue-500 relative' : ''
              }`}
            >
              {plano.id === 'semestral' && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <span className="bg-blue-500 text-white px-4 py-1 rounded-full text-sm font-semibold">
                    ⭐ POPULAR
                  </span>
                </div>
              )}

              <div className="text-center mb-6">
                <h3 className="text-2xl font-bold text-gray-900 mb-2">
                  {plano.nome}
                </h3>
                <div className="mb-4">
                  <span className="text-5xl font-bold text-gray-900">
                    R$ {plano.preco_mensal.toFixed(0)}
                  </span>
                  <span className="text-gray-600">/mês</span>
                </div>
                {plano.periodo_meses > 1 && (
                  <div className="text-sm text-gray-600">
                    Cobrado R$ {plano.valor_total.toFixed(0)} a cada {plano.periodo_meses} meses
                  </div>
                )}
              </div>

              {plano.economia > 0 && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-6 text-center">
                  <p className="text-green-700 font-semibold">
                    Economize R$ {plano.economia.toFixed(0)}
                  </p>
                  <p className="text-green-600 text-sm">
                    {plano.desconto_percent}% de desconto
                  </p>
                </div>
              )}

              <button
                onClick={() => handleAssinar(plano.id)}
                className={`w-full py-3 rounded-lg font-semibold transition ${
                  plano.id === 'semestral'
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                }`}
              >
                Assinar Agora
              </button>

              <div className="mt-8 space-y-3">
                <div className="flex items-center text-sm text-gray-600">
                  <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  Chatbot com IA ilimitado
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  Base de conhecimento
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  Suporte prioritário
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  Cancele quando quiser
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-12 text-center">
          <p className="text-gray-600 mb-4">
            Ainda em dúvida? Experimente grátis por 7 dias!
          </p>
          <button
            onClick={() => router.push('/cadastro')}
            className="text-blue-600 hover:underline font-medium"
          >
            Criar conta grátis →
          </button>
        </div>
      </div>
    </div>
  );
}
