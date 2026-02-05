/** @type {import('next').NextConfig} */
const nextConfig = {
  // TODO: Configuração básica do Next.js
  // Você pode adicionar configurações de imagens, redirects, etc. aqui
  output: 'standalone', // Necessário para Docker
  
  // TODO: Configurar dominio para imagens quando tiver
  // images: {
  //   domains: ['seu-dominio.com'],
  // },
}

module.exports = nextConfig
