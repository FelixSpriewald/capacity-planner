<template>
  <div class="sprints-view">
    <div class="page-header">
      <h1 class="page-title">
        <i class="pi pi-calendar"></i>
        Sprint Management
      </h1>
      <Button
        label="Neuer Sprint"
        icon="pi pi-plus"
        @click="createSprint"
        class="p-button-success"
      />
    </div>

    <div class="content-grid">
      <!-- Sprint Liste -->
      <div class="sprint-list">
        <Card>
          <template #title>Aktuelle Sprints</template>
          <template #content>
            <div v-if="loading" class="loading-state">
              <ProgressSpinner size="50px" />
              <p>Lade Sprints...</p>
            </div>

            <div v-else-if="sprints.length === 0" class="empty-state">
              <i class="pi pi-calendar-plus empty-icon"></i>
              <h3>Keine Sprints vorhanden</h3>
              <p>Erstelle deinen ersten Sprint um zu beginnen</p>
              <Button
                label="Sprint erstellen"
                icon="pi pi-plus"
                @click="createSprint"
                class="p-button-outlined"
              />
            </div>

            <div v-else class="sprint-cards">
              <Card
                v-for="sprint in sprints"
                :key="sprint.sprint_id"
                class="sprint-card"
              >
                <template #title>
                  <div class="sprint-title-row">
                    <span>{{ sprint.name }}</span>
                    <Button
                      icon="pi pi-pencil"
                      class="p-button-text p-button-sm"
                      @click="editSprint(sprint)"
                      v-tooltip="'Sprint bearbeiten'"
                    />
                  </div>
                </template>
                <template #content>
                  <div class="sprint-content">
                    <div class="sprint-info">
                      <div class="sprint-dates">
                        <span class="date-range">
                          {{ formatDateRange(sprint.start_date, sprint.end_date) }}
                        </span>
                        <Tag :value="getStatusLabel(sprint.status)" :severity="getStatusSeverity(sprint.status)" />
                      </div>
                      <div class="sprint-stats">
                        <div class="stat-item">
                          <i class="pi pi-users"></i>
                          <span>{{ sprint.member_count || 0 }} Teilnehmer</span>
                        </div>
                        <div class="stat-item">
                          <i class="pi pi-clock"></i>
                          <span>{{ sprint.total_capacity_hours || 0 }}h Kapazität</span>
                        </div>
                        <div class="stat-item">
                          <i class="pi pi-calendar"></i>
                          <span>{{ sprint.working_days || 0 }} Arbeitstage</span>
                        </div>
                      </div>
                      <div class="sprint-actions-bottom">
                        <Button
                          label="Team Roster"
                          icon="pi pi-users"
                          class="p-button-outlined p-button-sm"
                          @click="selectSprint(sprint); showRoster()"
                        />
                        <Button
                          label="Verfügbarkeit"
                          icon="pi pi-calendar"
                          class="p-button-outlined p-button-sm"
                          @click="selectSprint(sprint); showAvailability()"
                        />
                      </div>
                    </div>
                  </div>
                </template>
              </Card>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Sprint Form Dialog -->
    <SprintForm
      v-model:visible="showSprintForm"
      :sprint="editingSprint"
      :loading="formLoading"
      @submit="handleSprintSubmit"
    />

    <!-- Team Roster Dialog -->
    <TeamRosterDialog
      v-model:visible="showRosterDialog"
      :sprint="selectedSprint"
      :roster="roster"
      :members="members"
      :loading="rosterLoading"
      @add-member="handleAddMember"
      @update-member="handleUpdateMember"
      @remove-member="handleRemoveMember"
      @update:visible="handleRosterDialogClose"
    />

    <!-- Availability Dialog -->
    <AvailabilityDialog
      v-model:visible="showAvailabilityDialog"
      :sprint="selectedSprint"
      :loading="availabilityLoading"
      :availability="availabilityData"
      @toggle-availability="handleToggleAvailability"
      @open-roster="handleOpenRosterFromAvailability"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'


// PrimeVue Components
import Button from 'primevue/button'
import Card from 'primevue/card'
import Tag from 'primevue/tag'
import ProgressSpinner from 'primevue/progressspinner'

import SprintForm from '@/components/forms/SprintForm.vue'
import TeamRosterDialog from '@/components/dialogs/TeamRosterDialog.vue'
import AvailabilityDialog from '@/components/dialogs/AvailabilityDialog.vue'

// Stores and API
import { useSprintsStore } from '@/stores/sprints'
import { useMembersStore } from '@/stores/members'
import api from '@/services/api'

// Types
import type { Sprint, SprintStatus, SprintRoster, AvailabilityResponse, DayAvailability } from '@/types'

// Store instances
const sprintsStore = useSprintsStore()
const membersStore = useMembersStore()
const toast = useToast()


// Reactive state
const loading = ref(false)
const formLoading = ref(false)
const rosterLoading = ref(false)
const availabilityLoading = ref(false)

const showSprintForm = ref(false)
const showRosterDialog = ref(false)
const showAvailabilityDialog = ref(false)


const editingSprint = ref<Sprint | null>(null)
const selectedSprint = ref<Sprint | null>(null)

const roster = ref<SprintRoster[]>([])
const availabilityData = ref<AvailabilityResponse | null>(null)

// Computed properties
const sprints = computed(() => sprintsStore.sprints)
const members = computed(() => membersStore.members)

// Functions
const selectSprint = (sprint: Sprint) => {
  selectedSprint.value = sprint
}

const createSprint = () => {
  editingSprint.value = null
  showSprintForm.value = true
}

// Types
interface SprintFormData {
  name: string
  start_date: string
  end_date: string
  status?: SprintStatus
}



const handleSprintSubmit = async (formData: SprintFormData) => {
  try {
    formLoading.value = true

    if (editingSprint.value) {
      await sprintsStore.updateSprint(editingSprint.value.sprint_id, formData)
      await sprintsStore.fetchSprints()
      toast.add({
        severity: 'success',
        summary: 'Erfolg',
        detail: 'Sprint wurde erfolgreich aktualisiert',
        life: 3000
      })
    } else {
      const sprintData = {
        ...formData,
        status: (formData.status || 'draft') as SprintStatus
      }
      const newSprint = await sprintsStore.createSprint(sprintData)
      await sprintsStore.fetchSprints()
      toast.add({
        severity: 'success',
        summary: 'Erfolg',
        detail: `Sprint "${newSprint.name}" wurde erfolgreich erstellt`,
        life: 3000
      })
    }

    showSprintForm.value = false
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: err instanceof Error ? err.message : 'Fehler beim Speichern des Sprints',
      life: 5000
    })
  } finally {
    formLoading.value = false
  }
}

const editSprint = (sprint: Sprint) => {
  editingSprint.value = sprint
  showSprintForm.value = true
}



// Team Management
const handleAddMember = async (memberData: { member_id: number; allocation: number; assignment_from?: string; assignment_to?: string }) => {
  if (!selectedSprint.value) return

  try {
    rosterLoading.value = true

    await api.addMemberToRoster(selectedSprint.value.sprint_id, memberData)

    // Reload roster data
    const data = await api.getSprintRoster(selectedSprint.value.sprint_id)
    roster.value = data || []

    toast.add({
      severity: 'success',
      summary: 'Erfolg',
      detail: 'Team-Mitglied wurde hinzugefügt',
      life: 3000
    })
  } catch (error) {
    console.error('Error adding member:', error)
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: 'Fehler beim Hinzufügen des Team-Mitglieds',
      life: 3000
    })
  } finally {
    rosterLoading.value = false
  }
}

const handleUpdateMember = async (memberData: { member_id: number; allocation: number; assignment_from?: string; assignment_to?: string }) => {
  if (!selectedSprint.value) return

  try {
    rosterLoading.value = true

    await api.updateSprintRoster(selectedSprint.value.sprint_id, memberData.member_id, memberData)

    // Reload roster data
    const data = await api.getSprintRoster(selectedSprint.value.sprint_id)
    roster.value = data || []

    toast.add({
      severity: 'success',
      summary: 'Erfolg',
      detail: 'Team-Mitglied wurde aktualisiert',
      life: 3000
    })
  } catch (error) {
    console.error('Error updating member:', error)
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: 'Fehler beim Aktualisieren des Team-Mitglieds',
      life: 3000
    })
  } finally {
    rosterLoading.value = false
  }
}

const handleRemoveMember = async (memberId: number) => {
  if (!selectedSprint.value) return

  try {
    rosterLoading.value = true

    await api.removeMemberFromRoster(selectedSprint.value.sprint_id, memberId)

    // Reload roster data
    const data = await api.getSprintRoster(selectedSprint.value.sprint_id)
    roster.value = data || []

    toast.add({
      severity: 'success',
      summary: 'Erfolg',
      detail: 'Team-Mitglied wurde entfernt',
      life: 3000
    })
  } catch (error) {
    console.error('Error removing member:', error)
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: 'Fehler beim Entfernen des Team-Mitglieds',
      life: 3000
    })
  } finally {
    rosterLoading.value = false
  }
}

const showAvailability = async () => {
  if (!selectedSprint.value) return

  availabilityLoading.value = true
  try {
    const data = await api.getSprintAvailability(selectedSprint.value.sprint_id)
    availabilityData.value = data
  } catch (error) {
    console.error('Error loading availability:', error)
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: 'Fehler beim Laden der Verfügbarkeitsdaten',
      life: 3000
    })
  } finally {
    availabilityLoading.value = false
  }

  showAvailabilityDialog.value = true
}

const showRoster = async () => {
  if (!selectedSprint.value) return

  rosterLoading.value = true
  try {
    const data = await api.getSprintRoster(selectedSprint.value.sprint_id)
    roster.value = data || []
  } catch (error) {
    console.error('Error loading roster:', error)
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: 'Fehler beim Laden des Team Rosters',
      life: 3000
    })
  } finally {
    rosterLoading.value = false
  }

  showRosterDialog.value = true
}

const handleRosterDialogClose = async (visible: boolean) => {
  showRosterDialog.value = visible

  // When dialog is closed, refresh sprint data to update member count
  if (!visible) {
    try {
      await sprintsStore.fetchSprints()
    } catch (error) {
      console.error('Error refreshing sprints:', error)
    }
  }
}

const handleOpenRosterFromAvailability = () => {
  showAvailabilityDialog.value = false
  showRoster()
}

const handleToggleAvailability = async (memberId: number, date: string, currentDay: DayAvailability) => {
  if (!selectedSprint.value) return

  try {
    availabilityLoading.value = true

    const currentState = currentDay.override_state || currentDay.final_state
    let newState: 'available' | 'half' | 'unavailable' | null = 'available'

    // Cycle through: available → half → unavailable → available
    switch (currentState) {
      case 'available':
        newState = 'half'
        break
      case 'half':
        newState = 'unavailable'
        break
      case 'out': // Backend uses 'out', but API expects 'unavailable'
        newState = 'available'
        break
      case null:
      default:
        newState = 'available'
        break
    }

    // Use the store to update availability
    await sprintsStore.updateAvailabilityOverride(
      selectedSprint.value.sprint_id,
      memberId,
      date,
      newState,
      'Manual override'
    )

    // Reload availability data
    const data = await api.getSprintAvailability(selectedSprint.value.sprint_id)
    availabilityData.value = data

    toast.add({
      severity: 'success',
      summary: 'Erfolg',
      detail: 'Verfügbarkeit wurde aktualisiert',
      life: 2000
    })
  } catch (err) {
    console.error('Error updating availability:', err)
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: 'Fehler beim Aktualisieren der Verfügbarkeit',
      life: 3000
    })
  } finally {
    availabilityLoading.value = false
  }
}

// Utility functions
const formatDateRange = (startDate: string, endDate: string) => {
  const start = new Date(startDate).toLocaleDateString('de-DE', {
    day: '2-digit',
    month: '2-digit'
  })
  const end = new Date(endDate).toLocaleDateString('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
  return `${start} - ${end}`
}

const getStatusLabel = (status: SprintStatus) => {
  const labels = {
    'planned': 'Geplant',
    'active': 'Aktiv',
    'finished': 'Abgeschlossen'
  }
  return labels[status] || status
}

const getStatusSeverity = (status: SprintStatus) => {
  const severities = {
    'planned': 'info',
    'active': 'success',
    'finished': 'secondary'
  }
  return severities[status] || 'info'
}

// Lifecycle
onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([
      sprintsStore.fetchSprints(),
      membersStore.fetchMembers()
    ])
  } catch (err) {
    console.error('Error loading data:', err)
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: 'Fehler beim Laden der Daten',
      life: 5000
    })
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.sprints-view {
  padding: 1rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  color: var(--primary-color);
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

.sprint-list {
  min-height: 400px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
}

.empty-icon {
  font-size: 4rem;
  color: var(--surface-400);
  margin-bottom: 1rem;
}

.sprint-cards {
  display: grid;
  gap: 1rem;
}

.sprint-card {
  border: 1px solid var(--surface-border);
  transition: all 0.3s ease;
}

.sprint-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.sprint-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sprint-content {
  padding: 0;
}

.sprint-dates {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.date-range {
  font-weight: 500;
  color: var(--text-color-secondary);
}

.sprint-stats {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: var(--text-color-secondary);
}

.stat-item i {
  color: var(--primary-color);
}

.sprint-actions-bottom {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

/* Availability Dialog */
.availability-dialog {
  .p-dialog-content {
    padding: 0;
  }
}

.availability-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.availability-controls {
  padding: 1rem;
  border-bottom: 1px solid var(--surface-border);
  background: var(--surface-50);
}

.weekend-filter label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.availability-grid-container {
  flex: 1;
  overflow: auto;
  padding: 1rem;
}

.availability-grid {
  display: table;
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

.grid-header,
.grid-row,
.grid-totals {
  display: table-row;
}

.member-header,
.day-header,
.member-cell,
.availability-cell,
.total-cell {
  display: table-cell;
  padding: 8px 4px;
  border: 1px solid var(--surface-border);
  text-align: center;
  vertical-align: middle;
}

.member-header,
.member-cell {
  min-width: 150px;
  text-align: left;
  background: var(--surface-50);
  font-weight: 500;
  position: sticky;
  left: 0;
  z-index: 1;
}

.day-header {
  min-width: 60px;
  background: var(--surface-100);
  font-size: 0.8rem;
}

.day-header.weekend-day {
  background: var(--orange-100);
  color: var(--orange-800);
}

.day-header.after-weekend {
  border-left: 3px solid var(--primary-color);
}

.day-name {
  font-weight: 600;
}

.day-date {
  font-size: 0.7rem;
  opacity: 0.8;
}

.availability-cell {
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  min-width: 40px;
  height: 40px;
}

.availability-cell:hover {
  background: var(--surface-200);
}

.availability-cell.weekend-day {
  background: var(--orange-50);
}

.availability-cell.after-weekend {
  border-left: 3px solid var(--primary-color);
}

.availability-indicator {
  width: 100%;
  height: 100%;
  border-radius: 4px;
}

.availability-cell.available .availability-indicator {
  background: var(--green-500);
}

.availability-cell.half-available .availability-indicator {
  background: var(--orange-500);
}

.availability-cell.unavailable .availability-indicator {
  background: var(--red-500);
}

.availability-cell.weekend .availability-indicator {
  background: var(--surface-300);
}

.availability-cell.unknown .availability-indicator {
  background: var(--surface-200);
}

.grid-totals {
  border-top: 2px solid var(--primary-color);
  background: var(--surface-50);
}

.totals-label {
  background: var(--surface-100);
  font-weight: 600;
}

.total-cell {
  font-weight: 600;
  color: var(--primary-color);
}

.loading-container,
.empty-availability {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  height: 400px;
}

.empty-availability i {
  font-size: 3rem;
  color: var(--surface-400);
  margin-bottom: 1rem;
}

@media (max-width: 768px) {
  .sprint-stats {
    flex-direction: column;
    gap: 0.5rem;
  }

  .sprint-actions-bottom {
    flex-direction: column;
  }

  .availability-grid {
    font-size: 0.8rem;
  }

  .member-header,
  .member-cell {
    min-width: 120px;
  }

  .day-header,
  .availability-cell {
    min-width: 35px;
  }
}
</style>
