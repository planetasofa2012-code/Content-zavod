import { NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export const dynamic = 'force-dynamic'

// GET /api/posts — список постов
export async function GET() {
  const { data, error } = await supabase
    .from('posts')
    .select('*')
    .order('created_at', { ascending: false })

  if (error) return NextResponse.json({ error: error.message }, { status: 500 })
  return NextResponse.json(data)
}

// POST /api/posts — создать пост
export async function POST(req: Request) {
  const body = await req.json()

  const { data, error } = await supabase
    .from('posts')
    .insert({
      title: body.title,
      content: body.content,
      image_url: body.image_url,
      status: body.status || 'draft',
      platforms: body.platforms || [],
      ai_generated: body.ai_generated || false,
      tags: body.tags || [],
    })
    .select()
    .single()

  if (error) return NextResponse.json({ error: error.message }, { status: 500 })
  return NextResponse.json(data)
}
