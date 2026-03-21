// Блок 4: Решение / УТП — 4 ключевых отличия
const benefits = [
  {
    icon: '🎨',
    title: '3D-проект ДО оплаты',
    text: 'Вы увидите свою кухню в 3D и одобрите каждую деталь — только потом подписываем договор.',
  },
  {
    icon: '📋',
    title: 'Фиксированная цена',
    text: 'Цена из договора — окончательная. Ни рублём больше в процессе работы.',
  },
  {
    icon: '👤',
    title: 'Один мастер — весь заказ',
    text: 'Александр лично: замер, проект, контроль производства, монтаж. Без цепочки посредников.',
  },
  {
    icon: '🛡️',
    title: 'Гарантия 24 месяца',
    text: 'На корпус, фасады и фурнитуру. Если что-то случится — починим бесплатно.',
  },
]

export default function Solution() {
  return (
    <section className="py-20 bg-white">
      <div className="max-w-5xl mx-auto px-5">
        <span className="badge">С нами по-другому</span>
        <h2 className="section-title">
          Почему выбирают Кухню&nbsp;54
        </h2>
        <p className="section-sub mb-12">
          Честно о том, как мы работаем — без красивых слов и скрытых условий.
        </p>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {benefits.map((b, i) => (
            <div
              key={i}
              className="group bg-surface rounded-2xl p-6
                         hover:bg-primary hover:text-white
                         transition-all duration-300 cursor-default"
            >
              <div className="text-3xl mb-4">{b.icon}</div>
              <h3 className="font-bold text-base mb-2 group-hover:text-white text-ink">
                {b.title}
              </h3>
              <p className="text-sm leading-relaxed text-muted group-hover:text-white/85">
                {b.text}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
