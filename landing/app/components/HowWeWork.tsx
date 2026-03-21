// Блок 5: Как мы работаем — 4 шага с временными метками
const steps = [
  {
    num: '01',
    icon: '📱',
    title: 'Заявка',
    sub: 'Бесплатно',
    text: 'Оставьте номер — перезвоним в течение 30 минут. Или напишите в Telegram прямо сейчас.',
  },
  {
    num: '02',
    icon: '📐',
    title: 'Замер + 3D-эскиз',
    sub: 'Бесплатно',
    text: 'Приедем, всё замерим и сделаем 3D-проект вашей кухни. Вы видите результат до оплаты.',
  },
  {
    num: '03',
    icon: '🏭',
    title: 'Производство',
    sub: '14–30 дней',
    text: 'Изготавливаем мебель по утверждённому проекту. Присылаем фото в процессе.',
  },
  {
    num: '04',
    icon: '🏠',
    title: 'Монтаж + гарантия',
    sub: '1–2 дня',
    text: 'Привозим, собираем, подгоняем. Убираем за собой. Выдаём гарантийный талон на 24 месяца.',
  },
]

export default function HowWeWork() {
  return (
    <section className="bg-surface py-20">
      <div className="max-w-5xl mx-auto px-5">
        <span className="badge">Процесс</span>
        <h2 className="section-title">Как мы работаем</h2>
        <p className="section-sub mb-14">
          4 шага от заявки до готовой мебели — просто и предсказуемо.
        </p>

        {/* Шаги */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {steps.map((s, i) => (
            <div key={i} className="relative bg-white rounded-2xl p-6 shadow-sm">
              {/* Номер шага */}
              <div className="absolute -top-3 -right-3 w-9 h-9 rounded-full bg-primary text-white
                              text-xs font-bold flex items-center justify-center shadow">
                {s.num}
              </div>

              <div className="text-3xl mb-3">{s.icon}</div>
              <h3 className="font-bold text-ink text-base mb-0.5">{s.title}</h3>
              <span className="inline-block text-xs font-semibold text-primary bg-primary/10
                               rounded-full px-2.5 py-0.5 mb-3">
                {s.sub}
              </span>
              <p className="text-sm text-muted leading-relaxed">{s.text}</p>

              {/* Стрелка между шагами (только не у последнего) */}
              {i < steps.length - 1 && (
                <div className="hidden lg:block absolute -right-3 top-1/2 -translate-y-1/2
                                text-primary text-xl font-bold z-10">
                  →
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="text-center">
          <a href="#cta" className="btn-primary px-10 py-4 text-base">
            📐 Записаться на замер
          </a>
        </div>
      </div>
    </section>
  )
}
