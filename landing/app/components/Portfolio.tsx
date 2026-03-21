'use client'

import { useState } from 'react'

// Блок 8: Портфолио — галерея работ с фильтрами по типу мебели
// Данные — заглушки, позже заменяются на подгрузку из Supabase (таблица portfolio)

type Category = 'all' | 'kitchen' | 'wardrobe' | 'closet'

const items = [
  {
    id: 1, cat: 'kitchen' as Category,
    title: 'Кухня в скандинавском стиле',
    desc: 'МДФ эмаль, фурнитура Blum, 3.2 м',
    gradient: 'from-green-800 to-green-600',
    emoji: '🍽️',
  },
  {
    id: 2, cat: 'wardrobe' as Category,
    title: 'Шкаф-купе с зеркальными дверями',
    desc: 'ЛДСП Egger, зеркало, 2.4 × 2.4 м',
    gradient: 'from-blue-800 to-blue-600',
    emoji: '🪞',
  },
  {
    id: 3, cat: 'kitchen' as Category,
    title: 'Кухня П-образная',
    desc: 'МДФ плёнка, фурнитура Hettich',
    gradient: 'from-amber-700 to-amber-500',
    emoji: '👨‍🍳',
  },
  {
    id: 4, cat: 'closet' as Category,
    title: 'Гардеробная под заказ',
    desc: 'Открытые полки + выдвижные ящики',
    gradient: 'from-purple-800 to-purple-600',
    emoji: '👗',
  },
  {
    id: 5, cat: 'kitchen' as Category,
    title: 'Кухня в стиле лофт',
    desc: 'МДФ эмаль + дерево, 2.8 м',
    gradient: 'from-stone-700 to-stone-500',
    emoji: '🏠',
  },
  {
    id: 6, cat: 'wardrobe' as Category,
    title: 'Шкаф в прихожую',
    desc: 'ЛДСП, встроенная система хранения',
    gradient: 'from-teal-700 to-teal-500',
    emoji: '🧥',
  },
]

const tabs: { id: Category; label: string }[] = [
  { id: 'all',      label: 'Все работы' },
  { id: 'kitchen',  label: 'Кухни' },
  { id: 'wardrobe', label: 'Шкафы' },
  { id: 'closet',   label: 'Гардеробные' },
]

export default function Portfolio() {
  const [active, setActive] = useState<Category>('all')

  const filtered = active === 'all' ? items : items.filter(i => i.cat === active)

  return (
    <section id="portfolio" className="py-20 bg-white">
      <div className="max-w-5xl mx-auto px-5">
        <span className="badge">Наши работы</span>
        <h2 className="section-title">Смотрите, что мы делаем</h2>
        <p className="section-sub mb-8">
          Каждый проект — под размеры и стиль конкретной квартиры.
        </p>

        {/* Фильтры */}
        <div className="flex flex-wrap gap-2 mb-8">
          {tabs.map(t => (
            <button
              key={t.id}
              onClick={() => setActive(t.id)}
              className={`px-4 py-2 rounded-full text-sm font-semibold transition-all duration-200 ${
                active === t.id
                  ? 'bg-primary text-white shadow-sm'
                  : 'bg-surface text-muted hover:bg-primary/10 hover:text-primary'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* Сетка */}
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map(item => (
            <div
              key={item.id}
              className={`group relative rounded-2xl overflow-hidden aspect-square
                          bg-gradient-to-br ${item.gradient}
                          cursor-pointer hover:scale-[1.02] transition-transform duration-300`}
            >
              {/* Иконка-заглушка */}
              <div className="absolute inset-0 flex items-center justify-center text-6xl opacity-30">
                {item.emoji}
              </div>

              {/* Оверлей при наведении */}
              <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100
                              transition-opacity duration-300 flex flex-col justify-end p-4">
                <p className="text-white font-bold text-sm leading-tight">{item.title}</p>
                <p className="text-white/80 text-xs mt-1">{item.desc}</p>
              </div>

              {/* Подпись снизу (по умолчанию) */}
              <div className="absolute bottom-0 left-0 right-0 p-3 bg-gradient-to-t from-black/60 to-transparent
                              group-hover:opacity-0 transition-opacity duration-300">
                <p className="text-white text-xs font-medium">{item.title}</p>
              </div>
            </div>
          ))}
        </div>

        {/* TODO: заменить заглушки на реальные фото из Supabase (таблица portfolio) */}
        <p className="text-center text-muted text-sm mt-6">
          Фото будут добавлены после первых проектов 📸
        </p>
      </div>
    </section>
  )
}
