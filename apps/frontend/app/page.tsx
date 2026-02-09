import Header from '../components/Header';
import Hero from '../components/Hero';
import PartnersStripe from '../components/PartnersStripe';
import ChannelCards from '../components/ChannelCards';
import Features from '../components/Features';
import Stats from '../components/Stats';
import Testimonials from '../components/Testimonials';
import Steps from '../components/Steps';
import CTA from '../components/CTA';
import Footer from '../components/Footer';

// Força geração estática - super rápida, sem backend
export const dynamic = 'force-static';

export default function Home() {
  return (
    <>
      <Header />
      <main>
        <Hero />
        <PartnersStripe />
        <section id="canais">
          <ChannelCards />
        </section>
        <section id="recursos">
          <Features />
        </section>
        <Stats />
        <section id="depoimentos">
          <Testimonials />
        </section>
        <section id="como-funciona">
          <Steps />
        </section>
        <CTA />
      </main>
      <Footer />
    </>
  );
}
