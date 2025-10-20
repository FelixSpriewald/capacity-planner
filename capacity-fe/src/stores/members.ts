import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { Member, MemberFilter, SortOption } from '@/types'
import { apiClient } from '@/services/api'

export const useMembersStore = defineStore('members', () => {
  // State
  const members = ref<Member[]>([])
  const selectedMember = ref<Member | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Filters and sorting
  const filter = ref<MemberFilter>({})
  const sortOptions = ref<SortOption>({ field: 'name', direction: 'asc' })

  // Getters
  const filteredMembers = computed(() => {
    let result = [...members.value]

    // Apply filters
    if (filter.value.active !== undefined) {
      result = result.filter((m) => m.active === filter.value.active)
    }

    if (filter.value.region_code) {
      result = result.filter((m) => m.region_code === filter.value.region_code)
    }

    if (filter.value.search) {
      const search = filter.value.search.toLowerCase()
      result = result.filter(
        (m) =>
          m.name.toLowerCase().includes(search) || m.region_code.toLowerCase().includes(search),
      )
    }

    // Apply sorting
    result.sort((a, b) => {
      const { field, direction } = sortOptions.value
      let aValue = a[field as keyof Member]
      let bValue = b[field as keyof Member]

      if (typeof aValue === 'string') aValue = aValue.toLowerCase()
      if (typeof bValue === 'string') bValue = bValue.toLowerCase()

      if (aValue < bValue) return direction === 'asc' ? -1 : 1
      if (aValue > bValue) return direction === 'asc' ? 1 : -1
      return 0
    })

    return result
  })

  const activeMembers = computed(() => members.value.filter((m) => m.active))

  const membersByRegion = computed(() => {
    const regions = new Map<string, Member[]>()
    for (const member of members.value) {
      if (!regions.has(member.region_code)) {
        regions.set(member.region_code, [])
      }
      regions.get(member.region_code)!.push(member)
    }
    return Object.fromEntries(regions)
  })

  const stats = computed(() => ({
    total: members.value.length,
    active: activeMembers.value.length,
    inactive: members.value.length - activeMembers.value.length,
    totalCapacity: activeMembers.value.reduce((sum, m) => sum + m.employment_ratio * 40, 0),
    uniqueRegions: new Set(members.value.map((m) => m.region_code)).size,
  }))

  // Actions
  async function fetchMembers(includeInactive: boolean = true) {
    try {
      loading.value = true
      error.value = null
      members.value = await apiClient.getMembers(includeInactive)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch members'
      console.error('Failed to fetch members:', err)
    } finally {
      loading.value = false
    }
  }

  async function fetchMember(id: number) {
    try {
      loading.value = true
      error.value = null
      const member = await apiClient.getMember(id)
      selectedMember.value = member
      return member
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch member'
      console.error('Failed to fetch member:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createMember(memberData: Omit<Member, 'member_id'>) {
    try {
      loading.value = true
      error.value = null

      const newMember = await apiClient.createMember(memberData)
      members.value.push(newMember)
      return newMember
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create member'
      console.error('Failed to create member:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateMember(id: number, memberData: Partial<Member>) {
    try {
      loading.value = true
      error.value = null

      // Get current member data to merge with updates
      const currentMember = members.value.find(m => m.member_id === id)
      if (!currentMember) {
        throw new Error('Member not found in local state')
      }

      // Merge partial updates with existing data to create complete member object
      const completeData = {
        name: memberData.name ?? currentMember.name,
        employment_ratio: memberData.employment_ratio ?? currentMember.employment_ratio,
        region_code: memberData.region_code ?? currentMember.region_code,
        active: memberData.active ?? currentMember.active
      }

      const updatedMember = await apiClient.updateMember(id, completeData)

      const index = members.value.findIndex((m) => m.member_id === id)
      if (index !== -1) {
        members.value[index] = updatedMember
      }

      if (selectedMember.value?.member_id === id) {
        selectedMember.value = updatedMember
      }

      return updatedMember
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update member'
      console.error('Failed to update member:', err)

      // If member not found, refresh the members list
      if (err instanceof Error && err.message.includes('404')) {
        console.log('Member not found, refreshing members list...')
        await fetchMembers()
      }

      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteMember(id: number) {
    try {
      loading.value = true
      error.value = null

      await apiClient.deleteMember(id)

      // Update the member as inactive instead of removing from list
      const memberIndex = members.value.findIndex((m) => m.member_id === id)
      if (memberIndex !== -1) {
        const currentMember = members.value[memberIndex]
        if (currentMember) {
          members.value[memberIndex] = {
            member_id: currentMember.member_id,
            name: currentMember.name,
            employment_ratio: currentMember.employment_ratio,
            region_code: currentMember.region_code,
            active: false
          }
        }
      }

      if (selectedMember.value?.member_id === id) {
        selectedMember.value = null
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete member'
      console.error('Failed to delete member:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  function selectMember(member: Member | null) {
    selectedMember.value = member
  }

  function setFilter(newFilter: Partial<MemberFilter>) {
    filter.value = { ...filter.value, ...newFilter }
  }

  function setSorting(field: string, direction: 'asc' | 'desc') {
    sortOptions.value = { field, direction }
  }

  async function reactivateMember(id: number) {
    const member = members.value.find(m => m.member_id === id)
    if (!member) {
      throw new Error('Member nicht gefunden')
    }

    return updateMember(id, { active: true })
  }

  function clearError() {
    error.value = null
  }

  return {
    // State
    members,
    selectedMember,
    loading,
    error,
    filter,
    sortOptions,

    // Getters
    filteredMembers,
    activeMembers,
    membersByRegion,
    stats,

    // Actions
    fetchMembers,
    fetchMember,
    createMember,
    updateMember,
    deleteMember,
    reactivateMember,
    selectMember,
    setFilter,
    setSorting,
    clearError,
  }
})
