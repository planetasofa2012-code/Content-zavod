import { NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export const dynamic = 'force-dynamic'

// GET /api/leads — список лидов для CRM-канбана
export async function GET() {
  const { data, error } = await supabase
    .from('leads')
    .select('*')
    .order('created_at', { ascending: false })

  if (error) return NextResponse.json({ error: error.message }, { status: 500 })
  return NextResponse.json(data)
}

// POST /api/leads — создать нового лида (из формы на сайте)
export async function POST(req: Request) {
  const body = await req.json()
  const { name, phone, type, description, source } = body

  const { data, error } = await supabase
    .from('leads')
    .insert({
      name,
      phone,
      type: type || 'kitchen',
      description,
      source: source || 'site',
      status: 'lead',
      priority: 'medium',
    })
    .select()
    .single()

  if (error) return NextResponse.json({ error: error.message }, { status: 500 })
  return NextResponse.json(data)
}
