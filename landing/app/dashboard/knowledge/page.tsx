'use client'

import { useEffect, useState } from 'react'

interface KnowledgeEntry {
  id: string
  category: string
  question: string
  answer: string
  source: string
  created_at: string
}

const categories = [
  { id: 'all',       label: '📚 Все',        color: '' },
  { id: 'materials', label: '🪵 Материалы',  color: 'bg-amber-50 text-amber-700' },
  { id: 'pricing',   label: '💰 Цены',       color: 'bg-green-50 text-green-700' },
  { id: 'process',   label: '⚙️ Процесс',    color: 'bg-blue-50 text-blue-700' },
  { id: 'faq',       label: '❓ FAQ',         color: 'bg-purple-50 text-purple-700' },
  { id: 'portfolio', label: '📸 Портфолио',  color: 'bg-pink-50 text-pink-700' },
  { id: 'reviews',   label: '⭐ Отзывы',     color: 'bg-yellow-50 text-yellow-700' },
]

export default function KnowledgePage() {
  const [entries, setEntries] = useState<KnowledgeEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [activeCat, setActiveCat] = useState('all')
  const [search, setSearch] = useState('')
  const [openId, setOpenId] = useState<string | null>(null)

  useEffect(() => {
    async function load() {
      try {
        const params = new URLSearchParams()
        if (activeCat !== 'all') params.set('category', activeCat)
        if (search.trim()) params.set('search', search.trim())

        const res = await fetch(`/api/knowledge?${params}`)
        const data = await res.json()
        setEntries(Array.isArray(data) ? data : [])
      } catch (e) {
        console.error('Ошибка загрузки:', e)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [activeCat, search])

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-ink">База знаний</h2>

      {/* Поиск */}
      <input
        type="text"
        placeholder="🔍 Поиск по базе знаний..."
        value={search}
        onChange={e => setSearch(e.target.value)}
        className="w-full bg-white border border-gray-200 rounded-xl px-4 py-3 text-sm
                   focus:outline-none focus:border-primary transition-colors"
      />

      {/* Категории */}
      <div className="flex gap-2 overflow-x-auto pb-1 -mx-1 px-1">
        {categories.map(c => (
          <button
            key={c.id}
            onClick={() => { setActiveCat(c.id); setLoading(true) }}
            className={`whitespace-nowrap text-xs px-3 py-1.5 rounded-full font-medium transition-all flex-shrink-0 ${
              activeCat === c.id
                ? 'bg-primary text-white'
                : 'bg-gray-100 text-muted hover:bg-gray-200'
            }`}
          >
            {c.label}
          </button>
        ))}
      </div>

      {/* Список */}
      {loading ? (
        <div className="text-center py-12">
          <div className="text-3xl animate-pulse mb-2">🧠</div>
          <p className="text-sm text-muted">Загрузка...</p>
        </div>
      ) : entries.length === 0 ? (
        <div className="text-center py-16">
          <div className="text-5xl mb-4">📖</div>
          <h3 className="text-lg font-bold text-ink mb-2">База знаний пуста</h3>
          <p className="text-sm text-muted mb-6">
            Записи появятся здесь автоматически из интервью с ботом
          </p>
          <div className="text-sm text-muted bg-gray-50 rounded-xl p-4 max-w-sm mx-auto">
            💡 Начните интервью с ботом, чтобы заполнить базу знаний о вашем бизнесе
          </div>
        </div>
      ) : (
        <div className="space-y-2">
          {entries.map(entry => (
            <div
              key={entry.id}
              className="bg-white rounded-2xl overflow-hidden border border-gray-100
                         hover:border-primary/20 transition-colors"
            >
              <button
                onClick={() => setOpenId(openId === entry.id ? null : entry.id)}
                className="w-full flex items-center justify-between px-5 py-4 text-left"
              >
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium flex-shrink-0 ${
                    categories.find(c => c.id === entry.category)?.color || 'bg-gray-100 text-muted'
                  }`}>
                    {entry.category}
                  </span>
                  <span className="font-medium text-sm text-ink truncate">{entry.question}</span>
                </div>
                <span className={`text-primary text-xl flex-shrink-0 ml-2 transition-transform duration-300 ${
                  openId === entry.id ? 'rotate-45' : ''
                }`}>+</span>
              </button>

              {openId === entry.id && (
                <div className="px-5 pb-4 text-sm text-muted leading-relaxed border-t border-gray-50 pt-3">
                  {entry.answer}
                  <div className="mt-2 text-xs text-muted/60">
                    Источник: {entry.source === 'interview' ? '🎤 Интервью' : entry.source === 'ai' ? '🤖 AI' : '📝 Вручную'}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
