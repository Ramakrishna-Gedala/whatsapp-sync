export type MessageType = 'text' | 'image' | 'audio' | 'video' | 'document' | 'location'
export type MessageSource = 'whatsapp_group' | 'manual_chat'

export interface Message {
  id: string
  whatsapp_message_id: string
  group_id: string | null
  sender_id: string
  sender_name: string | null
  message_type: MessageType
  raw_content: string | null
  source: MessageSource
  processed: boolean
  whatsapp_timestamp: number
  created_at: string
}
