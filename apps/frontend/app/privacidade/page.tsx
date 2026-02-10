export default function PrivacidadePage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Política de Privacidade</h1>
        
        <div className="prose prose-blue max-w-none">
          <p className="text-gray-600 mb-4">
            Última atualização: {new Date().toLocaleDateString('pt-BR')}
          </p>

          <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">1. Informações que Coletamos</h2>
          <p className="text-gray-700 mb-4">
            Coletamos as seguintes informações quando você usa nossa plataforma:
          </p>
          <ul className="list-disc list-inside text-gray-700 mb-4 space-y-2">
            <li><strong>Dados de cadastro:</strong> nome, e-mail, telefone (opcional)</li>
            <li><strong>Dados de uso:</strong> conversas, mensagens, interações com o bot</li>
            <li><strong>Dados técnicos:</strong> IP, navegador, dispositivo, cookies</li>
            <li><strong>Dados de pagamento:</strong> processados pelo Stripe (não armazenamos cartões)</li>
          </ul>

          <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">2. Como Usamos suas Informações</h2>
          <p className="text-gray-700 mb-4">
            Utilizamos suas informações para:
          </p>
          <ul className="list-disc list-inside text-gray-700 mb-4 space-y-2">
            <li>Fornecer e melhorar nossos serviços</li>
            <li>Processar pagamentos e gerenciar assinaturas</li>
            <li>Enviar notificações importantes sobre sua conta</li>
            <li>Treinar e melhorar nossos modelos de IA</li>
            <li>Prevenir fraudes e garantir segurança</li>
          </ul>

          <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">3. Compartilhamento de Dados</h2>
          <p className="text-gray-700 mb-4">
            Não vendemos seus dados pessoais. Compartilhamos informações apenas com:
          </p>
          <ul className="list-disc list-inside text-gray-700 mb-4 space-y-2">
            <li><strong>Provedores de serviço:</strong> OpenAI (IA), Stripe (pagamentos), AWS (hospedagem)</li>
            <li><strong>Requisitos legais:</strong> quando exigido por lei ou ordem judicial</li>
          </ul>

          <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">4. Segurança dos Dados</h2>
          <p className="text-gray-700 mb-4">
            Implementamos medidas de segurança técnicas e organizacionais para proteger seus dados:
          </p>
          <ul className="list-disc list-inside text-gray-700 mb-4 space-y-2">
            <li>Criptografia SSL/TLS para transmissão de dados</li>
            <li>Senhas criptografadas com bcrypt</li>
            <li>Backups regulares e redundância</li>
            <li>Monitoramento de segurança 24/7</li>
          </ul>

          <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">5. Seus Direitos (LGPD)</h2>
          <p className="text-gray-700 mb-4">
            De acordo com a Lei Geral de Proteção de Dados (LGPD), você tem direito a:
          </p>
          <ul className="list-disc list-inside text-gray-700 mb-4 space-y-2">
            <li>Acessar seus dados pessoais</li>
            <li>Corrigir dados incompletos ou desatualizados</li>
            <li>Solicitar exclusão de seus dados</li>
            <li>Revogar consentimento a qualquer momento</li>
            <li>Exportar seus dados em formato estruturado</li>
          </ul>

          <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">6. Cookies</h2>
          <p className="text-gray-700 mb-4">
            Utilizamos cookies essenciais para funcionamento da plataforma e cookies de análise para 
            melhorar a experiência do usuário. Você pode gerenciar cookies nas configurações do navegador.
          </p>

          <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">7. Retenção de Dados</h2>
          <p className="text-gray-700 mb-4">
            Mantemos seus dados enquanto sua conta estiver ativa. Após cancelamento, dados são mantidos 
            por 90 dias para recuperação e depois excluídos permanentemente.
          </p>

          <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">8. Menores de Idade</h2>
          <p className="text-gray-700 mb-4">
            Nossos serviços não são destinados a menores de 18 anos. Não coletamos intencionalmente 
            dados de menores.
          </p>

          <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">9. Alterações nesta Política</h2>
          <p className="text-gray-700 mb-4">
            Podemos atualizar esta política periodicamente. Notificaremos sobre mudanças significativas 
            por e-mail ou através da plataforma.
          </p>

          <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">10. Contato</h2>
          <p className="text-gray-700 mb-4">
            Para exercer seus direitos ou esclarecer dúvidas sobre privacidade, entre em contato através 
            do suporte dentro da plataforma ou envie e-mail para: privacidade@iabot.com
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
