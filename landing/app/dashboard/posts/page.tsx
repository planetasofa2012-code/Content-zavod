'use client'

import { useEffect, useState } from 'react'

interface Post {
  id: string
  title: string
  content: string
  image_url: string | null
  status: string
  platforms: string[]
  published_at: string | null
  stats: { views: number; likes: number; comments: number }
  ai_generated: boolean
  created_at: string
}

const platformEmoji: Record<string, string> = {
  telegram: '✈️',
  vk: '🔵',
  instagram: '📸',
  pinterest: '📌',
}

export default function PostsPage() {
  const [posts, setPosts] = useState<Post[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'published' | 'draft'>('all')

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch('/api/posts')
        const data = await res.json()
        setPosts(Array.isArray(data) ? data : [])
      } catch (e) {
        console.error('Ошибка загрузки постов:', e)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const filtered = filter === 'all' ? posts : posts.filter(p => p.status === filter)

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="text-4xl mb-3 animate-pulse">📝</div>
          <p className="text-muted">Загрузка постов...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-ink">Посты</h2>

      {/* Фильтры */}
      <div className="flex gap-2">
        {([
          { id: 'all' as const, label: 'Все', count: posts.length },
          { id: 'published' as const, label: 'Опубликованы', count: posts.filter(p => p.status === 'published').length },
          { id: 'draft' as const, label: 'Черновики', count: posts.filter(p => p.status === 'draft').length },
        ]).map(f => (
          <button
            key={f.id}
            onClick={() => setFilter(f.id)}
            className={`text-sm px-4 py-2 rounded-full font-medium transition-all ${
              filter === f.id
                ? 'bg-primary text-white'
                : 'bg-gray-100 text-muted hover:bg-gray-200'
            }`}
          >
            {f.label} ({f.count})
          </button>
        ))}
      </div>

      {/* Список постов */}
      {filtered.length === 0 ? (
        <div className="text-center py-16">
          <div className="text-5xl mb-4">📭</div>
          <h3 className="text-lg font-bold text-ink mb-2">Пока нет постов</h3>
          <p className="text-sm text-muted mb-6">
            Посты будут появляться здесь автоматически, когда бот создаст контент
          </p>
          <div className="text-sm text-muted bg-gray-50 rounded-xl p-4 max-w-sm mx-auto">
            💡 Чтобы создать пост, отправьте фото кухни боту <strong>@kuhnya154</strong> в Telegram
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map(post => (
            <div key={post.id} className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
              <div className="flex gap-3">
                {/* Превью */}
                {post.image_url ? (
                  <img
                    src={post.image_url}
                    alt={post.title}
                    className="w-20 h-20 rounded-xl object-cover flex-shrink-0"
                  />
                ) : (
                  <div className="w-20 h-20 rounded-xl bg-gradient-to-br from-green-100 to-green-200
                                  flex items-center justify-center text-2xl flex-shrink-0">
                    📝
                  </div>
                )}

                <div className="flex-1 min-w-0">
                  <h4 className="font-semibold text-sm text-ink truncate">{post.title}</h4>
                  <p className="text-xs text-muted line-clamp-2 mt-0.5">{post.content}</p>

                  {/* Платформы */}
                  <div className="flex items-center gap-2 mt-2">
                    {post.platforms.map(p => (
                      <span key={p} className="text-xs">{platformEmoji[p] || p}</span>
                    ))}
                    <span className={`ml-auto text-xs px-2 py-0.5 rounded-full font-medium ${
                      post.status === 'published'
                        ? 'bg-green-100 text-green-700'
                        : 'bg-gray-100 text-muted'
                    }`}>
                      {post.status === 'published' ? '✅ Опубликован' : '📝 Черновик'}
                    </span>
                  </div>

                  {/* Статистика для опубликованных */}
                  {post.status === 'published' && post.stats && (
                    <div className="flex gap-3 mt-2 text-xs text-muted">
                      <span>👁 {post.stats.views}</span>
                      <span>❤️ {post.stats.likes}</span>
                      <span>💬 {post.stats.comments}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
