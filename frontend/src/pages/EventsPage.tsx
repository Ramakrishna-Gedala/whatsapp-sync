import { useState, useCallback, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { RefreshCw, Loader2, MessageSquarePlus } from 'lucide-react'
import GroupSelector from '@/components/groups/GroupSelector'
import EventList from '@/components/events/EventList'
import EventFilters from '@/components/events/EventFilters'
import { useGroups } from '@/hooks/useGroups'
import { useGroupMessages } from '@/hooks/useGroupMessages'
import { useEvents } from '@/hooks/useEvents'
import { useGroupStore } from '@/store/useGroupStore'
import { useEventStore } from '@/store/useEventStore'
import type { EventFilters as EventFilterParams } from '@/api/eventsApi'

export default function EventsPage() {
  const { groups, isLoading: groupsLoading } = useGroups()
  const { selectedGroupId, selectedGroupName } = useGroupStore()
  const { processMessages, isPending: syncing } = useGroupMessages()
  const storeEvents = useEventStore((s) => s.events)

  const [queryFilters, setQueryFilters] = useState<EventFilterParams>({})
  const filterDebounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const effectiveFilters: EventFilterParams = {
    ...queryFilters,
    ...(selectedGroupId ? { group_id: selectedGroupId } : {}),
  }

  const { events: fetchedEvents, total, isLoading: eventsLoading } = useEvents(effectiveFilters)

  // Merge: store events take priority (for optimistic prepend), filtered by current filters
  const displayEvents = storeEvents.length > 0 && !Object.keys(queryFilters).length
    ? storeEvents
    : fetchedEvents

  const handleFiltersChange = useCallback((filters: Record<string, string | undefined>) => {
    if (filterDebounceRef.current) clearTimeout(filterDebounceRef.current)
    filterDebounceRef.current = setTimeout(() => {
      setQueryFilters(filters as EventFilterParams)
    }, 300)
  }, [])

  useEffect(() => {
    return () => {
      if (filterDebounceRef.current) clearTimeout(filterDebounceRef.current)
    }
  }, [])

  return (
    <div className="h-full flex flex-col">
      {/* Page header */}
      <div className="border-b border-slate-200 dark:border-od-border bg-white dark:bg-od-bg2 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">Events Dashboard</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              {total > 0 ? `${total} events total` : 'No events yet'}
              {selectedGroupName && (
                <span className="ml-2 text-amber-600 dark:text-amber-400">
                  · {selectedGroupName}
                </span>
              )}
            </p>
          </div>
          <Link
            to="/chat"
            className="btn-ghost text-sm"
          >
            <MessageSquarePlus size={16} />
            Manual Parser
          </Link>
        </div>
      </div>

      {/* Controls */}
      <div className="border-b border-slate-200 dark:border-od-border bg-white dark:bg-od-bg2 px-6 py-3 space-y-3">
        {/* Group selector + sync */}
        <div className="flex items-center gap-3 flex-wrap">
          <GroupSelector groups={groups} isLoading={groupsLoading} />
          <button
            onClick={() => {
              if (selectedGroupId) processMessages({ groupId: selectedGroupId })
            }}
            disabled={!selectedGroupId || syncing}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {syncing ? (
              <><Loader2 size={16} className="animate-spin" /> Syncing...</>
            ) : (
              <><RefreshCw size={16} /> Sync Messages</>
            )}
          </button>
        </div>

        {/* Filters */}
        <EventFilters onFiltersChange={handleFiltersChange} />
      </div>

      {/* Events list */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        <EventList
          events={displayEvents}
          isLoading={eventsLoading}
        />
      </div>
    </div>
  )
}
