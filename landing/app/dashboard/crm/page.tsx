'use client'

import { useState } from 'react'
import { useRealtimeLeads, Lead } from '@/hooks/useRealtime'

// Колонки CRM-канбана
const columns = [
  { id: 'lead',         label: 'Лиды',         color: 'border-orange-400' },
  { id: 'measurement',  label: 'Замер',         color: 'border-blue-400' },
  { id: 'project',      label: 'Проект',        color: 'border-yellow-400' },
  { id: 'production',   label: 'Производство',  color: 'border-green-400' },
  { id: 'installation', label: 'Монтаж',        color: 'border-purple-400' },
  { id: 'review',       label: 'Отзыв',         color: 'border-pink-400' },
]

const sourceEmoji: Record<string, string> = {
  telegram: '✈️ Telegram',
  vk: '🔵 VK',
  avito: '🟢 Avito',
  site: '🌐 Сайт',
  referral: '👥 Знакомые',
}

const priorityDot: Record<string, string> = {
  high: 'bg-red-400',
  medium: 'bg-yellow-400',
  low: 'bg-green-400',
}

function formatBudget(n: number) {
  if (!n) return ''
  return new Intl.NumberFormat('ru-RU').format(n) + ' ₽'
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
}

export default function CRMPage() {
  // 🔴 Realtime-подписка: лиды обновляются мгновенно
  const { leads, setLeads, loading, newLeadAlert } = useRealtimeLeads()
  const [selected, setSelected] = useState<Lead | null>(null)
  const [showAdd, setShowAdd] = useState(false)
  const [newLead, setNewLead] = useState({ name: '', phone: '', type: 'kitchen', source: 'site' })

  // Сменить статус лида (перемещение по канбану)
  async function moveToStatus(leadId: string, newStatus: string) {
    await fetch(`/api/leads/${leadId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus }),
    })
    setLeads(prev => prev.map(l => l.id === leadId ? { ...l, status: newStatus } : l))
    setSelected(null)
  }

  // Добавить нового лида
  async function addLead() {
    if (!newLead.name.trim()) return

    const res = await fetch('/api/leads', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newLead),
    })
    const data = await res.json()
    setLeads(prev => [data, ...prev])
    setNewLead({ name: '', phone: '', type: 'kitchen', source: 'site' })
    setShowAdd(false)
  }

  // Удалить лида
  async function deleteLead(leadId: string) {
    await fetch(`/api/leads/${leadId}`, { method: 'DELETE' })
    setLeads(prev => prev.filter(l => l.id !== leadId))
    setSelected(null)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="text-4xl mb-3 animate-pulse">📋</div>
          <p className="text-muted">Загрузка CRM...</p>
        </div>
      </div>
    )
  }

  const leadsInWork = leads.filter(l => !['lead', 'done'].includes(l.status)).length
  const leadsDone = leads.filter(l => l.status === 'done').length

  return (
    <div className="space-y-4">
      {/* 🔔 Toast: новый лид в реальном времени */}
      {newLeadAlert && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 z-[60] animate-slide-down
                        bg-gradient-to-r from-green-500 to-green-600 text-white
                        rounded-2xl px-5 py-3 shadow-xl flex items-center gap-3 max-w-sm">
          <span className="text-2xl">🔔</span>
          <div>
            <p className="font-bold text-sm">Новый лид!</p>
            <p className="text-xs opacity-90">{newLeadAlert.name} · {sourceEmoji[newLeadAlert.source] || newLeadAlert.source}</p>
          </div>
        </div>
      )}

      {/* Заголовок */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="text-xl font-bold text-ink">CRM — Заказы</h2>
          {/* Индикатор live-подключения */}
          <span className="flex items-center gap-1 text-xs text-green-600 bg-green-50 px-2 py-0.5 rounded-full">
            <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
            LIVE
          </span>
        </div>
        <button
          onClick={() => setShowAdd(true)}
          className="bg-primary text-white text-sm font-semibold px-4 py-2 rounded-xl
                     hover:bg-primary-dark transition-colors"
        >
          + Добавить
        </button>
      </div>

      {/* Сводка */}
      <div className="flex gap-3 text-sm">
        <span className="bg-orange-100 text-orange-700 px-3 py-1 rounded-full font-medium">
          Лидов: {leads.filter(l => l.status === 'lead').length}
        </span>
        <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full font-medium">
          В работе: {leadsInWork}
        </span>
        <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full font-medium">
          Готово: {leadsDone}
        </span>
      </div>

      {/* Канбан-доска */}
      <div className="overflow-x-auto -mx-4 px-4">
        <div className="flex gap-3 min-w-[900px]">
          {columns.map(col => {
            const colLeads = leads.filter(l => l.status === col.id)
            return (
              <div key={col.id} className={`flex-1 min-w-[150px] border-t-3 ${col.color} rounded-2xl bg-gray-50 p-3`}>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-bold text-ink">{col.label}</h3>
                  <span className="text-xs bg-white rounded-full px-2 py-0.5 text-muted font-medium">
                    {colLeads.length}
                  </span>
                </div>

                <div className="space-y-2">
                  {colLeads.length === 0 ? (
                    <div className="text-center py-6 text-muted text-xs">Пусто</div>
                  ) : (
                    colLeads.map(lead => (
                      <div
                        key={lead.id}
                        onClick={() => setSelected(lead)}
                        className="bg-white rounded-xl p-3 shadow-sm cursor-pointer
                                   hover:shadow-md hover:-translate-y-0.5 transition-all duration-200
                                   border border-gray-100"
                      >
                        <div className="flex items-start justify-between mb-1">
                          <p className="font-semibold text-sm text-ink">{lead.name}</p>
                          <div className={`w-2.5 h-2.5 rounded-full ${priorityDot[lead.priority] || 'bg-gray-300'}`} />
                        </div>
                        {lead.description && (
                          <p className="text-xs text-muted mb-1 line-clamp-2">{lead.description}</p>
                        )}
                        {lead.budget > 0 && (
                          <p className="text-sm font-bold text-ink mb-1">
                            ~{formatBudget(lead.budget)}
                          </p>
                        )}
                        <div className="flex items-center justify-between text-xs text-muted">
                          <span className="text-xs">{formatDate(lead.created_at)}</span>
                        </div>
                        {lead.source && (
                          <span className="inline-block mt-1.5 text-xs bg-gray-100 text-muted px-2 py-0.5 rounded-full">
                            {sourceEmoji[lead.source] || lead.source}
                          </span>
                        )}
                      </div>
                    ))
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Модал: детали лида */}
      {selected && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-end sm:items-center justify-center p-4"
             onClick={() => setSelected(null)}>
          <div className="bg-white rounded-2xl w-full max-w-md p-6 space-y-4"
               onClick={e => e.stopPropagation()}>
            <h3 className="font-bold text-lg text-ink">{selected.name}</h3>
            {selected.phone && <p className="text-sm text-muted">📱 {selected.phone}</p>}
            {selected.description && <p className="text-sm text-muted">{selected.description}</p>}
            {selected.budget > 0 && (
              <p className="text-lg font-bold text-primary">{formatBudget(selected.budget)}</p>
            )}
            <p className="text-xs text-muted">
              Источник: {sourceEmoji[selected.source] || selected.source} · {formatDate(selected.created_at)}
            </p>

            {/* Переместить */}
            <div>
              <p className="text-xs font-semibold text-muted uppercase mb-2">Переместить в:</p>
              <div className="flex flex-wrap gap-1.5">
                {columns.map(col => (
                  <button
                    key={col.id}
                    onClick={() => moveToStatus(selected.id, col.id)}
                    disabled={selected.status === col.id}
                    className={`text-xs px-3 py-1.5 rounded-lg font-medium transition-colors ${
                      selected.status === col.id
                        ? 'bg-primary text-white'
                        : 'bg-gray-100 text-muted hover:bg-primary/10 hover:text-primary'
                    }`}
                  >
                    {col.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex gap-2">
              {selected.phone && (
                <a href={`tel:${selected.phone}`}
                   className="flex-1 bg-primary text-white text-center py-2.5 rounded-xl text-sm font-semibold no-underline">
                  📞 Позвонить
                </a>
              )}
              <button
                onClick={() => deleteLead(selected.id)}
                className="px-4 py-2.5 rounded-xl text-sm font-semibold bg-red-50 text-red-600
                           hover:bg-red-100 transition-colors"
              >
                🗑️
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Модал: добавить лида */}
      {showAdd && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-end sm:items-center justify-center p-4"
             onClick={() => setShowAdd(false)}>
          <div className="bg-white rounded-2xl w-full max-w-md p-6 space-y-4"
               onClick={e => e.stopPropagation()}>
            <h3 className="font-bold text-lg text-ink">Новый лид</h3>

            <input
              type="text"
              placeholder="Имя клиента"
              value={newLead.name}
              onChange={e => setNewLead(p => ({ ...p, name: e.target.value }))}
              className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm
                         focus:outline-none focus:border-primary"
            />
            <input
              type="tel"
              placeholder="Телефон"
              value={newLead.phone}
              onChange={e => setNewLead(p => ({ ...p, phone: e.target.value }))}
              className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm
                         focus:outline-none focus:border-primary"
            />

            <div className="flex gap-2">
              {[
                { v: 'kitchen', l: '🍽️ Кухня' },
                { v: 'wardrobe', l: '🪞 Шкаф' },
                { v: 'closet', l: '👗 Гардероб' },
              ].map(t => (
                <button
                  key={t.v}
                  onClick={() => setNewLead(p => ({ ...p, type: t.v }))}
                  className={`flex-1 text-xs py-2 rounded-xl font-medium border transition-colors ${
                    newLead.type === t.v
                      ? 'bg-primary text-white border-primary'
                      : 'bg-white text-muted border-gray-200'
                  }`}
                >
                  {t.l}
                </button>
              ))}
            </div>

            <div className="flex gap-2">
              {[
                { v: 'site', l: '🌐 Сайт' },
                { v: 'telegram', l: '✈️ TG' },
                { v: 'avito', l: '🟢 Avito' },
                { v: 'referral', l: '👥' },
              ].map(s => (
                <button
                  key={s.v}
                  onClick={() => setNewLead(p => ({ ...p, source: s.v }))}
                  className={`flex-1 text-xs py-2 rounded-xl font-medium border transition-colors ${
                    newLead.source === s.v
                      ? 'bg-primary text-white border-primary'
                      : 'bg-white text-muted border-gray-200'
                  }`}
                >
                  {s.l}
                </button>
              ))}
            </div>

            <button
              onClick={addLead}
              disabled={!newLead.name.trim()}
              className="w-full bg-primary text-white py-3 rounded-xl font-semibold text-sm
                         hover:bg-primary-dark transition-colors disabled:opacity-50"
            >
              Добавить лида
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
