import { create } from 'zustand'
import type { Event, EventType, Priority, EventStatus } from '@/types/event'

interface EventFiltersState {
  event_type?: EventType
  priority?: Priority
  status?: EventStatus
}

interface EventStore {
  events: Event[]
  totalEvents: number
  filters: EventFiltersState
  setEvents: (events: Event[], total?: number) => void
  prependEvents: (newEvents: Event[]) => void
  updateEventStatus: (eventId: string, status: EventStatus) => void
  setFilters: (filters: EventFiltersState) => void
  clearFilters: () => void
}

export const useEventStore = create<EventStore>((set, get) => ({
  events: [],
  totalEvents: 0,
  filters: {},

  setEvents: (events, total) =>
    set({ events, totalEvents: total ?? events.length }),

  prependEvents: (newEvents) => {
    if (!newEvents.length) return
    const existing = get().events
    const existingIds = new Set(existing.map((e) => e.id))
    const dedupedNew = newEvents.filter((e) => !existingIds.has(e.id))
    set({
      events: [...dedupedNew, ...existing],
      totalEvents: get().totalEvents + dedupedNew.length,
    })
  },

  updateEventStatus: (eventId, status) => {
    set({
      events: get().events.map((e) =>
        e.id === eventId ? { ...e, status } : e
      ),
    })
  },

  setFilters: (filters) => set({ filters }),
  clearFilters: () => set({ filters: {} }),
}))
