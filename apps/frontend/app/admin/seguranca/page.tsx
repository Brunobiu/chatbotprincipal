'use client'

import { useState, useEffect } from 'react'

interface Estatisticas {
  tentativas_login_24h: number
  falhas_login_24h: number
  taxa_falha: number
  ips_bloqueados_ativos: number
  acoes_auditoria_24h: number
  top_ips_falhas: Array<{ip: string, falhas: number}>
}

interface LoginAttempt {
  id: number
  email: string
  ip: string
  success: boolean
  user_agent: string | null
  created_at: string
}

interface IPBloqueado {
  id: number
  ip: string
  reason: string | null
  blocked_at: string
  expires_at: string
}

type AbaAtiva = 'estatisticas' | 'tentativas' | 'ips-bloqueados'

export default function SegurancaAdminPage() {
  const [abaAtiva, setAbaAtiva] = useState<AbaAtiva>('estatisticas')
  const [estatisticas, setEstatisticas] = useState<Estatisticas | null>(null)
  const [tentativas, setTentativas] = useState<LoginAttempt[]>([])
  const [ipsBloqueados, setIpsBloqueados] = useState<IPBloqueado[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    carregarEstatisticas()
  }, [])

  useEffect(() => {
    if (abaAtiva === 'tentativas') {
      carregarTentativas()
    } else if (abaAtiva === 'ips-bloqueados') {
      carregarIpsBloqueados()
    }
  }, [abaAtiva])

  const carregarEstatisticas = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      const res = await fetch('http://localhost:8000/api/v1/admin/seguranca/estatisticas', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (res.ok) {
        const data = await res.json()
        setEstatisticas(data)
      }
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error)
    } finally {
      setLoading(false)
    }
  }

  const carregarTentativas = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      const res = await fetch('http://localhost:8000/api/v1/admin/seguranca/tentativas-login?limit=50', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (res.ok) {
        const data = await res.json()
        setTentativas(data.attempts)
      }
    } catch (error) {
      console.error('Erro ao carregar tentativas:', error)
    }
  }

  const carregarIpsBloqueados = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      const res = await fetch('http://localhost:8000/api/v1/admin/seguranca/ips-bloqueados', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (res.ok) {
        const data = await res.json()
        setIpsBloqueados(data.bloqueios)
      }
    } catch (error) {
      console.error('Erro ao carregar IPs bloqueados:', error)
    }
  }

  const desbloquearIP = async (ip: string) => {
    if (!confirm(`Desbloquear IP ${ip}?`)) return
    
    try {
      const token = localStorage.getItem('admin_token')
      const res = await fetch('http://localhost:8000/api/v1/admin/seguranca/desbloquear-ip', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ ip })
      })
      
      if (res.ok) {
        await carregarIpsBloqueados()
        await carregarEstatisticas()
      } else {
        alert('Erro ao desbloquear IP')
      }
    } catch (error) {
      console.error('Erro ao desbloquear IP:', error)
      alert('Erro ao desbloquear IP')
    }
  }

  const formatarData = (data: string) => {
    return new Date(data).toLocaleString('pt-BR')
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">🔒 Segurança e Auditoria</h1>
        <p className="text-gray-600 mt-2">Monitore tentativas de login, IPs bloqueados e atividades suspeitas</p>
      </div>

      {/* Abas */}
      <div className="bg-white rounded-lg shadow mb-6">
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px">
            <button
              onClick={() => setAbaAtiva('estatisticas')}
              className={`px-6 py-4 text-sm font-medium border-b-2 ${
                abaAtiva === 'estatisticas'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Estatísticas
            </button>
            <button
              onClick={() => setAbaAtiva('tentativas')}
              className={`px-6 py-4 text-sm font-medium border-b-2 ${
                abaAtiva === 'tentativas'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Tentativas de Login
            </button>
            <button
              onClick={() => setAbaAtiva('ips-bloqueados')}
              className={`px-6 py-4 text-sm font-medium border-b-2 ${
                abaAtiva === 'ips-bloqueados'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              IPs Bloqueados
            </button>
          </nav>
        </div>

        <div className="p-6">
          {/* Estatísticas */}
          {abaAtiva === 'estatisticas' && estatisticas && (
            <div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="text-sm text-gray-600">Tentativas Login (24h)</div>
                  <div className="text-2xl font-bold text-blue-600">{estatisticas.tentativas_login_24h}</div>
                </div>
                
                <div className="bg-red-50 p-4 rounded-lg">
                  <div className="text-sm text-gray-600">Falhas Login (24h)</div>
                  <div className="text-2xl font-bold text-red-600">{estatisticas.falhas_login_24h}</div>
                  <div className="text-sm text-gray-500">Taxa: {estatisticas.taxa_falha}%</div>
                </div>
                
                <div className="bg-orange-50 p-4 rounded-lg">
                  <div className="text-sm text-gray-600">IPs Bloqueados Ativos</div>
                  <div className="text-2xl font-bold text-orange-600">{estatisticas.ips_bloqueados_ativos}</div>
                </div>
              </div>

              {estatisticas.top_ips_falhas.length > 0 && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-semibold mb-3">Top IPs com Mais Falhas (24h)</h3>
                  <div className="space-y-2">
                    {estatisticas.top_ips_falhas.map((item, idx) => (
                      <div key={idx} className="flex justify-between items-center">
                        <span className="font-mono text-sm">{item.ip}</span>
                        <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-semibold">
                          {item.falhas} falhas
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Tentativas de Login */}
          {abaAtiva === 'tentativas' && (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">IP</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Data</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {tentativas.map((t) => (
                    <tr key={t.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{t.email}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-600">{t.ip}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                          t.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {t.success ? 'Sucesso' : 'Falha'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatarData(t.created_at)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* IPs Bloqueados */}
          {abaAtiva === 'ips-bloqueados' && (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">IP</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Motivo</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Bloqueado Em</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Expira Em</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ações</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {ipsBloqueados.map((b) => (
                    <tr key={b.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">{b.ip}</td>
                      <td className="px-6 py-4 text-sm text-gray-600">{b.reason || '-'}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatarData(b.blocked_at)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatarData(b.expires_at)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <button
                          onClick={() => desbloquearIP(b.ip)}
                          className="text-blue-600 hover:text-blue-800 font-medium"
                        >
                          Desbloquear
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              
              {ipsBloqueados.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  Nenhum IP bloqueado no momento
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
