import apiClient from './axiosClient'
import type { ProcessMessagesResponse } from '@/types/event'

export const messagesApi = {
  processMessages: async (groupId: string, limit = 2000): Promise<ProcessMessagesResponse> => {
    const { data } = await apiClient.post<ProcessMessagesResponse>(
      `/groups/${groupId}/messages/process`,
      { limit }
    )
    return data
  },
}
