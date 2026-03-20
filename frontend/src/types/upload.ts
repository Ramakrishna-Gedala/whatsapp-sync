import type { Event } from './event'

export interface FileUploadResult {
  file_name: string
  total_messages_found: number
  events_created: number
  events_failed: number
  events: Event[]
  parse_errors: string[]
}

export interface SupportedTypesResponse {
  supported_mime_types: string[]
}
