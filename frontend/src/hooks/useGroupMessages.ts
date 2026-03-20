import { useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { messagesApi } from '@/api/messagesApi'
import { useEventStore } from '@/store/useEventStore'

export function useGroupMessages() {
  const queryClient = useQueryClient()
  const prependEvents = useEventStore((s) => s.prependEvents)

  const { mutate: processMessages, isPending } = useMutation({
    mutationFn: ({ groupId, limit }: { groupId: string; limit?: number }) =>
      messagesApi.processMessages(groupId, limit),
    onSuccess: (data) => {
      if (data.events.length > 0) {
        prependEvents(data.events)
      }
      queryClient.invalidateQueries({ queryKey: ['events'] })

      if (data.events_created > 0) {
        toast.success(
          `Synced ${data.events_created} new event${data.events_created > 1 ? 's' : ''}` +
            (data.events_skipped > 0 ? `, ${data.events_skipped} already existed` : '')
        )
      } else {
        toast.info(
          data.events_skipped > 0
            ? `No new events — ${data.events_skipped} messages already processed`
            : 'No messages found in this group'
        )
      }
    },
    onError: () => {
      toast.error('Failed to process messages. Check your Green API connection.')
    },
  })

  return { processMessages, isPending }
}
