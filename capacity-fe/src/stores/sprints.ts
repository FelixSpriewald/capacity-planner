import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { Sprint, SprintFilter, SortOption, AvailabilityResponse, SprintRoster } from '@/types'
import { apiClient } from '@/services/api'

export const useSprintsStore = defineStore('sprints', () => {
  // State
  const sprints = ref<Sprint[]>([])
  const selectedSprint = ref<Sprint | null>(null)
  const availability = ref<AvailabilityResponse | null>(null)
  const roster = ref<SprintRoster[]>([])
  const loading = ref(false)
  const rosterLoading = ref(false)
  const error = ref<string | null>(null)

  // Filters and sorting
  const filter = ref<SprintFilter>({})
  const sortOptions = ref<SortOption>({ field: 'start_date', direction: 'desc' })

  // Getters
  const filteredSprints = computed(() => {
    let result = [...sprints.value]

  // Apply filters
  if (filter.value.name) {
    result = result.filter((s) => s.name.toLowerCase().includes(filter.value.name!.toLowerCase()))
  }    // Apply sorting
    result.sort((a, b) => {
      const { field, direction } = sortOptions.value
      let aValue = a[field as keyof Sprint]
      let bValue = b[field as keyof Sprint]

      // Handle undefined values
      if (aValue === undefined && bValue === undefined) return 0
      if (aValue === undefined) return direction === 'asc' ? -1 : 1
      if (bValue === undefined) return direction === 'asc' ? 1 : -1

      if (typeof aValue === 'string') aValue = aValue.toLowerCase()
      if (typeof bValue === 'string') bValue = bValue.toLowerCase()

      if (aValue < bValue) return direction === 'asc' ? -1 : 1
      if (aValue > bValue) return direction === 'asc' ? 1 : -1
      return 0
    })

    return result
  })

  const activeSprints = computed(() => sprints.value.filter((s) => s.status === 'active'))

  const plannedSprints = computed(() => sprints.value.filter((s) => s.status === 'planned'))

  const finishedSprints = computed(() => sprints.value.filter((s) => s.status === 'finished'))

  const sprintsByStatus = computed(() => ({
    planned: plannedSprints.value,
    active: activeSprints.value,
    finished: finishedSprints.value,
  }))

  const stats = computed(() => ({
    total: sprints.value.length,
    planned: plannedSprints.value.length,
    active: activeSprints.value.length,
    finished: finishedSprints.value.length,
  }))

  // Actions
  async function fetchSprints() {
    try {
      loading.value = true
      error.value = null
      console.log('Store: fetching sprints from API...')
      const fetchedSprints = await apiClient.getSprints()
      console.log('Store: received sprints from API:', fetchedSprints)
      sprints.value = fetchedSprints
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch sprints'
      console.error('Failed to fetch sprints:', err)
    } finally {
      loading.value = false
    }
  }

  async function fetchSprint(id: number) {
    try {
      loading.value = true
      error.value = null
      const sprint = await apiClient.getSprint(id)
      selectedSprint.value = sprint
      return sprint
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch sprint'
      console.error('Failed to fetch sprint:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createSprint(sprintData: Omit<Sprint, 'sprint_id'>) {
    try {
      loading.value = true
      error.value = null
      const newSprint = await apiClient.createSprint(sprintData)
      sprints.value.push(newSprint)
      return newSprint
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create sprint'
      console.error('Failed to create sprint:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateSprint(id: number, sprintData: Partial<Sprint>) {
    try {
      loading.value = true
      error.value = null
      console.log('Store: updating sprint', id, 'with data:', sprintData)
      const updatedSprint = await apiClient.updateSprint(id, sprintData)
      console.log('Store: received updated sprint from API:', updatedSprint)

      const index = sprints.value.findIndex((s) => s.sprint_id === id)
      console.log('Store: found sprint at index:', index, 'in list of', sprints.value.length, 'sprints')
      if (index !== -1) {
        sprints.value[index] = updatedSprint
        console.log('Store: updated sprint in list')
      }

      if (selectedSprint.value?.sprint_id === id) {
        selectedSprint.value = updatedSprint
        console.log('Store: updated selected sprint')
      }

      return updatedSprint
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update sprint'
      console.error('Failed to update sprint:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteSprint(id: number) {
    try {
      loading.value = true
      error.value = null
      await apiClient.deleteSprint(id)

      sprints.value = sprints.value.filter((s) => s.sprint_id !== id)

      if (selectedSprint.value?.sprint_id === id) {
        selectedSprint.value = null
        availability.value = null
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete sprint'
      console.error('Failed to delete sprint:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchAvailability(sprintId: number) {
    try {
      loading.value = true
      error.value = null
      availability.value = await apiClient.getSprintAvailability(sprintId)
      return availability.value
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch availability'
      console.error('Failed to fetch availability:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateAvailabilityOverride(
    sprintId: number,
    memberId: number,
    day: string,
    state: 'available' | 'unavailable' | 'half' | null,
    reason?: string,
  ) {
    try {
      await apiClient.updateAvailabilityOverride(sprintId, memberId, day, { state, reason })

      // Refresh availability data
      await fetchAvailability(sprintId)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update override'
      console.error('Failed to update override:', err)
      throw err
    }
  }

  function selectSprint(sprint: Sprint | null) {
    selectedSprint.value = sprint
    if (!sprint) {
      availability.value = null
    }
  }

  function setFilter(newFilter: Partial<SprintFilter>) {
    filter.value = { ...filter.value, ...newFilter }
  }

  function setSorting(field: string, direction: 'asc' | 'desc') {
    sortOptions.value = { field, direction }
  }

  function clearError() {
    error.value = null
  }

  async function fetchRoster(sprintId: number) {
    try {
      rosterLoading.value = true
      error.value = null
      roster.value = await apiClient.getSprintRoster(sprintId)
      return roster.value
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch roster'
      console.error('Failed to fetch roster:', err)
      throw err
    } finally {
      rosterLoading.value = false
    }
  }

  async function addMemberToRoster(
    sprintId: number,
    memberData: { member_id: number; allocation: number; assignment_from?: string; assignment_to?: string }
  ) {
    try {
      rosterLoading.value = true
      error.value = null
      await apiClient.addMemberToRoster(sprintId, memberData)
      // Refresh roster
      await fetchRoster(sprintId)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to add member to roster'
      console.error('Failed to add member to roster:', err)
      throw err
    } finally {
      rosterLoading.value = false
    }
  }

  async function updateRosterMember(
    sprintId: number,
    memberData: { member_id: number; allocation: number; assignment_from?: string; assignment_to?: string }
  ) {
    try {
      rosterLoading.value = true
      error.value = null
      await apiClient.updateSprintRoster(sprintId, memberData.member_id, {
        allocation: memberData.allocation,
        assignment_from: memberData.assignment_from,
        assignment_to: memberData.assignment_to
      })
      // Refresh roster
      await fetchRoster(sprintId)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update roster member'
      console.error('Failed to update roster member:', err)
      throw err
    } finally {
      rosterLoading.value = false
    }
  }

  async function removeMemberFromRoster(sprintId: number, memberId: number) {
    try {
      if (rosterLoading.value) {
        console.log('Roster operation already in progress, skipping...')
        return
      }

      rosterLoading.value = true
      error.value = null
      await apiClient.removeMemberFromRoster(sprintId, memberId)
      // Refresh roster
      await fetchRoster(sprintId)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to remove member from roster'
      console.error('Failed to remove member from roster:', err)
      throw err
    } finally {
      rosterLoading.value = false
    }
  }

  function clearRoster() {
    roster.value = []
  }

  function clearAvailability() {
    availability.value = null
  }

  return {
    // State
    sprints,
    selectedSprint,
    availability,
    roster,
    loading,
    rosterLoading,
    error,
    filter,
    sortOptions,

    // Getters
    filteredSprints,
    activeSprints,
    plannedSprints,
    finishedSprints,
    sprintsByStatus,
    stats,

    // Actions
    fetchSprints,
    fetchSprint,
    createSprint,
    updateSprint,
    deleteSprint,
    fetchAvailability,
    updateAvailabilityOverride,
    fetchRoster,
    addMemberToRoster,
    updateRosterMember,
    removeMemberFromRoster,
    selectSprint,
    setFilter,
    setSorting,
    clearError,
    clearAvailability,
    clearRoster,
  }
})
