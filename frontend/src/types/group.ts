export interface Group {
  id: string
  group_id: string
  name: string
  description: string | null
}

export interface GroupsResponse {
  groups: Group[]
  total: number
}
