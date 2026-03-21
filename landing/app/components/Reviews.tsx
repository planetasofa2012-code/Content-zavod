'use client'

import { useState } from 'react'

// Блок 7: Отзывы клиентов — карусель с 5 звёздами
const reviews = [
  {
    name: 'Мария К.',
    role: 'Кухня 3.5 м, МДФ эмаль',
    text: 'Александр сделал всё точно по размерам — кухня встала как влитая. Очень красиво получилось, соседи спрашивают, где заказывали. Третий раз уже к нему обращаемся!',
    stars: 5,
    initial: 'М',
    color: 'bg-pink-100 text-pink-700',
  },
  {
    name: 'Иван Д.',
    role: 'Шкаф-купе, зеркальные двери',
    text: 'Понравилось, что показал 3D-проект ещё до начала работ. Я понял сразу, что получу. Сроки выдержал, качество отличное. Рекомендую.',
    stars: 5,
    initial: 'И',
    color: 'bg-blue-100 text-blue-700',
  },
  {
    name: 'Светлана Р.',
    role: 'Гардеробная под заказ',
    text: 'Никогда не думала, что индивидуальный заказ будет таким доступным. Сделал ровно то, что я хотела, и даже предложил пару крутых идей, которые я сама не придумала бы.',
    stars: 5,
    initial: 'С',
    color: 'bg-green-100 text-green-700',
  },
  {
    name: 'Андрей В.',
    role: 'Кухня + шкаф в прихожую',
    text: 'Заказывал уже третий раз. Приятно работать с человеком, который следит за качеством лично. Все замечания учёл сразу.',
    stars: 5,
    initial: 'А',
    color: 'bg-amber-100 text-amber-700',
  },
  {
    name: 'Наталья П.',
    role: 'Кухня в новостройке',
    text: 'Понравилась честность — сразу сказал что реально, а что нет за мой бюджет. Не навязывал лишнего. Кухня получилась красивой и функциональной.',
    stars: 5,
    initial: 'Н',
    color: 'bg-purple-100 text-purple-700',
  },
]

export default function Reviews() {
  const [current, setCurrent] = useState(0)

  const prev = () => setCurrent(c => (c === 0 ? reviews.length - 1 : c - 1))
  const next = () => setCurrent(c => (c === reviews.length - 1 ? 0 : c + 1))

  const r = reviews[current]

  return (
    <section className="bg-surface py-20">
      <div className="max-w-5xl mx-auto px-5">
        <span className="badge">Отзывы</span>
        <h2 className="section-title">Что говорят клиенты</h2>
        <p className="section-sub mb-12">Настоящие отзывы — без купленных звёзд.</p>

        {/* Основная карточка */}
        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-2xl p-8 shadow-md relative">
            {/* Аватар */}
            <div className="flex items-center gap-4 mb-6">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center
                               font-bold text-lg ${r.color}`}>
                {r.initial}
              </div>
              <div>
                <p className="font-bold text-ink">{r.name}</p>
                <p className="text-muted text-sm">{r.role}</p>
              </div>
              {/* Звёзды */}
              <div className="ml-auto text-gold text-lg tracking-tight">
                {'★'.repeat(r.stars)}
              </div>
            </div>

            {/* Цитата */}
            <blockquote className="text-ink/80 text-base leading-relaxed italic">
              &laquo;{r.text}&raquo;
            </blockquote>
          </div>

          {/* Навигация */}
          <div className="flex items-center justify-center gap-4 mt-6">
            <button
              onClick={prev}
              className="w-10 h-10 rounded-full bg-white shadow border border-gray-200
                         flex items-center justify-center hover:bg-primary hover:text-white
                         hover:border-primary transition-all duration-200"
            >
              ←
            </button>

            {/* Точки */}
            <div className="flex gap-2">
              {reviews.map((_, i) => (
                <button
                  key={i}
                  onClick={() => setCurrent(i)}
                  className={`w-2.5 h-2.5 rounded-full transition-all duration-200 ${
                    i === current ? 'bg-primary w-6' : 'bg-gray-300'
                  }`}
                />
              ))}
            </div>

            <button
              onClick={next}
              className="w-10 h-10 rounded-full bg-white shadow border border-gray-200
                         flex items-center justify-center hover:bg-primary hover:text-white
                         hover:border-primary transition-all duration-200"
            >
              →
            </button>
          </div>
        </div>
      </div>
    </section>
  )
}
