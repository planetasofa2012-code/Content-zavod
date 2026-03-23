import { createClient, SupabaseClient } from '@supabase/supabase-js'

// Supabase-клиент (серверный — только для API-роутов)
// Ленивая инициализация: создаётся при первом вызове, а не при импорте
// Это предотвращает ошибки при сборке Docker-образа
let _supabase: SupabaseClient | null = null

export function getSupabase(): SupabaseClient {
  if (!_supabase) {
    const supabaseUrl = process.env.SUPABASE_URL!
    const supabaseKey = process.env.SUPABASE_ANON_KEY!
    _supabase = createClient(supabaseUrl, supabaseKey)
  }
  return _supabase
}

// Обратная совместимость — геттер для существующих импортов
export const supabase = new Proxy({} as SupabaseClient, {
  get(_, prop) {
    return (getSupabase() as any)[prop]
  }
})
