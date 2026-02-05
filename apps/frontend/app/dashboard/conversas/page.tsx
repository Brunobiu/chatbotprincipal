'use client'

export default function ConversasPage() {
  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Conversas</h1>
      
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-center py-12">
          <div className="text-6xl mb-4">💭</div>
          <h2 className="text-2xl font-semibold mb-2">Em Desenvolvimento</h2>
          <p className="text-gray-600 mb-6">
            Aqui você poderá acompanhar e gerenciar todas as conversas<br />
            do seu bot com os clientes.
          </p>
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 max-w-2xl mx-auto text-left">
            <h3 className="font-semibold mb-2">O que virá nesta seção:</h3>
            <ul className="space-y-2 text-sm text-gray-700">
              <li>✓ Lista de conversas ativas</li>
              <li>✓ Histórico de mensagens (30 dias)</li>
              <li>✓ Filtro por status (IA ativa, aguardando humano)</li>
              <li>✓ Interface de chat para resposta manual</li>
              <li>✓ Notificações de conversas pendentes</li>
              <li>✓ Indicador de confiança da IA</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
