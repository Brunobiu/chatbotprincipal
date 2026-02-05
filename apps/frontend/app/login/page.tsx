'use client'

// TODO: Página de Login - formulário visual apenas (sem autenticação real ainda)
// TODO: Na FASE 5 será implementada autenticação real com JWT
// TODO: Na FASE 6 será criada proteção de rotas (middleware/guards)
import { useState } from 'react'
import Link from 'next/link'

export default function LoginPage() {
  // TODO: Estados do formulário - serão usados na FASE 5 para autenticação
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  
  // TODO: Função de login - será implementada na FASE 5
  // TODO: Atualmente é apenas visual - não autentica de verdade
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // TODO: Implementar autenticação real na FASE 5
    console.log('Email:', email, 'Senha:', password)
    alert('Login funcionalidade ainda não implementada. FASE 5.')
  }
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full">
        
        {/* TODO: Título da página */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2">
            Entrar
          </h1>
          <p className="text-gray-600">
            Acesse seu dashboard para gerenciar seu bot
          </p>
        </div>
        
        {/* TODO: Formulário de login */}
        <div className="bg-white p-8 rounded border border-gray-200">
          <form onSubmit={handleSubmit} className="space-y-6">
            
            {/* Campo de email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-gray-500"
                placeholder="seu@email.com"
                required
              />
            </div>
            
            {/* Campo de senha */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Senha
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-gray-500"
                placeholder="••••••••"
                required
              />
            </div>
            
            {/* TODO: Adicionar "Esqueceu a senha?" quando implementar recuperação */}
            {/* <div className="text-right">
              <Link href="/forgot-password" className="text-sm text-gray-600 hover:text-gray-900">
                Esqueceu a senha?
              </Link>
            </div> */}
            
            {/* Botão de login */}
            <button
              type="submit"
              className="w-full bg-gray-900 text-white py-3 font-semibold rounded hover:bg-gray-700 transition"
            >
              Entrar
            </button>
            
          </form>
          
          {/* TODO: Link para cadastro quando tiver */}
          {/* <div className="mt-6 text-center">
            <p className="text-gray-600">
              Ainda não tem conta?{' '}
              <Link href="/register" className="text-gray-900 font-semibold hover:underline">
                Cadastre-se
              </Link>
            </p>
          </div> */}
        </div>
        
        {/* Link voltar para home */}
        <div className="mt-6 text-center">
          <Link href="/" className="text-gray-600 hover:text-gray-900 text-sm">
            ← Voltar para home
          </Link>
        </div>
        
      </div>
    </div>
  )
}
