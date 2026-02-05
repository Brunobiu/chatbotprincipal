/* eslint-disable @next/next/no-img-element */
// TODO: Hero Section - seção principal da landing page
// TODO: Personalize o título, descrição e CTA quando definir identidade visual
import Link from 'next/link'

export default function Hero() {
  return (
    <section className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        
        {/* TODO: Título principal - defina um nome cativante para o bot */}
        <h1 className="text-5xl md:text-6xl font-bold mb-6">
          Chatbot Inteligente para WhatsApp
        </h1>
        
        {/* TODO: Descrição - explique o que o bot faz de forma simples */}
        <p className="text-xl md:text-2xl text-gray-700 mb-8 max-w-3xl mx-auto">
          Automatize seu atendimento com IA. Respondemos a perguntas dos seus clientes 24/7, usando sua base de conhecimento.
        </p>
        
        {/* TODO: Botão de CTA (Call-to-Action) - personalize texto e cor */}
        <Link 
          href="/checkout" 
          className="inline-block bg-gray-900 text-white px-8 py-4 text-lg font-semibold rounded hover:bg-gray-700 transition"
        >
          Quero Assinar
        </Link>
        
        {/* TODO: Você pode adicionar mais elementos como: */}
        {/* - Imagem/ilustração */}
        {/* - Vídeo demonstrativo */}
        {/* - Depoimentos de clientes */}
        {/* - Número de clientes satisfeitos */}
        
        {/* Exemplo: <div className="mt-12"> */}
        {/*   <p className="text-gray-600"> */}
        {/*     <span className="font-bold">100+</span> empresas confiam no nosso bot */}
        {/*   </p> */}
        {/* </div> */}
        
      </div>
    </section>
  )
}
