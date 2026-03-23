import { NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export const dynamic = 'force-dynamic'

// POST /api/lead — форма заявки с лендинга → создаёт лида в CRM
export async function POST(req: Request) {
  const body = await req.json()
  const { name, phone } = body

  if (!name || !phone) {
    return NextResponse.json({ error: 'Имя и телефон обязательны' }, { status: 400 })
  }

  // Создаём лида в Supabase
  const { data, error } = await supabase
    .from('leads')
    .insert({
      name,
      phone,
      type: 'kitchen',
      source: 'site',
      status: 'lead',
      priority: 'medium',
      description: 'Заявка с сайта',
    })
    .select()
    .single()

  if (error) {
    console.error('Ошибка создания лида:', error)
    return NextResponse.json({ error: error.message }, { status: 500 })
  }

  return NextResponse.json({ ok: true, lead: data })
}
