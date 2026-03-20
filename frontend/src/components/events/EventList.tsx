import { useVirtualizer } from '@tanstack/react-virtual'
import { useRef } from 'react'
import EventCard from './EventCard'
import type { Event } from '@/types/event'

interface EventListProps {
  events: Event[]
  isLoading: boolean
}

function SkeletonCard() {
  return (
    <div className="card p-4 space-y-3 animate-pulse">
      <div className="flex gap-2">
        <div className="h-5 w-16 bg-slate-200 dark:bg-od-border rounded-full" />
        <div className="h-5 w-24 bg-slate-200 dark:bg-od-border rounded-full" />
      </div>
      <div className="h-4 w-3/4 bg-slate-200 dark:bg-od-border rounded" />
      <div className="h-3 w-full bg-slate-100 dark:bg-od-bg2 rounded" />
      <div className="h-3 w-5/6 bg-slate-100 dark:bg-od-bg2 rounded" />
    </div>
  )
}

export default function EventList({ events, isLoading }: EventListProps) {
  const parentRef = useRef<HTMLDivElement>(null)

  const virtualizer = useVirtualizer({
    count: events.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 200,
    overscan: 5,
  })

  if (isLoading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => <SkeletonCard key={i} />)}
      </div>
    )
  }

  if (events.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-center">
        <div className="text-5xl mb-4">📋</div>
        <h3 className="text-lg font-medium text-slate-700 dark:text-slate-300 mb-2">
          No events yet
        </h3>
        <p className="text-sm text-slate-500 dark:text-slate-500 max-w-xs">
          Select a group and click "Sync Messages" to load and parse WhatsApp messages into events.
        </p>
      </div>
    )
  }

  // Use virtualization for large lists, plain rendering for small
  if (events.length <= 50) {
    return (
      <div className="space-y-3">
        {events.map((event) => (
          <EventCard key={event.id} event={event} />
        ))}
      </div>
    )
  }

  return (
    <div ref={parentRef} className="overflow-y-auto" style={{ height: 'calc(100vh - 280px)' }}>
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          position: 'relative',
        }}
      >
        {virtualizer.getVirtualItems().map((item) => (
          <div
            key={item.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              transform: `translateY(${item.start}px)`,
              paddingBottom: '12px',
            }}
          >
            <EventCard event={events[item.index]} />
          </div>
        ))}
      </div>
    </div>
  )
}
