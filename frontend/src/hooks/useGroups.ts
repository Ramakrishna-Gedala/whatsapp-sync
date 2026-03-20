import { useQuery } from '@tanstack/react-query'
import { groupsApi } from '@/api/groupsApi'
import type { Group } from '@/types/group'

export function useGroups() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['groups'],
    queryFn: groupsApi.getGroups,
    staleTime: 60_000,
  })

  const groups: Group[] = data?.groups ?? []
  return { groups, isLoading, error }
}
