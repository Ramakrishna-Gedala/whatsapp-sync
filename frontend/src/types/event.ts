export type EventType =
  | 'maintenance_request'
  | 'lease_inquiry'
  | 'payment_issue'
  | 'move_in'
  | 'move_out'
  | 'noise_complaint'
  | 'safety_concern'
  | 'amenity_request'
  | 'general_inquiry'
  | 'other'

export type Priority = 'low' | 'medium' | 'high' | 'urgent'
export type EventStatus = 'open' | 'in_progress' | 'resolved' | 'closed'
export type MessageSource = 'whatsapp_group' | 'manual_chat' | 'file_upload'

export interface Event {
  id: string
  whatsapp_message_id: string
  group_id: string | null
  event_type: EventType
  priority: Priority
  status: EventStatus
  title: string
  description: string
  tenant_id: string | null
  tenant_name: string | null
  property_id: string | null
  community_id: string | null
  address: string | null
  ai_confidence: number | null
  source: MessageSource
  created_at: string
  updated_at: string
}

export interface EventsResponse {
  events: Event[]
  total: number
}

export interface ProcessMessagesResponse {
  events_created: number
  events_skipped: number
  events: Event[]
}

export interface ChatMessageResponse {
  event: Event
  formatted_message: string
}
