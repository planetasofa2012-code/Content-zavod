'use client'

import { useEffect, useState } from 'react'

// Типы данных
interface Stats {
  posts: { total: number; published: number }
  leads: { total: number; in_work: number; done: number }
  measurements: number
  ai_responses: number
  knowledge_entries: number
}

interface Lead {
  id: string
  name: string
  type: string
  source: string
  created_at: string
}

// Форматирование даты в "5 мин назад" / "1 час назад"
function timeAgo(dateStr: string) {
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'только что'
  if (mins < 60) return `${mins} мин назад`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours} ч назад`
  const days = Math.floor(hours / 24)
  return `${days} дн назад`
}

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [recentLeads, setRecentLeads] = useState<Lead[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const [statsRes, leadsRes] = await Promise.all([
          fetch('/api/stats'),
          fetch('/api/leads'),
        ])
        const statsData = await statsRes.json()
        const leadsData = await leadsRes.json()

        setStats(statsData)
        setRecentLeads(Array.isArray(leadsData) ? leadsData.slice(0, 5) : [])
      } catch (e) {
        console.error('Ошибка загрузки:', e)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="text-4xl mb-3 animate-pulse">📊</div>
          <p className="text-muted">Загрузка данных...</p>
        </div>
      </div>
    )
  }

  const statCards = [
    {
      icon: '📝',
      value: stats?.posts.published ?? 0,
      label: 'Постов',
      sub: `из ${stats?.posts.total ?? 0} всего`,
      color: 'bg-blue-50 text-blue-600',
    },
    {
      icon: '🔥',
      value: stats?.leads.total ?? 0,
      label: 'Лидов',
      sub: `${stats?.leads.in_work ?? 0} в работе`,
      color: 'bg-orange-50 text-orange-600',
    },
    {
      icon: '📐',
      value: stats?.measurements ?? 0,
      label: 'Замеры',
      sub: 'прошли замер',
      color: 'bg-green-50 text-green-600',
    },
    {
      icon: '🤖',
      value: stats?.ai_responses ?? 0,
      label: 'AI ответы',
      sub: 'диалогов',
      color: 'bg-purple-50 text-purple-600',
    },
  ]

  return (
    <div className="space-y-6">
      {/* Приветствие */}
      <div>
        <h2 className="text-2xl font-bold text-ink">Привет, Александр 👋</h2>
        <p className="text-muted text-sm mt-1">Вот что происходит с твоим бизнесом</p>
      </div>

      {/* Статистика — 4 карточки */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {statCards.map((s, i) => (
          <div key={i} className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
            <div className={`w-10 h-10 rounded-xl ${s.color} flex items-center justify-center text-lg mb-3`}>
              {s.icon}
            </div>
            <div className="text-2xl font-extrabold text-ink">{s.value}</div>
            <div className="text-sm font-medium text-ink">{s.label}</div>
            <div className="text-xs text-muted mt-0.5">{s.sub}</div>
          </div>
        ))}
      </div>

      {/* Быстрые действия */}
      <div>
        <h3 className="text-xs font-semibold text-muted uppercase tracking-wider mb-3">
          Быстрые действия
        </h3>
        <div className="grid grid-cols-2 gap-3">
          {[
            { icon: '✍️', label: 'Создать пост', color: 'bg-gradient-to-r from-green-500 to-green-600', href: '/dashboard/posts' },
            { icon: '🎤', label: 'Интервью', color: 'bg-gradient-to-r from-blue-500 to-blue-600', href: '#' },
            { icon: '📋', label: 'CRM', color: 'bg-gradient-to-r from-orange-500 to-orange-600', href: '/dashboard/crm' },
            { icon: '📊', label: 'Аналитика', color: 'bg-gradient-to-r from-purple-500 to-purple-600', href: '#' },
          ].map((a, i) => (
            <a
              key={i}
              href={a.href}
              className={`${a.color} text-white rounded-2xl p-4 flex items-center gap-3
                         hover:opacity-90 hover:-translate-y-0.5 transition-all duration-200
                         shadow-sm no-underline`}
            >
              <span className="text-xl">{a.icon}</span>
              <span className="font-semibold text-sm">{a.label}</span>
            </a>
          ))}
        </div>
      </div>

      {/* Последние события */}
      <div>
        <h3 className="text-xs font-semibold text-muted uppercase tracking-wider mb-3">
          Последние события
        </h3>
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 divide-y divide-gray-50">
          {recentLeads.length === 0 ? (
            <div className="p-6 text-center text-muted">
              <div className="text-3xl mb-2">📭</div>
              <p className="text-sm">Пока нет событий. Лиды появятся здесь автоматически!</p>
            </div>
          ) : (
            recentLeads.map((lead) => (
              <div key={lead.id} className="flex items-center gap-3 px-4 py-3">
                <div className="w-8 h-8 rounded-full bg-orange-100 text-orange-600
                                flex items-center justify-center text-sm flex-shrink-0">
                  🔔
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-ink truncate">
                    Новая заявка: {lead.name}, {lead.type === 'kitchen' ? 'кухня' : lead.type}
                  </p>
                  <p className="text-xs text-muted">
                    {lead.source} · {timeAgo(lead.created_at)}
                  </p>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* FAB — создать пост */}
      <a
        href="/dashboard/posts"
        className="fixed bottom-24 right-5 w-14 h-14 bg-primary text-white rounded-full
                   flex items-center justify-center text-2xl shadow-lg
                   hover:bg-primary-dark transition-all animate-pulse2 z-30 no-underline"
      >
        +
      </a>
    </div>
  )
}
