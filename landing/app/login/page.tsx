'use client'

import { useState, FormEvent } from 'react'
import { useRouter } from 'next/navigation'

export default function LoginPage() {
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const res = await fetch('/api/auth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password }),
      })

      if (res.ok) {
        router.push('/dashboard')
      } else {
        setError('Неверный пароль')
      }
    } catch {
      setError('Ошибка соединения')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      className="min-h-screen flex items-center justify-center p-5"
      style={{
        background: 'linear-gradient(135deg, #0f2c1a 0%, #1a4a2e 50%, #2D7D46 100%)',
      }}
    >
      {/* Паттерн */}
      <div
        className="fixed inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/svg%3E")`,
        }}
      />

      <div className="relative w-full max-w-sm">
        {/* Логотип */}
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">🏠</div>
          <h1 className="text-2xl font-extrabold text-white">
            Кухня<span className="text-green-300">54</span>
          </h1>
          <p className="text-white/60 text-sm mt-1">Панель управления</p>
        </div>

        {/* Форма */}
        <form
          onSubmit={handleSubmit}
          className="bg-white/10 backdrop-blur-md border border-white/20
                     rounded-2xl p-6 space-y-4"
        >
          <div>
            <label className="block text-white/70 text-sm font-medium mb-2">
              🔐 Пароль
            </label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="Введите пароль"
              autoFocus
              required
              className="w-full bg-white/90 text-gray-900 placeholder-gray-400
                         rounded-xl px-4 py-3.5 text-sm
                         focus:outline-none focus:bg-white focus:ring-2 focus:ring-green-300
                         transition-all"
            />
          </div>

          {error && (
            <p className="text-red-300 text-sm text-center bg-red-500/10 rounded-lg py-2">
              ❌ {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading || !password}
            className="w-full bg-white text-green-800 font-bold text-base
                       rounded-xl py-3.5
                       hover:bg-green-50 transition-all duration-200
                       disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? '⏳ Проверяем...' : 'Войти →'}
          </button>

          <p className="text-white/30 text-xs text-center">
            Доступ только для владельца
          </p>
        </form>
      </div>
    </div>
  )
}
