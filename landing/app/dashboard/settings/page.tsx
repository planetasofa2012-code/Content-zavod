'use client'

import Link from 'next/link'

// Страница настроек / «Ещё»
const menuItems = [
  {
    section: 'Управление',
    items: [
      { icon: '📊', label: 'Аналитика', href: '/dashboard/analytics', badge: '' },
      { icon: '🎙️', label: 'AI-интервью', href: '/dashboard/interview', badge: 'NEW' },
      { icon: '📤', label: 'Площадки', href: '/dashboard/platforms', badge: '4' },
    ],
  },
  {
    section: 'Настройки',
    items: [
      { icon: '🤖', label: 'AI-модели', href: '/dashboard/settings/ai', badge: '' },
      { icon: '🎨', label: 'Шаблоны постов', href: '/dashboard/settings/templates', badge: '' },
      { icon: '🔔', label: 'Уведомления', href: '/dashboard/settings/notifications', badge: '' },
    ],
  },
  {
    section: 'Ещё',
    items: [
      { icon: '🌐', label: 'Лендинг (сайт)', href: '/', badge: '' },
      { icon: '📱', label: 'Telegram-боты', href: 'https://t.me/kuhnya54_bot', badge: '' },
      { icon: '❓', label: 'Помощь', href: '/dashboard/help', badge: '' },
    ],
  },
]

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-ink">Настройки</h2>

      {/* Профиль */}
      <div className="bg-white rounded-2xl p-4 shadow-sm flex items-center gap-4">
        <div className="w-14 h-14 bg-primary rounded-full flex items-center justify-center text-white text-xl font-bold">
          АС
        </div>
        <div>
          <p className="font-bold text-ink">Александр Самосудов</p>
          <p className="text-sm text-muted">Кухня 54 • Новосибирск</p>
        </div>
      </div>

      {/* Статус системы */}
      <div className="bg-green-50 rounded-2xl p-4 border border-green-200">
        <div className="flex items-center gap-2 mb-2">
          <span className="w-2.5 h-2.5 bg-green-500 rounded-full animate-pulse" />
          <span className="font-semibold text-green-800 text-sm">Все системы работают</span>
        </div>
        <div className="grid grid-cols-2 gap-2 text-xs text-green-700">
          <span>✅ Контент-бот</span>
          <span>✅ AI-агент</span>
          <span>✅ Telegram</span>
          <span>⚠️ VK (нет токена)</span>
        </div>
      </div>

      {/* Меню */}
      {menuItems.map((section) => (
        <div key={section.section}>
          <h3 className="text-xs font-semibold text-muted uppercase tracking-wide mb-2 px-1">
            {section.section}
          </h3>
          <div className="bg-white rounded-2xl shadow-sm divide-y divide-gray-100">
            {section.items.map((item) => (
              <Link
                key={item.label}
                href={item.href}
                className="flex items-center justify-between px-4 py-3.5 hover:bg-gray-50 
                           transition-colors first:rounded-t-2xl last:rounded-b-2xl"
              >
                <div className="flex items-center gap-3">
                  <span className="text-lg">{item.icon}</span>
                  <span className="text-sm font-medium text-ink">{item.label}</span>
                </div>
                <div className="flex items-center gap-2">
                  {item.badge && (
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                      item.badge === 'NEW' 
                        ? 'bg-primary text-white' 
                        : 'bg-gray-100 text-muted'
                    }`}>
                      {item.badge}
                    </span>
                  )}
                  <span className="text-muted text-sm">›</span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      ))}

      {/* Версия */}
      <p className="text-center text-xs text-muted py-4">
        Контент-завод v1.0.0 • Кухня 54
      </p>
    </div>
  )
}
