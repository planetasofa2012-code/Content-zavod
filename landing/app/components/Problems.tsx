// Блок 3: Боли клиента — 4 проблемы с которыми обращаются
const problems = [
  {
    emoji: '😩',
    title: '«Потратил деньги, а кухня не влезла в проём»',
    text: 'Замер сделали на глаз, в итоге — переплата, переделки и месяц нервов.',
  },
  {
    emoji: '😤',
    title: '«Исполнитель пропал после предоплаты»',
    text: 'Взяли 50%, пообещали через 2 недели — и тишина. Знакомо?',
  },
  {
    emoji: '😰',
    title: '«Фурнитура сломалась через полгода»',
    text: 'Дешёвые петли, рельсы без доводчика. Переделывать дороже, чем сделать правильно сразу.',
  },
  {
    emoji: '😣',
    title: '«Сроки сорвали на 2 месяца»',
    text: 'Ремонт стоит, семья ждёт, мастер каждую неделю придумывает новые отговорки.',
  },
]

export default function Problems() {
  return (
    <section className="bg-surface py-20">
      <div className="max-w-5xl mx-auto px-5">
        <span className="badge">Узнаёте себя?</span>
        <h2 className="section-title">
          С чем приходят клиенты
        </h2>
        <p className="section-sub mb-12">
          Большинство наших заказчиков уже сталкивались с этим хотя бы раз.
          Мы работаем по-другому — и расскажем как.
        </p>

        <div className="grid sm:grid-cols-2 gap-5">
          {problems.map((p, i) => (
            <div
              key={i}
              className="bg-white rounded-2xl p-7 shadow-sm border-l-4 border-red-300
                         hover:shadow-md hover:-translate-y-0.5 transition-all duration-200"
            >
              <div className="text-3xl mb-3">{p.emoji}</div>
              <h3 className="font-semibold text-ink text-base mb-2">{p.title}</h3>
              <p className="text-muted text-sm leading-relaxed">{p.text}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
