'use client'

import { useState, useEffect } from 'react'

// Блок 1: Шапка — sticky, логотип, телефон, CTA
export default function Header() {
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <header
      className={`sticky top-0 z-50 transition-shadow duration-300 ${
        scrolled ? 'shadow-md bg-white/95 backdrop-blur-md' : 'bg-white'
      } border-b border-gray-100`}
    >
      <div className="max-w-5xl mx-auto px-5 flex items-center justify-between h-16 sm:h-[68px]">
        {/* Логотип */}
        <a href="#" className="flex items-center gap-2 no-underline">
          <span className="text-2xl">🏠</span>
          <span className="font-extrabold text-lg text-ink">
            Кухня<span className="text-primary">54</span>
          </span>
        </a>

        {/* Правая часть: телефон + кнопка */}
        <div className="flex items-center gap-4">
          <a
            href="tel:+79131234567"
            className="hidden sm:block font-semibold text-ink text-sm hover:text-primary transition-colors"
          >
            +7 (913) 123-45-67
          </a>
          <a href="#cta" className="btn-primary text-sm px-5 py-2.5">
            Заказать замер
          </a>
        </div>
      </div>
    </header>
  )
}
