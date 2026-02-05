// TODO: Benefits Section - seção de benefícios
// TODO: Personalize os benefícios quando tiver mais detalhes do produto
export default function Benefits() {
  const benefits = [
    {
      // TODO: Você pode substituir por ícones (Lucide, Heroicons, etc.)
      title: 'Atendimento 24/7',
      description: 'Seu bot responde a qualquer hora, mesmo fora do horário comercial. Nunca mais perca um cliente.',
    },
    {
      title: 'Base de Conhecimento Personalizada',
      description: 'Use sua própria documentação para responder. O bot aprende com o seu negócio.',
    },
    {
      title: 'Fácil de Configurar',
      description: 'Conecte com WhatsApp, faça upload dos documentos e pronto. Sem código necessário.',
    },
  ]
  
  return (
    <section className="py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* TODO: Título da seção */}
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Por que escolher nosso bot?
          </h2>
          <p className="text-gray-600 text-lg">
            Benefícios que transformam seu atendimento
          </p>
        </div>
        
        {/* Grid de benefícios */}
        <div className="grid md:grid-cols-3 gap-8">
          {benefits.map((benefit, index) => (
            <div 
              key={index} 
              className="p-8 border border-gray-200 rounded hover:border-gray-400 transition"
            >
              {/* TODO: Você pode adicionar ícones aqui */}
              {/* Exemplo: <Icon className="w-12 h-12 mb-4 text-primary" /> */}
              
              <h3 className="text-xl font-semibold mb-3">
                {benefit.title}
              </h3>
              <p className="text-gray-600">
                {benefit.description}
              </p>
            </div>
          ))}
        </div>
        
        {/* TODO: Você pode adicionar mais benefícios */}
        {/* TODO: Você pode adicionar uma seção de preços aqui */}
        
      </div>
    </section>
  )
}
