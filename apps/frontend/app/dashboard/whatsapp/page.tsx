'use client'

export default function WhatsAppPage() {
  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Conectar WhatsApp</h1>
      
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-center py-12">
          <div className="text-6xl mb-4">💬</div>
          <h2 className="text-2xl font-semibold mb-2">Em Desenvolvimento</h2>
          <p className="text-gray-600 mb-6">
            Aqui você poderá conectar seu número do WhatsApp<br />
            escaneando um QR Code.
          </p>
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 max-w-2xl mx-auto text-left">
            <h3 className="font-semibold mb-2">O que virá nesta seção:</h3>
            <ul className="space-y-2 text-sm text-gray-700">
              <li>✓ QR Code para conectar WhatsApp</li>
              <li>✓ Status da conexão em tempo real</li>
              <li>✓ Informações do número conectado</li>
              <li>✓ Botão para desconectar</li>
              <li>✓ Integração com Evolution API</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
