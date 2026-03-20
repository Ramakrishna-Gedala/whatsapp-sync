import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { chatApi } from '@/api/chatApi'
import { useEventStore } from '@/store/useEventStore'
import type { Event } from '@/types/event'

export function useChat() {
  const queryClient = useQueryClient()
  const prependEvents = useEventStore((s) => s.prependEvents)
  const [lastCreatedEvent, setLastCreatedEvent] = useState<Event | null>(null)

  const { mutate: submitMessage, isPending } = useMutation({
    mutationFn: (text: string) => chatApi.sendMessage(text),
    onSuccess: (data) => {
      prependEvents([data.event])
      setLastCreatedEvent(data.event)
      queryClient.invalidateQueries({ queryKey: ['events'] })
      toast.success(`Event created: ${data.event.title}`)
    },
    onError: () => {
      toast.error('Failed to parse message. Please try again.')
    },
  })

  return { submitMessage, isPending, lastCreatedEvent }
}
