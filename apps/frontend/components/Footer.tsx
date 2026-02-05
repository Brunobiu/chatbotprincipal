/* eslint-disable @next/next/no-img-element */
// TODO: Footer simples com links básicos
// TODO: Personalize quando tiver mais páginas
import Link from 'next/link'

export default function Footer() {
  return (
    <footer className="bg-gray-900 text-white py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Grid de links */}
        <div className="grid md:grid-cols-4 gap-8">
          
          {/* Coluna 1: Sobre */}
          <div>
            {/* TODO: Logo no footer */}
            <div className="text-xl font-bold mb-4">
              Bot IA
            </div>
            <p className="text-gray-400 text-sm">
              Chatbot inteligente para WhatsApp com IA. Automatize seu atendimento.
            </p>
          </div>
          
          {/* Coluna 2: Produto */}
          <div>
            <h3 className="font-semibold mb-4">Produto</h3>
            <ul className="space-y-2">
              {/* TODO: Adicionar links quando tiver páginas */}
              <li>
                <Link href="/" className="text-gray-400 hover:text-white text-sm">
                  Home
                </Link>
              </li>
              <li>
                <Link href="/checkout" className="text-gray-400 hover:text-white text-sm">
                  Preços
                </Link>
              </li>
            </ul>
          </div>
          
          {/* Coluna 3: Suporte */}
          <div>
            <h3 className="font-semibold mb-4">Suporte</h3>
            <ul className="space-y-2">
              {/* TODO: Adicionar links quando tiver páginas */}
              <li>
                <a href="#" className="text-gray-400 hover:text-white text-sm">
                  Ajuda
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-white text-sm">
                  Contato
                </a>
              </li>
            </ul>
          </div>
          
          {/* Coluna 4: Legal */}
          <div>
            <h3 className="font-semibold mb-4">Legal</h3>
            <ul className="space-y-2">
              {/* TODO: Adicionar links quando tiver páginas */}
              <li>
                <a href="#" className="text-gray-400 hover:text-white text-sm">
                  Termos de Uso
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-white text-sm">
                  Privacidade
                </a>
              </li>
            </ul>
          </div>
          
        </div>
        
        {/* Linha de copyright */}
        <div className="border-t border-gray-800 mt-12 pt-8 text-center text-gray-400 text-sm">
          <p>
            © {new Date().getFullYear()} Bot IA. Todos os direitos reservados.
          </p>
          {/* TODO: Adicionar links de redes sociais quando tiver */}
          {/* <div className="mt-4 flex justify-center space-x-4"> */}
          {/*   <a href="#" className="text-gray-400 hover:text-white"> */}
          {/*     Instagram */}
          {/*   </a> */}
          {/*   <a href="#" className="text-gray-400 hover:text-white"> */}
          {/*     LinkedIn */}
          {/*   </a> */}
          {/* </div> */}
        </div>
        
      </div>
    </footer>
  )
}
