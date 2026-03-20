import { useCallback } from 'react'
import { useEventStore } from '@/store/useEventStore'
import type { EventType, Priority, EventStatus } from '@/types/event'

const EVENT_TYPES: { value: EventType; label: string }[] = [
  { value: 'maintenance_request', label: 'Maintenance' },
  { value: 'lease_inquiry', label: 'Lease Inquiry' },
  { value: 'payment_issue', label: 'Payment Issue' },
  { value: 'move_in', label: 'Move In' },
  { value: 'move_out', label: 'Move Out' },
  { value: 'noise_complaint', label: 'Noise Complaint' },
  { value: 'safety_concern', label: 'Safety Concern' },
  { value: 'amenity_request', label: 'Amenity Request' },
  { value: 'general_inquiry', label: 'General Inquiry' },
  { value: 'other', label: 'Other' },
]

const PRIORITIES: { value: Priority; label: string }[] = [
  { value: 'urgent', label: 'Urgent' },
  { value: 'high', label: 'High' },
  { value: 'medium', label: 'Medium' },
  { value: 'low', label: 'Low' },
]

const STATUSES: { value: EventStatus; label: string }[] = [
  { value: 'open', label: 'Open' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'resolved', label: 'Resolved' },
  { value: 'closed', label: 'Closed' },
]

interface EventFiltersProps {
  onFiltersChange: (filters: Record<string, string | undefined>) => void
}

export default function EventFilters({ onFiltersChange }: EventFiltersProps) {
  const { filters, setFilters, clearFilters } = useEventStore()

  const handleChange = useCallback(
    (key: string, value: string) => {
      const newFilters = {
        ...filters,
        [key]: value || undefined,
      }
      setFilters(newFilters as typeof filters)
      onFiltersChange(newFilters)
    },
    [filters, setFilters, onFiltersChange]
  )

  const hasFilters = Object.values(filters).some(Boolean)

  const selectCls =
    'text-sm bg-white dark:bg-od-bg2 border border-slate-200 dark:border-od-border rounded-lg px-3 py-2 text-slate-700 dark:text-od-fg focus:outline-none focus:ring-2 focus:ring-amber-500 cursor-pointer'

  return (
    <div className="flex flex-wrap items-center gap-2">
      <select
        value={filters.event_type ?? ''}
        onChange={(e) => handleChange('event_type', e.target.value)}
        className={selectCls}
      >
        <option value="">All Types</option>
        {EVENT_TYPES.map((t) => (
          <option key={t.value} value={t.value}>{t.label}</option>
        ))}
      </select>

      <select
        value={filters.priority ?? ''}
        onChange={(e) => handleChange('priority', e.target.value)}
        className={selectCls}
      >
        <option value="">All Priorities</option>
        {PRIORITIES.map((p) => (
          <option key={p.value} value={p.value}>{p.label}</option>
        ))}
      </select>

      <select
        value={filters.status ?? ''}
        onChange={(e) => handleChange('status', e.target.value)}
        className={selectCls}
      >
        <option value="">All Statuses</option>
        {STATUSES.map((s) => (
          <option key={s.value} value={s.value}>{s.label}</option>
        ))}
      </select>

      {hasFilters && (
        <button
          onClick={() => {
            clearFilters()
            onFiltersChange({})
          }}
          className="text-sm text-amber-600 dark:text-amber-400 hover:underline px-2"
        >
          Clear filters
        </button>
      )}
    </div>
  )
}
