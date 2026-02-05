// Layout base do Next.js
// TODO: Este é o layout principal que envolve todas as páginas
// TODO: Você pode adicionar um favicon, meta tags personalizadas, analytics, etc.
import type { Metadata } from 'next'
import './globals.css'

// TODO: Metadados do site - personalize quando definir nome e descrição
export const metadata: Metadata = {
  title: 'Chatbot WhatsApp com IA', // TODO: Definir nome do bot
  description: 'Automatize seu atendimento com IA no WhatsApp', // TODO: Melhorar descrição
}

// TODO: Aprender sobre rootLayout: https://nextjs.org/docs/app/building-your-application/routing/pages-and-layouts#root-layout-required
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      <body className="bg-white text-gray-900">
        {/* TODO: Você pode adicionar um Header global aqui se quiser que apareça em todas as páginas */}
        {children}
        
        {/* TODO: Você pode adicionar um Footer global aqui se quiser que apareça em todas as páginas */}
      </body>
    </html>
  )
}
