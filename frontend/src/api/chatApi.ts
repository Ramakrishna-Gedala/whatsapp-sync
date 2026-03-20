import apiClient from './axiosClient'
import type { ChatMessageResponse } from '@/types/event'

export const chatApi = {
  sendMessage: async (text: string, messageType = 'text'): Promise<ChatMessageResponse> => {
    const { data } = await apiClient.post<ChatMessageResponse>('/chat/message', {
      text,
      message_type: messageType,
    })
    return data
  },
}
