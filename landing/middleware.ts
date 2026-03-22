import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Middleware: защита дашборда и API
// Лендинг (/) — открыт всем
// /api/lead (POST) — открыт (форма заявки с сайта)
// /dashboard/* и /api/* — только с cookie "auth_token"

const PUBLIC_PATHS = ['/', '/api/lead']

export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl

  // Лендинг и статика — пропускаем
  if (
    pathname === '/' ||
    pathname.startsWith('/_next') ||
    pathname.startsWith('/icons') ||
    pathname === '/manifest.json' ||
    pathname === '/sw.js' ||
    pathname === '/favicon.ico' ||
    pathname === '/login'
  ) {
    return NextResponse.next()
  }

  // Публичные API: форма заявки + авторизация
  if (
    (pathname === '/api/lead' && req.method === 'POST') ||
    (pathname === '/api/auth' && req.method === 'POST')
  ) {
    return NextResponse.next()
  }

  // Проверяем авторизацию для /dashboard/* и /api/*
  if (pathname.startsWith('/dashboard') || pathname.startsWith('/api')) {
    const token = req.cookies.get('auth_token')?.value

    if (!token || token !== process.env.APP_SECRET) {
      // API-запросы → 401
      if (pathname.startsWith('/api')) {
        return NextResponse.json(
          { error: 'Unauthorized' },
          { status: 401 }
        )
      }
      // Страницы дашборда → редирект на логин
      return NextResponse.redirect(new URL('/login', req.url))
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    // Проверяем все пути кроме статики
    '/((?!_next/static|_next/image|favicon.ico|icons|manifest.json|sw.js).*)',
  ],
}
