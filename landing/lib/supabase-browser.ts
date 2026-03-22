import { createClient } from '@supabase/supabase-js'

// Клиентский Supabase — для Realtime-подписок в браузере
// Anon-ключ безопасен на клиенте: RLS-политики контролируют доступ
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabaseBrowser = createClient(supabaseUrl, supabaseKey, {
  realtime: {
    params: {
      eventsPerSecond: 10,
    },
  },
})
