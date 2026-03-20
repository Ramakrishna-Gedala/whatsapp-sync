import apiClient from './axiosClient'
import type { GroupsResponse, Group } from '@/types/group'

export const groupsApi = {
  getGroups: async (): Promise<GroupsResponse> => {
    const { data } = await apiClient.get<GroupsResponse>('/groups')
    return data
  },

  getGroup: async (groupId: string): Promise<Group> => {
    const { data } = await apiClient.get<Group>(`/groups/${groupId}`)
    return data
  },
}
