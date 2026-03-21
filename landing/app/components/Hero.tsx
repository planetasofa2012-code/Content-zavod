// Блок 2: Главный экран — H1, оффер, CTA, бейджи доверия
export default function Hero() {
  return (
    <section
      className="relative min-h-screen flex items-center overflow-hidden"
      style={{
        background: 'linear-gradient(135deg, #0f2c1a 0%, #1a4a2e 50%, #2D7D46 100%)',
      }}
    >
      {/* Паттерн-подложка */}
      <div
        className="absolute inset-0 opacity-[0.04]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/svg%3E")`,
        }}
      />

      <div className="relative max-w-5xl mx-auto px-5 py-24 text-white">
        {/* Бейдж */}
        <div className="inline-flex items-center gap-2 bg-white/10 backdrop-blur border border-white/20 rounded-full px-4 py-1.5 text-sm font-medium mb-7">
          🏠 Мебель на заказ · Новосибирск
        </div>

        {/* H1 */}
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-tight mb-5 max-w-2xl">
          Кухня мечты{' '}
          <em className="not-italic text-green-300">за 30 дней.</em>
          <br />
          Платите только за утверждённый проект
        </h1>

        {/* Подзаголовок */}
        <p className="text-lg sm:text-xl opacity-90 mb-9 max-w-xl">
          Покажем 3D-эскиз и рассчитаем стоимость — бесплатно, до договора.
          Корпусная мебель под ваши размеры от мастера с 10-летним опытом.
        </p>

        {/* CTA-кнопки */}
        <div className="flex flex-wrap gap-3 mb-12">
          <a href="#cta" className="btn-primary text-base px-8 py-4">
            🏠 Бесплатный замер
          </a>
          <a href="#portfolio" className="btn-outline text-base px-8 py-4">
            Смотреть работы →
          </a>
        </div>

        {/* Бейджи доверия */}
        <div className="flex flex-wrap gap-6 text-sm font-medium opacity-85">
          <span className="flex items-center gap-2">🏆 10+ лет опыта</span>
          <span className="flex items-center gap-2">👥 450+ клиентов</span>
          <span className="flex items-center gap-2">🛡️ Гарантия 24 мес.</span>
        </div>
      </div>
    </section>
  )
}
