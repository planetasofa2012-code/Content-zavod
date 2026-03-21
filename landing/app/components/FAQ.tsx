'use client'

import { useState } from 'react'

// Блок 10: FAQ — часто задаваемые вопросы (аккордеон)
const faqs = [
  {
    q: 'Сколько стоит замер?',
    a: 'Замер — бесплатно. Мы приедем в удобное для вас время, всё измерим и сразу сделаем 3D-эскиз на месте или пришлём на следующий день.',
  },
  {
    q: 'Сколько времени займёт производство кухни?',
    a: 'Обычно 14–30 рабочих дней с момента подписания договора. Точные сроки фиксируем в договоре. Если задержим — штраф в нашу сторону.',
  },
  {
    q: 'А если мне не понравится результат?',
    a: 'Вы утверждаете 3D-проект до начала производства. Если в проекте всё верно — результат совпадёт с ним точно. Если обнаружится производственный дефект — устраняем бесплатно по гарантии.',
  },
  {
    q: 'Работаете ли вы по всему Новосибирску?',
    a: 'Да, выезжаем в любой район города. Для пригорода (до 40 км) — небольшая доплата за выезд, уточняем индивидуально.',
  },
  {
    q: 'Можно ли изменить проект после подписания договора?',
    a: 'Небольшие изменения возможны в первые 3 дня после подписания — это бесплатно. Серьёзные правки после запуска в производство могут повлечь доплату — обсуждаем честно.',
  },
  {
    q: 'Вы работаете по всем стилям кухонь?',
    a: 'Да: скандинавский, лофт, минимализм, классика, современный. Делаем под ваш интерьер. Если есть референсы из Pinterest — берите с собой на замер.',
  },
  {
    q: 'Как проходит оплата?',
    a: '50% после подписания договора и утверждения проекта. 50% после монтажа и приёмки. Никаких скрытых платежей.',
  },
]

export default function FAQ() {
  const [open, setOpen] = useState<number | null>(null)

  return (
    <section className="py-20 bg-white">
      <div className="max-w-3xl mx-auto px-5">
        <span className="badge">FAQ</span>
        <h2 className="section-title">Частые вопросы</h2>
        <p className="section-sub mb-10">Отвечаем честно, без маркетинговых уловок.</p>

        <div className="space-y-3">
          {faqs.map((f, i) => (
            <div
              key={i}
              className="bg-surface rounded-2xl overflow-hidden border border-transparent
                         hover:border-primary/20 transition-colors"
            >
              <button
                onClick={() => setOpen(open === i ? null : i)}
                className="w-full flex items-center justify-between px-6 py-4 text-left"
              >
                <span className="font-semibold text-ink text-sm sm:text-base pr-4">{f.q}</span>
                <span
                  className={`text-primary text-xl flex-shrink-0 transition-transform duration-300 ${
                    open === i ? 'rotate-45' : 'rotate-0'
                  }`}
                >
                  +
                </span>
              </button>

              {open === i && (
                <div className="px-6 pb-5 text-muted text-sm leading-relaxed">
                  {f.a}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
