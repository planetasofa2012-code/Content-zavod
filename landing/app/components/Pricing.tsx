// Блок 8а: Тарифы — 3 пакета на выбор
const plans = [
  {
    name: 'Базовый',
    price: 'от 80 000 ₽',
    desc: 'Надёжно и практично',
    features: [
      'ЛДСП Egger 16–25 мм',
      'Фурнитура GTV / Gamet',
      'Стандартные фасады',
      'Монтаж включён',
      'Гарантия 12 мес.',
    ],
    popular: false,
    cta: 'Выбрать базовый',
  },
  {
    name: 'Оптимальный',
    price: 'от 130 000 ₽',
    desc: 'Хит — берут 70% клиентов',
    features: [
      'ЛДСП + МДФ плёнка',
      'Фурнитура Hettich',
      'Доводчики на всех дверцах',
      'Подсветка рабочей зоны',
      'Гарантия 18 мес.',
    ],
    popular: true,
    cta: 'Выбрать оптимальный',
  },
  {
    name: 'Премиум',
    price: 'от 200 000 ₽',
    desc: 'Как в шоу-руме — на 20 лет',
    features: [
      'МДФ эмаль всех RAL-цветов',
      'Фурнитура Blum (лифт, тандем)',
      'Встроенная подсветка LED',
      '3D-визуализация бесплатно',
      'Гарантия 24 мес.',
    ],
    popular: false,
    cta: 'Выбрать премиум',
  },
]

export default function Pricing() {
  return (
    <section className="bg-surface py-20">
      <div className="max-w-5xl mx-auto px-5">
        <span className="badge">Пакеты</span>
        <h2 className="section-title">Выберите пакет</h2>
        <p className="section-sub mb-12">
          Все цены — за полный цикл: замер, проект, производство, монтаж.
        </p>

        <div className="grid sm:grid-cols-3 gap-6">
          {plans.map((p, i) => (
            <div
              key={i}
              className={`relative rounded-2xl p-7 flex flex-col transition-all duration-300 ${
                p.popular
                  ? 'bg-primary text-white shadow-xl scale-[1.03]'
                  : 'bg-white shadow-sm hover:shadow-md hover:-translate-y-1'
              }`}
            >
              {/* Значок «хит» */}
              {p.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2
                                bg-gold text-ink text-xs font-bold px-4 py-1 rounded-full">
                  ⭐ Хит продаж
                </div>
              )}

              <div className={`text-sm font-semibold mb-1 ${p.popular ? 'text-white/70' : 'text-muted'}`}>
                {p.desc}
              </div>
              <h3 className={`text-xl font-bold mb-2 ${p.popular ? 'text-white' : 'text-ink'}`}>
                {p.name}
              </h3>
              <div className={`text-2xl font-extrabold mb-6 ${p.popular ? 'text-white' : 'text-primary'}`}>
                {p.price}
              </div>

              <ul className="flex-1 space-y-2.5 mb-7">
                {p.features.map((f, j) => (
                  <li key={j} className="flex items-start gap-2 text-sm">
                    <span className={`mt-0.5 flex-shrink-0 ${p.popular ? 'text-green-300' : 'text-primary'}`}>
                      ✓
                    </span>
                    <span className={p.popular ? 'text-white/90' : 'text-muted'}>{f}</span>
                  </li>
                ))}
              </ul>

              <a
                href="#cta"
                className={`text-center rounded-xl py-3 font-semibold text-sm transition-all block ${
                  p.popular
                    ? 'bg-white text-primary hover:bg-gray-50'
                    : 'bg-primary text-white hover:bg-primary-dark'
                }`}
              >
                {p.cta}
              </a>
            </div>
          ))}
        </div>

        <p className="text-center text-muted text-sm mt-8">
          Цены ориентировочные. Точная стоимость — после замера. Всегда фиксируется в договоре.
        </p>
      </div>
    </section>
  )
}
