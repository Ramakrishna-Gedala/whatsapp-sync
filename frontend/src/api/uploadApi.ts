import apiClient from './axiosClient'
import type { FileUploadResult } from '@/types/upload'

export const uploadApi = {
  uploadFile: async (file: File, groupId?: string): Promise<FileUploadResult> => {
    const formData = new FormData()
    formData.append('file', file)
    if (groupId) formData.append('group_id', groupId)

    const { data } = await apiClient.post<FileUploadResult>('/upload/file', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120_000, // large files + many OpenAI calls can take time
    })
    return data
  },

  getSupportedTypes: async (): Promise<string[]> => {
    const { data } = await apiClient.get<{ supported_mime_types: string[] }>(
      '/upload/supported-types'
    )
    return data.supported_mime_types
  },
}
