import { useState } from 'react'
import { formatDistanceToNow } from 'date-fns'
import {
  ChevronDown,
  ChevronUp,
  Building2,
  User,
  MessageCircle,
  Smartphone,
  FileText,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { eventsApi } from '@/api/eventsApi'
import { useEventStore } from '@/store/useEventStore'
import type { Event, EventStatus, Priority, EventType } from '@/types/event'

const PRIORITY_CONFIG: Record<Priority, { label: string; className: string }> = {
  urgent: { label: 'URGENT', className: 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-400' },
  high: { label: 'HIGH', className: 'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-400' },
  medium: { label: 'MEDIUM', className: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-400' },
  low: { label: 'LOW', className: 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-400' },
}

const EVENT_TYPE_LABELS: Record<EventType, string> = {
  maintenance_request: 'Maintenance',
  lease_inquiry: 'Lease Inquiry',
  payment_issue: 'Payment Issue',
  move_in: 'Move In',
  move_out: 'Move Out',
  noise_complaint: 'Noise Complaint',
  safety_concern: 'Safety Concern',
  amenity_request: 'Amenity Request',
  general_inquiry: 'General Inquiry',
  other: 'Other',
}

const STATUS_OPTIONS: { value: EventStatus; label: string }[] = [
  { value: 'open', label: 'Open' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'resolved', label: 'Resolved' },
  { value: 'closed', label: 'Closed' },
]

const STATUS_COLORS: Record<EventStatus, string> = {
  open: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-400',
  in_progress: 'bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-400',
  resolved: 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-400',
  closed: 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400',
}

interface EventCardProps {
  event: Event
}

export default function EventCard({ event }: EventCardProps) {
  const [expanded, setExpanded] = useState(false)
  const [updatingStatus, setUpdatingStatus] = useState(false)
  const updateEventStatus = useEventStore((s) => s.updateEventStatus)

  const priority = PRIORITY_CONFIG[event.priority]

  const handleStatusChange = async (newStatus: EventStatus) => {
    if (newStatus === event.status) return
    setUpdatingStatus(true)
    try {
      await eventsApi.updateStatus(event.id, newStatus)
      updateEventStatus(event.id, newStatus)
    } catch {
      // toast handled by interceptor
    } finally {
      setUpdatingStatus(false)
    }
  }

  return (
    <div className={cn(
      'card p-4 transition-all animate-fade-in',
      event.priority === 'urgent' && 'border-l-4 border-l-red-500',
      event.priority === 'high' && 'border-l-4 border-l-orange-500',
    )}>
      {/* Header row */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2 flex-wrap min-w-0">
          <span className={cn('badge', priority.className)}>{priority.label}</span>
          <span className="badge bg-slate-100 text-slate-600 dark:bg-od-border dark:text-od-fg">
            {EVENT_TYPE_LABELS[event.event_type]}
          </span>
          <span className={cn('badge', STATUS_COLORS[event.status])}>
            {event.status.replace('_', ' ')}
          </span>
          {event.source === 'manual_chat' && (
            <span className="badge bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-400">
              <MessageCircle size={10} /> Manual
            </span>
          )}
          {event.source === 'whatsapp_group' && (
            <span className="badge bg-teal-100 text-teal-700 dark:bg-teal-900/40 dark:text-teal-400">
              <Smartphone size={10} /> WhatsApp
            </span>
          )}
          {event.source === 'file_upload' && (
            <span className="badge bg-violet-100 text-violet-700 dark:bg-violet-900/40 dark:text-violet-400">
              <FileText size={10} /> File
            </span>
          )}
        </div>
        <span className="text-xs text-slate-400 shrink-0 font-mono">
          {formatDistanceToNow(new Date(event.created_at), { addSuffix: true })}
        </span>
      </div>

      {/* Title */}
      <h3 className="mt-2 font-semibold text-slate-900 dark:text-slate-100 text-sm leading-snug">
        {event.title}
      </h3>

      {/* Description — truncated or expanded */}
      <p
        className={cn(
          'mt-1.5 text-sm text-slate-600 dark:text-od-fg leading-relaxed',
          !expanded && 'line-clamp-2'
        )}
      >
        {event.description}
      </p>

      {/* Expand/collapse */}
      {event.description.length > 150 && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="mt-1 flex items-center gap-1 text-xs text-amber-600 dark:text-amber-400 hover:underline"
        >
          {expanded ? <><ChevronUp size={12} /> Show less</> : <><ChevronDown size={12} /> Show more</>}
        </button>
      )}

      {/* Metadata row */}
      <div className="mt-3 flex flex-wrap gap-2 items-center">
        {event.property_id && (
          <span className="badge bg-blue-50 text-blue-700 dark:bg-od-border dark:text-od-accent font-mono text-xs">
            <Building2 size={10} /> {event.property_id}
          </span>
        )}
        {event.community_id && (
          <span className="badge bg-slate-100 text-slate-600 dark:bg-od-border dark:text-od-fg text-xs">
            {event.community_id}
          </span>
        )}
        {event.tenant_name && (
          <span className="badge bg-purple-50 text-purple-700 dark:bg-od-border dark:text-od-purple text-xs">
            <User size={10} /> {event.tenant_name}
          </span>
        )}
        {event.ai_confidence !== null && event.ai_confidence !== undefined && (
          <span className="ml-auto text-xs text-slate-400 font-mono">
            AI {Math.round(event.ai_confidence * 100)}%
          </span>
        )}
      </div>

      {/* Status selector */}
      <div className="mt-3 pt-3 border-t border-slate-100 dark:border-od-border flex items-center gap-2">
        <span className="text-xs text-slate-400">Status:</span>
        <select
          value={event.status}
          onChange={(e) => handleStatusChange(e.target.value as EventStatus)}
          disabled={updatingStatus}
          className="text-xs bg-transparent border border-slate-200 dark:border-od-border rounded-md px-2 py-1 text-slate-700 dark:text-od-fg focus:outline-none focus:ring-1 focus:ring-amber-500 disabled:opacity-50 cursor-pointer"
        >
          {STATUS_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
        {updatingStatus && (
          <span className="text-xs text-amber-500 animate-pulse">Saving...</span>
        )}
      </div>
    </div>
  )
}
