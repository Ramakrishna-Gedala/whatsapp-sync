import { useQuery } from '@tanstack/react-query'
import { useEffect } from 'react'
import { eventsApi, type EventFilters } from '@/api/eventsApi'
import { useEventStore } from '@/store/useEventStore'

export function useEvents(filters: EventFilters = {}) {
  const setEvents = useEventStore((s) => s.setEvents)

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['events', filters],
    queryFn: () => eventsApi.getEvents(filters),
    staleTime: 30_000,
  })

  useEffect(() => {
    if (data) {
      setEvents(data.events, data.total)
    }
  }, [data, setEvents])

  return {
    events: data?.events ?? [],
    total: data?.total ?? 0,
    isLoading,
    error,
    refetch,
  }
}
