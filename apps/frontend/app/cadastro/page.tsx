'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import FingerprintJS from '@fingerprintjs/fingerprintjs';

function AuthForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isLogin, setIsLogin] = useState(searchParams.get('mode') !== 'cadastro');
  
  const [formData, setFormData] = useState({
    nome: '',
    email: '',
    telefone: '',
    senha: '',
    confirmarSenha: '',
    aceitarTermos: false
  });
  const [erro, setErro] = useState('');
  const [loading, setLoading] = useState(false);
  const [fingerprint, setFingerprint] = useState<string | null>(null);

  // Capturar fingerprint ao carregar página
  useEffect(() => {
    const getFingerprint = async () => {
      try {
        const fp = await FingerprintJS.load();
        const result = await fp.get();
        setFingerprint(result.visitorId);
      } catch (error) {
        console.error('Erro ao capturar fingerprint:', error);
      }
    };
    getFingerprint();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErro('');

    if (isLogin) {
      // LOGIN
      if (!formData.email || !formData.senha) {
        setErro('Preencha email e senha');
        return;
      }

      setLoading(true);

      try {
        const res = await fetch('http://localhost:8000/api/v1/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: formData.email,
            senha: formData.senha
          })
        });

        const data = await res.json();

        if (!res.ok) {
          setErro(data.detail || 'Erro ao fazer login');
          setLoading(false);
          return;
        }

        localStorage.setItem('token', data.access_token);
        router.push('/dashboard');
      } catch (error) {
        setErro('Erro ao conectar com servidor');
        setLoading(false);
      }
    } else {
      // CADASTRO
      if (!formData.nome || !formData.email || !formData.senha) {
        setErro('Preencha todos os campos obrigatórios');
        return;
      }

      if (formData.senha.length < 8) {
        setErro('Senha deve ter no mínimo 8 caracteres');
        return;
      }

      if (formData.senha !== formData.confirmarSenha) {
        setErro('As senhas não coincidem');
        return;
      }

      if (!formData.aceitarTermos) {
        setErro('Você deve aceitar os termos de uso');
        return;
      }

      setLoading(true);

      try {
        const res = await fetch('http://localhost:8000/api/v1/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            nome: formData.nome,
            email: formData.email,
            telefone: formData.telefone || null,
            senha: formData.senha,
            aceitar_termos: formData.aceitarTermos,
            device_fingerprint: fingerprint
          })
        });

        const data = await res.json();

        if (!res.ok) {
          if (data.detail && typeof data.detail === 'object') {
            if (data.detail.code === 'TEMP_EMAIL_BLOCKED') {
              setErro('❌ E-mails temporários não são permitidos. Use um e-mail válido.');
            } else if (data.detail.code === 'IP_LIMIT_EXCEEDED') {
              setErro('⚠️ Limite de cadastros atingido. Tente novamente mais tarde.');
            } else if (data.detail.code === 'DEVICE_ALREADY_USED') {
              setErro('⚠️ Este dispositivo já possui um trial ativo.');
            } else {
              setErro(data.detail.message || 'Erro ao criar conta');
            }
          } else {
            setErro(data.detail || 'Erro ao criar conta');
          }
          setLoading(false);
          return;
        }

        localStorage.setItem('token', data.access_token);
        router.push('/dashboard');
      } catch (error) {
        setErro('Erro ao conectar com servidor');
        setLoading(false);
      }
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {isLogin ? 'Bem-vindo de volta!' : 'Criar Conta Grátis'}
          </h1>
          <p className="text-gray-600">
            {isLogin ? 'Entre com suas credenciais' : '7 dias de trial gratuito • Sem cartão de crédito'}
          </p>
        </div>

        {/* Toggle Login/Cadastro */}
        <div className="flex gap-2 mb-6 bg-gray-100 p-1 rounded-lg">
          <button
            type="button"
            onClick={() => {
              setIsLogin(true);
              setErro('');
            }}
            className={`flex-1 py-2 rounded-md font-medium transition ${
              isLogin
                ? 'bg-white text-blue-600 shadow'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Login
          </button>
          <button
            type="button"
            onClick={() => {
              setIsLogin(false);
              setErro('');
            }}
            className={`flex-1 py-2 rounded-md font-medium transition ${
              !isLogin
                ? 'bg-white text-blue-600 shadow'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Cadastro
          </button>
        </div>

        {erro && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
            {erro}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Nome - só no cadastro */}
          {!isLogin && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nome Completo *
              </label>
              <input
                type="text"
                value={formData.nome}
                onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Seu nome"
              />
            </div>
          )}

          {/* Email */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email *
            </label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="seu@email.com"
            />
          </div>

          {/* Telefone - só no cadastro */}
          {!isLogin && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Telefone (opcional)
              </label>
              <input
                type="tel"
                value={formData.telefone}
                onChange={(e) => setFormData({ ...formData, telefone: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="(00) 00000-0000"
              />
              <p className="text-xs text-gray-500 mt-1">
                Para receber notificações por SMS
              </p>
            </div>
          )}

          {/* Senha */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Senha *
            </label>
            <input
              type="password"
              value={formData.senha}
              onChange={(e) => setFormData({ ...formData, senha: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder={isLogin ? 'Sua senha' : 'Mínimo 8 caracteres'}
            />
          </div>

          {/* Confirmar Senha - só no cadastro */}
          {!isLogin && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Confirmar Senha *
              </label>
              <input
                type="password"
                value={formData.confirmarSenha}
                onChange={(e) => setFormData({ ...formData, confirmarSenha: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Digite a senha novamente"
              />
            </div>
          )}

          {/* Termos - só no cadastro */}
          {!isLogin && (
            <div className="flex items-start">
              <input
                type="checkbox"
                checked={formData.aceitarTermos}
                onChange={(e) => setFormData({ ...formData, aceitarTermos: e.target.checked })}
                className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label className="ml-2 text-sm text-gray-600">
                Aceito os{' '}
                <Link href="/termos" className="text-blue-600 hover:underline">
                  termos de uso
                </Link>{' '}
                e{' '}
                <Link href="/privacidade" className="text-blue-600 hover:underline">
                  política de privacidade
                </Link>
              </label>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (isLogin ? 'Entrando...' : 'Criando conta...') : (isLogin ? 'Entrar' : 'Criar Conta Grátis')}
          </button>
        </form>

        {/* Link alternativo */}
        <div className="mt-6 text-center text-sm text-gray-600">
          {isLogin ? (
            <>
              Não tem uma conta?{' '}
              <button
                onClick={() => setIsLogin(false)}
                className="text-blue-600 hover:underline font-medium"
              >
                Criar conta grátis
              </button>
            </>
          ) : (
            <>
              Já tem uma conta?{' '}
              <button
                onClick={() => setIsLogin(true)}
                className="text-blue-600 hover:underline font-medium"
              >
                Fazer login
              </button>
            </>
          )}
        </div>

        {/* Trust badges - só no cadastro */}
        {!isLogin && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <div className="flex items-center justify-center space-x-6 text-sm text-gray-500">
              <div className="flex items-center">
                <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                7 dias grátis
              </div>
              <div className="flex items-center">
                <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                Sem cartão
              </div>
              <div className="flex items-center">
                <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                Cancele quando quiser
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function AuthPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        </div>
      </div>
    }>
      <AuthForm />
    </Suspense>
  );
}
