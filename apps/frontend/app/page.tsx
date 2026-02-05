// TODO: Landing Page principal do projeto
// TODO: Esta página é o primeiro contato do usuário com o seu SaaS
import Header from '../components/Header'
import Hero from '../components/Hero'
import Benefits from '../components/Benefits'
import Footer from '../components/Footer'

export default function Home() {
  return (
    <div className="min-h-screen">
      {/* Header com navegação */}
      <Header />
      
      {/* Hero Section - primeira impressão */}
      <Hero />
      
      {/* Benefits Section - por que usar o produto */}
      <Benefits />
      
      {/* TODO: Você pode adicionar mais seções aqui: */}
      {/* - Como funciona */}
      {/* - Preços */}
      {/* - Depoimentos */}
      {/* - FAQ */}
      {/* - CTA final */}
      
      {/* Exemplo de seção adicional (comentado): */}
      {/* <section className="py-20 bg-gray-50"> */}
      {/*   <div className="max-w-7xl mx-auto px-4 text-center"> */}
      {/*     <h2 className="text-3xl font-bold mb-4"> */}
      {/*       Pronto para transformar seu atendimento? */}
      {/*     </h2> */}
      {/*     <p className="text-gray-600 mb-8"> */}
      {/*       Comece agora em 3 minutos. */}
      {/*     </p> */}
      {/*     <Link */}
      {/*       href="/checkout" */}
      {/*       className="inline-block bg-gray-900 text-white px-8 py-4 text-lg font-semibold rounded hover:bg-gray-700" */}
      {/*     > */}
      {/*       Começar Agora */}
      {/*     </Link> */}
      {/*   </div> */}
      {/* </section> */}
      
      {/* Footer */}
      <Footer />
    </div>
  )
}
