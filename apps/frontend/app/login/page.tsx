'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import FingerprintJS from '@fingerprintjs/fingerprintjs'

export default function LoginPage() {
  const router = useRouter()
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [nome, setNome] = useState('')
  const [telefone, setTelefone] = useState('')
  const [confirmarSenha, setConfirmarSenha] = useState('')
  const [aceitarTermos, setAceitarTermos] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [fingerprint, setFingerprint] = useState<string | null>(null)
  
  // Capturar fingerprint
  useEffect(() => {
    const getFingerprint = async () => {
      try {
        const fp = await FingerprintJS.load()
        const result = await fp.get()
        setFingerprint(result.visitorId)
      } catch (error) {
        console.error('Erro ao capturar fingerprint:', error)
      }
    }
    getFingerprint()
  }, [])
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    
    try {
      if (isLogin) {
        // LOGIN
        const response = await fetch('http://localhost:8000/api/v1/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, senha: password }),
        })
        
        if (!response.ok) {
          const data = await response.json()
          throw new Error(data.detail || 'Email ou senha incorretos')
        }
        
        const data = await response.json()
        localStorage.setItem('token', data.access_token)
        localStorage.setItem('cliente', JSON.stringify(data.cliente))
        router.push('/dashboard')
        
      } else {
        // CADASTRO
        if (!nome || !email || !password) {
          throw new Error('Preencha todos os campos obrigatórios')
        }
        
        if (password.length < 8) {
          throw new Error('Senha deve ter no mínimo 8 caracteres')
        }
        
        if (password !== confirmarSenha) {
          throw new Error('As senhas não coincidem')
        }
        
        if (!aceitarTermos) {
          throw new Error('Você deve aceitar os termos de uso')
        }
        
        const response = await fetch('http://localhost:8000/api/v1/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            nome,
            email,
            telefone: telefone || null,
            senha: password,
            aceitar_termos: aceitarTermos,
            device_fingerprint: fingerprint
          }),
        })
        
        const data = await response.json()
        
        if (!response.ok) {
          if (data.detail && typeof data.detail === 'object') {
            throw new Error(data.detail.message || 'Erro ao criar conta')
          }
          throw new Error(data.detail || 'Erro ao criar conta')
        }
        
        localStorage.setItem('token', data.access_token)
        router.push('/dashboard')
      }
      
    } catch (err: any) {
      setError(err.message || 'Erro ao processar. Tente novamente.')
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div className="min-h-screen flex">
      {/* Lado Esquerdo - Imagem/Ilustração */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-purple-600 via-blue-600 to-indigo-700 relative overflow-hidden">
        <div className="absolute inset-0 bg-black opacity-20"></div>
        
        {/* Padrão de fundo */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 left-0 w-96 h-96 bg-white rounded-full blur-3xl"></div>
          <div className="absolute bottom-0 right-0 w-96 h-96 bg-white rounded-full blur-3xl"></div>
        </div>
        
        {/* Conteúdo */}
        <div className="relative z-10 flex flex-col justify-center items-center w-full p-6 text-white">
          <div className="max-w-md">
            <div className="mb-4">
              <div className="text-3xl mb-2">🤖</div>
              <h1 className="text-2xl font-bold mb-1.5">WhatsApp AI Bot</h1>
              <p className="text-base text-blue-100">Automatize seu atendimento</p>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-start gap-2">
                <div className="text-base">✅</div>
                <div>
                  <h3 className="font-semibold text-xs">Respostas Instantâneas</h3>
                  <p className="text-blue-100 text-[10px]">IA responde 24/7</p>
                </div>
              </div>
              
              <div className="flex items-start gap-2">
                <div className="text-base">🎯</div>
                <div>
                  <h3 className="font-semibold text-xs">Personalização Total</h3>
                  <p className="text-blue-100 text-[10px]">Configure tom e conhecimento</p>
                </div>
              </div>
              
              <div className="flex items-start gap-2">
                <div className="text-base">📊</div>
                <div>
                  <h3 className="font-semibold text-xs">Análises Detalhadas</h3>
                  <p className="text-blue-100 text-[10px]">Métricas em tempo real</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Lado Direito - Formulário */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-6 bg-gray-50">
        <div className="max-w-md w-full">
          {/* Logo Mobile */}
          <div className="lg:hidden text-center mb-6">
            <div className="text-4xl mb-2">🤖</div>
            <h1 className="text-xl font-bold text-gray-900">WhatsApp AI Bot</h1>
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-lg">
            <div className="mb-4">
              <h2 className="text-2xl font-bold text-gray-900 mb-1">
                {isLogin ? 'Bem-vindo!' : 'Criar Conta'}
              </h2>
              <p className="text-sm text-gray-600">
                {isLogin ? 'Entre para continuar' : '7 dias grátis • Sem cartão'}
              </p>
            </div>
            
            <form onSubmit={handleSubmit} className="space-y-3">
              {error && (
                <div className="bg-red-50 border-l-4 border-red-500 text-red-700 px-3 py-2 rounded text-sm animate-shake">
                  <div className="flex items-center gap-2">
                    <span>⚠️</span>
                    <span>{error}</span>
                  </div>
                </div>
              )}
              
              {/* Nome - só no cadastro */}
              {!isLogin && (
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">Nome Completo *</label>
                  <input
                    type="text"
                    value={nome}
                    onChange={(e) => setNome(e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                    placeholder="Seu nome"
                    disabled={loading}
                  />
                </div>
              )}
              
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Email *</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                  placeholder="seu@email.com"
                  required
                  disabled={loading}
                />
              </div>
              
              {/* Telefone - só no cadastro e OBRIGATÓRIO */}
              {!isLogin && (
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">Telefone *</label>
                  <input
                    type="tel"
                    value={telefone}
                    onChange={(e) => setTelefone(e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                    placeholder="(00) 00000-0000"
                    disabled={loading}
                  />
                </div>
              )}
              
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Senha *</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                  placeholder={isLogin ? '••••••••' : 'Mínimo 8 caracteres'}
                  required
                  disabled={loading}
                />
              </div>
              
              {/* Confirmar Senha - só no cadastro */}
              {!isLogin && (
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">Confirmar Senha *</label>
                  <input
                    type="password"
                    value={confirmarSenha}
                    onChange={(e) => setConfirmarSenha(e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                    placeholder="Digite novamente"
                    disabled={loading}
                  />
                </div>
              )}
              
              {/* Termos - só no cadastro */}
              {!isLogin && (
                <div className="flex items-start">
                  <input
                    type="checkbox"
                    checked={aceitarTermos}
                    onChange={(e) => setAceitarTermos(e.target.checked)}
                    className="mt-0.5 h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                  />
                  <label className="ml-2 text-xs text-gray-600">
                    Aceito os{' '}
                    <Link href="/termos" target="_blank" className="text-purple-600 hover:underline">
                      termos
                    </Link>{' '}
                    e{' '}
                    <Link href="/privacidade" target="_blank" className="text-purple-600 hover:underline">
                      privacidade
                    </Link>
                  </label>
                </div>
              )}
              
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white py-2.5 rounded-lg text-sm font-semibold hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {isLogin ? 'Entrando...' : 'Criando...'}
                  </span>
                ) : (
                  isLogin ? 'Entrar' : 'Criar Conta Grátis'
                )}
              </button>
            </form>
            
            <div className="mt-4 text-center">
              <button
                onClick={() => {
                  setIsLogin(!isLogin)
                  setError('')
                }}
                className="text-sm text-purple-600 hover:text-purple-700 font-medium transition-colors"
              >
                {isLogin ? 'Não tem conta? Criar agora →' : '← Já tem conta? Entrar'}
              </button>
            </div>
          </div>
          
          <p className="text-center text-sm text-gray-500 mt-6">
            © 2024 WhatsApp AI Bot. Todos os direitos reservados.
          </p>
        </div>
      </div>
      
      <style jsx>{`
        @keyframes fade-in {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }
        
        @keyframes slide-up {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes shake {
          0%, 100% {
            transform: translateX(0);
          }
          10%, 30%, 50%, 70%, 90% {
            transform: translateX(-5px);
          }
          20%, 40%, 60%, 80% {
            transform: translateX(5px);
          }
        }
        
        .animate-fade-in {
          animation: fade-in 0.6s ease-out;
        }
        
        .animate-slide-up {
          animation: slide-up 0.8s ease-out 0.3s both;
        }
        
        .animate-shake {
          animation: shake 0.5s ease-in-out;
        }
      `}</style>
    </div>
  )
}
