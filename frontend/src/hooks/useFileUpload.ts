import { useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { uploadApi } from '@/api/uploadApi'
import { useEventStore } from '@/store/useEventStore'
import type { FileUploadResult } from '@/types/upload'

export function useFileUpload() {
  const queryClient = useQueryClient()
  const prependEvents = useEventStore((s) => s.prependEvents)

  const { mutate: uploadFile, isPending, data: lastResult, reset } = useMutation({
    mutationFn: ({ file, groupId }: { file: File; groupId?: string }) =>
      uploadApi.uploadFile(file, groupId),

    onSuccess: (result: FileUploadResult) => {
      if (result.events.length > 0) {
        prependEvents(result.events)
      }
      queryClient.invalidateQueries({ queryKey: ['events'] })

      toast.success(
        `"${result.file_name}" processed — ` +
          `${result.events_created} events created from ${result.total_messages_found} messages` +
          (result.events_failed > 0 ? `, ${result.events_failed} failed` : '')
      )

      if (result.parse_errors.length > 0) {
        toast.warning(`Parse warnings: ${result.parse_errors.slice(0, 3).join(' | ')}`)
      }
    },

    onError: () => {
      // Global axios interceptor already shows a toast; no duplicate needed
    },
  })

  return {
    uploadFile,
    isPending,
    lastResult: lastResult ?? null,
    reset,
  }
}
