import type { Metadata, Viewport } from 'next'
import { Inter, Epilogue } from 'next/font/google'
import './globals.css'

const inter = Inter({ 
  subsets: ['latin', 'cyrillic'],
  variable: '--font-inter',
})

const epilogue = Epilogue({ 
  subsets: ['latin'],
  variable: '--font-epilogue',
})

export const viewport: Viewport = {
  themeColor: '#2D7D46',
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
}

export const metadata: Metadata = {
  title: 'Кухня 54 — Мебель на заказ в Новосибирске',
  description:
    'Кухни, шкафы, гардеробные на заказ. 10+ лет опыта, 450+ клиентов. ' +
    'Бесплатный замер и 3D-эскиз. Гарантия 24 месяца.',
  manifest: '/manifest.json',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: 'Кухня 54',
  },
  openGraph: {
    title: 'Кухня мечты за 30 дней — Кухня 54',
    description:
      'Мебель на заказ в Новосибирске. Бесплатный замер и 3D-эскиз до оплаты.',
    locale: 'ru_RU',
    type: 'website',
  },
  robots: { index: true, follow: true },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ru">
      <head>
        <link rel="apple-touch-icon" href="/icons/icon-192.png" />
      </head>
      <body className={`${inter.variable} ${epilogue.variable} font-sans`}>
        {children}
        {/* Регистрация Service Worker для PWA */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              if ('serviceWorker' in navigator) {
                window.addEventListener('load', () => {
                  navigator.serviceWorker.register('/sw.js');
                });
              }
            `,
          }}
        />
      </body>
    </html>
  )
}
