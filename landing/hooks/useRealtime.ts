'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import { supabaseBrowser } from '@/lib/supabase-browser'
import type { RealtimeChannel } from '@supabase/supabase-js'

// Тип лида
export interface Lead {
  id: string
  name: string
  phone: string
  type: string
  description: string
  budget: number
  status: string
  priority: string
  source: string
  notes: string
  created_at: string
  updated_at: string
}

/**
 * Хук для реалтайм-подписки на таблицу leads.
 * При INSERT/UPDATE/DELETE — обновляет список мгновенно.
 * Показывает toast-уведомление при новых лидах.
 */
export function useRealtimeLeads() {
  const [leads, setLeads] = useState<Lead[]>([])
  const [loading, setLoading] = useState(true)
  const [newLeadAlert, setNewLeadAlert] = useState<Lead | null>(null)
  const channelRef = useRef<RealtimeChannel | null>(null)

  // Первоначальная загрузка
  const fetchLeads = useCallback(async () => {
    try {
      const res = await fetch('/api/leads')
      const data = await res.json()
      setLeads(Array.isArray(data) ? data : [])
    } catch (e) {
      console.error('Ошибка загрузки лидов:', e)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchLeads()

    // Подписываемся на Realtime-изменения таблицы leads
    const channel = supabaseBrowser
      .channel('leads-realtime')
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'leads',
        },
        (payload) => {
          const newLead = payload.new as Lead
          console.log('🔔 Новый лид:', newLead.name)
          setLeads(prev => [newLead, ...prev])
          setNewLeadAlert(newLead)

          // Убираем уведомление через 5 секунд
          setTimeout(() => setNewLeadAlert(null), 5000)
        }
      )
      .on(
        'postgres_changes',
        {
          event: 'UPDATE',
          schema: 'public',
          table: 'leads',
        },
        (payload) => {
          const updated = payload.new as Lead
          console.log('✏️ Лид обновлён:', updated.name, '→', updated.status)
          setLeads(prev => prev.map(l => l.id === updated.id ? updated : l))
        }
      )
      .on(
        'postgres_changes',
        {
          event: 'DELETE',
          schema: 'public',
          table: 'leads',
        },
        (payload) => {
          const deleted = payload.old as { id: string }
          console.log('🗑️ Лид удалён:', deleted.id)
          setLeads(prev => prev.filter(l => l.id !== deleted.id))
        }
      )
      .subscribe((status) => {
        console.log('📡 Realtime leads:', status)
      })

    channelRef.current = channel

    // Очистка подписки при размонтировании
    return () => {
      if (channelRef.current) {
        supabaseBrowser.removeChannel(channelRef.current)
      }
    }
  }, [fetchLeads])

  return { leads, setLeads, loading, newLeadAlert, refetch: fetchLeads }
}


/**
 * Универсальный хук для реалтайм-подписки на любую таблицу.
 */
export function useRealtimeTable<T extends { id: string }>(table: string, apiEndpoint: string) {
  const [items, setItems] = useState<T[]>([])
  const [loading, setLoading] = useState(true)
  const channelRef = useRef<RealtimeChannel | null>(null)

  const fetchItems = useCallback(async () => {
    try {
      const res = await fetch(apiEndpoint)
      const data = await res.json()
      setItems(Array.isArray(data) ? data : [])
    } catch (e) {
      console.error(`Ошибка загрузки ${table}:`, e)
    } finally {
      setLoading(false)
    }
  }, [table, apiEndpoint])

  useEffect(() => {
    fetchItems()

    const channel = supabaseBrowser
      .channel(`${table}-realtime`)
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table },
        (payload) => {
          if (payload.eventType === 'INSERT') {
            setItems(prev => [payload.new as T, ...prev])
          } else if (payload.eventType === 'UPDATE') {
            const updated = payload.new as T
            setItems(prev => prev.map(i => i.id === updated.id ? updated : i))
          } else if (payload.eventType === 'DELETE') {
            const deleted = payload.old as { id: string }
            setItems(prev => prev.filter(i => i.id !== deleted.id))
          }
        }
      )
      .subscribe()

    channelRef.current = channel

    return () => {
      if (channelRef.current) {
        supabaseBrowser.removeChannel(channelRef.current)
      }
    }
  }, [table, fetchItems])

  return { items, setItems, loading, refetch: fetchItems }
}
