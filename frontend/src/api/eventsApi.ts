import apiClient from './axiosClient'
import type { Event, EventsResponse, EventStatus, EventType, Priority } from '@/types/event'

export interface EventFilters {
  group_id?: string
  event_type?: EventType
  priority?: Priority
  status?: EventStatus
  skip?: number
  limit?: number
}

export const eventsApi = {
  getEvents: async (filters: EventFilters = {}): Promise<EventsResponse> => {
    const params = Object.fromEntries(
      Object.entries(filters).filter(([, v]) => v !== undefined && v !== null && v !== '')
    )
    const { data } = await apiClient.get<EventsResponse>('/events', { params })
    return data
  },

  getEvent: async (eventId: string): Promise<Event> => {
    const { data } = await apiClient.get<Event>(`/events/${eventId}`)
    return data
  },

  updateStatus: async (eventId: string, status: EventStatus): Promise<Event> => {
    const { data } = await apiClient.patch<Event>(`/events/${eventId}/status`, { status })
    return data
  },
}
