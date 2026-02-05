/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      // TODO: Adicionar cores personalizadas quando definir a identidade visual
      // colors: {
      //   primary: '#sua-cor-primaria',
      //   secondary: '#sua-cor-secundaria',
      // },
      
      // TODO: Adicionar fontes personalizadas
      // fontFamily: {
      //   sans: ['Sua Fonte', 'sans-serif'],
      // },
    },
  },
  plugins: [],
}
