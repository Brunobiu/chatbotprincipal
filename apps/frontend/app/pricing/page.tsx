import Header from '../../components/Header';
import Footer from '../../components/Footer';
import Link from 'next/link';

// Força geração estática - super rápida
export const dynamic = 'force-static';

export default function PricingPage() {
  const plans = [
    {
      name: 'Mensal',
      price: 'R$ 147',
      period: '/mês',
      description: 'Ideal para testar',
      features: [
        'WhatsApp Bot com IA',
        'Base de conhecimento ilimitada',
        'Respostas automáticas 24/7',
        'Sistema de fallback humano',
        'Dashboard completo',
        'Suporte por e-mail',
      ],
      highlight: false,
    },
    {
      name: 'Trimestral',
      price: 'R$ 127',
      period: '/mês',
      description: 'Mais popular',
      originalPrice: 'R$ 147',
      savings: 'Economize R$ 60',
      features: [
        'Tudo do plano Mensal',
        'Desconto de 14%',
        'Suporte prioritário',
        'Relatórios avançados',
        'Treinamento de IA',
        'Analytics detalhado',
      ],
      highlight: true,
    },
    {
      name: 'Semestral',
      price: 'R$ 97',
      period: '/mês',
      description: 'Melhor custo-benefício',
      originalPrice: 'R$ 147',
      savings: 'Economize R$ 300',
      features: [
        'Tudo do plano Trimestral',
        'Desconto de 34%',
        'Suporte VIP',
        'Consultoria mensal',
        'API personalizada',
        'Integrações customizadas',
      ],
      highlight: false,
    },
  ];

  return (
    <>
      <Header />
      <main className="min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
        {/* Hero Section */}
        <section className="pt-32 pb-16 px-4">
          <div className="max-w-7xl mx-auto text-center">
            <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Planos e Preços
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-2xl mx-auto">
              Escolha o plano ideal para o seu negócio. Todos com 7 dias de teste grátis.
            </p>
            <div className="inline-flex items-center gap-2 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 px-4 py-2 rounded-full">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span className="font-semibold">7 dias grátis • Sem cartão de crédito</span>
            </div>
          </div>
        </section>

        {/* Pricing Cards */}
        <section className="pb-20 px-4">
          <div className="max-w-7xl mx-auto grid md:grid-cols-3 gap-8">
            {plans.map((plan) => (
              <div
                key={plan.name}
                className={`relative bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 ${
                  plan.highlight ? 'ring-4 ring-blue-500 scale-105' : ''
                }`}
              >
                {plan.highlight && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-blue-500 text-white px-4 py-1 rounded-full text-sm font-semibold">
                    Mais Popular
                  </div>
                )}

                <div className="text-center mb-6">
                  <h3 className="text-2xl font-bold mb-2 dark:text-white">{plan.name}</h3>
                  <p className="text-gray-600 dark:text-gray-400 text-sm">{plan.description}</p>
                </div>

                <div className="text-center mb-6">
                  {plan.originalPrice && (
                    <div className="text-gray-400 line-through text-sm">{plan.originalPrice}</div>
                  )}
                  <div className="flex items-baseline justify-center gap-1">
                    <span className="text-5xl font-bold dark:text-white">{plan.price}</span>
                    <span className="text-gray-600 dark:text-gray-400">{plan.period}</span>
                  </div>
                  {plan.savings && (
                    <div className="text-green-600 dark:text-green-400 text-sm font-semibold mt-2">
                      {plan.savings}
                    </div>
                  )}
                </div>

                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, idx) => (
                    <li key={idx} className="flex items-start gap-3">
                      <svg className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      <span className="text-gray-700 dark:text-gray-300">{feature}</span>
                    </li>
                  ))}
                </ul>

                <Link
                  href="/cadastro"
                  className={`block w-full text-center py-3 px-6 rounded-lg font-semibold transition-all ${
                    plan.highlight
                      ? 'bg-blue-600 text-white hover:bg-blue-700'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  Começar Teste Grátis
                </Link>
              </div>
            ))}
          </div>
        </section>

        {/* FAQ Section */}
        <section className="pb-20 px-4">
          <div className="max-w-3xl mx-auto">
            <h2 className="text-3xl font-bold text-center mb-12 dark:text-white">
              Perguntas Frequentes
            </h2>
            <div className="space-y-6">
              <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-md">
                <h3 className="font-semibold text-lg mb-2 dark:text-white">
                  Como funciona o teste grátis?
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Você tem 7 dias para testar todas as funcionalidades sem precisar cadastrar cartão de crédito.
                </p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-md">
                <h3 className="font-semibold text-lg mb-2 dark:text-white">
                  Posso cancelar a qualquer momento?
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Sim! Você pode cancelar sua assinatura a qualquer momento sem multas ou taxas.
                </p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-md">
                <h3 className="font-semibold text-lg mb-2 dark:text-white">
                  Posso mudar de plano depois?
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Sim! Você pode fazer upgrade ou downgrade do seu plano a qualquer momento.
                </p>
              </div>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
