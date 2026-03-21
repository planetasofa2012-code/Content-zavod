'use client'

import { useState, FormEvent } from 'react'

// Блок 10: Финальная форма заявки — имя + телефон → уведомление в Telegram
export default function CTA() {
  const [name,    setName]    = useState('')
  const [phone,   setPhone]   = useState('')
  const [status,  setStatus]  = useState<'idle' | 'loading' | 'ok' | 'err'>('idle')

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setStatus('loading')
    try {
      const res = await fetch('/api/lead', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, phone }),
      })
      if (res.ok) {
        setStatus('ok')
        setName('')
        setPhone('')
      } else {
        setStatus('err')
      }
    } catch {
      setStatus('err')
    }
  }

  return (
    <section id="cta" className="py-20 bg-primary">
      <div className="max-w-xl mx-auto px-5 text-center text-white">
        <div className="text-5xl mb-4">🎁</div>
        <h2 className="text-3xl sm:text-4xl font-extrabold mb-3">
          Бесплатный замер +
          <br />
          3D-эскиз в подарок
        </h2>
        <p className="text-white/80 text-base mb-9">
          Оставьте номер — перезвоним в течение 30 минут и согласуем удобное время.
        </p>

        {status === 'ok' ? (
          /* Успешная отправка */
          <div className="bg-white/15 backdrop-blur rounded-2xl p-8">
            <div className="text-4xl mb-3">✅</div>
            <p className="font-bold text-xl mb-2">Заявка принята!</p>
            <p className="text-white/80 text-sm">
              Александр перезвонит вам в течение 30 минут.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="bg-white/10 backdrop-blur rounded-2xl p-6 space-y-4">
            <input
              type="text"
              placeholder="👤 Ваше имя"
              value={name}
              onChange={e => setName(e.target.value)}
              required
              className="w-full bg-white/90 text-ink placeholder-muted rounded-xl px-4 py-3.5
                         text-sm focus:outline-none focus:bg-white transition-colors"
            />
            <input
              type="tel"
              placeholder="📱 Телефон: +7 (___) ___-__-__"
              value={phone}
              onChange={e => setPhone(e.target.value)}
              required
              className="w-full bg-white/90 text-ink placeholder-muted rounded-xl px-4 py-3.5
                         text-sm focus:outline-none focus:bg-white transition-colors"
            />

            <button
              type="submit"
              disabled={status === 'loading'}
              className="w-full bg-gold text-ink font-bold text-base rounded-xl py-4
                         hover:bg-amber-400 transition-all duration-200 hover:-translate-y-0.5
                         disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {status === 'loading' ? '⏳ Отправляем...' : '📐 Записаться на замер'}
            </button>

            {status === 'err' && (
              <p className="text-red-300 text-sm text-center">
                Ошибка отправки. Напишите нам в Telegram: @kuhnya154
              </p>
            )}

            <p className="text-white/55 text-xs text-center pt-1">
              🔒 Данные не передаём третьим лицам
            </p>
          </form>
        )}

        {/* Альтернативные способы связи */}
        <div className="flex flex-wrap justify-center gap-3 mt-8">
          <a
            href="https://t.me/kuhnya154"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 bg-white/15 hover:bg-white/25 transition-colors
                       rounded-xl px-5 py-2.5 text-sm font-semibold"
          >
            ✈️ Telegram
          </a>
          <a
            href="tel:+79131234567"
            className="flex items-center gap-2 bg-white/15 hover:bg-white/25 transition-colors
                       rounded-xl px-5 py-2.5 text-sm font-semibold"
          >
            📞 Позвонить
          </a>
        </div>
      </div>
    </section>
  )
}
