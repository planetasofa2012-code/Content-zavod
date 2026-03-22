import { NextResponse } from 'next/server'

// POST /api/auth — проверка пароля → установка cookie
export async function POST(req: Request) {
  const body = await req.json()
  const { password } = body

  const secret = process.env.APP_SECRET

  if (!password || password !== secret) {
    return NextResponse.json(
      { error: 'Неверный пароль' },
      { status: 401 }
    )
  }

  // Устанавливаем cookie на 30 дней
  const response = NextResponse.json({ ok: true })
  response.cookies.set('auth_token', secret!, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 60 * 60 * 24 * 30, // 30 дней
    path: '/',
  })

  return response
}
