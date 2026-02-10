export default function TermosPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Termos de Uso</h1>
        
        <div className="prose prose-blue max-w-none">
          <p className="text-gray-600 mb-4">
            Última atualização: {new Date().toLocaleDateString('pt-BR')}
          </p>

          <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">1. Aceitação dos Termos</h2>
          <p className="text-gray-700 mb-4">
            Ao acessar e usar nossa plataforma de automação com IA, você concorda com estes termos de uso. 
            Se você não concordar com qualquer parte destes termos, não utilize nossos serviços.
          </p>

          <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">2. Descrição do Serviço</h2>
          <p className="text-gray-700 mb-4">
            Oferecemos uma plataforma SaaS de automação de conversas com inteligência artificial para 
            WhatsApp, Instagram, TikTok e Messenger. O serviço inclui chatbot com IA, base de conhecimento 
            e sistema de fallback para atendimento humano.
          </p>

          <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">3. Trial Gratuito</h2>
          <p className="text-gray-700 mb-4">
            Oferecemos 7 dias de trial gratuito sem necessidade de cartão de crédito. Após o período de 
            trial, você pode escolher um plano pago ou cancelar sua conta sem custos.
          </p>

          <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">4. Uso Aceitável</h2>
          <p className="text-gray-700 mb-4">
            Você concorda em usar nossos serviços apenas para fins legais e de acordo com todas as leis 
            aplicáveis. É proibido:
          </p>
          <ul className="list-disc list-inside text-gray-700 mb-4 space-y-2">
            <li>Enviar spam ou mensagens não solicitadas</li>
            <li>Violar direitos de propriedade intelectual</li>
            <li>Usar o serviço para atividades ilegais</li>
            <li>Tentar hackear ou comprometer a segurança da plataforma</li>
          </ul>

          <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">5. Pagamentos e Cancelamento</h2>
          <p className="text-gray-700 mb-4">
            Os pagamentos são processados mensalmente, trimestralmente ou semestralmente conforme o plano 
            escolhido. Você pode cancelar sua assinatura a qualquer momento através do painel de controle.
          </p>

          <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">6. Propriedade Intelectual</h2>
          <p className="text-gray-700 mb-4">
            Todo o conteúdo, código, design e funcionalidades da plataforma são de nossa propriedade 
            exclusiva e protegidos por leis de direitos autorais.
          </p>

          <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">7. Limitação de Responsabilidade</h2>
          <p className="text-gray-700 mb-4">
            Não nos responsabilizamos por danos indiretos, incidentais ou consequenciais resultantes do 
            uso ou impossibilidade de uso de nossos serviços.
          </p>

          <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">8. Modificações</h2>
          <p className="text-gray-700 mb-4">
            Reservamos o direito de modificar estes termos a qualquer momento. Notificaremos os usuários 
            sobre mudanças significativas por e-mail.
          </p>

          <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">9. Contato</h2>
          <p className="text-gray-700 mb-4">
            Para dúvidas sobre estes termos, entre em contato através do suporte dentro da plataforma.
          </p>
        </div>

        <div className="mt-8 pt-6 border-t">
          <a href="/cadastro" className="text-blue-600 hover:underline">
            ← Voltar para cadastro
          </a>
        </div>
      </div>
    </div>
  );
}
