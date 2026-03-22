'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

// Навигация для внутренних страниц (дашборд, CRM, посты)
const navItems = [
  { href: '/dashboard', label: 'Главная', icon: '📊' },
  { href: '/dashboard/posts', label: 'Посты', icon: '📸' },
  { href: '/dashboard/crm', label: 'CRM', icon: '🗂️' },
  { href: '/dashboard/knowledge', label: 'База', icon: '🧠' },
  { href: '/dashboard/settings', label: 'Ещё', icon: '⚙️' },
]

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()

  return (
    <div className="min-h-screen bg-surface pb-20">
      {/* Верхняя шапка */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-lg border-b border-gray-100">
        <div className="flex items-center justify-between px-4 py-3">
          <div>
            <h1 className="text-lg font-bold text-ink">Контент-завод</h1>
            <p className="text-xs text-muted">Кухня 54</p>
          </div>
          <div className="flex items-center gap-3">
            {/* Кнопка уведомлений */}
            <button className="relative p-2 rounded-xl hover:bg-gray-100 transition-colors">
              <span className="text-xl">🔔</span>
              <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center">
                3
              </span>
            </button>
          </div>
        </div>
      </header>

      {/* Контент страницы */}
      <main className="px-4 py-4">
        {children}
      </main>

      {/* Нижняя навигация — как в мобильном приложении */}
      <nav className="fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-200 safe-area-bottom">
        <div className="flex justify-around items-center py-2">
          {navItems.map((item) => {
            const isActive = pathname === item.href || 
              (item.href !== '/dashboard' && pathname.startsWith(item.href))
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex flex-col items-center gap-0.5 px-3 py-1 rounded-xl transition-colors ${
                  isActive
                    ? 'text-primary'
                    : 'text-muted hover:text-ink'
                }`}
              >
                <span className="text-xl">{item.icon}</span>
                <span className="text-[10px] font-medium">{item.label}</span>
              </Link>
            )
          })}
        </div>
      </nav>
    </div>
  )
}
