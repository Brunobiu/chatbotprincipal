/* eslint-disable @next/next/no-img-element */
// TODO: Header simples com links
// TODO: Você pode adicionar um logo personalizado quando tiver
import Link from 'next/link'

export default function Header() {
  return (
    <header className="border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex justify-between items-center">
          {/* TODO: Adicionar logo quando definir identidade visual */}
          {/* Exemplo: <Image src="/logo.png" alt="Logo" width={150} height={40} /> */}
          <div className="text-xl font-bold">
            Bot IA
          </div>
          
          {/* TODO: Links de navegação - personalize conforme necessário */}
          <nav className="flex space-x-6">
            <Link href="/" className="text-gray-700 hover:text-gray-900">
              Home
            </Link>
            <Link href="/login" className="text-gray-700 hover:text-gray-900">
              Login
            </Link>
            {/* TODO: Adicionar mais links quando tiver mais páginas */}
            {/* <Link href="/pricing" className="text-gray-700 hover:text-gray-900"> */}
            {/*   Preços */}
            {/* </Link> */}
            {/* <Link href="/about" className="text-gray-700 hover:text-gray-900"> */}
            {/*   Sobre */}
            {/* </Link> */}
          </nav>
        </div>
      </div>
    </header>
  )
}
