import { NextRequest, NextResponse } from 'next/server'

// API-маршрут: приём заявки с лендинга → уведомление владельцу в Telegram
export async function POST(req: NextRequest) {
  const { name, phone } = await req.json()

  if (!name || !phone) {
    return NextResponse.json({ error: 'Заполните все поля' }, { status: 400 })
  }

  const token  = process.env.TG_CONTENT_BOT_TOKEN
  const chatId = process.env.OWNER_ID

  if (!token || !chatId) {
    // Токены не настроены — логируем но не ломаем пользователю форму
    console.warn('TG_CONTENT_BOT_TOKEN или OWNER_ID не настроены в .env.local')
    return NextResponse.json({ ok: true })
  }

  const text =
    `🔔 <b>Новая заявка с сайта!</b>\n\n` +
    `👤 Имя: ${name}\n` +
    `📱 Телефон: ${phone}\n\n` +
    `💬 Источник: Лендинг kuhnya54\n` +
    `⏰ Время: ${new Date().toLocaleString('ru-RU', { timeZone: 'Asia/Novosibirsk' })}`

  await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chat_id:    chatId,
      text,
      parse_mode: 'HTML',
    }),
  })

  return NextResponse.json({ ok: true })
}
