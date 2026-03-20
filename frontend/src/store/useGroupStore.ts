import { create } from 'zustand'

interface GroupStore {
  selectedGroupId: string | null
  selectedGroupName: string | null
  setSelectedGroup: (id: string, name: string) => void
  clearGroup: () => void
}

export const useGroupStore = create<GroupStore>((set) => ({
  selectedGroupId: null,
  selectedGroupName: null,
  setSelectedGroup: (id, name) => set({ selectedGroupId: id, selectedGroupName: name }),
  clearGroup: () => set({ selectedGroupId: null, selectedGroupName: null }),
}))
