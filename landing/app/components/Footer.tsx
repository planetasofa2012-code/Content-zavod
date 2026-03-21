// Блок 11: Футер — контакты, соцсети, копирайт
export default function Footer() {
  return (
    <footer className="bg-ink text-white/80 py-12">
      <div className="max-w-5xl mx-auto px-5">
        <div className="grid sm:grid-cols-3 gap-8 mb-8">
          {/* Бренд */}
          <div>
            <a href="#" className="flex items-center gap-2 mb-3 no-underline">
              <span className="text-2xl">🏠</span>
              <span className="font-extrabold text-lg text-white">
                Кухня<span className="text-primary">54</span>
              </span>
            </a>
            <p className="text-sm leading-relaxed">
              Корпусная мебель на заказ в Новосибирске.
              Кухни, шкафы, гардеробные.
            </p>
          </div>

          {/* Контакты */}
          <div>
            <h4 className="font-semibold text-white mb-3 text-sm">Контакты</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <a href="tel:+79131234567" className="hover:text-primary transition-colors">
                  📱 +7 (913) 123-45-67
                </a>
              </li>
              <li>📍 Новосибирск</li>
              <li>
                <a
                  href="https://t.me/kuhnya154"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-primary transition-colors"
                >
                  ✈️ @kuhnya154
                </a>
              </li>
            </ul>
          </div>

          {/* Соцсети */}
          <div>
            <h4 className="font-semibold text-white mb-3 text-sm">Мы в соцсетях</h4>
            <div className="flex flex-wrap gap-2">
              {[
                { href: 'https://t.me/kuhnya154',              label: 'Telegram',   emoji: '✈️' },
                { href: 'https://vk.com/wall-kuhnya54',        label: 'ВКонтакте',  emoji: '🔵' },
                { href: 'https://instagram.com/kuhnya54',      label: 'Instagram',  emoji: '📸' },
                { href: 'https://pinterest.com',               label: 'Pinterest',  emoji: '📌' },
              ].map(s => (
                <a
                  key={s.label}
                  href={s.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1.5 bg-white/10 hover:bg-primary hover:text-white
                             transition-all rounded-lg px-3 py-1.5 text-xs font-medium"
                >
                  <span>{s.emoji}</span>
                  <span>{s.label}</span>
                </a>
              ))}
            </div>
          </div>
        </div>

        <div className="border-t border-white/10 pt-6 flex flex-col sm:flex-row items-center
                        justify-between gap-3 text-xs text-white/40">
          <span>© 2026 Кухня54 · Александр Самосудов</span>
          <span>Мебель на заказ в Новосибирске</span>
        </div>
      </div>
    </footer>
  )
}
