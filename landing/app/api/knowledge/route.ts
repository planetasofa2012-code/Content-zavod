import { NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export const dynamic = 'force-dynamic'

// GET /api/knowledge — список записей базы знаний
export async function GET(req: Request) {
  const { searchParams } = new URL(req.url)
  const category = searchParams.get('category')
  const search = searchParams.get('search')

  let query = supabase
    .from('knowledge_entries')
    .select('*')
    .order('created_at', { ascending: false })

  if (category && category !== 'all') {
    query = query.eq('category', category)
  }

  if (search) {
    query = query.or(`question.ilike.%${search}%,answer.ilike.%${search}%`)
  }

  const { data, error } = await query

  if (error) return NextResponse.json({ error: error.message }, { status: 500 })
  return NextResponse.json(data)
}

// POST /api/knowledge — добавить запись
export async function POST(req: Request) {
  const body = await req.json()

  const { data, error } = await supabase
    .from('knowledge_entries')
    .insert({
      category: body.category || 'faq',
      question: body.question,
      answer: body.answer,
      source: body.source || 'manual',
    })
    .select()
    .single()

  if (error) return NextResponse.json({ error: error.message }, { status: 500 })
  return NextResponse.json(data)
}
