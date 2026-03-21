'use client'

import { useEffect, useRef, useState } from 'react'

// Блок 6: Цифры и факты — анимированный счётчик при попадании в viewport
const stats = [
  { value: 10,  suffix: '+', label: 'лет опыта',           desc: 'в корпусной мебели' },
  { value: 450, suffix: '+', label: 'выполненных заказов', desc: 'за всё время' },
  { value: 98,  suffix: '%', label: 'повторных обращений', desc: 'клиенты возвращаются' },
  { value: 24,  suffix: '',  label: 'месяца гарантии',     desc: 'на корпус и фурнитуру' },
]

function Counter({ target, suffix }: { target: number; suffix: string }) {
  const [count, setCount] = useState(0)
  const ref = useRef<HTMLSpanElement>(null)
  const started = useRef(false)

  useEffect(() => {
    const el = ref.current
    if (!el) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !started.current) {
          started.current = true
          const duration = 1200
          const steps = 40
          const inc = target / steps
          let cur = 0
          const timer = setInterval(() => {
            cur += inc
            if (cur >= target) { setCount(target); clearInterval(timer) }
            else setCount(Math.floor(cur))
          }, duration / steps)
        }
      },
      { threshold: 0.4 }
    )
    observer.observe(el)
    return () => observer.disconnect()
  }, [target])

  return (
    <span ref={ref}>
      {count}{suffix}
    </span>
  )
}

export default function Stats() {
  return (
    <section className="bg-primary py-16">
      <div className="max-w-5xl mx-auto px-5">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 text-white text-center">
          {stats.map((s, i) => (
            <div key={i} className="p-4">
              <div className="text-4xl sm:text-5xl font-extrabold mb-1">
                <Counter target={s.value} suffix={s.suffix} />
              </div>
              <div className="font-semibold text-base mb-0.5">{s.label}</div>
              <div className="text-white/70 text-sm">{s.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
