import Header from '../../components/Header';
import Footer from '../../components/Footer';
import Link from 'next/link';

// Força geração estática - super rápida
export const dynamic = 'force-static';

export default function AboutPage() {
  return (
    <>
      <Header />
      <main className="min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
        {/* Hero Section */}
        <section className="pt-32 pb-16 px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Sobre Nós
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
              Transformando o atendimento ao cliente com inteligência artificial
            </p>
          </div>
        </section>

        {/* Mission Section */}
        <section className="pb-16 px-4">
          <div className="max-w-4xl mx-auto">
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 md:p-12">
              <h2 className="text-3xl font-bold mb-6 dark:text-white">Nossa Missão</h2>
              <p className="text-lg text-gray-700 dark:text-gray-300 mb-4">
                Democratizar o acesso à tecnologia de chatbots com inteligência artificial, 
                permitindo que empresas de todos os tamanhos ofereçam atendimento 24/7 de 
                alta qualidade no WhatsApp.
              </p>
              <p className="text-lg text-gray-700 dark:text-gray-300">
                Acreditamos que todo negócio merece ter um assistente virtual inteligente, 
                capaz de responder dúvidas, qualificar leads e melhorar a experiência do cliente.
              </p>
            </div>
          </div>
        </section>

        {/* Values Section */}
        <section className="pb-16 px-4">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-3xl font-bold text-center mb-12 dark:text-white">
              Nossos Valores
            </h2>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="bg-white dark:bg-gray-800 rounded-xl p-8 shadow-lg">
                <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold mb-3 dark:text-white">Inovação</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Utilizamos as tecnologias mais avançadas de IA para entregar resultados excepcionais.
                </p>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-xl p-8 shadow-lg">
                <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold mb-3 dark:text-white">Simplicidade</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Tecnologia poderosa não precisa ser complicada. Nossa plataforma é intuitiva e fácil de usar.
                </p>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-xl p-8 shadow-lg">
                <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold mb-3 dark:text-white">Suporte</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Estamos sempre disponíveis para ajudar você a ter sucesso com nossa plataforma.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Technology Section */}
        <section className="pb-16 px-4">
          <div className="max-w-4xl mx-auto">
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl shadow-xl p-8 md:p-12 text-white">
              <h2 className="text-3xl font-bold mb-6">Tecnologia de Ponta</h2>
              <div className="space-y-4">
                <div className="flex items-start gap-4">
                  <svg className="w-6 h-6 flex-shrink-0 mt-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <h3 className="font-semibold text-lg mb-1">GPT-4 da OpenAI</h3>
                    <p className="text-blue-100">
                      Utilizamos o modelo de linguagem mais avançado do mundo para conversas naturais e inteligentes.
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <svg className="w-6 h-6 flex-shrink-0 mt-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <h3 className="font-semibold text-lg mb-1">RAG (Retrieval-Augmented Generation)</h3>
                    <p className="text-blue-100">
                      Sistema de base de conhecimento que garante respostas precisas baseadas no seu conteúdo.
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <svg className="w-6 h-6 flex-shrink-0 mt-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <h3 className="font-semibold text-lg mb-1">Sistema de Confiança</h3>
                    <p className="text-blue-100">
                      Fallback automático para humano quando a IA não tem certeza da resposta.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="pb-20 px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-3xl font-bold mb-6 dark:text-white">
              Pronto para Começar?
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
              Teste grátis por 7 dias. Sem cartão de crédito.
            </p>
            <Link
              href="/cadastro"
              className="inline-block bg-blue-600 text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-blue-700 transition-colors"
            >
              Começar Teste Grátis
            </Link>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
