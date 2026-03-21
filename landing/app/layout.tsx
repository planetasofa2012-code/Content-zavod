import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin', 'cyrillic'] })

export const metadata: Metadata = {
  title: 'Мебель на заказ в Новосибирске — Кухня 54 | Бесплатный замер',
  description:
    'Кухни, шкафы, гардеробные на заказ. 10+ лет опыта, 450+ клиентов. ' +
    'Бесплатный замер и 3D-эскиз. Гарантия 24 месяца.',
  openGraph: {
    title: 'Кухня мечты за 30 дней — Кухня 54',
    description:
      'Мебель на заказ в Новосибирске. Бесплатный замер и 3D-эскиз до оплаты.',
    locale: 'ru_RU',
    type: 'website',
  },
  // Разрешаем индексацию
  robots: { index: true, follow: true },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ru">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
