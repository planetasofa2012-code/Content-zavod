import type { Config } from 'tailwindcss'

const config: Config = {
  content: ['./app/**/*.{ts,tsx,js,jsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#2D7D46',
          dark:    '#1f5c32',
          light:   '#e8f5ee',
        },
        gold:    '#F59E0B',
        ink:     '#1A1A2E',
        muted:   '#6B7280',
        surface: '#F8F9FA',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      keyframes: {
        // Анимация всплытия карточек
        fadeUp: {
          '0%':   { opacity: '0', transform: 'translateY(24px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        // Пульсация кнопки чата
        pulse2: {
          '0%, 100%': { boxShadow: '0 0 0 0 rgba(45,125,70,0.4)' },
          '50%':       { boxShadow: '0 0 0 10px rgba(45,125,70,0)' },
        },
      },
      animation: {
        fadeUp: 'fadeUp 0.5s ease both',
        pulse2: 'pulse2 2s ease infinite',
      },
    },
  },
  plugins: [],
}

export default config
