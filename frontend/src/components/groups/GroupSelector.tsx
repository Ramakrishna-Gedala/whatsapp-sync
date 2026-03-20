import { useGroupStore } from '@/store/useGroupStore'
import type { Group } from '@/types/group'
import { cn } from '@/lib/utils'

interface GroupSelectorProps {
  groups: Group[]
  isLoading: boolean
}

export default function GroupSelector({ groups, isLoading }: GroupSelectorProps) {
  const { selectedGroupId, setSelectedGroup } = useGroupStore()

  if (isLoading) {
    return (
      <div className="h-10 w-56 bg-slate-200 dark:bg-od-border animate-pulse rounded-lg" />
    )
  }

  return (
    <select
      value={selectedGroupId ?? ''}
      onChange={(e) => {
        const group = groups.find((g) => g.group_id === e.target.value)
        if (group) setSelectedGroup(group.group_id, group.name)
      }}
      disabled={groups.length === 0}
      className={cn(
        'text-sm bg-white dark:bg-od-bg2 border border-slate-200 dark:border-od-border',
        'rounded-lg px-3 py-2 text-slate-700 dark:text-od-fg',
        'focus:outline-none focus:ring-2 focus:ring-amber-500 cursor-pointer',
        'min-w-[200px] disabled:opacity-50 disabled:cursor-not-allowed'
      )}
    >
      <option value="">
        {groups.length === 0 ? 'No groups found' : 'Select a group...'}
      </option>
      {groups.map((group) => (
        <option key={group.group_id} value={group.group_id}>
          {group.name}
        </option>
      ))}
    </select>
  )
}
