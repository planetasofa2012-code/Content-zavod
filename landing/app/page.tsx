import Header     from './components/Header'
import Hero       from './components/Hero'
import Problems   from './components/Problems'
import Solution   from './components/Solution'
import HowWeWork  from './components/HowWeWork'
import Stats      from './components/Stats'
import Portfolio  from './components/Portfolio'
import Reviews    from './components/Reviews'
import Calculator from './components/Calculator'
import Pricing    from './components/Pricing'
import FAQ        from './components/FAQ'
import CTA        from './components/CTA'
import Footer     from './components/Footer'

// Главная страница лендинга — 11 блоков продающей страницы
export default function HomePage() {
  return (
    <>
      <Header />
      <main>
        <Hero />
        <Problems />
        <Solution />
        <HowWeWork />
        <Stats />
        <Portfolio />
        <Reviews />
        <Calculator />
        <Pricing />
        <FAQ />
        <CTA />
      </main>
      <Footer />
    </>
  )
}
