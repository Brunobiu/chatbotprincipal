import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'IA Bot - Automatize suas Conversas com Inteligência Artificial',
  description: 'Venda mais, aumente seu engajamento e ganhe mais seguidores com automações inteligentes para Instagram, WhatsApp, TikTok e Messenger.',
  keywords: 'automação, chatbot, instagram, whatsapp, messenger, tiktok, marketing, leads, conversas, IA',
  openGraph: {
    title: 'IA Bot - Automatize suas Conversas',
    description: 'Transforme cada conversa em uma oportunidade de negócio',
    type: 'website',
    locale: 'pt_BR',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR" className="scroll-smooth">
      <body className="antialiased">
        {children}
      </body>
    </html>
  )
}
