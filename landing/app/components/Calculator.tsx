'use client'

import { useState, useMemo } from 'react'

// Блок 9: Калькулятор стоимости — интерактивный виджет
// Цены приблизительные, для реального расчёта — замер

const BASE_PRICE: Record<string, number> = {
  kitchen:  40000,  // базовая цена за погонный метр (кухня)
  wardrobe: 25000,  // шкаф-купе за погонный метр
  closet:   20000,  // гардеробная за кв.м
}

const MATERIAL_K: Record<string, number> = {
  ldsp:      1.0,  // ЛДСП
  mdf_film:  1.4,  // МДФ плёнка
  mdf_paint: 1.8,  // МДФ эмаль
}

const FITTINGS_K: Record<string, number> = {
  std:   1.0,  // Стандарт
  hett:  1.25, // Hettich
  blum:  1.5,  // Blum (премиум)
}

function fmt(n: number) {
  return new Intl.NumberFormat('ru-RU').format(Math.round(n))
}

export default function Calculator() {
  const [type,     setType]     = useState('kitchen')
  const [size,     setSize]     = useState(3.0)
  const [material, setMaterial] = useState('mdf_film')
  const [fittings, setFittings] = useState('hett')

  const { low, high } = useMemo(() => {
    const base = BASE_PRICE[type] * size * MATERIAL_K[material] * FITTINGS_K[fittings]
    return { low: base * 0.9, high: base * 1.15 }
  }, [type, size, material, fittings])

  return (
    <section className="py-20 bg-white">
      <div className="max-w-5xl mx-auto px-5">
        <span className="badge">Калькулятор</span>
        <h2 className="section-title">Рассчитайте стоимость</h2>
        <p className="section-sub mb-10">
          Примерная цена за 30 секунд. Точный расчёт — на бесплатном замере.
        </p>

        <div className="max-w-2xl bg-surface rounded-2xl p-8 shadow-sm">
          {/* Тип мебели */}
          <div className="mb-6">
            <label className="block text-sm font-semibold text-ink mb-2">Тип мебели</label>
            <div className="flex gap-2 flex-wrap">
              {[
                { v: 'kitchen',  l: '🍽️ Кухня' },
                { v: 'wardrobe', l: '🪞 Шкаф-купе' },
                { v: 'closet',   l: '👗 Гардеробная' },
              ].map(({ v, l }) => (
                <button
                  key={v}
                  onClick={() => setType(v)}
                  className={`px-4 py-2.5 rounded-xl text-sm font-semibold border transition-all ${
                    type === v
                      ? 'bg-primary text-white border-primary'
                      : 'bg-white text-muted border-gray-200 hover:border-primary hover:text-primary'
                  }`}
                >
                  {l}
                </button>
              ))}
            </div>
          </div>

          {/* Размер */}
          <div className="mb-6">
            <label className="block text-sm font-semibold text-ink mb-2">
              Размер: <span className="text-primary">{size.toFixed(1)} м</span>
            </label>
            <input
              type="range"
              min={1.5} max={6} step={0.1}
              value={size}
              onChange={e => setSize(+e.target.value)}
              className="w-full accent-primary"
            />
            <div className="flex justify-between text-xs text-muted mt-1">
              <span>1.5 м</span><span>6 м</span>
            </div>
          </div>

          {/* Материал фасадов */}
          <div className="mb-6">
            <label className="block text-sm font-semibold text-ink mb-2">Материал фасадов</label>
            <select
              value={material}
              onChange={e => setMaterial(e.target.value)}
              className="w-full bg-white border border-gray-200 rounded-xl px-4 py-3 text-sm
                         focus:outline-none focus:border-primary transition-colors"
            >
              <option value="ldsp">ЛДСП — бюджетно и практично</option>
              <option value="mdf_film">МДФ плёнка — хорошее соотношение цена/качество</option>
              <option value="mdf_paint">МДФ эмаль — как в шоу-руме, на 15–20 лет</option>
            </select>
          </div>

          {/* Фурнитура */}
          <div className="mb-8">
            <label className="block text-sm font-semibold text-ink mb-2">Фурнитура</label>
            <div className="flex gap-2 flex-wrap">
              {[
                { v: 'std',  l: 'Стандарт', hint: '' },
                { v: 'hett', l: 'Hettich',  hint: '⭐' },
                { v: 'blum', l: 'Blum',     hint: '⭐⭐' },
              ].map(({ v, l, hint }) => (
                <button
                  key={v}
                  onClick={() => setFittings(v)}
                  className={`px-4 py-2.5 rounded-xl text-sm font-semibold border transition-all ${
                    fittings === v
                      ? 'bg-primary text-white border-primary'
                      : 'bg-white text-muted border-gray-200 hover:border-primary hover:text-primary'
                  }`}
                >
                  {l} {hint}
                </button>
              ))}
            </div>
          </div>

          {/* Результат */}
          <div className="bg-primary/10 rounded-2xl p-6 mb-6 text-center">
            <p className="text-sm text-muted mb-1">Примерная стоимость</p>
            <p className="text-3xl font-extrabold text-primary">
              {fmt(low)} — {fmt(high)} ₽
            </p>
            <p className="text-xs text-muted mt-2">
              Точная цена — на замере. Отклонение ≤10%
            </p>
          </div>

          <a href="#cta" className="btn-primary w-full text-center block py-4">
            📐 Узнать точную цену — бесплатно
          </a>
        </div>
      </div>
    </section>
  )
}
