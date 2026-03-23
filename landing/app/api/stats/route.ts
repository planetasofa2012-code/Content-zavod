import { NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export const dynamic = 'force-dynamic'

// GET /api/stats — сводная статистика для дашборда
export async function GET() {
  // Параллельно получаем все метрики
  const [leadsRes, postsRes, knowledgeRes, conversationsRes] = await Promise.all([
    supabase.from('leads').select('id, status', { count: 'exact' }),
    supabase.from('posts').select('id, status', { count: 'exact' }),
    supabase.from('knowledge_entries').select('id', { count: 'exact' }),
    supabase.from('conversations').select('id', { count: 'exact' }),
  ])

  // Считаем лидов по статусам
  const leads = leadsRes.data || []
  const leadsInWork = leads.filter(l =>
    ['measurement', 'project', 'production', 'installation'].includes(l.status)
  ).length
  const leadsDone = leads.filter(l => ['done', 'review'].includes(l.status)).length

  // Считаем посты
  const posts = postsRes.data || []
  const postsPublished = posts.filter(p => p.status === 'published').length

  // Замеры (лиды со статусом measurement+)
  const measurements = leads.filter(l =>
    ['measurement', 'project', 'production', 'installation', 'review', 'done'].includes(l.status)
  ).length

  return NextResponse.json({
    posts: {
      total: posts.length,
      published: postsPublished,
    },
    leads: {
      total: leads.length,
      in_work: leadsInWork,
      done: leadsDone,
    },
    measurements,
    ai_responses: conversationsRes.data?.length || 0,
    knowledge_entries: knowledgeRes.data?.length || 0,
  })
}
