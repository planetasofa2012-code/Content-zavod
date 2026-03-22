import { createClient } from '@supabase/supabase-js'

// Supabase-клиент (серверный — только для API-роутов)
// Ключ НЕ имеет префикса NEXT_PUBLIC_ → не попадает в клиентский бандл
const supabaseUrl = process.env.SUPABASE_URL!
const supabaseKey = process.env.SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseKey)
