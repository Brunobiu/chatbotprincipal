'use client';

import { useEffect, useState } from 'react';

interface ResumoIA {
  novos_clientes: Array<{nome: string; email: string; hora: string}>;
  trials_expirando: Array<{nome: string; dias: number}>;
  cancelamentos: Array<{nome: string; hora: string}>;
  dicas: string[];
  financeiro: {
    receita_mensal: number;
    clientes_pagos: number;
    custo_openai: number;
    lucro: number;
    margem: number;
  };
  ultima_atualizacao: string;
}

export default function IAWidget() {
  const [resumo, setResumo] = useState<ResumoIA | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchResumo();
    // Atualizar a cada 1 hora
    const interval = setInterval(fetchResumo, 3600000);
    return () => clearInterval(interval);
  }, []);

  const fetchResumo = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/admin/ia/resumo-atual');
      const data = await res.json();
      setResumo(data);
    } catch (error) {
      console.error('Erro ao buscar resumo:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return null;
  if (!resumo) return null;

  const hoje = new Date().toLocaleDateString('pt-BR');

  return (
    <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg shadow-lg p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold flex items-center">
          🤖 ASSISTENTE IA - Resumo de Hoje ({hoje})
        </h2>
        <button
          onClick={fetchResumo}
          className="bg-white/20 hover:bg-white/30 px-3 py-1 rounded text-sm transition"
        >
          🔄 Atualizar
        </button>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Coluna Esquerda */}
        <div className="space-y-4">
          {/* Novos Clientes */}
          {resumo.novos_clientes.length > 0 && (
            <div className="bg-white/10 rounded-lg p-4">
              <h3 className="font-semibold mb-2 flex items-center">
                📊 NOVOS CLIENTES ({resumo.novos_clientes.length})
              </h3>
              <ul className="space-y-1 text-sm">
                {resumo.novos_clientes.slice(0, 3).map((c, i) => (
                  <li key={i}>• {c.nome} - cadastrou às {c.hora}</li>
                ))}
                {resumo.novos_clientes.length > 3 && (
                  <li className="text-white/70">+ {resumo.novos_clientes.length - 3} mais</li>
                )}
              </ul>
            </div>
          )}

          {/* Trials Expirando */}
          {resumo.trials_expirando.length > 0 && (
            <div className="bg-orange-500/20 rounded-lg p-4">
              <h3 className="font-semibold mb-2 flex items-center">
                ⚠️ TRIALS EXPIRANDO ({resumo.trials_expirando.length})
              </h3>
              <ul className="space-y-1 text-sm">
                {resumo.trials_expirando.slice(0, 3).map((c, i) => (
                  <li key={i}>• {c.nome} - expira em {c.dias} dia{c.dias !== 1 ? 's' : ''}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Cancelamentos */}
          {resumo.cancelamentos.length > 0 && (
            <div className="bg-red-500/20 rounded-lg p-4">
              <h3 className="font-semibold mb-2 flex items-center">
                ❌ CANCELAMENTOS ({resumo.cancelamentos.length})
              </h3>
              <ul className="space-y-1 text-sm">
                {resumo.cancelamentos.map((c, i) => (
                  <li key={i}>• {c.nome} - cancelou às {c.hora}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Coluna Direita */}
        <div className="space-y-4">
          {/* Dicas */}
          {resumo.dicas.length > 0 && (
            <div className="bg-yellow-500/20 rounded-lg p-4">
              <h3 className="font-semibold mb-2 flex items-center">
                💡 DICAS DE IA
              </h3>
              <ul className="space-y-2 text-sm">
                {resumo.dicas.map((dica, i) => (
                  <li key={i}>• {dica}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Financeiro */}
          <div className="bg-green-500/20 rounded-lg p-4">
            <h3 className="font-semibold mb-2 flex items-center">
              💰 ANÁLISE FINANCEIRA
            </h3>
            <div className="space-y-1 text-sm">
              <p>• Receita mensal: R$ {resumo.financeiro.receita_mensal.toFixed(2)} ({resumo.financeiro.clientes_pagos} clientes)</p>
              <p>• Custo OpenAI: R$ {resumo.financeiro.custo_openai.toFixed(2)}</p>
              <p>• Lucro líquido: R$ {resumo.financeiro.lucro.toFixed(2)} (margem: {resumo.financeiro.margem}%)</p>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-4 text-xs text-white/70 text-right">
        Última atualização: {new Date(resumo.ultima_atualizacao).toLocaleTimeString('pt-BR')}
      </div>
    </div>
  );
}
