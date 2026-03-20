import { Link } from 'react-router-dom'
import { ArrowRight, Building2, User, MapPin } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { Event, Priority } from '@/types/event'

const PRIORITY_CONFIG: Record<Priority, { label: string; className: string }> = {
  urgent: { label: 'URGENT', className: 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-400' },
  high: { label: 'HIGH', className: 'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-400' },
  medium: { label: 'MEDIUM', className: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-400' },
  low: { label: 'LOW', className: 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-400' },
}

const EVENT_ICONS: Record<string, string> = {
  maintenance_request: '🔧',
  lease_inquiry: '📋',
  payment_issue: '💳',
  move_in: '📦',
  move_out: '🚚',
  noise_complaint: '🔊',
  safety_concern: '⚠️',
  amenity_request: '🏊',
  general_inquiry: '❓',
  other: '📝',
}

interface ChatEventPreviewProps {
  event: Event
}

export default function ChatEventPreview({ event }: ChatEventPreviewProps) {
  const priority = PRIORITY_CONFIG[event.priority]
  const icon = EVENT_ICONS[event.event_type] ?? '📝'
  const confidence = event.ai_confidence !== null ? Math.round((event.ai_confidence ?? 0) * 100) : null

  return (
    <div className="card p-5 animate-slide-in space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xl">{icon}</span>
          <span className="font-semibold text-slate-800 dark:text-slate-100 capitalize">
            {event.event_type.replace(/_/g, ' ')}
          </span>
          <span className={cn('badge', priority.className)}>{priority.label}</span>
        </div>
        <span className="badge bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-400">
          Created
        </span>
      </div>

      <div>
        <p className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-1">Title</p>
        <p className="text-sm font-medium text-slate-800 dark:text-slate-100">{event.title}</p>
      </div>

      <div className="flex flex-wrap gap-3">
        {event.property_id && (
          <div className="flex items-center gap-1.5 text-sm text-slate-600 dark:text-od-fg">
            <Building2 size={14} className="text-amber-500" />
            <span className="font-mono">{event.property_id}</span>
          </div>
        )}
        {event.community_id && (
          <div className="flex items-center gap-1.5 text-sm text-slate-600 dark:text-od-fg">
            <span className="text-amber-500">🏘</span>
            {event.community_id}
          </div>
        )}
        {event.tenant_name && (
          <div className="flex items-center gap-1.5 text-sm text-slate-600 dark:text-od-fg">
            <User size={14} className="text-amber-500" />
            {event.tenant_name}
          </div>
        )}
        {event.address && (
          <div className="flex items-center gap-1.5 text-sm text-slate-600 dark:text-od-fg">
            <MapPin size={14} className="text-amber-500" />
            {event.address}
          </div>
        )}
      </div>

      <div>
        <p className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-1">Description</p>
        <p className="text-sm text-slate-600 dark:text-od-fg leading-relaxed">{event.description}</p>
      </div>

      {confidence !== null && (
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">AI Confidence</p>
            <span className="text-xs font-mono text-slate-600 dark:text-od-fg">{confidence}%</span>
          </div>
          <div className="h-1.5 bg-slate-100 dark:bg-od-border rounded-full overflow-hidden">
            <div
              className={cn(
                'h-full rounded-full transition-all',
                confidence >= 80 ? 'bg-green-500' :
                confidence >= 60 ? 'bg-yellow-500' : 'bg-orange-500'
              )}
              style={{ width: `${confidence}%` }}
            />
          </div>
        </div>
      )}

      <Link
        to="/events"
        className="flex items-center gap-1.5 text-sm text-amber-600 dark:text-amber-400 hover:underline font-medium"
      >
        View all events <ArrowRight size={14} />
      </Link>
    </div>
  )
}
